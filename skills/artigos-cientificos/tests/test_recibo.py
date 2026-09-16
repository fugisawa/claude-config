"""As etiquetas A–D, o recibo de quem não abriu e a procedência da cópia obtida à mão."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import _caminho  # noqa: F401
import acesso
import artigo
import procedencia
from fontes import Registro

PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj << >> endobj\n%%EOF\n"
QUANDO = "2026-09-16T12:00:00-03:00"
RESULTADO = {
    "doi": "10.1007/s10648-025-10003-9", "status": "aberto", "degrau": "unpaywall", "etiqueta": "A",
    "url": "https://rep/x.pdf", "url_final": "https://rep/x.pdf", "formato": "pdf",
    "versao": "publishedVersion", "licenca": "", "sha256": "fece3dafc697518e4183f15aa0b5de99",
    "paginas": 27, "tentado_em": QUANDO, "baixado_em": QUANDO, "diario": ["crossref: ok"],
    "meta": {"titulo": "Increasing Video Lecture Playback Speed Can Impair Test Performance",
             "autores": ["Emily Tharumalingam", "Brady R. T. Roberts"],
             "periodico": "Educational Psychology Review", "ano": 2025, "volume": "37", "numero": "2",
             "paginas": "35"},
}
NAO_ABERTO = {**RESULTADO, "status": "nao_aberto", "degrau": "", "etiqueta": "",
              "diario": ["openalex: oa_status=closed, 0 candidato(s)"]}


def falso_buscar(respostas):
    def buscar(url, **kw):
        for trecho, resposta in respostas.items():
            if trecho in url:
                return resposta
        return 404, None
    return buscar


def falso_obter(respostas):
    def obter(url, **kw):
        status, corpo, final = respostas.get(url, (404, b"", url))
        return status, corpo, final, {}
    return obter


def extrair_falso(arquivo, formato):
    destino = arquivo.with_suffix(".txt")
    destino.write_text("texto extraído", encoding="utf-8")
    return destino


def info_falso(arquivo):
    return {"paginas": 27, "produtor": "Springer"}


class Etiquetas(unittest.TestCase):
    def test_todo_degrau_automatico_e_rota_a_e_o_manual_nao_tem_etiqueta_implicita(self):
        for degrau in acesso.DEGRAUS:
            self.assertEqual(procedencia.etiqueta_do_degrau(degrau), "A", degrau)
        self.assertEqual(procedencia.etiqueta_do_degrau("manual"), "")
        self.assertEqual(procedencia.nome_da_etiqueta("C"), "rota C, cinzenta")
        self.assertEqual(procedencia.nome_da_etiqueta(""), "")

    def test_abrir_carrega_a_etiqueta_e_a_data_da_tentativa(self):
        buscar = falso_buscar({"api.openalex.org": (200, {
            "doi": "https://doi.org/10.1/x", "open_access": {"is_oa": True},
            "best_oa_location": {"is_oa": True, "pdf_url": "https://rep/x.pdf", "version": "publishedVersion"}})})
        obter = falso_obter({"https://rep/x.pdf": (200, PDF, "https://rep/x.pdf")})
        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir("10.1/x", Path(pasta), buscar=buscar, obter=obter, extrair=extrair_falso, agora=QUANDO)
            self.assertEqual((r["status"], r["etiqueta"], r["tentado_em"]), ("aberto", "A", QUANDO))
            listado = acesso.abrir("10.1/x", Path(pasta), buscar=buscar, obter=obter, apenas_listar=True, agora=QUANDO)
        self.assertEqual((listado["status"], listado["tentado_em"]), ("listado", QUANDO))
        self.assertNotIn("etiqueta", listado)

    def test_paragrafo_traz_a_rota(self):
        p = procedencia.paragrafo_fonte(procedencia.registro_de_procedencia(RESULTADO, "2026-09-16"))
        self.assertIn("Cópia obtida em https://rep/x.pdf, por Unpaywall (rota A, licenciada)", p)
        self.assertNotIn("Ressalva", p)
        self.assertNotIn("redistribuir", p)

    def test_versao_que_nao_e_a_publicada_ganha_ressalva(self):
        reg = procedencia.registro_de_procedencia({**RESULTADO, "versao": "acceptedVersion"})
        self.assertIn("Ressalva: a versão lida não é a publicada", procedencia.paragrafo_fonte(reg))

    def test_rota_c_avisa_que_nao_se_redistribui(self):
        reg = procedencia.registro_de_procedencia(
            {**RESULTADO, "degrau": "manual", "etiqueta": "C", "origem": "site do coautor Brady Roberts"})
        p = procedencia.paragrafo_fonte(reg)
        self.assertIn("por site do coautor Brady Roberts (rota C, cinzenta)", p)
        self.assertIn("não redistribuir", p)
        self.assertEqual(reg["etiqueta_nome"], "cinzenta")


class ReciboNaoObtido(unittest.TestCase):
    def test_traz_data_diario_pendencias_e_reavaliacao(self):
        reg = procedencia.registro_de_procedencia(
            NAO_ABERTO, pendencias=["pedido ao autor rascunhado em 2026-09-16 para Emily Tharumalingam"],
            reavaliar_em="2026-10-16")
        p = procedencia.paragrafo_fonte(reg)
        self.assertIn("não obtido por via legal em 2026-09-16", p)
        self.assertIn("oa_status=closed", p)
        self.assertIn("Pendências: pedido ao autor rascunhado em 2026-09-16 para Emily Tharumalingam.", p)
        self.assertIn("Reavaliar em 2026-10-16.", p)
        self.assertEqual((reg["etiqueta"], reg["reavaliar_em"]), ("", "2026-10-16"))

    def test_sem_pendencias_nao_inventa(self):
        p = procedencia.paragrafo_fonte(procedencia.registro_de_procedencia(NAO_ABERTO))
        self.assertIn("⚑", p)
        self.assertNotIn("Pendências", p)
        self.assertNotIn("Reavaliar", p)


class RegistrarManual(unittest.TestCase):
    def test_pdf_do_site_do_autor_vira_procedencia_de_rota_c(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "copia.pdf"
            arquivo.write_bytes(PDF)
            meta = Registro(doi="10.1/x", titulo="T", autores=("Ana Silva",), ano=2025)
            r = acesso.registrar_manual("10.1/x", arquivo, url="https://autor.ca/x.pdf", origem="site do coautor",
                                        etiqueta="C", versao="publicada", meta=meta,
                                        extrair=extrair_falso, info=info_falso, agora=QUANDO)
            self.assertEqual((r["status"], r["degrau"], r["etiqueta"], r["versao"], r["paginas"]),
                             ("aberto", "manual", "C", "publishedVersion", 27))
            self.assertEqual(len(r["sha256"]), 64)
            self.assertEqual(r["meta"]["autores"], ["Ana Silva"])
            self.assertTrue(Path(r["texto"]).exists())
            p = procedencia.paragrafo_fonte(procedencia.registro_de_procedencia(r, "2026-09-16"))
        self.assertIn("https://autor.ca/x.pdf, por site do coautor (rota C, cinzenta)", p)
        self.assertIn("conferidos no texto em 2026-09-16", p)

    def test_rota_d_e_recusada_e_so_pdf_ou_xml_de_verdade_entra(self):
        with tempfile.TemporaryDirectory() as pasta:
            pdf = Path(pasta) / "copia.pdf"
            pdf.write_bytes(PDF)
            html = Path(pasta) / "pagina.html"
            html.write_bytes(b"<html>")
            falso = Path(pasta) / "falso.pdf"
            falso.write_bytes(b"<html>paywall</html>")
            for arquivo, etiqueta in ((pdf, "D"), (html, "A"), (falso, "A")):
                with self.assertRaises(RuntimeError):
                    acesso.registrar_manual("10.1/x", arquivo, url="u", origem="o", etiqueta=etiqueta,
                                            extrair=extrair_falso, info=info_falso)


class CliRecibo(unittest.TestCase):
    def _capturar(self, argv):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            codigo = artigo.main(argv)
        return codigo, saida.getvalue()

    def test_abrir_nao_aberto_imprime_o_recibo_e_so_grava_quando_ha_destino(self):
        original = acesso.abrir
        acesso.abrir = lambda doi, destino, **kw: {**NAO_ABERTO, "doi": doi, "meta": None, "candidatos": []}
        try:
            with tempfile.TemporaryDirectory() as pasta:
                codigo, saida = self._capturar(["abrir", "10.1000/x", "--destino", pasta, "--json",
                                                "--pendencia", "pedido rascunhado em 2026-09-16 para X",
                                                "--reavaliar-em", "2026-10-16"])
                self.assertEqual(codigo, 2)
                r = json.loads(saida)
                self.assertIn("Pendências: pedido rascunhado em 2026-09-16 para X.", r["recibo"])
                self.assertIn("Reavaliar em 2026-10-16.", r["recibo"])
                gravado = json.loads(Path(r["procedencia"]).read_text(encoding="utf-8"))
                self.assertEqual(gravado["reavaliar_em"], "2026-10-16")
            codigo, saida = self._capturar(["abrir", "10.1000/x", "--json"])
            self.assertEqual(codigo, 2)
            self.assertNotIn("procedencia", json.loads(saida))
        finally:
            acesso.abrir = original

    def test_registrar_pela_cli(self):
        original_meta, original_reg = artigo._metadados, acesso.registrar_manual
        artigo._metadados = lambda doi, email: {"titulo": "T", "autores": ["Ana Silva"], "ano": 2025, "periodico": "Rev"}
        acesso.registrar_manual = lambda *a, **k: original_reg(*a, **{**k, "extrair": extrair_falso, "info": info_falso})
        try:
            with tempfile.TemporaryDirectory() as pasta:
                arquivo = Path(pasta) / "copia.pdf"
                arquivo.write_bytes(PDF)
                codigo, saida = self._capturar(["registrar", "10.1000/x", "--arquivo", str(arquivo),
                                                "--url", "https://autor.ca/x.pdf", "--origem", "site do coautor",
                                                "--etiqueta", "C", "--versao", "publicada", "--json"])
                self.assertEqual(codigo, 0)
                r = json.loads(saida)
                self.assertEqual(r["etiqueta"], "C")
                self.assertTrue(Path(r["procedencia"]).exists())
                self.assertIn("rota C, cinzenta", r["recibo"])
                with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                    artigo.main(["registrar", "10.1000/x", "--arquivo", str(arquivo), "--url", "u",
                                 "--origem", "o", "--etiqueta", "D"])
        finally:
            artigo._metadados, acesso.registrar_manual = original_meta, original_reg


if __name__ == "__main__":
    unittest.main()
