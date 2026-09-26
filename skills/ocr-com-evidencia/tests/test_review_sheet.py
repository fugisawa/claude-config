"""Seam tests for review_sheet.py: batch output in, review sheet and draft transcription out.

The fixture is a hand-built batch output tree with known candidate texts, so the
agreement figures asserted here come from a worked example, not from the code.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SCRIPT = SCRIPTS / "review_sheet.py"

TESSERACT_TEXT = "Seção 3 — Coordenação\nA licitação exigirá aptidão técnica.\nValores: 1.234,56 em 12/08/2026."
# Line 1 differs only in accents/punctuation (agrees loosely); line 2 drops a word; line 3 reads O for 0.
RAPIDOCR_TEXT = "Secao 3 - Coordenacao\nA licitacao exigira aptidao.\nValores: 1.234,56 em 12/O8/2026."


def run(*args: str, expect: int | None = 0) -> subprocess.CompletedProcess:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if expect is not None:
        assert proc.returncode == expect, f"rc={proc.returncode}\n{proc.stderr}"
    return proc


def candidate(engine: str, variant: str, text: str, confidence: float = 0.9, **extra) -> dict:
    """RapidOCR scores lines in 0–1; Tesseract in 0–100. The fixture keeps each engine's scale."""
    lines = [{"text": line, "confidence": confidence, "box": {}} for line in text.splitlines()]
    return {"engine": engine, "variant": variant, "lines": lines, **extra}


def fake_batch(root: Path, *, with_tesseract: bool, images: tuple[str, ...] = ("pagina_1",)) -> Path:
    """A batch_ocr.py output tree with the fields review_sheet.py reads."""
    ocr_records = []
    for index, stem in enumerate(images):
        ocr_dir = root / "ocr" / stem
        (ocr_dir / "candidates").mkdir(parents=True)
        (ocr_dir / "preprocessed").mkdir()
        (ocr_dir / "preprocessed" / f"{stem}_rectified_color.png").write_bytes(b"png")
        candidates = [candidate("rapidocr", "color", RAPIDOCR_TEXT), candidate("rapidocr", "gray", "Secao 3\nlixo")]
        if with_tesseract:
            candidates += [candidate("tesseract", "color", TESSERACT_TEXT, confidence=90.0, lang="por", psm=6, returncode=0, stderr="", words=[])]
        payload = {"source": f"{stem}.jpg", "source_path": f"/fotos/{stem}.jpg", "sha256": f"{index:064x}", "stem": f"{stem}_rectified", "candidates": candidates}
        (ocr_dir / "candidates" / f"{stem}_rectified.json").write_text(json.dumps(payload), encoding="utf-8")
        selected = root / "rectified" / f"{stem}_rectified.png"
        selected.parent.mkdir(exist_ok=True)
        selected.write_bytes(b"png")
        ocr_records.append({
            "source": f"{stem}.jpg", "source_path": f"/fotos/{stem}.jpg", "source_sha256": f"{index:064x}",
            "selected_input": str(selected), "route": "rectified", "status": "completed" if with_tesseract else "completed_language_unapplied",
            "output_dir": str(ocr_dir), "candidate_count": len(candidates), "language_applied_by": ["tesseract"] if with_tesseract else [],
        })
    manifest = {
        "schema_version": 2, "status": "completed" if with_tesseract else "partial", "language_requested": "por",
        "language_applied_by": ["tesseract"] if with_tesseract else [], "input_count": len(images),
        "rectification": [], "ocr": ocr_records, "warnings": [],
    }
    (root / "batch_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


class TestReviewSheet:
    def test_writes_review_and_draft(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        run(str(batch))
        assert (batch / "review.md").exists()
        assert (batch / "transcricao.md").exists()

    def test_agreement_ignores_accents_punctuation_and_spacing_but_not_characters(self, tmp_path):
        """RapidOCR cannot emit diacritics, so exact comparison would never agree; loose comparison still catches O/0 and dropped words."""
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        run(str(batch), "--json")
        rows = json.loads((batch / "review.json").read_text(encoding="utf-8"))["images"][0]["lines"]
        assert [row["agrees"] for row in rows] == [True, False, False]

    def test_best_candidate_prefers_confident_content_over_line_count(self, tmp_path):
        """A variant inflated by low-confidence noise lines must not win just for being longer."""
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        ocr_dir = batch / "ocr" / "pagina_1"
        payload = json.loads((ocr_dir / "candidates" / "pagina_1_rectified.json").read_text(encoding="utf-8"))
        noisy = candidate("tesseract", "denoised", "\n".join(["x"] * 12), confidence=5.0, lang="por", psm=6, returncode=0, stderr="", words=[])
        payload["candidates"].append(noisy)
        (ocr_dir / "candidates" / "pagina_1_rectified.json").write_text(json.dumps(payload), encoding="utf-8")
        run(str(batch), "--json")
        item = json.loads((batch / "review.json").read_text(encoding="utf-8"))["images"][0]
        assert item["base_variant"] == "color"

    def test_lines_read_only_by_the_other_engine_are_surfaced(self, tmp_path):
        """A truncated base reading must not silently drop what the other engine read (a whole chapter vanished this way)."""
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        ocr_dir = batch / "ocr" / "pagina_1"
        path = ocr_dir / "candidates" / "pagina_1_rectified.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for c in payload["candidates"]:
            if c["engine"] == "rapidocr" and c["variant"] == "color":
                c["lines"].append({"text": "Capitulo 9 - Extra", "confidence": 0.9, "box": {}})
        path.write_text(json.dumps(payload), encoding="utf-8")
        run(str(batch), "--json")
        item = json.loads((batch / "review.json").read_text(encoding="utf-8"))["images"][0]
        assert item["lines_only_in_other"] == 1
        draft = (batch / "transcricao.md").read_text(encoding="utf-8")
        assert 'REVISAR: só o rapidocr leu "Capitulo 9 - Extra"' in draft
        review = (batch / "review.md").read_text(encoding="utf-8")
        assert "Capitulo 9 - Extra" in review

    def test_short_fragments_only_in_other_stay_out_of_the_draft(self, tmp_path):
        """RapidOCR splits '1.1. Título …… 21' into three boxes; the number and the '1.1.' are fragments, not missing lines."""
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        path = batch / "ocr" / "pagina_1" / "candidates" / "pagina_1_rectified.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for c in payload["candidates"]:
            if c["engine"] == "rapidocr" and c["variant"] == "color":
                c["lines"] += [{"text": "21", "confidence": 0.9, "box": {}}, {"text": "1.1.", "confidence": 0.9, "box": {}}]
        path.write_text(json.dumps(payload), encoding="utf-8")
        run(str(batch), "--json")
        item = json.loads((batch / "review.json").read_text(encoding="utf-8"))["images"][0]
        assert item["lines_only_in_other"] == 0
        assert item["fragments_only_in_other"] == ["21", "1.1."]
        draft = (batch / "transcricao.md").read_text(encoding="utf-8")
        assert 'só o rapidocr leu "21"' not in draft
        review = (batch / "review.md").read_text(encoding="utf-8")
        assert "Fragmentos" in review and "`21`" in review

    def test_review_reports_agreement_between_engines(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        run(str(batch), "--json")
        report = json.loads((batch / "review.json").read_text(encoding="utf-8"))
        item = report["images"][0]
        assert item["engines"] == ["rapidocr", "tesseract"]
        # Worked example: three lines; only the first reads the same once accents, punctuation and spaces are ignored.
        assert item["lines_total"] == 3
        assert item["lines_agreeing"] == 1
        assert item["lines_disagreeing"] == 2

    def test_draft_marks_disagreeing_lines_and_keeps_provenance(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        run(str(batch))
        draft = (batch / "transcricao.md").read_text(encoding="utf-8")
        assert draft.startswith("---\n"), "frontmatter with provenance is required"
        assert "status: revisar" in draft
        assert "<!-- imagem: pagina_1.jpg" in draft and "sha256:" in draft
        assert "Seção 3 — Coordenação" in draft, "the Portuguese-capable engine is the base text"
        assert draft.count("<!-- REVISAR") == 2
        assert "Valores: 1.234,56 em 12/08/2026. <!-- REVISAR" in draft, "the base engine text is kept, the other reading is quoted"
        assert 'rapidocr leu "Valores: 1.234,56 em 12/O8/2026."' in draft

    def test_single_engine_flags_every_line_as_unverified(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=False)
        run(str(batch), "--json")
        report = json.loads((batch / "review.json").read_text(encoding="utf-8"))
        item = report["images"][0]
        assert item["engines"] == ["rapidocr"]
        assert item["lines_agreeing"] == 0
        draft = (batch / "transcricao.md").read_text(encoding="utf-8")
        assert "sem segunda leitura" in draft

    def test_review_lists_evidence_paths(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=True)
        run(str(batch))
        review = (batch / "review.md").read_text(encoding="utf-8")
        assert "pagina_1_rectified.png" in review
        assert "pagina_1_rectified_color.png" in review

    def test_multiple_images_keep_input_order(self, tmp_path):
        batch = fake_batch(tmp_path / "batch", with_tesseract=True, images=("pagina_2", "pagina_1"))
        run(str(batch), "--json")
        report = json.loads((batch / "review.json").read_text(encoding="utf-8"))
        assert [i["source"] for i in report["images"]] == ["pagina_2.jpg", "pagina_1.jpg"]

    def test_missing_manifest_is_an_error(self, tmp_path):
        proc = run(str(tmp_path), expect=None)
        assert proc.returncode == 2
        assert "batch_manifest.json" in proc.stderr

    def test_help(self):
        proc = run("--help")
        assert "batch" in proc.stdout.lower()
