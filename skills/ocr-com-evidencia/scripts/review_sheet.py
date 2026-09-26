#!/usr/bin/env python3
"""Turn a batch_ocr.py output tree into a review sheet and a draft transcription.

The sheet puts, per image, the best reading of each engine side by side and says
which lines the two engines read identically. Agreement between independent
engines is evidence; disagreement marks the line for visual review. It is not
accuracy: two engines can agree on a wrong reading.

Usage:
  python review_sheet.py BATCH_DIR            # writes review.md, review.json, transcricao.md
  python review_sheet.py BATCH_DIR --json     # also prints review.json to stdout

The draft ``transcricao.md`` uses the language-capable engine as base text,
carries provenance in frontmatter and one marker per image, and flags every
line that lacks a second identical reading with ``<!-- REVISAR ... -->``.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_USAGE = 2
UNVERIFIED = "sem segunda leitura"
SAME_LINE_RATIO = 0.6  # below this, the closest other line is a different line, not a different reading
MIN_SUBSTRING = 8  # a loose reading this long contained in the other is the same line with junk appended


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def loose(text: str) -> str:
    """Letters and digits only, no diacritics, no case: RapidOCR never emits accents, so
    comparing with them would never agree; O/0, dropped words and wrong digits still differ."""
    stripped = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", stripped.casefold())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def best_by_engine(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """One candidate per engine, by total confidence: a variant inflated with low-confidence
    noise lines (dotted leaders, bleed-through) must not win just for being longer."""
    best: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        current = best.get(candidate["engine"])
        score = (sum(float(x.get("confidence", 0)) for x in candidate["lines"]), len(candidate["lines"]))
        if current is None or score > current["_score"]:
            best[candidate["engine"]] = {**candidate, "_score": score}
    return best


def texts_of(candidate: dict[str, Any]) -> list[str]:
    return [normalize(line["text"]) for line in candidate["lines"] if normalize(line["text"])]


def same_line(a: str, b: str) -> float:
    """Similarity of two loose readings; containment counts as identity, because Tesseract
    appends dotted-leader junk to a line RapidOCR reads clean."""
    short, long = sorted((a, b), key=len)
    if len(short) >= MIN_SUBSTRING and short in long:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def compare_lines(base: list[str], other: list[str] | None) -> tuple[list[dict[str, Any]], list[str]]:
    """Per base line: an identical loose reading, else the closest remaining one. Second value:
    other-engine lines that matched no base line — what the base reading missed entirely."""
    if other is None:
        return [{"text": text, "agrees": False, "other": None, "ratio": None} for text in base], []
    remaining = {index: loose(text) for index, text in enumerate(other)}
    rows = []
    for text in base:
        key = loose(text)
        match = next((i for i, k in remaining.items() if k and k == key), None)
        if match is not None:
            rows.append({"text": text, "agrees": True, "other": other[match], "ratio": 1.0})
            del remaining[match]
            continue
        ranked = sorted(((same_line(key, k), i) for i, k in remaining.items()), reverse=True)
        ratio, index = ranked[0] if ranked else (0.0, None)
        if index is not None and ratio >= SAME_LINE_RATIO:
            del remaining[index]  # the same line, read differently — it is accounted for
        closest = other[index] if index is not None else None
        rows.append({"text": text, "agrees": False, "other": closest, "ratio": round(ratio, 2)})
    only_in_other = [other[i] for i in sorted(remaining) if remaining[i]]
    return rows, only_in_other


def split_fragments(only_in_other: list[str]) -> tuple[list[str], list[str]]:
    """Lines long enough to be missing content, apart from fragments (a page number, a
    section label) that the other engine boxed separately from a line the base has."""
    lines = [t for t in only_in_other if len(loose(t)) >= MIN_SUBSTRING]
    fragments = [t for t in only_in_other if len(loose(t)) < MIN_SUBSTRING]
    return lines, fragments


def evidence_paths(record: dict[str, Any]) -> list[str]:
    paths = [record.get("selected_input", "")]
    preprocessed = Path(record["output_dir"]) / "preprocessed"
    paths += [str(p) for p in sorted(preprocessed.glob("*_color.png"))] if preprocessed.is_dir() else []
    return [p for p in paths if p]


def review_image(record: dict[str, Any], preferred: list[str]) -> dict[str, Any]:
    head = {"source": record["source"], "sha256": record.get("source_sha256", ""), "route": record.get("route"), "status": record.get("status"), "evidence": evidence_paths(record)}
    payloads = sorted((Path(record["output_dir"]) / "candidates").glob("*.json")) if record.get("output_dir") else []
    candidates = [c for path in payloads for c in load_json(path).get("candidates", [])]
    if record.get("status") == "error" or not candidates:
        return {**head, "engines": [], "base_engine": None, "lines": [], "lines_total": 0, "lines_agreeing": 0, "lines_disagreeing": 0, "only_in_other": [], "lines_only_in_other": 0, "fragments_only_in_other": [], "agreement_ratio": None}
    best = best_by_engine(candidates)
    engines = sorted(best)
    base_engine = next((e for e in preferred if e in best), engines[0])
    others = [e for e in engines if e != base_engine]
    base_lines = texts_of(best[base_engine])
    other_lines = texts_of(best[others[0]]) if others else None
    rows, unmatched = compare_lines(base_lines, other_lines)
    only_in_other, fragments = split_fragments(unmatched)
    agreeing = sum(row["agrees"] for row in rows)
    return {
        **head,
        "engines": engines,
        "base_engine": base_engine,
        "base_variant": best[base_engine].get("variant"),
        "other_engine": others[0] if others else None,
        "lines": rows,
        "lines_total": len(rows),
        "lines_agreeing": agreeing,
        "lines_disagreeing": len(rows) - agreeing,
        "only_in_other": only_in_other,
        "lines_only_in_other": len(only_in_other),
        "fragments_only_in_other": fragments,
        "agreement_ratio": round(agreeing / len(rows), 2) if rows else None,
    }


def render_review(batch: Path, manifest: dict[str, Any], images: list[dict[str, Any]]) -> str:
    md = [
        f"# Folha de revisão — `{batch}`",
        "",
        f"- Status do lote: `{manifest.get('status')}` · idioma pedido: `{manifest.get('language_requested') or '(nenhum)'}` · aplicado por: {', '.join(manifest.get('language_applied_by', [])) or 'nenhum motor'}",
        "- Concordância entre motores é evidência, não prova: confira as linhas marcadas contra a imagem, e as âncoras (acentos, números, datas, títulos, numeração) mesmo nas que concordam.",
        "",
        *(f"> {w}" for w in manifest.get("warnings", [])),
        "",
    ]
    for item in images:
        md += [f"## `{item['source']}`", "", f"- Rota: `{item['route']}` · status: `{item['status']}`"]
        md += [f"- Evidência: `{p}`" for p in item["evidence"]]
        if not item["engines"]:
            md += ["- Sem candidatos: imagem com erro ou sem saída. Transcrever por visão, se for o caso, e marcar como tal.", ""]
            continue
        md += [
            f"- Motores: {', '.join(item['engines'])} · base: `{item['base_engine']}/{item.get('base_variant')}` · concordância: {item['lines_agreeing']}/{item['lines_total']} linhas · só o outro motor leu: {item['lines_only_in_other']} linhas",
            "",
            f"| # | base ({item['base_engine']}) | outra leitura ({item['other_engine'] or '—'}) | igual |",
            "|---|---|---|---|",
        ]
        for index, row in enumerate(item["lines"], 1):
            other = row["other"] if row["other"] is not None else f"({UNVERIFIED})"
            mark = "sim" if row["agrees"] else (f"não ({row['ratio']})" if row["ratio"] is not None else "—")
            md.append(f"| {index} | {row['text']} | {other} | {mark} |")
        if item["only_in_other"]:
            md += ["", f"Só o `{item['other_engine']}` leu (a base não tem linha correspondente — cobertura a conferir na imagem):", ""]
            md += [f"- {text}" for text in item["only_in_other"]]
        if item["fragments_only_in_other"]:
            md += ["", "Fragmentos só do outro motor (número de página, rótulo de seção — situe-os na linha certa ao conferir): " + ", ".join(f"`{t}`" for t in item["fragments_only_in_other"])]
        md.append("")
    return "\n".join(md) + "\n"


def render_draft(batch: Path, manifest: dict[str, Any], images: list[dict[str, Any]]) -> str:
    md = [
        "---",
        "titulo: Transcrição OCR — rascunho para revisão",
        f"fonte_lote: {batch}",
        f"gerado_em: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"idioma_pedido: {manifest.get('language_requested') or ''}",
        f"idioma_aplicado_por: {', '.join(manifest.get('language_applied_by', []))}",
        "status: revisar",
        f"imagens: {len(images)}",
        "---",
        "",
    ]
    for item in images:
        md.append(f"<!-- imagem: {item['source']} | sha256: {item['sha256']} | rota: {item['route']} | base: {item['base_engine']}/{item.get('base_variant')} | concordância: {item['lines_agreeing']}/{item['lines_total']} -->")
        md.append("")
        if not item["engines"]:
            md += ["<!-- REVISAR: sem candidatos de OCR para esta imagem -->", ""]
            continue
        for row in item["lines"]:
            if row["agrees"]:
                md.append(row["text"])
            elif row["other"] is None:
                md.append(f"{row['text']} <!-- REVISAR: {UNVERIFIED} -->")
            else:
                md.append(f"{row['text']} <!-- REVISAR: {item['other_engine']} leu \"{row['other']}\" -->")
        for text in item["only_in_other"]:
            md.append(f"<!-- REVISAR: só o {item['other_engine']} leu \"{text}\" — conferir na imagem onde esta linha entra -->")
        md.append("")
    return "\n".join(md) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("batch_dir", type=Path, help="output directory of batch_ocr.py")
    parser.add_argument("--json", action="store_true", help="also print review.json to stdout")
    args = parser.parse_args()

    manifest_path = args.batch_dir / "batch_manifest.json"
    if not manifest_path.is_file():
        parser.error(f"{manifest_path} not found; point at a batch_ocr.py output directory")
    manifest = load_json(manifest_path)
    preferred = list(manifest.get("language_applied_by", [])) + ["tesseract", "rapidocr"]
    images = [review_image(record, preferred) for record in manifest.get("ocr", [])]
    report = {
        "batch": str(args.batch_dir),
        "status": manifest.get("status"),
        "language_requested": manifest.get("language_requested"),
        "language_applied_by": manifest.get("language_applied_by", []),
        "images": images,
    }
    (args.batch_dir / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.batch_dir / "review.md").write_text(render_review(args.batch_dir, manifest, images), encoding="utf-8")
    (args.batch_dir / "transcricao.md").write_text(render_draft(args.batch_dir, manifest, images), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in images:
            print(f"{item['source']}: {item['lines_agreeing']}/{item['lines_total']} linhas com segunda leitura igual")
        print(f"review.md, review.json e transcricao.md escritos em {args.batch_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
