#!/usr/bin/env python3
"""artigo.py — achar, abrir e conferir artigos científicos, com procedência.

    python3 artigo.py resolver <doi | url | citação>        metadados (Crossref + OpenAlex)
    python3 artigo.py buscar "<consulta>" [--desde 2020] [-n 10]
    python3 artigo.py abrir <doi> [--destino DIR] [--listar] [--conferido-em AAAA-MM-DD]
    python3 artigo.py conferir <arquivo.txt|.pdf> "<expressão>" ["<expressão>" ...]

O e-mail para o "polite pool" (Crossref, OpenAlex) e para o Unpaywall, que o exige, vem de
`ARTIGOS_EMAIL` ou de `--email`; sem ele, o Unpaywall é pulado e o resto funciona.
Saída humana por padrão; `--json` devolve o dicionário inteiro.

Códigos de saída: 0 ok · 2 não abriu / não encontrou · 1 erro de uso ou de ambiente.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import acesso
import fontes
import leitura
import procedencia
import texto as modulo_texto


def _email(args) -> str | None:
    return args.email or os.environ.get("ARTIGOS_EMAIL") or None


def _linha_registro(reg: fontes.Registro) -> str:
    autores = procedencia.autores_curtos(reg.autores)
    oa = reg.oa_status or ("aberto" if reg.is_oa else "?")
    cit = f"{reg.citado_por} cit." if reg.citado_por is not None else ""
    return (f"{reg.ano or '----'} · {oa:<7} · {cit:>9} · {reg.doi}\n"
            f"       {autores}: {reg.titulo[:110]}\n"
            f"       {reg.periodico}{' ' + reg.volume if reg.volume else ''}"
            f"{'(' + reg.numero + ')' if reg.numero else ''}"
            f"{' ' + reg.paginas if reg.paginas else ''}")


def cmd_resolver(args) -> int:
    doi = fontes.extrair_doi(args.doi_ou_texto)
    if not doi:
        return cmd_buscar(argparse.Namespace(consulta=args.doi_ou_texto, desde=None, n=5,
                                             email=args.email, json=args.json))
    email = _email(args)
    registros = []
    for url, normalizar in ((fontes.crossref_url(doi, email),
                             lambda o: fontes.normalizar_crossref(o["message"])),
                            (fontes.openalex_url(doi, email), fontes.normalizar_openalex)):
        status, obj = fontes.http_json(url, email=email)
        if status == 200 and isinstance(obj, dict):
            registros.append(normalizar(obj))
    if not registros:
        print(f"Nenhuma API resolveu o DOI {doi}.", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([r.__dict__ for r in registros], ensure_ascii=False, indent=2))
        return 0
    for reg in registros:
        print(f"[{reg.fonte}] " + _linha_registro(reg))
    return 0


def cmd_buscar(args) -> int:
    email = _email(args)
    url = fontes.openalex_busca_url(args.consulta, desde=args.desde, n=args.n, email=email)
    status, obj = fontes.http_json(url, email=email)
    if status != 200 or not isinstance(obj, dict):
        print(f"OpenAlex respondeu HTTP {status}.", file=sys.stderr)
        return 2
    registros = fontes.normalizar_openalex_lista(obj)
    if args.json:
        print(json.dumps([r.__dict__ for r in registros], ensure_ascii=False, indent=2))
        return 0
    total = (obj.get("meta") or {}).get("count")
    print(f"OpenAlex: {total} resultado(s) para {args.consulta!r}; os {len(registros)} primeiros:\n")
    for reg in registros:
        print(_linha_registro(reg) + "\n")
    return 0 if registros else 2


def cmd_abrir(args) -> int:
    doi = fontes.extrair_doi(args.doi)
    if not doi:
        print(f"Não achei um DOI em {args.doi!r}.", file=sys.stderr)
        return 1
    destino = Path(args.destino)
    resultado = acesso.abrir(doi, destino, email=_email(args), apenas_listar=args.listar)
    reg = procedencia.registro_de_procedencia(resultado, args.conferido_em)
    if resultado["status"] == "aberto":
        caminho = procedencia.gravar(destino, procedencia.slug_de_doi(doi), reg)
        resultado = {**resultado, "procedencia": str(caminho)}
    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0 if resultado["status"] in ("aberto", "listado") else 2
    print(f"DOI {doi}")
    if resultado.get("meta"):
        m = resultado["meta"]
        print(f"  {procedencia.autores_curtos(m.get('autores') or [])} ({m.get('ano')}): {m.get('titulo', '')[:120]}")
    print("  diário:")
    for linha in resultado["diario"]:
        print(f"    - {linha}")
    if args.listar or resultado["status"] != "aberto":
        print(f"  candidatos ({len(resultado['candidatos'])}):")
        for c in resultado["candidatos"]:
            print(f"    - [{c['degrau']}] {c['tipo']} {c['versao'] or 'versão ?'} {c['url']}")
    if resultado["status"] == "aberto":
        print(f"  ABERTO via {resultado['degrau']} ({resultado['formato']}, "
              f"{resultado.get('paginas') or '?'} páginas, versão {resultado['versao'] or '?'})")
        print(f"  arquivo:     {resultado['arquivo']}")
        print(f"  texto:       {resultado['texto']}")
        print(f"  procedência: {resultado['procedencia']}")
        print("\n" + procedencia.paragrafo_fonte(reg))
        return 0
    if args.listar:
        return 0 if resultado["status"] == "listado" else 2
    if resultado["status"] != "aberto":
        print("  NÃO ABERTO pelos degraus automáticos. Siga os manuais, nesta ordem:")
        print("    1. cópia do autor: WebSearch \"<título>\" filetype:pdf; página pessoal; repositório da universidade")
        print("    2. pré-publicação: OSF Preprints, PsyArXiv, EdArXiv, arXiv, SSRN")
        print("    3. conectores com texto integral: scite (read_fulltext), PubMed/PMC, Consensus")
        print("    4. navegador da app na página do DOI (passa o portão de cookies; a paywall não)")
        print("    5. repositório de dados do artigo (OSF) — dados e código, não o texto")
        print("    6. pedido ao autor (references/pedido-ao-autor.md) e acesso institucional")
        print("  Enquanto isso, o valor fica ⚑ não conferido em fonte primária.")
    return 2


def cmd_conferir(args) -> int:
    arquivo = Path(args.arquivo)
    if not arquivo.exists():
        print(f"Arquivo não existe: {arquivo}", file=sys.stderr)
        return 1
    if arquivo.suffix.lower() == ".pdf":
        arquivo = leitura.extrair_texto(arquivo, "pdf")
    conteudo = arquivo.read_text(encoding="utf-8", errors="replace")
    achados = modulo_texto.procurar(conteudo, args.expressoes, contexto=args.contexto)
    print(modulo_texto.relatorio(achados, args.expressoes))
    faltando = [e for e in args.expressoes if not any(a.expressao == e for a in achados)]
    return 2 if faltando else 0


def montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="artigo.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)

    r = sub.add_parser("resolver", help="metadados de um DOI (ou busca, se não houver DOI)")
    r.add_argument("doi_ou_texto")

    b = sub.add_parser("buscar", help="busca por assunto no OpenAlex")
    b.add_argument("consulta")
    b.add_argument("--desde", type=int, default=None, help="ano inicial")
    b.add_argument("-n", type=int, default=10, help="quantos resultados (máx. 100)")

    a = sub.add_parser("abrir", help="roda a escada de acesso e baixa o texto integral")
    a.add_argument("doi")
    a.add_argument("--destino", default=".", help="pasta onde gravar PDF, texto e procedência")
    a.add_argument("--listar", action="store_true", help="só lista os candidatos, sem baixar")
    a.add_argument("--conferido-em", default=None, help="data da conferência para o parágrafo Fonte")

    c = sub.add_parser("conferir", help="procura expressões no texto extraído, com contexto")
    c.add_argument("arquivo")
    c.add_argument("expressoes", nargs="+")
    c.add_argument("--contexto", type=int, default=1)

    for s in (r, b, a, c):
        s.add_argument("--email", default=None, help="e-mail para polite pool e Unpaywall")
        s.add_argument("--json", action="store_true", help="saída em JSON")
    return p


COMANDOS = {"resolver": cmd_resolver, "buscar": cmd_buscar, "abrir": cmd_abrir,
            "conferir": cmd_conferir}


def main(argv: list[str] | None = None) -> int:
    args = montar_parser().parse_args(argv)
    try:
        return COMANDOS[args.comando](args)
    except (RuntimeError, subprocess.CalledProcessError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
