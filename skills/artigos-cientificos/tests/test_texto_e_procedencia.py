import tempfile
import unittest
from pathlib import Path

import _caminho  # noqa: F401
import artigo
import leitura
import procedencia
import texto

TRECHO = """Results of the categorical model
    Playback speed 1.5x: g = −0.09, 95% CI [−0.23, 0.05], k = 36, p = .19
    Playback speed 2x:   g = −0.36, 95% CI [−0.49, −0.23], k = 48, p < .001
Table 2 prints k = 49 for 2x.
"""


class Procurar(unittest.TestCase):
    def test_tolera_menos_tipografico_virgula_decimal_e_espacos(self):
        achados = texto.procurar(TRECHO, ["g = -0,36", "g=-0.09", "k = 48"])
        self.assertEqual([a.linha for a in achados], [3, 2, 3])
        self.assertIn("2x", achados[0].texto)

    def test_numero_nao_casa_dentro_de_numero_maior(self):
        self.assertEqual(texto.procurar("Resultado: k = 360 participantes.", ["k = 36"]), [])
        self.assertEqual(texto.procurar("p = .195 no modelo", ["p = .19"]), [])
        self.assertEqual(texto.procurar("g = 10.36 no total", ["g = 0.36"]), [])
        self.assertEqual(len(texto.procurar("k = 36, p = .19", ["k = 36", "p = .19"])), 2)

    def test_reporta_o_que_nao_achou(self):
        achados = texto.procurar(TRECHO, ["g = -0.86"])
        self.assertEqual(achados, [])
        self.assertIn("não encontrado", texto.relatorio(achados, ["g = -0.86"]))

    def test_contexto_vem_junto(self):
        a = texto.procurar(TRECHO, ["p < .001"], contexto=1)[0]
        self.assertEqual(len(a.antes), 1)
        self.assertIn("Table 2", a.depois[0])


class Jats(unittest.TestCase):
    def test_corpo_vira_paragrafos(self):
        xml = b'<article xmlns:x="u"><front><title>T</title></front><body><p>um</p><sec><title>Res</title><p>dois</p></sec></body></article>'
        self.assertEqual(leitura.jats_para_texto(xml), "um\n\nRes\n\ndois")

    def test_elemento_aninhado_nao_duplica(self):
        xml = b'<article><body><fig><caption><title>Legenda</title><p>texto da legenda</p></caption></fig></body></article>'
        self.assertEqual(leitura.jats_para_texto(xml), "Legenda texto da legenda")
        em_linha = b'<article><body><p>CO<sub>2</sub> e <italic>g</italic> = 1</p></body></article>'
        self.assertEqual(leitura.jats_para_texto(em_linha), "CO2 e g = 1")

    def test_xml_quebrado_nao_derruba(self):
        self.assertEqual(leitura.jats_para_texto(b"<a><b>"), "<a><b>")


class Procedencia(unittest.TestCase):
    RESULTADO = {
        "doi": "10.1007/s10648-025-10003-9", "status": "aberto", "degrau": "unpaywall",
        "url": "https://rep/x.pdf", "url_final": "https://rep/x.pdf", "formato": "pdf",
        "versao": "publishedVersion", "licenca": "", "sha256": "fece3dafc697518e4183f15aa0b5de99",
        "paginas": 27, "baixado_em": "2026-09-16T11:00:00-03:00", "diario": ["crossref: ok"],
        "meta": {"titulo": "Increasing Video Lecture Playback Speed Can Impair Test Performance",
                 "autores": ["Emily Tharumalingam", "Brady R. T. Roberts", "Jonathan M. Fawcett", "Evan F. Risko"],
                 "periodico": "Educational Psychology Review", "ano": 2025, "volume": "37", "numero": "2", "paginas": "35"},
    }

    def test_slug(self):
        self.assertEqual(procedencia.slug_de_doi("10.1007/S10648-025-10003-9"), "10-1007-s10648-025-10003-9")

    def test_autores_curtos(self):
        self.assertEqual(procedencia.autores_curtos(["Ana Silva"]), "Silva")
        self.assertEqual(procedencia.autores_curtos(["Ana Silva", "Bia Souza"]), "Silva e Souza")
        self.assertEqual(procedencia.autores_curtos(["A B", "C D", "E F"]), "B e col.")

    def test_paragrafo_fonte_aberto(self):
        reg = procedencia.registro_de_procedencia(self.RESULTADO, "2026-09-16")
        p = procedencia.paragrafo_fonte(reg)
        self.assertTrue(p.startswith("Fonte: Tharumalingam e col. (2025)"))
        for trecho in ("*Educational Psychology Review* 37(2), 35", "DOI 10.1007/s10648-025-10003-9",
                       "Unpaywall", "versão publicada", "27 páginas", "SHA-256 fece3dafc697", "conferidos no texto em 2026-09-16"):
            self.assertIn(trecho, p)

    def test_paragrafo_fonte_nao_aberto_mantem_a_bandeira(self):
        reg = procedencia.registro_de_procedencia({**self.RESULTADO, "status": "nao_aberto"})
        self.assertIn("⚑", procedencia.paragrafo_fonte(reg))
        self.assertIn("não conferidos", procedencia.paragrafo_fonte(reg))

    def test_gravar(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = procedencia.gravar(Path(pasta), "x", {"a": 1})
            self.assertEqual(caminho.name, "x.procedencia.json")
            self.assertIn('"a": 1', caminho.read_text())


class Cli(unittest.TestCase):
    def test_conferir_devolve_2_quando_falta_algo(self):
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "t.txt"
            arq.write_text(TRECHO, encoding="utf-8")
            self.assertEqual(artigo.main(["conferir", str(arq), "g = -0.36"]), 0)
            self.assertEqual(artigo.main(["conferir", str(arq), "g = -0.36", "g = -0.86"]), 2)
            self.assertEqual(artigo.main(["conferir", str(Path(pasta) / "nao-existe.txt", ), "x"]), 1)

    def test_abrir_sem_doi_e_erro_de_uso(self):
        self.assertEqual(artigo.main(["abrir", "sem doi aqui"]), 1)


if __name__ == "__main__":
    unittest.main()
