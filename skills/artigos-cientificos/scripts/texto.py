"""Conferência de números e afirmações no texto extraído, sem despejar o texto no contexto.

A busca tolera o que o `pdftotext` e a tipografia mudam: sinal de menos tipográfico (U+2212),
meia-risca (U+2013) e os hífens U+2010 e U+2011 no lugar do sinal, espaço duro, vírgula decimal
contra ponto, espaço a mais ou a menos em qualquer ponto da expressão, inclusive entre palavras que
o `pdftotext` colou, ligaduras (U+FB00 a U+FB06) e hífen discricionário (U+00AD).
Com `atravessa_linhas`, ela acha também a expressão que a quebra de linha partiu: procura no texto
emendado, com a hifenização de fim de linha desfeita, e emenda a página do `pdftotext -layout`
coluna por coluna, porque linha por linha as colunas se intercalam. Quando vem a mesma cópia na
ordem de leitura (`pdftotext -raw`), procura-se também nela, e cada linha dela é devolvida com o
número da linha do texto que a contém. O resultado é uma lista de achados com número da linha e
contexto para cada lado, que é o que se lê para decidir — e o que se cita.
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, replace
from itertools import accumulate

TROCAS = str.maketrans({
    "−": "-", "–": "-", "‐": "-", "‑": "-", " ": " ",
    " ": " ", " ": " ",
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
    "\ufb05": "st", "\ufb06": "st",   # ligaduras
    "\u00ad": "",   # hífen discricionário no meio da palavra; o do fim de linha virou "-" em normalizar
})

# Para achar as colunas numa página do `pdftotext -layout`. A calha é o espaço em branco vertical
# entre duas colunas, e o vão é uma sequência de dois ou mais espaços dentro de uma linha.
LINHAS_MIN_PARA_COLUNAS = 8     # com menos linhas de texto, a página não dá sinal bastante da calha
LARGURA_MAX_DA_PAGINA = 400     # página com linha mais longa não é diagramada: é texto corrido, como o do JATS
COLUNA_MIN = 15                 # a coluna mais estreita, em caracteres
LINHAS_MIN_COM_VAO = 4          # quantas linhas, no mínimo, têm vão na calha com texto dos dois lados
FRACAO_MIN_COM_VAO = 0.2        # e que parte das linhas da página elas têm de ser
FRACAO_MAX_QUE_CRUZA = 0.25     # parte das linhas que podem atravessar a calha: título, rodapé, figura
PESO_DE_QUEM_CRUZA = 3          # na escolha da calha, uma linha que a atravessa desconta três com vão
TOLERANCIA_DA_CALHA = 6         # quanto o vão onde a linha se corta pode se afastar da calha


@dataclass(frozen=True)
class Achado:
    """Uma ocorrência. Na que atravessa linhas, `texto` é o pedaço onde ela começa, e `antes` e `depois`
    são os pedaços vizinhos na mesma coluna, não as linhas físicas, onde as colunas vêm intercaladas."""
    expressao: str
    linha: int
    texto: str
    antes: tuple[str, ...]
    depois: tuple[str, ...]
    continuacao: tuple[tuple[int, str], ...] = ()   # (linha, texto) das outras linhas que a ocorrência ocupa


@dataclass(frozen=True)
class _Trecho:
    """Um pedaço de linha no texto emendado: de que linha veio e onde ficou."""
    linha: int | None   # índice da linha, a partir de 0; None se o pedaço não está no texto conferido
    texto: str
    inicio: int
    fim: int


def normalizar(s: str) -> str:
    """O texto com as trocas de `TROCAS` e cada sequência de espaços reduzida a um."""
    s = re.sub("\u00ad(?=\\s|$)", "-", s)   # o hífen discricionário só aparece onde a linha quebrou
    return re.sub(r"[ \t]+", " ", s.translate(TROCAS))


def _literal(trecho: str) -> str:
    """O trecho escapado, em que o hífen depois de letra vira opcional: a emenda das linhas apaga o
    hífen de "self-" + "report" como apaga o de "perfor-" + "mance"."""
    return "-?".join(re.escape(p) for p in re.split(r"(?<=[^\W\d_])-(?=[^\W\d_]|$)", trecho))


def _padrao(expressao: str) -> re.Pattern:
    """Regex tolerante: espaço opcional em qualquer ponto, inclusive em volta de operadores, decimal
    com vírgula ou ponto, e a expressão emendada como o texto, se veio colada com a quebra de linha."""
    corrida, _ = _emendar([(0, normalizar(l)) for l in expressao.splitlines()])
    partes = []
    for trecho in re.split(r"(\s+|[=<>≤≥]|[.,](?=\d))", corrida):
        if not trecho:
            continue
        if trecho.isspace():
            partes.append(r"\s*")
        elif trecho in "=<>≤≥":
            partes.append(r"\s*" + re.escape(trecho) + r"\s*")
        elif trecho in ".,":
            partes.append(r"[.,]")
        else:
            inicio = r"(?<!\d)" if trecho[0].isdigit() else ""
            fim = r"(?!\d)" if trecho[-1].isdigit() else ""
            partes.append(inicio + _literal(trecho) + fim)
    return re.compile("".join(partes), re.IGNORECASE)


def _paginas(texto: str) -> list[list[tuple[int, str]]]:
    """As linhas de cada página, com o índice que o `str.splitlines` lhes dá; o form feed que o
    `pdftotext` põe no fim da página fecha a página."""
    paginas: list[list[tuple[int, str]]] = [[]]
    for i, (linha, peca) in enumerate(zip(texto.splitlines(), texto.splitlines(keepends=True))):
        paginas[-1].append((i, linha))
        if peca.endswith("\f"):
            paginas.append([])
    return [p for p in paginas if p]


def _calhas(linhas: list[str]) -> list[int]:
    """As posições de caractere onde a página do `pdftotext -layout` se divide em colunas, da
    esquerda para a direita. Há calha onde muitas linhas têm vão, com texto dos dois lados, e quase
    nenhuma tem texto naquela posição; sem sinal claro disso, a lista vem vazia."""
    com_texto = [l.replace("\t", " ") for l in linhas if l.strip()]
    if len(com_texto) < LINHAS_MIN_PARA_COLUNAS:
        return []
    largura = max(len(l) for l in com_texto)
    if largura > LARGURA_MAX_DA_PAGINA:
        return []
    vao = [0] * (largura + 1)      # contagens por posição, montadas como diferenças e somadas depois
    cruza = [0] * (largura + 1)
    for l in com_texto:
        ini, fim = len(l) - len(l.lstrip()), len(l.rstrip())
        cruza[ini] += 1
        cruza[fim] -= 1
        for m in re.finditer(r" {2,}", l[ini:fim]):
            a, b = ini + m.start(), ini + m.end()
            vao[a] += 1
            vao[b] -= 1
            cruza[a] -= 1
            cruza[b] += 1
    vao, cruza = list(accumulate(vao)), list(accumulate(cruza))
    n = len(com_texto)
    pontos = {x: vao[x] - PESO_DE_QUEM_CRUZA * cruza[x] for x in range(COLUNA_MIN, largura - COLUNA_MIN + 1)
              if vao[x] >= max(LINHAS_MIN_COM_VAO, FRACAO_MIN_COM_VAO * n) and cruza[x] <= FRACAO_MAX_QUE_CRUZA * n}
    calhas: list[int] = []
    for x in sorted(pontos, key=lambda x: -pontos[x]):
        a = b = x                  # o centro do platô de mesma pontuação é o meio do vão
        while pontos.get(a - 1) == pontos[x]:
            a -= 1
        while pontos.get(b + 1) == pontos[x]:
            b += 1
        centro = (a + b) // 2
        if all(abs(centro - c) >= COLUNA_MIN for c in calhas):
            calhas.append(centro)
    return sorted(calhas)


def _dividir(linha: str, calhas: list[int]) -> list[str] | None:
    """Os pedaços da linha, um por coluna, vazio onde a coluna não tem texto nesta linha; None quando
    o texto atravessa uma calha, como o título e o rodapé que ocupam a largura toda."""
    s = linha.replace("\t", " ")
    ini, fim = len(s) - len(s.lstrip()), len(s.rstrip())
    vaos = [(ini + m.start(), ini + m.end()) for m in re.finditer(r" {2,}", s[ini:fim])]
    cortes = set()
    for x in calhas:
        if not (ini < x - 1 and fim > x + 1):
            continue               # todo o texto da linha fica de um lado desta calha
        distancia, a, b = min(((0 if a <= x < b else min(abs(a - x), abs(b - 1 - x)), a, b) for a, b in vaos),
                              default=(TOLERANCIA_DA_CALHA + 1, 0, 0))
        if distancia > TOLERANCIA_DA_CALHA:
            return None
        cortes.add((a, b))
    pedacos = [""] * (len(calhas) + 1)
    pos = 0
    for a, b in sorted(cortes) + [(len(linha), len(linha))]:
        pedaco = linha[pos:a]
        if pedaco.strip():
            comeco = pos + len(pedaco) - len(pedaco.lstrip())
            k = sum(1 for x in calhas if x < comeco)
            pedacos[k] = f"{pedacos[k]} {pedaco.strip()}".strip()
        pos = b
    return pedacos


def _fluxo(texto: str) -> list[tuple[int, str]]:
    """As linhas com texto, cada uma com o seu índice, remontadas coluna por coluna. Numa página em
    colunas, vem cada coluna de cima a baixo, uma depois da outra; a linha que atravessa as colunas
    fecha o bloco que vinha antes dela, e o bloco seguinte recomeça pela primeira coluna."""
    fluxo: list[tuple[int, str]] = []
    for pagina in _paginas(texto):
        calhas = _calhas([l for _, l in pagina])
        colunas: list[list[tuple[int, str]]] = [[] for _ in range(len(calhas) + 1)]
        for i, linha in pagina:
            if not linha.strip():
                continue
            pedacos = _dividir(linha, calhas) if calhas else [linha]
            if pedacos is None:
                fluxo.extend(t for coluna in colunas for t in coluna)
                colunas = [[] for _ in range(len(calhas) + 1)]
                fluxo.append((i, normalizar(linha)))
                continue
            for k, pedaco in enumerate(pedacos):
                if pedaco.strip():
                    colunas[k].append((i, normalizar(pedaco)))
        fluxo.extend(t for coluna in colunas for t in coluna)
    return fluxo


def _chave(s: str) -> str:
    """A linha sem espaço nenhum: nas duas saídas do `pdftotext`, a mesma linha vem espaçada diferente."""
    return re.sub(r"\s+", "", normalizar(s))


def _fluxo_da_ordem(texto: str, ordem: str) -> list[tuple[int | None, str]]:
    """As linhas de `ordem`, a mesma cópia na ordem de leitura (a do `pdftotext -raw`), cada uma com
    o índice da linha de `texto` que a contém. Essa linha se procura na mesma página e, havendo mais
    de uma, fica a mais próxima da que coube à linha anterior; quando nenhuma a contém, o índice é
    None. A lista vem vazia se o número de páginas não bate, sinal de que as duas não vêm da mesma
    cópia."""
    paginas, paginas_da_ordem = _paginas(texto), _paginas(ordem)
    if len(paginas) != len(paginas_da_ordem):
        return []
    fluxo: list[tuple[int | None, str]] = []
    for pagina, da_ordem in zip(paginas, paginas_da_ordem):
        chaves = [(i, _chave(l)) for i, l in pagina]
        anterior = pagina[0][0] - 1
        for _, linha in da_ordem:
            chave = _chave(linha)
            if not chave:
                continue
            candidatas = [i for i, c in chaves if chave in c]
            if not candidatas:
                fluxo.append((None, normalizar(linha)))
                continue
            anterior = min(candidatas, key=lambda i: (abs(i - anterior - 1), i))
            fluxo.append((anterior, normalizar(linha)))
    return fluxo


def _juncao(anterior: str, seguinte: str) -> tuple[int, str]:
    """Como emendar duas linhas: quantos caracteres tirar do fim da anterior, e o separador."""
    if re.search(r"[^\W\d_]-$", anterior) and seguinte[:1].islower():
        return 1, ""     # palavra partida pela hifenização: "perfor-" + "mance"
    if anterior.endswith("-") and len(anterior) > 1 and not anterior[-2].isspace():
        return 0, ""     # o hífen é da palavra: "COVID-" + "19", "231-" + "245"
    return 0, " "


def _emendar(fluxo: list[tuple[int, str]]) -> tuple[str, list[_Trecho]]:
    """O fluxo virado em texto corrido, com a posição de cada trecho nele."""
    partes: list[str] = []
    trechos: list[_Trecho] = []
    pos = 0
    for linha, pedaco in fluxo:
        s = pedaco.strip()
        if trechos:
            corte, separador = _juncao(trechos[-1].texto, s)
            if corte:
                partes[-1] = partes[-1][:-corte]
                pos -= corte
                trechos[-1] = replace(trechos[-1], fim=trechos[-1].fim - corte)
            partes.append(separador)
            pos += len(separador)
        trechos.append(_Trecho(linha, s, pos, pos + len(s)))
        partes.append(s)
        pos += len(s)
    return "".join(partes), trechos


def _atravessam(padrao: re.Pattern, emendado: str, trechos: list[_Trecho]):
    """Os índices dos trechos que cada ocorrência toca, só das que atravessam quebra de linha."""
    inicios = [t.inicio for t in trechos]
    for m in padrao.finditer(emendado):
        achado = m.group()
        ini = m.start() + len(achado) - len(achado.lstrip())
        fim = m.end() - (len(achado) - len(achado.rstrip()))
        k = max(0, bisect.bisect_right(inicios, ini) - 1)
        tocados = []
        while k < len(trechos) and trechos[k].inicio < fim:
            if trechos[k].fim > ini:
                tocados.append(k)
            k += 1
        if len(tocados) > 1:
            yield tocados


def procurar(texto: str, expressoes: list[str], contexto: int = 1, *,
             atravessa_linhas: bool = False, ordem_de_leitura: str | None = None) -> list[Achado]:
    """Cada linha onde a expressão aparece. Com `atravessa_linhas`, vem também a ocorrência que a
    quebra de linha partiu, achada no texto emendado coluna por coluna e devolvida com as linhas que
    ocupa em `continuacao`. Com `ordem_de_leitura`, a mesma cópia na ordem em que o PDF a desenha, procura-se
    também nela, e vale só a ocorrência cujas linhas estão todas em `texto`."""
    linhas = normalizar(texto).splitlines()
    fluxos = [_emendar(_fluxo(texto))] if atravessa_linhas else []
    if ordem_de_leitura:
        fluxos.append(_emendar(_fluxo_da_ordem(texto, ordem_de_leitura)))
    achados = []
    for expressao in expressoes:
        padrao = _padrao(expressao)
        meus: dict[int, Achado] = {}
        for i, linha in enumerate(linhas):
            if padrao.search(linha):
                meus[i] = Achado(
                    expressao=expressao, linha=i + 1, texto=linha.strip(),
                    antes=tuple(l.strip() for l in linhas[max(0, i - contexto):i]),
                    depois=tuple(l.strip() for l in linhas[i + 1:i + 1 + contexto]))
        for emendado, trechos in fluxos:
            for tocados in _atravessam(padrao, emendado, trechos):
                primeiro, ultimo = tocados[0], tocados[-1]
                if trechos[primeiro].linha in meus or any(trechos[k].linha is None for k in tocados):
                    continue
                meus[trechos[primeiro].linha] = Achado(
                    expressao=expressao, linha=trechos[primeiro].linha + 1, texto=trechos[primeiro].texto,
                    antes=tuple(t.texto for t in trechos[max(0, primeiro - contexto):primeiro]),
                    depois=tuple(t.texto for t in trechos[ultimo + 1:ultimo + 1 + contexto]),
                    continuacao=tuple((trechos[k].linha + 1, trechos[k].texto) for k in tocados[1:]))
        achados.extend(meus[i] for i in sorted(meus))
    return achados


def relatorio(achados: list[Achado], expressoes: list[str], limite: int = 6) -> str:
    """Um bloco por expressão: quantas vezes apareceu e as primeiras ocorrências com contexto."""
    blocos = []
    for expressao in expressoes:
        meus = [a for a in achados if a.expressao == expressao]
        if not meus:
            blocos.append(f"✗ {expressao!r}: não encontrado")
            continue
        blocos.append(f"✓ {expressao!r}: {len(meus)} ocorrência(s)")
        for a in meus[:limite]:
            for l in a.antes:
                blocos.append(f"      {l}")
            blocos.append(f"  {a.linha:>5} {a.texto}")
            for n, l in a.continuacao:
                blocos.append(f"  {n:>5} {l}")
            for l in a.depois:
                blocos.append(f"      {l}")
        if len(meus) > limite:
            blocos.append(f"      … e mais {len(meus) - limite}")
    return "\n".join(blocos)
