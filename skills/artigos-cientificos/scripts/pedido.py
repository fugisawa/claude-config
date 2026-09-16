"""O pedido de cópia ao autor: a skill redige, a sessão cria o RASCUNHO no Gmail, o Daniel envia.

As regras vêm do que as editoras permitem e do custo que um pedido tem para quem o recebe: um
pedido por autor por artigo, sem repetir antes de 30 dias; até 120 palavras, com o DOI, o motivo
concreto e a promessa de uso pessoal; no idioma do autor; ao autor de correspondência. O script
não tem acesso ao Gmail nem o quer: devolve `to`, `subject` e `body`, e a sessão chama
`create_draft` com isso. `send_message` não entra em lugar nenhum desta skill.
"""
from __future__ import annotations

import datetime as dt
import os

import procedencia

LIMITE_DE_PALAVRAS = 120
JANELA_DE_REPETICAO = dt.timedelta(days=30)
PAISES_LUSOFONOS = frozenset({"BR", "PT", "AO", "MZ", "CV", "GW", "ST", "TL"})
ASSINATURA_PADRAO = "Daniel Fugisawa"
EDITORAS_COM_SHARE_LINK = ("elsevier",)
AVISO = ("Crie o rascunho com o conector Gmail (`create_draft`) usando `to`, `subject` e `body`; "
         "se `to` estiver vazio, o endereço está na primeira página do artigo ou na página do DOI. "
         "Nunca `send_message`: quem envia é o Daniel, depois de ler. Um pedido por autor por artigo; "
         "sem resposta, não repetir antes de 30 dias; a pendência vai para a bandeira do material "
         "(`artigo.py abrir <doi> --pendencia \"…\"`).")

ASSUNTO = {"pt": 'Pedido de cópia do artigo "{titulo}"', "en": 'Request for a copy of "{titulo}"'}
SAUDACAO = {"pt": ("Prezado(a) Prof(a). {sobrenome},", "Prezado(a) autor(a),"),
            "en": ("Dear Dr. {sobrenome},", "Dear author,")}
CORPO = {
    "pt": ("Estou preparando material de estudo sobre {tema} e gostaria de ler o artigo \"{titulo}\""
           "{veiculo}, doi:{doi}. Não tenho acesso institucional ao periódico, e as vias de acesso "
           "aberto que tentei não têm cópia.\n\nSeria possível me enviar o manuscrito aceito ou a versão "
           "publicada{share}?{politica} O uso é só leitura e citação, sem redistribuição.\n\n"
           "Obrigado,\n{assinatura}"),
    "en": ("I am preparing study material on {tema} and would like to read your article \"{titulo}\""
           "{veiculo}, doi:{doi}. I have no institutional access to the journal, and the open-access "
           "routes I tried found no copy.\n\nCould you send me the accepted manuscript or the published "
           "version{share}?{politica} I will use it for reading and citation only and will not "
           "redistribute it.\n\nThank you,\n{assinatura}"),
}
POLITICA = {"pt": " A política de compartilhamento da maioria das editoras permite ao autor enviar cópia "
                  "a colegas para uso pessoal.",
            "en": " Most publishers' sharing policies allow authors to share a copy privately with "
                  "colleagues for personal use."}
SHARE = {"pt": " (ou um Share Link)", "en": " (or a Share Link)"}


def contar_palavras(texto: str) -> int:
    return len(texto.split())


def idioma_para(pais: str) -> str:
    """Português para autor de país lusófono; inglês para os demais."""
    return "pt" if (pais or "").upper() in PAISES_LUSOFONOS else "en"


def destinatario(meta: dict) -> dict:
    """Quem recebe: o autor de correspondência que o OpenAlex marca; sem marca, o primeiro autor,
    com o aviso de conferir na primeira página. O e-mail nunca vem daqui: Crossref e OpenAlex não o têm."""
    autores = list(meta.get("autores") or [])
    nome = meta.get("correspondente") or (autores[0] if autores else "")
    if meta.get("correspondente_marcado"):
        criterio = "autor de correspondência marcado pelo OpenAlex"
    else:
        criterio = "primeiro autor; o OpenAlex não marca o correspondente, confira na primeira página"
    return {"nome": nome, "pais": meta.get("pais_correspondente") or "", "criterio": criterio}


def _veiculo(meta: dict) -> str:
    partes = [p for p in (meta.get("periodico") or "", str(meta.get("ano") or "")) if p]
    return f" ({', '.join(partes)})" if partes else ""


def _pede_share_link(meta: dict) -> bool:
    editora = (meta.get("editora") or "").lower()
    return any(nome in editora for nome in EDITORAS_COM_SHARE_LINK)


def redigir(meta: dict, *, idioma: str, tema: str, assinatura: str, sobrenome: str = "",
            compacto: bool = False) -> dict:
    """Assunto e corpo no idioma pedido. `compacto` retira a frase sobre a política da editora, que
    é a primeira a sair quando o título é longo demais para o limite de palavras."""
    if idioma not in CORPO:
        raise RuntimeError(f"idioma {idioma!r}: use pt ou en")
    titulo = meta.get("titulo") or "(título não informado)"
    saudacao = SAUDACAO[idioma][0].format(sobrenome=sobrenome) if sobrenome else SAUDACAO[idioma][1]
    corpo = CORPO[idioma].format(
        tema=tema, titulo=titulo, veiculo=_veiculo(meta), doi=meta.get("doi") or "?",
        share=SHARE[idioma] if _pede_share_link(meta) else "",
        politica="" if compacto else POLITICA[idioma], assinatura=assinatura)
    return {"subject": ASSUNTO[idioma].format(titulo=titulo), "body": f"{saudacao}\n\n{corpo}"}


def pendencia(nome: str, hoje: dt.date) -> str:
    """A linha que vai para o recibo do material, com a data antes da qual não se repete o pedido."""
    limite = (hoje + JANELA_DE_REPETICAO).isoformat()
    return (f"pedido ao autor rascunhado em {hoje.isoformat()} para {nome or 'autor não identificado'}; "
            f"sem resposta, não repetir antes de {limite}")


def montar(meta: dict, *, tema: str, para: str | None = None, assinatura: str | None = None,
           idioma: str | None = None, hoje: dt.date | None = None) -> dict:
    """Tudo o que o `create_draft` precisa, mais o destinatário sugerido, a pendência e o aviso."""
    dest = destinatario(meta)
    idioma = idioma or idioma_para(dest["pais"])
    assinatura = assinatura or os.environ.get("ARTIGOS_ASSINATURA") or ASSINATURA_PADRAO
    sobrenome = procedencia.sobrenome(dest["nome"])
    rascunho = redigir(meta, idioma=idioma, tema=tema, assinatura=assinatura, sobrenome=sobrenome)
    if contar_palavras(rascunho["body"]) > LIMITE_DE_PALAVRAS:
        rascunho = redigir(meta, idioma=idioma, tema=tema, assinatura=assinatura, sobrenome=sobrenome,
                           compacto=True)
    palavras = contar_palavras(rascunho["body"])
    return {
        "to": [para] if para else [],
        "subject": rascunho["subject"],
        "body": rascunho["body"],
        "palavras": palavras,
        "cabe_no_limite": palavras <= LIMITE_DE_PALAVRAS,
        "idioma": idioma,
        "destinatario": dest,
        "pendencia": pendencia(dest["nome"], hoje or dt.date.today()),
        "aviso": AVISO,
    }
