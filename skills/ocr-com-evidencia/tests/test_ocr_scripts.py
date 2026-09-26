"""Seam tests for the photo OCR helper scripts. No network required.

The seams are the three CLIs (``rectify_photos.py``, ``ocr_photos.py``,
``batch_ocr.py``) and the manifests they write. Tests that need Tesseract
skip when it is not on ``PATH``; everything else runs with RapidOCR alone.

Run from the skill directory with the environment that has the dependencies:

    uv run --with pytest --python ~/.venvs/ocr-docs/bin/python -m pytest tests
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
CLIS = ["rectify_photos.py", "ocr_photos.py", "batch_ocr.py"]
HAS_TESSERACT = shutil.which("tesseract") is not None
needs_tesseract = pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract not on PATH")
MISSING_PACK = "xyz"  # no Tesseract distribution ships a language with this code

# Words a Portuguese-capable engine must read back with their diacritics.
ANCHORS = ["Seção", "Coordenação", "licitação", "aptidão", "órgão", "cônjuge", "três", "exceção", "União", "em 12/08/2026"]
PAGE_LINES = [
    "A licitação exigirá comprovação de aptidão técnica.",
    "Ação, órgão, cônjuge, três, avaliação, exceção.",
    "Valores: 1.234,56 e 987,00 em 12/08/2026.",
    "Página 47 — Tribunal de Contas da União.",
]
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]


def run(script: str, *args: str, expect: int | None = 0) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, encoding="utf-8", env=env,
    )
    if expect is not None:
        assert proc.returncode == expect, f"{script} {args}: rc={proc.returncode}\n{proc.stderr}"
    return proc


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def synthetic_photo(target: Path, title: str) -> Path:
    """Render a white page with Portuguese text on a grey, slightly rotated background."""
    page = Image.new("RGB", (1000, 740), "white")
    draw = ImageDraw.Draw(page)
    draw.text((60, 50), title, font=font(34), fill="black")
    y = 130
    for line in PAGE_LINES:
        draw.text((60, y), line, font=font(24), fill="black")
        y += 48
    photo = Image.new("RGB", (1300, 1000), (90, 90, 95))
    photo.paste(page, (150, 130))
    photo = photo.rotate(2.0, resample=Image.Resampling.BICUBIC, fillcolor=(90, 90, 95))
    target.parent.mkdir(parents=True, exist_ok=True)
    photo.save(target, quality=92) if target.suffix.lower() in {".jpg", ".jpeg"} else photo.save(target)
    return target


def corrupt_image(target: Path) -> Path:
    """A file with an image extension whose bytes no decoder accepts."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"this is not an image\x00\x01\x02")
    return target


@pytest.fixture(scope="module")
def png_dir(tmp_path_factory) -> Path:
    directory = tmp_path_factory.mktemp("png_in")
    synthetic_photo(directory / "pagina_teste.png", "Seção 3 — Coordenação e Manutenção")
    return directory


@pytest.fixture(scope="module")
def sideways_dir(tmp_path_factory) -> Path:
    """The same page photographed with the phone held sideways (no EXIF orientation)."""
    directory = tmp_path_factory.mktemp("sideways_in")
    upright = synthetic_photo(directory / "_upright.png", "Seção 3 — Coordenação e Manutenção")
    with Image.open(upright) as image:
        image.rotate(90, expand=True).save(directory / "deitada.png")
    upright.unlink()
    return directory


@pytest.fixture(scope="module")
def mixed_dir(tmp_path_factory) -> Path:
    """One readable page next to one corrupt file."""
    directory = tmp_path_factory.mktemp("mixed_in")
    synthetic_photo(directory / "boa.png", "Seção 9 — Página legível")
    corrupt_image(directory / "ruim.png")
    return directory


@pytest.fixture(scope="module")
def homonyms(tmp_path_factory) -> tuple[Path, Path]:
    """Two different photos that share a file name in different directories."""
    root = tmp_path_factory.mktemp("homonyms")
    first = synthetic_photo(root / "a" / "pagina.png", "Seção 1 — Primeira página")
    second = synthetic_photo(root / "b" / "pagina.png", "Seção 2 — Segunda página")
    return first, second


def candidate_texts(ocr_dir: Path, engine: str) -> list[str]:
    return [p.read_text(encoding="utf-8") for p in (ocr_dir / "candidates").glob(f"*_{engine}_*.txt")]


class TestInputs:
    @pytest.mark.parametrize("script", CLIS)
    def test_directory_without_images_is_an_error(self, script, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        proc = run(script, str(empty), "--output-dir", str(tmp_path / "out"), expect=None)
        assert proc.returncode == 2
        assert "no supported image" in proc.stderr.lower()

    @pytest.mark.parametrize("script", CLIS)
    def test_explicit_path_that_does_not_exist_is_an_error(self, script, png_dir, tmp_path):
        ghost = tmp_path / "nao_existe.png"
        proc = run(script, str(png_dir / "pagina_teste.png"), str(ghost), "--output-dir", str(tmp_path / "out"), expect=None)
        assert proc.returncode == 2
        assert ghost.name in proc.stderr
        assert not (tmp_path / "out").exists(), "nothing may be written when an input is rejected"


class TestRectifyPhotos:
    def test_png_directory_is_processed(self, png_dir, tmp_path):
        run("rectify_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"))
        records = load(tmp_path / "out" / "rectification_manifest.json")["files"]
        assert len(records) == 1
        assert records[0]["status"] in {"rectified", "abstain"}
        assert Path(records[0]["source_path"]).is_absolute()

    def test_several_inputs_in_one_run(self, homonyms, tmp_path):
        first, second = homonyms
        run("rectify_photos.py", str(first), str(second), "--output-dir", str(tmp_path / "out"))
        records = load(tmp_path / "out" / "rectification_manifest.json")["files"]
        assert len(records) == 2

    def test_homonymous_sources_do_not_collide(self, homonyms, tmp_path):
        first, second = homonyms
        run("rectify_photos.py", str(first), str(second), "--output-dir", str(tmp_path / "out"))
        records = load(tmp_path / "out" / "rectification_manifest.json")["files"]
        assert {r["source_path"] for r in records} == {str(first.resolve()), str(second.resolve())}
        outputs = [r["output"] for r in records if r["status"] == "rectified"]
        assert len(outputs) == len(set(outputs))

    def test_corrupt_image_is_recorded_not_fatal(self, mixed_dir, tmp_path):
        run("rectify_photos.py", str(mixed_dir), "--output-dir", str(tmp_path / "out"))
        records = {r["source"]: r for r in load(tmp_path / "out" / "rectification_manifest.json")["files"]}
        assert records["ruim.png"]["status"] == "error"
        assert records["boa.png"]["status"] in {"rectified", "abstain"}


class TestOcrPhotos:
    def test_png_directory_is_processed(self, png_dir, tmp_path):
        run("ocr_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", expect=None)
        manifest = load(tmp_path / "out" / "manifest.json")
        assert [f["source"] for f in manifest["files"]] == ["pagina_teste.png"]

    def test_requested_language_is_not_claimed_without_an_engine_that_applies_it(self, png_dir, tmp_path):
        proc = run("ocr_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--no-tesseract", expect=3)
        manifest = load(tmp_path / "out" / "manifest.json")
        assert manifest["language_requested"] == "por"
        assert manifest["language_applied_by"] == []
        assert manifest["status"] == "completed_language_unapplied"
        assert any("not applied" in w for w in manifest["warnings"])
        assert "language" not in manifest, "the old ambiguous key must not survive"
        assert proc.returncode == 3

    @needs_tesseract
    def test_tesseract_present_but_pack_missing_is_reported_unapplied(self, png_dir, tmp_path):
        proc = run("ocr_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", MISSING_PACK, "--psm", "6", expect=3)
        manifest = load(tmp_path / "out" / "manifest.json")
        assert manifest["language_applied_by"] == []
        assert manifest["status"] == "completed_language_unapplied"
        assert any(MISSING_PACK in w and "not applied" in w for w in manifest["warnings"])
        assert proc.returncode == 3

    @needs_tesseract
    def test_tesseract_applies_the_requested_language(self, png_dir, tmp_path):
        run("ocr_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--psm", "6")
        manifest = load(tmp_path / "out" / "manifest.json")
        assert manifest["language_applied_by"] == ["tesseract"]
        assert manifest["status"] == "completed"
        payload = load(tmp_path / "out" / "candidates" / "pagina_teste.json")
        assert any(c["engine"] == "tesseract" and c["lang"] == "por" for c in payload["candidates"])

    @needs_tesseract
    def test_portuguese_accents_survive_in_at_least_one_candidate(self, png_dir, tmp_path):
        run("ocr_photos.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--psm", "6")
        texts = candidate_texts(tmp_path / "out", "tesseract")
        assert texts, "no tesseract candidate files written"
        assert any(all(anchor in text for anchor in ANCHORS) for text in texts), texts

    @needs_tesseract
    def test_sideways_photo_is_oriented_before_recognition(self, sideways_dir, tmp_path):
        run("ocr_photos.py", str(sideways_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--psm", "6")
        manifest = load(tmp_path / "out" / "manifest.json")
        assert manifest["files"][0]["rotation_applied"] in (90, 270)
        texts = candidate_texts(tmp_path / "out", "tesseract")
        assert any(all(anchor in text for anchor in ANCHORS) for text in texts), texts

    def test_rotation_can_be_pinned(self, sideways_dir, tmp_path):
        run("ocr_photos.py", str(sideways_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", "--rotate", "0", expect=None)
        manifest = load(tmp_path / "out" / "manifest.json")
        assert manifest["files"][0]["rotation_applied"] == 0

    def test_corrupt_image_is_recorded_and_the_rest_still_runs(self, mixed_dir, tmp_path):
        proc = run("ocr_photos.py", str(mixed_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", expect=2)
        manifest = load(tmp_path / "out" / "manifest.json")
        files = {f["source"]: f for f in manifest["files"]}
        assert files["ruim.png"]["status"] == "error" and files["ruim.png"]["reason"]
        assert files["boa.png"]["status"] == "ok" and files["boa.png"]["candidate_count"] > 0
        assert manifest["status"] == "partial"
        assert proc.returncode == 2


class TestBatchOcr:
    def test_without_a_language_engine_the_batch_is_partial(self, png_dir, tmp_path):
        proc = run("batch_ocr.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--no-tesseract", expect=2)
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        assert manifest["status"] == "partial"
        assert manifest["language_requested"] == "por"
        assert manifest["language_applied_by"] == []
        assert manifest["ocr"][0]["status"] == "completed_language_unapplied"
        assert any("not applied" in w for w in manifest["warnings"])
        assert "language" not in manifest
        assert proc.returncode == 2

    @needs_tesseract
    def test_pack_missing_makes_the_batch_partial(self, png_dir, tmp_path):
        run("batch_ocr.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", MISSING_PACK, "--psm", "6", expect=2)
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        assert manifest["status"] == "partial"
        assert manifest["language_applied_by"] == []

    @needs_tesseract
    def test_png_directory_completes_with_tesseract(self, png_dir, tmp_path):
        run("batch_ocr.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--lang", "por", "--psm", "6")
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        assert manifest["status"] == "completed"
        assert manifest["language_applied_by"] == ["tesseract"]
        assert manifest["rectification"][0]["status"] == "rectified"
        assert manifest["ocr"][0]["route"] == "rectified"

    def test_rectified_evidence_survives_the_run(self, png_dir, tmp_path):
        run("batch_ocr.py", str(png_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", expect=None)
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        record = manifest["ocr"][0]
        assert record["route"] == "rectified"
        assert Path(record["selected_input"]).exists(), "the manifest must not point at a deleted file"

    def test_homonymous_sources_get_distinct_ocr_directories(self, homonyms, tmp_path):
        first, second = homonyms
        run("batch_ocr.py", str(first), str(second), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", expect=None)
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        dirs = [Path(r["output_dir"]) for r in manifest["ocr"]]
        assert len(dirs) == 2 and dirs[0] != dirs[1]
        assert all((d / "manifest.json").exists() for d in dirs)
        assert {r["source_path"] for r in manifest["rectification"]} == {str(first.resolve()), str(second.resolve())}

    def test_corrupt_image_yields_an_error_record_not_a_crash(self, mixed_dir, tmp_path):
        proc = run("batch_ocr.py", str(mixed_dir), "--output-dir", str(tmp_path / "out"), "--scale", "1", "--no-tesseract", expect=2)
        manifest = load(tmp_path / "out" / "batch_manifest.json")
        statuses = {r["source"]: r["status"] for r in manifest["ocr"]}
        assert statuses["ruim.png"] == "error"
        assert statuses["boa.png"] == "completed_language_unapplied"
        assert proc.returncode == 2


PEP723 = re.compile(r"(?m)^# /// script$\s(?P<content>(^#(| .*)$\s)+)^# ///$")
EXPECTED_DEPENDENCIES = {
    "rectify_photos.py": ["opencv-python-headless", "numpy"],
    "ocr_photos.py": ["pillow", "rapidocr-onnxruntime"],
    "batch_ocr.py": ["opencv-python-headless", "numpy", "pillow", "rapidocr-onnxruntime"],
}


class TestPackaging:
    @pytest.mark.parametrize("script,packages", EXPECTED_DEPENDENCIES.items())
    def test_pep723_block_declares_runtime_dependencies(self, script, packages):
        source = (SCRIPTS / script).read_text(encoding="utf-8")
        match = PEP723.search(source)
        assert match, f"{script} has no PEP 723 block"
        assert match.start() < source.index("\nimport "), f"{script}: the block must precede the imports"
        block = match.group("content")
        for package in packages:
            assert package in block, f"{script}: {package} missing from dependencies"

    @pytest.mark.parametrize("script", CLIS)
    def test_help_exits_cleanly(self, script):
        proc = run(script, "--help")
        assert "--output-dir" in proc.stdout
