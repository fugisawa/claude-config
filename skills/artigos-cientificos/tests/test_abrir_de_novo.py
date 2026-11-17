"""O `abrir` que roda de novo sobre o recibo que já está no destino. O caso é o de 28/09/2026: as cópias de
Marrin (2012), enviada pelo autor, e de Mandel e Barnes (2014), lida no PubMed Central, foram registradas à
mão com o `registrar`, e um novo `abrir` trocava o recibo delas pelo de "não obtido" quando a escada falhava,
ou escrevia `<slug>.pdf` e `<slug>.txt` por cima da cópia de Marrin quando abria. A cópia aberta só se troca
com `--substituir`. O recibo de "não obtido" passa ao novo o diário, depois da linha que marca a nova
tentativa, e a data da primeira; a tentativa que repete o resultado da anterior fica numa linha só, como a do
`abrir --pendencia` rodado logo depois do pedido ao autor (decisões do Daniel em 28/09/2026)."""
import contextlib
import functools
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _caminho  # noqa: F401
import acesso
import artigo
import procedencia

DOI = "10.1080/02684527.2012.699290"
SLUG = procedencia.slug_de_doi(DOI)
OUTRO_DOI_DO_MESMO_NOME = "10.1080/02684527/2012/699290"   # só a pontuação muda, e o nome do arquivo é o mesmo
META = {"titulo": "Evaluating the Quality of Intelligence Analysis: By What (Mis) Measure?", "autores": ["Stephen Marrin"],
        "periodico": "Intelligence and National Security", "ano": 2012, "volume": "27", "numero": "6",
        "paginas": "896-912"}
PRIMEIRA = "2026-09-26T02:20:38-03:00"      # a escada falhou, e o pedido ao autor foi rascunhado
CHEGOU = "2026-09-27T15:07:12-03:00"        # a cópia do autor foi registrada
QUANDO = "2026-10-26T10:00:00-03:00"        # o abrir de novo, na data de reavaliar
DIARIO_DA_FALHA = ["crossref: metadados obtidos", "openalex: oa_status=closed, 0 candidato(s)",
                   "unpaywall: oa_status=closed, 0 candidato(s)", "semantic-scholar: 0 candidato(s)",
                   "europepmc: sem texto integral"]
ORIGEM = "cópia enviada pelo autor Stephen Marrin em 2026-09-27, em resposta ao pedido de 2026-09-26"
PENDENCIA = "pedido ao autor rascunhado em 2026-09-26 para Stephen Marrin"
PDF_DO_AUTOR = b"%PDF-1.4\n% a copia que o autor enviou\n%%EOF\n"
TEXTO_DO_AUTOR = "Evaluating the Quality of Intelligence Analysis\n"
URL_OA = "https://repositorio.exemplo/marrin-2012.pdf"
PDF_DA_ESCADA = b"%PDF-1.7\n% a copia que a escada abriu\n%%EOF\n"
OPENALEX_ABERTO = {"doi": f"https://doi.org/{DOI}", "open_access": {"is_oa": True},
                   "best_oa_location": {"is_oa": True, "pdf_url": URL_OA, "version": "publishedVersion"}}
# o diário da escada falsa quando tudo responde 404, sem ARTIGOS_EMAIL
DIARIO_DA_ESCADA_QUE_FALHA = ["crossref: sem registro", "openalex: sem registro", acesso.SEM_EMAIL,
                              "semantic-scholar: sem registro", "europepmc: sem texto integral", "ncbi-efetch: sem PMCID"]


def recibo_da_falha(diario=DIARIO_DA_FALHA) -> dict:
    """O recibo de Marrin (2012) depois que a escada falhou e o pedido ao autor foi rascunhado."""
    return procedencia.registro_de_procedencia(
        {"doi": DOI, "status": "nao_aberto", "meta": META, "tentado_em": PRIMEIRA, "diario": list(diario)},
        pendencias=[PENDENCIA], reavaliar_em="2026-10-26")


def recibo_da_copia_do_autor(pasta: Path) -> dict:
    """O recibo que o `registrar` gravou quando a cópia do autor chegou, com a cópia e o texto no nome do DOI."""
    return procedencia.registro_de_procedencia(
        {"doi": DOI, "status": "aberto", "meta": META, "degrau": "manual", "etiqueta": "A", "origem": ORIGEM,
         "url": "anexo-de-e-mail", "url_final": "anexo-de-e-mail", "formato": "pdf", "versao": "publishedVersion",
         "arquivo": str(pasta / f"{SLUG}.pdf"), "texto": str(pasta / f"{SLUG}.txt"),
         "sha256": hashlib.sha256(PDF_DO_AUTOR).hexdigest(), "tentado_em": PRIMEIRA, "baixado_em": CHEGOU,
         "diario": DIARIO_DA_FALHA + [f"manual: {ORIGEM}, em anexo-de-e-mail"]}, "2026-09-27")


def escada(abre: bool, consultas: list):
    """A rede falsa: com `abre`, o OpenAlex aponta um PDF que responde; sem, tudo responde 404. Cada consulta
    fica em `consultas`."""
    def buscar(url, **kw):
        consultas.append(url)
        return (200, OPENALEX_ABERTO) if abre and "api.openalex.org" in url else (404, None)

    def obter(url, **kw):
        consultas.append(url)
        return (200, PDF_DA_ESCADA, url, {}) if abre and url == URL_OA else (404, b"", url, {})
    return buscar, obter


def extrair_falso(arquivo, formato):
    destino = arquivo.with_suffix(".txt")
    destino.write_text("texto extraído da cópia da escada", encoding="utf-8")
    return destino


def extrair_que_falha(arquivo, formato):
    """O pdftotext diante de um PDF truncado, que passa no teste do cabeçalho: cria o .txt vazio e sai com erro."""
    arquivo.with_suffix(".txt").write_text("", encoding="utf-8")
    raise subprocess.CalledProcessError(1, ["pdftotext", "-layout", str(arquivo)])


class Pasta(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta)
        self.consultas = []

    def recibo(self) -> Path:
        return self.pasta / f"{SLUG}.procedencia.json"

    def gravado(self) -> dict:
        return json.loads(self.recibo().read_text(encoding="utf-8"))

    def rodar(self, *argv, abre: bool, quando: str = QUANDO, extrair=extrair_falso, doi: str = DOI):
        """O `abrir` pela linha de comando, com a rede falsa e sem ARTIGOS_EMAIL, que mudaria o diário."""
        buscar, obter = escada(abre, self.consultas)
        sem_rede = functools.partial(acesso.abrir, buscar=buscar, obter=obter, extrair=extrair, agora=quando)
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.object(acesso, "abrir", sem_rede), mock.patch.dict(os.environ), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            os.environ.pop("ARTIGOS_EMAIL", None)
            try:
                codigo = artigo.main(["abrir", doi, "--destino", str(self.pasta), *argv])
            except SystemExit as saiu:          # o argparse sai assim diante de opção que não conhece
                codigo = saiu.code
        return codigo, saida.getvalue(), erro.getvalue()


class CopiaAberta(Pasta):
    """O recibo que o `registrar` gravou para a cópia que o autor enviou."""
    def setUp(self):
        super().setUp()
        self.pdf, self.txt = self.pasta / f"{SLUG}.pdf", self.pasta / f"{SLUG}.txt"
        self.pdf.write_bytes(PDF_DO_AUTOR)
        self.txt.write_text(TEXTO_DO_AUTOR, encoding="utf-8")
        procedencia.gravar(self.pasta, SLUG, recibo_da_copia_do_autor(self.pasta))
        self.antes = self.recibo().read_bytes()

    def test_nao_troca_o_recibo_da_copia_aberta_pelo_de_nao_obtido(self):
        codigo, _, _ = self.rodar(abre=False)
        self.assertEqual(codigo, 1)
        self.assertEqual(self.recibo().read_bytes(), self.antes)

    def test_nao_escreve_por_cima_da_copia_quando_a_escada_abriria(self):
        codigo, _, _ = self.rodar(abre=True)
        self.assertEqual(codigo, 1)
        self.assertEqual((self.pdf.read_bytes(), self.txt.read_text(encoding="utf-8")), (PDF_DO_AUTOR, TEXTO_DO_AUTOR))
        self.assertEqual(self.recibo().read_bytes(), self.antes)

    def test_para_antes_de_consultar_a_rede_e_diz_as_tres_maneiras_de_seguir(self):
        _, _, erro = self.rodar(abre=True)
        self.assertEqual(self.consultas, [])
        for trecho in (self.recibo().name, "--substituir", "--listar", "--destino"):
            self.assertIn(trecho, erro)

    def test_com_substituir_a_copia_que_a_escada_abre_toma_o_lugar_da_manual(self):
        codigo, _, _ = self.rodar("--substituir", abre=True)
        self.assertEqual(codigo, 0)
        self.assertEqual((self.pdf.read_bytes(), self.txt.read_text(encoding="utf-8")),
                         (PDF_DA_ESCADA, "texto extraído da cópia da escada"))
        self.assertEqual((self.gravado()["degrau"], self.gravado()["sha256"]),
                         ("openalex", hashlib.sha256(PDF_DA_ESCADA).hexdigest()))

    def test_com_substituir_a_extracao_que_falha_deixa_a_copia_o_texto_e_o_recibo_como_estavam(self):
        codigo, _, _ = self.rodar("--substituir", abre=True, extrair=extrair_que_falha)
        self.assertEqual(codigo, 1)
        self.assertEqual((self.pdf.read_bytes(), self.txt.read_text(encoding="utf-8")), (PDF_DO_AUTOR, TEXTO_DO_AUTOR))
        self.assertEqual(self.recibo().read_bytes(), self.antes)
        self.assertEqual(sorted(p.name for p in self.pasta.iterdir()),
                         sorted([self.pdf.name, self.txt.name, self.recibo().name]))

    def test_com_substituir_o_recibo_novo_nao_emenda_o_da_copia_aberta(self):
        self.rodar("--substituir", abre=True)
        gravado = self.gravado()
        self.assertEqual(gravado["tentado_em"], QUANDO)
        self.assertNotIn(f"manual: {ORIGEM}, em anexo-de-e-mail", gravado["diario"])

    def test_com_substituir_a_escada_que_falha_deixa_o_recibo_como_estava_e_diz_isso(self):
        codigo, saida, _ = self.rodar("--substituir", abre=False)
        self.assertEqual(codigo, 2)
        self.assertEqual(self.recibo().read_bytes(), self.antes)
        self.assertIn(self.recibo().name, saida)

    def test_recibo_de_outro_doi_com_o_mesmo_nome_de_arquivo_para_o_abrir_mesmo_com_substituir(self):
        codigo, _, erro = self.rodar("--substituir", abre=True, doi=OUTRO_DOI_DO_MESMO_NOME)
        self.assertEqual(codigo, 1)
        self.assertIn(DOI, erro)
        self.assertEqual((self.pdf.read_bytes(), self.recibo().read_bytes()), (PDF_DO_AUTOR, self.antes))
        self.assertEqual(self.consultas, [])

    def test_listar_segue_livre_porque_nao_grava_nada(self):
        codigo, saida, _ = self.rodar("--listar", abre=True)
        self.assertEqual(codigo, 0)
        self.assertIn(URL_OA, saida)
        self.assertEqual(self.recibo().read_bytes(), self.antes)


class NaoObtido(Pasta):
    """O recibo de Marrin (2012) antes de a cópia do autor chegar: a escada falhou e o pedido foi rascunhado."""
    def setUp(self):
        super().setUp()
        procedencia.gravar(self.pasta, SLUG, recibo_da_falha())

    def test_a_copia_que_abre_herda_o_diario_depois_da_linha_da_nova_tentativa(self):
        codigo, _, _ = self.rodar(abre=True)
        self.assertEqual(codigo, 0)
        diario = self.gravado()["diario"]
        self.assertEqual(diario[:6], DIARIO_DA_FALHA + ["nova tentativa em 2026-10-26"])
        self.assertEqual(diario[-1], f"openalex: aberto como pdf a partir de {URL_OA}")

    def test_a_copia_que_abre_guarda_a_data_da_primeira_tentativa_e_nao_as_pendencias(self):
        self.rodar(abre=True)
        gravado = self.gravado()
        self.assertEqual((gravado["tentado_em"], gravado["baixado_em"]), (PRIMEIRA, QUANDO))
        self.assertEqual((gravado["pendencias"], gravado["reavaliar_em"]), ([], ""))

    def test_a_tentativa_que_falha_com_outro_resultado_entra_inteira_depois_da_linha(self):
        codigo, _, _ = self.rodar(abre=False)
        self.assertEqual(codigo, 2)
        gravado = self.gravado()
        self.assertEqual(gravado["diario"],
                         DIARIO_DA_FALHA + ["nova tentativa em 2026-10-26"] + DIARIO_DA_ESCADA_QUE_FALHA)
        self.assertEqual(gravado["tentado_em"], PRIMEIRA)

    def test_a_tentativa_que_falha_de_novo_guarda_as_pendencias_e_a_data_de_reavaliar(self):
        _, saida, _ = self.rodar(abre=False)
        gravado = self.gravado()
        self.assertEqual((gravado["pendencias"], gravado["reavaliar_em"]), ([PENDENCIA], "2026-10-26"))
        self.assertIn(f"Pendências: {PENDENCIA}.", saida)

    def test_recibo_de_outro_doi_com_o_mesmo_nome_de_arquivo_nao_passa_o_diario(self):
        antes = self.recibo().read_bytes()
        codigo, _, _ = self.rodar(abre=False, doi=OUTRO_DOI_DO_MESMO_NOME)
        self.assertEqual(codigo, 1)
        self.assertEqual(self.recibo().read_bytes(), antes)

    def test_o_que_se_passa_de_novo_toma_o_lugar_do_antigo_campo_a_campo(self):
        self.rodar("--pendencia", "pedido ao autor enviado em 2026-09-27", abre=False)
        gravado = self.gravado()
        self.assertEqual((gravado["pendencias"], gravado["reavaliar_em"]),
                         (["pedido ao autor enviado em 2026-09-27"], "2026-10-26"))


class TentativaRepetida(Pasta):
    """O `abrir` que roda de novo e dá com o mesmo resultado, como o `abrir --pendencia` logo depois do pedido."""
    def test_a_que_repete_o_resultado_da_anterior_fica_numa_linha_so(self):
        self.rodar(abre=False, quando=PRIMEIRA)
        self.rodar("--pendencia", PENDENCIA, "--reavaliar-em", "2026-10-26", abre=False,
                   quando="2026-09-26T02:40:00-03:00")
        self.assertEqual(self.gravado()["diario"],
                         DIARIO_DA_ESCADA_QUE_FALHA + ["nova tentativa em 2026-09-26, com o mesmo resultado"])

    def test_cada_repeticao_ganha_a_sua_linha(self):
        for quando in (PRIMEIRA, QUANDO, "2026-11-26T10:00:00-03:00"):
            self.rodar(abre=False, quando=quando)
        self.assertEqual(self.gravado()["diario"], DIARIO_DA_ESCADA_QUE_FALHA + [
            "nova tentativa em 2026-10-26, com o mesmo resultado", "nova tentativa em 2026-11-26, com o mesmo resultado"])

    def test_o_resultado_se_compara_com_o_da_ultima_tentativa_e_nao_com_o_da_primeira(self):
        procedencia.gravar(self.pasta, SLUG, recibo_da_falha())      # a primeira, com outro diário
        self.rodar(abre=False, quando=QUANDO)                         # a segunda, com o da escada falsa
        self.rodar(abre=False, quando="2026-11-26T10:00:00-03:00")    # a terceira repete a segunda
        self.assertEqual(self.gravado()["diario"], DIARIO_DA_FALHA + ["nova tentativa em 2026-10-26"]
                         + DIARIO_DA_ESCADA_QUE_FALHA + ["nova tentativa em 2026-11-26, com o mesmo resultado"])


class ExtracaoQueFalha(Pasta):
    def test_nao_deixa_a_copia_baixada_pela_metade_e_diz_de_onde_ela_veio(self):
        codigo, _, erro = self.rodar(abre=True, extrair=extrair_que_falha)
        self.assertEqual(codigo, 1)
        self.assertEqual(list(self.pasta.iterdir()), [])
        self.assertIn(URL_OA, erro)


class ReciboIlegivel(Pasta):
    def test_para_o_abrir_antes_da_rede_e_fica_como_estava(self):
        self.recibo().write_text("{ recibo cortado", encoding="utf-8")
        codigo, _, erro = self.rodar(abre=True)
        self.assertEqual(codigo, 1)
        self.assertIn(self.recibo().name, erro)
        self.assertEqual(self.recibo().read_text(encoding="utf-8"), "{ recibo cortado")
        self.assertEqual(self.consultas, [])


if __name__ == "__main__":
    unittest.main()
