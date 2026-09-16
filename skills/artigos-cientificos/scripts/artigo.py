#!/usr/bin/env python3
"""artigo.py — achar, abrir, registrar, conferir e pedir artigos científicos, com procedência.

    python3 artigo.py resolver <doi | url | citação>        metadados (Crossref + OpenAlex)
    python3 artigo.py buscar "<consulta>" [--desde 2020] [-n 10]
    python3 artigo.py abrir <doi> [--destino DIR] [--listar] [--conferido-em AAAA-MM-DD]
                                  [--pendencia "…"]... [--reavaliar-em AAAA-MM-DD]
    python3 artigo.py registrar <doi> --arquivo copia.pdf --url URL --origem "…" --etiqueta A|B|C
                                  [--versao publicada|aceita|submetida] [--conferido-em …] [--destino DIR]
    python3 artigo.py pedido <doi> --tema "…" [--para EMAIL] [--idioma auto|pt|en] [--assinatura "…"]
    python3 artigo.py conferir <arquivo.txt|.pdf> "<expressão>" ["<expressão>" ...]

O e-mail para o "polite pool" (Crossref, OpenAlex) e para o Unpaywall, que o exige, vem de
`ARTIGOS_EMAIL` ou de `--email`; sem ele, o Unpaywall é pulado e o resto funciona.
Saída humana por padrão; `--json` devolve o dicionário inteiro.

`registrar` é para a cópia que veio de degrau manual (site do autor, pedido atendido): grava a
mesma procedência do `abrir`, com a etiqueta que você declara (A, B ou C; D não se registra).
`pedido` redige o e-mail ao autor e imprime o que o conector Gmail `create_draft` precisa;
nada aqui envia e-mail.

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
import pedido as modulo_pedido
import procedencia
import texto as modulo_texto

MANUAIS = (
    "1. cópia do autor: WebSearch \"<título>\" filetype:pdf; página pessoal; repositório da universidade"
    " (A se for repositório; C se for o PDF da editora no site do autor); depois `registrar`",
    "2. pré-publicação: OSF Preprints, PsyArXiv, EdArXiv, arXiv (também hf://papers/<id>/paper.md), SSRN",
    "3. conectores com texto integral: scite (read_fulltext), PubMed/PMC",
    "4. navegador da app na página do DOI (passa o portão de cookies; a barreira de pagamento não)",
    "5. dados e código do artigo (OSF, GitHub, Zenodo): recomputar o número, não ler o texto",
    "6. o acesso do perfil (SKILL.md): CAFe, biblioteca, COMUT, compra só com orçamento; vazio, pule",
    "7. pedido ao autor: `artigo.py pedido <doi> --tema \"…\"` e o rascunho no Gmail; nunca envio",
)


def _email(args) -> str | None:
    return args.email or os.environ.get("ARTIGOS_EMAIL") or None


def _registros(doi: str, email: str | None) -> list[fontes.Registro]:
    """Crossref e OpenAlex, nesta ordem, com o que cada um resolveu."""
    saida = []
    for url, normalizar in ((fontes.crossref_url(doi, email),
                             lambda o: fontes.normalizar_crossref(o["message"])),
                            (fontes.openalex_url(doi, email), fontes.normalizar_openalex)):
        status, obj = fontes.http_json(url, email=email)
        if status == 200 and isinstance(obj, dict):
            saida.append(normalizar(obj))
    return saida


def _metadados(doi: str, email: str | None) -> dict | None:
    """Os dois registros fundidos: a Crossref manda no bibliográfico, e o OpenAlex entra com o que
    só ele tem (autor de correspondência, situação de acesso)."""
    registros = _registros(doi, email)
    if not registros:
        return None
    fundido: dict = {}
    for reg in sorted(registros, key=lambda r: r.fonte == "crossref"):
        for chave, valor in reg.__dict__.items():
            if chave not in fundido or valor not in ("", None, (), False):
                fundido[chave] = valor
    return {**fundido, "autores": list(fundido.get("autores") or [])}


def _linha_registro(reg: fontes.Registro) -> str:
    autores = procedencia.autores_curtos(reg.autores)
    oa = reg.oa_status or ("aberto" if reg.is_oa else "?")
    cit = f"{reg.citado_por} cit." if reg.citado_por is not None else ""
    return (f"{reg.ano or '----'} · {oa:<7} · {cit:>9} · {reg.doi}\n"
            f"       {autores}: {reg.titulo[:110]}\n"
            f"       {reg.periodico}{' ' + reg.volume if reg.volume else ''}"
            f"{'(' + reg.numero + ')' if reg.numero else ''}"
            f"{' ' + reg.paginas if reg.paginas else ''}")


def _doi_ou_erro(texto_com_doi: str) -> str | None:
    doi = fontes.extrair_doi(texto_com_doi)
    if not doi:
        print(f"Não achei um DOI em {texto_com_doi!r}.", file=sys.stderr)
    return doi


def cmd_resolver(args) -> int:
    doi = fontes.extrair_doi(args.doi_ou_texto)
    if not doi:
        return cmd_buscar(argparse.Namespace(consulta=args.doi_ou_texto, desde=None, n=5,
                                             email=args.email, json=args.json))
    registros = _registros(doi, _email(args))
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


def _imprimir_cabecalho(resultado: dict, doi: str) -> None:
    print(f"DOI {doi}")
    if resultado.get("meta"):
        m = resultado["meta"]
        print(f"  {procedencia.autores_curtos(m.get('autores') or [])} ({m.get('ano')}): {m.get('titulo', '')[:120]}")
    print("  diário:")
    for linha in resultado["diario"]:
        print(f"    - {linha}")


def _imprimir_candidatos(resultado: dict) -> None:
    print(f"  candidatos ({len(resultado['candidatos'])}):")
    for c in resultado["candidatos"]:
        print(f"    - [{c['degrau']}] {c['tipo']} {c['versao'] or 'versão ?'} {c['url']}")


def cmd_abrir(args) -> int:
    doi = _doi_ou_erro(args.doi)
    if not doi:
        return 1
    destino = Path(args.destino or ".")
    resultado = acesso.abrir(doi, destino, email=_email(args), apenas_listar=args.listar)
    reg = procedencia.registro_de_procedencia(resultado, args.conferido_em,
                                              pendencias=args.pendencia or [],
                                              reavaliar_em=args.reavaliar_em)
    if resultado["status"] == "aberto" or (args.destino and not args.listar):
        destino.mkdir(parents=True, exist_ok=True)
        caminho = procedencia.gravar(destino, procedencia.slug_de_doi(doi), reg)
        resultado = {**resultado, "procedencia": str(caminho)}
    resultado = {**resultado, "etiqueta": reg["etiqueta"], "recibo": procedencia.paragrafo_fonte(reg)}
    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0 if resultado["status"] in ("aberto", "listado") else 2
    _imprimir_cabecalho(resultado, doi)
    if args.listar or resultado["status"] != "aberto":
        _imprimir_candidatos(resultado)
    if resultado["status"] == "aberto":
        print(f"  ABERTO via {resultado['degrau']} ({resultado['formato']}, "
              f"{resultado.get('paginas') or '?'} páginas, versão {resultado['versao'] or '?'}, "
              f"{procedencia.nome_da_etiqueta(reg['etiqueta'])})")
        print(f"  arquivo:     {resultado['arquivo']}")
        print(f"  texto:       {resultado['texto']}")
        print(f"  procedência: {resultado['procedencia']}")
        print("\n" + resultado["recibo"])
        return 0
    if args.listar:
        return 0 if resultado["status"] == "listado" else 2
    print("  NÃO OBTIDO por via legal pelos degraus automáticos. Siga os manuais, nesta ordem:")
    for linha in MANUAIS:
        print(f"    {linha}")
    if resultado.get("procedencia"):
        print(f"  recibo gravado em: {resultado['procedencia']}")
    print("\n" + resultado["recibo"])
    return 2


def cmd_registrar(args) -> int:
    doi = _doi_ou_erro(args.doi)
    if not doi:
        return 1
    arquivo = Path(args.arquivo)
    if not arquivo.exists():
        print(f"Arquivo não existe: {arquivo}", file=sys.stderr)
        return 1
    destino = Path(args.destino) if args.destino else arquivo.parent
    resultado = acesso.registrar_manual(doi, arquivo, url=args.url, origem=args.origem,
                                        etiqueta=args.etiqueta, versao=args.versao,
                                        meta=_metadados(doi, _email(args)))
    reg = procedencia.registro_de_procedencia(resultado, args.conferido_em)
    destino.mkdir(parents=True, exist_ok=True)
    caminho = procedencia.gravar(destino, procedencia.slug_de_doi(doi), reg)
    resultado = {**resultado, "procedencia": str(caminho), "recibo": procedencia.paragrafo_fonte(reg)}
    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0
    print(f"DOI {doi}: registrado como {procedencia.nome_da_etiqueta(args.etiqueta)} "
          f"({resultado['formato']}, {resultado.get('paginas') or '?'} páginas, "
          f"versão {resultado['versao'] or 'não declarada'})")
    print(f"  arquivo:     {resultado['arquivo']}")
    print(f"  texto:       {resultado['texto']}")
    print(f"  procedência: {resultado['procedencia']}")
    print("\n" + resultado["recibo"])
    return 0


def cmd_pedido(args) -> int:
    doi = _doi_ou_erro(args.doi)
    if not doi:
        return 1
    meta = _metadados(doi, _email(args))
    if meta is None:
        print(f"Nenhuma API resolveu o DOI {doi}; sem metadados não há pedido.", file=sys.stderr)
        return 2
    rascunho = modulo_pedido.montar(meta, tema=args.tema, para=args.para, assinatura=args.assinatura,
                                    idioma=None if args.idioma == "auto" else args.idioma)
    if args.json:
        print(json.dumps(rascunho, ensure_ascii=False, indent=2))
        return 0
    dest = rascunho["destinatario"]
    print(f"Destinatário sugerido: {dest['nome'] or '?'} ({dest['criterio']}); "
          f"idioma {rascunho['idioma']}; {rascunho['palavras']} palavras")
    print(f"to:      {', '.join(rascunho['to']) or '(vazio: leia o e-mail na primeira página do artigo)'}")
    print(f"subject: {rascunho['subject']}")
    print("body:\n" + rascunho["body"])
    print(f"\npendência: {rascunho['pendencia']}")
    print(f"aviso: {rascunho['aviso']}")
    return 0


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
    a.add_argument("--destino", default=None, help="pasta de PDF, texto e procedência (padrão: a atual)")
    a.add_argument("--listar", action="store_true", help="só lista os candidatos, sem baixar")
    a.add_argument("--conferido-em", default=None, help="data da conferência para o parágrafo Fonte")
    a.add_argument("--pendencia", action="append", default=None,
                   help="pendência para o recibo, repetível: pedido rascunhado, embargo…")
    a.add_argument("--reavaliar-em", default=None, help="data de voltar a tentar, para o recibo")

    g = sub.add_parser("registrar", help="procedência de uma cópia obtida por degrau manual")
    g.add_argument("doi")
    g.add_argument("--arquivo", required=True, help="o PDF ou XML JATS que você obteve")
    g.add_argument("--url", required=True, help="de onde a cópia veio")
    g.add_argument("--origem", required=True,
                   help="quem a serviu: 'repositório da USP', 'site do coautor X', 'enviada pelo autor'")
    g.add_argument("--etiqueta", required=True, choices=procedencia.ETIQUETAS_REGISTRAVEIS,
                   help="A licenciada · B exceção legal (trecho) · C cinzenta; D não se registra")
    g.add_argument("--versao", default="", choices=("", "publicada", "aceita", "submetida"))
    g.add_argument("--conferido-em", default=None)
    g.add_argument("--destino", default=None, help="pasta da procedência (padrão: a do arquivo)")

    e = sub.add_parser("pedido", help="redige o pedido de cópia ao autor; rascunho no Gmail, nunca envio")
    e.add_argument("doi")
    e.add_argument("--tema", required=True, help="o motivo concreto, numa linha: o que o artigo fundamenta")
    e.add_argument("--para", default=None, help="e-mail do autor, lido na primeira página do artigo")
    e.add_argument("--idioma", default="auto", choices=("auto", "pt", "en"))
    e.add_argument("--assinatura", default=None, help="padrão: ARTIGOS_ASSINATURA, ou o nome do Daniel")

    c = sub.add_parser("conferir", help="procura expressões no texto extraído, com contexto")
    c.add_argument("arquivo")
    c.add_argument("expressoes", nargs="+")
    c.add_argument("--contexto", type=int, default=1)

    for s in (r, b, a, g, e, c):
        s.add_argument("--email", default=None, help="e-mail para polite pool e Unpaywall")
        s.add_argument("--json", action="store_true", help="saída em JSON")
    return p


COMANDOS = {"resolver": cmd_resolver, "buscar": cmd_buscar, "abrir": cmd_abrir,
            "registrar": cmd_registrar, "pedido": cmd_pedido, "conferir": cmd_conferir}


def main(argv: list[str] | None = None) -> int:
    args = montar_parser().parse_args(argv)
    try:
        return COMANDOS[args.comando](args)
    except (RuntimeError, subprocess.CalledProcessError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
