"""A capa do ResearchGate, que sai da cópia de leitura no `registrar` e no `abrir`. O caso é o de
28/09/2026: o autor pediu que ela saísse de todas as cópias, e isso foi feito à mão em Chang e Tetlock
(2016) e em Klein e Borders (2016). O PDF obtido vai para `originais/`, com o mesmo nome e a data que
tinha; a cópia de leitura fica no lugar dele, sem a p. 1 e com a data de agora; o recibo e o parágrafo
`Fonte:` continuam com o hash e as páginas do PDF obtido, que é o que se confere contra a URL."""
import contextlib
import functools
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import _caminho  # noqa: F401
import acesso
import artigo
import leitura
import procedencia

try:
    import pypdf  # noqa: F401
    TEM_PYPDF = True
except ImportError:
    TEM_PYPDF = False
TEM_POPPLER = all(shutil.which(b) for b in ("pdftotext", "pdfinfo"))

DOI = "10.1177/1555343416636515"
URL = "https://www.shadowboxtraining.com/wp-content/uploads/2021/05/The_ShadowBox_Approach_to_Cognitive_Skills_Trainin.pdf"
ORIGEM = "site da ShadowBox LLC, empresa do coautor Joseph Borders"
QUANDO = "2026-09-28T15:00:00-03:00"
ANTES = time.mktime((2026, 9, 26, 17, 43, 59, 0, 0, -1))   # a data do PDF obtido, baixado em 26/09
NOME = "klein-borders-2016-manual.pdf"
CAPA = ["See discussions, stats, and author profiles for this publication at:",
        "https://www.researchgate.net/publication/299540302",
        "The ShadowBox Approach to Cognitive Skills Training",
        "CITATION READS"]
PRIMEIRA = ["Journal of Cognitive Engineering and Decision Making",
            "The ShadowBox Approach to Cognitive Skills Training",
            "Gary Klein and Joseph Borders"]
SEGUNDA = ["Results", "ShadowBox trainees matched the experts on more items."]


def pdf_de_paginas(paginas: list[list[str]]) -> bytes:
    """Um PDF com uma página para cada lista de linhas, em Helvetica 10, uma linha embaixo da outra."""
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(len(paginas)))
    objetos = ["<< /Type /Catalog /Pages 2 0 R >>",
               f"<< /Type /Pages /Kids [{kids}] /Count {len(paginas)} >>",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, linhas in enumerate(paginas):
        fluxo = "BT /F1 10 Tf " + " ".join(f"1 0 0 1 50 {700 - 14 * k} Tm ({s}) Tj" for k, s in enumerate(linhas)) + " ET"
        objetos += [f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {5 + 2 * i} 0 R"
                    " /Resources << /Font << /F1 3 0 R >> >> >>",
                    f"<< /Length {len(fluxo)} >>\nstream\n{fluxo}\nendstream"]
    pdf, posicoes = "%PDF-1.4\n", []
    for n, corpo in enumerate(objetos, 1):
        posicoes.append(len(pdf))
        pdf += f"{n} 0 obj\n{corpo}\nendobj\n"
    xref = len(pdf)
    pdf += (f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n" + "".join(f"{p:010d} 00000 n \n" for p in posicoes)
            + f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n")
    return pdf.encode("latin-1")


COM_CAPA = pdf_de_paginas([CAPA, PRIMEIRA, SEGUNDA])


def sha256(corpo: bytes) -> str:
    return hashlib.sha256(corpo).hexdigest()


class Pasta(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta)
        self.arquivo = self.pasta / NOME
        self.original = self.pasta / "originais" / NOME

    def obtido(self, corpo: bytes = COM_CAPA) -> Path:
        self.arquivo.write_bytes(corpo)
        os.utime(self.arquivo, (ANTES, ANTES))
        return self.arquivo

    def registrar(self, **kw) -> dict:
        return acesso.registrar_manual(DOI, self.arquivo, url=URL, origem=ORIGEM, etiqueta="C",
                                       versao="publicada", agora=QUANDO, **kw)


class DeteccaoDaCapa(unittest.TestCase):
    def test_as_duas_marcas_do_researchgate_na_mesma_linha_ou_em_linhas_separadas(self):
        self.assertTrue(leitura.eh_capa_do_researchgate(
            "See discussions, stats, and author profiles for this publication at: "
            "https://www.researchgate.net/publication/296331734\n\n\nRethinking the training of intelligence analysts\n"))
        self.assertTrue(leitura.eh_capa_do_researchgate(
            "See discussions, stats, and author profiles for this\npublication at:\n"
            "https://www.researchgate.net/publication/299540302\n"))

    def test_o_endereco_do_researchgate_sozinho_nao_faz_capa(self):
        self.assertFalse(leitura.eh_capa_do_researchgate(
            "Retrieved from https://www.researchgate.net/publication/299540302 on 12 May 2020."))
        self.assertFalse(leitura.eh_capa_do_researchgate(""))


class ParagrafoFonte(unittest.TestCase):
    RESULTADO = {
        "doi": DOI, "status": "aberto", "degrau": "manual", "origem": ORIGEM, "etiqueta": "C", "url": URL,
        "url_final": URL, "formato": "pdf", "versao": "publishedVersion", "paginas": 14,
        "sha256": "a31979778eb18918149b4e37d3d6b86ccba4e511ec065faefbedb85ac16547bc",
        "arquivo": f"fontes/copias/{NOME}", "baixado_em": QUANDO, "diario": [],
        "meta": {"titulo": "The ShadowBox Approach to Cognitive Skills Training", "autores": ["Gary Klein", "Joseph Borders"],
                 "periodico": "Journal of Cognitive Engineering and Decision Making", "ano": 2016},
        "copia_de_leitura": {"retirada": "capa do ResearchGate", "pagina_retirada": 1, "paginas": 13,
                             "sha256": "5ee9b57164928e08a9f064a07bf528923e16d30fc84139da2bc7a413d797df41",
                             "pdf_obtido": f"/home/outra/analista_intel/fontes/copias/originais/{NOME}",
                             "ferramenta": "pypdf 6.14.2"},
    }

    def test_diz_que_a_copia_de_leitura_e_o_pdf_obtido_sem_a_capa(self):
        reg = procedencia.registro_de_procedencia(self.RESULTADO, "2026-09-26")
        self.assertEqual(reg["copia_de_leitura"], self.RESULTADO["copia_de_leitura"])
        p = procedencia.paragrafo_fonte(reg)
        self.assertIn("versão publicada, 14 páginas, SHA-256 a31979778eb1…; valores conferidos no texto em 2026-09-26.", p)
        self.assertIn("A cópia de leitura é o PDF obtido sem a p. 1, a capa do ResearchGate, e tem 13 páginas; "
                      f"o SHA-256 e as páginas acima são os do PDF obtido, guardado em originais/{NOME}.", p)
        self.assertNotIn("/home/outra", p)

    def test_sem_corte_o_paragrafo_nao_fala_de_copia_de_leitura(self):
        reg = procedencia.registro_de_procedencia({**self.RESULTADO, "copia_de_leitura": None})
        self.assertIsNone(reg["copia_de_leitura"])
        self.assertNotIn("cópia de leitura", procedencia.paragrafo_fonte(reg))


@unittest.skipUnless(TEM_POPPLER and TEM_PYPDF, "sem pdftotext, pdfinfo ou pypdf")
class CapaRetiradaNoRegistro(Pasta):
    def setUp(self):
        super().setUp()
        self.obtido()
        self.inicio = time.time()
        self.r = self.registrar()

    def test_o_pdf_obtido_vai_intacto_para_originais_com_a_data_que_tinha(self):
        self.assertEqual(self.original.read_bytes(), COM_CAPA)
        self.assertEqual(int(self.original.stat().st_mtime), int(ANTES))

    def test_a_copia_de_leitura_fica_no_lugar_sem_a_capa_e_com_a_data_de_agora(self):
        self.assertEqual(self.r["arquivo"], str(self.arquivo))
        texto = Path(self.r["texto"]).read_text(encoding="utf-8")
        self.assertNotIn("See discussions", texto)
        self.assertEqual(texto.count("\f"), 2)
        self.assertTrue(texto.lstrip().startswith("Journal of Cognitive Engineering and Decision Making"))
        self.assertGreaterEqual(self.arquivo.stat().st_mtime, self.inicio - 1)
        self.assertGreater(self.arquivo.stat().st_mtime, self.original.stat().st_mtime)

    def test_o_recibo_guarda_o_hash_e_as_paginas_do_pdf_obtido(self):
        self.assertEqual((self.r["sha256"], self.r["paginas"]), (sha256(COM_CAPA), 3))
        copia = self.r["copia_de_leitura"]
        self.assertEqual((copia["retirada"], copia["pagina_retirada"], copia["paginas"], copia["pdf_obtido"]),
                         ("capa do ResearchGate", 1, 2, str(self.original)))
        self.assertEqual(copia["sha256"], sha256(self.arquivo.read_bytes()))

    def test_o_diario_diz_o_que_saiu_e_onde_esta_o_pdf_obtido(self):
        linha = self.r["diario"][-1]
        self.assertIn("capa do ResearchGate (p. 1 do PDF obtido) retirada com pypdf", linha)
        self.assertIn(f"tem 2 páginas e SHA-256 {sha256(self.arquivo.read_bytes())}", linha)
        self.assertIn(f"o PDF obtido, de 3 páginas e com o SHA-256 deste recibo, está em {self.original}", linha)


@unittest.skipUnless(TEM_POPPLER and TEM_PYPDF, "sem pdftotext, pdfinfo ou pypdf")
class CopiaQueFicaComoVeio(Pasta):
    def test_com_manter_capa(self):
        self.obtido()
        r = self.registrar(manter_capa=True)
        self.assertEqual(self.arquivo.read_bytes(), COM_CAPA)
        self.assertFalse(self.original.parent.exists())
        self.assertIsNone(r["copia_de_leitura"])
        self.assertIn("See discussions", Path(r["texto"]).read_text(encoding="utf-8"))

    def test_sem_a_capa_do_researchgate(self):
        sem_capa = pdf_de_paginas([PRIMEIRA + ["Retrieved from https://www.researchgate.net/publication/1"], SEGUNDA])
        self.obtido(sem_capa)
        r = self.registrar()
        self.assertEqual(self.arquivo.read_bytes(), sem_capa)
        self.assertFalse(self.original.parent.exists())
        self.assertIsNone(r["copia_de_leitura"])
        self.assertEqual(r["sha256"], sha256(sem_capa))


@unittest.skipUnless(TEM_POPPLER and TEM_PYPDF, "sem pdftotext, pdfinfo ou pypdf")
class OriginaisJaOcupado(Pasta):
    def test_outro_pdf_guardado_com_o_mesmo_nome_nao_se_sobrescreve(self):
        self.obtido()
        self.original.parent.mkdir()
        self.original.write_bytes(b"%PDF-1.4 outro download")
        with self.assertRaisesRegex(RuntimeError, "originais"):
            self.registrar()
        self.assertEqual(self.original.read_bytes(), b"%PDF-1.4 outro download")
        self.assertEqual(self.arquivo.read_bytes(), COM_CAPA)
        self.assertFalse(self.arquivo.with_suffix(".txt").exists())

    def test_copia_de_leitura_de_um_corte_anterior_nao_se_registra_como_pdf_obtido(self):
        self.obtido()
        self.registrar()
        leitura_ = self.arquivo.read_bytes()
        with self.assertRaisesRegex(RuntimeError, f"originais/{NOME}"):
            self.registrar(sobrescrever_texto=True)
        self.assertEqual(self.arquivo.read_bytes(), leitura_)
        self.assertEqual(self.original.read_bytes(), COM_CAPA)


@unittest.skipUnless(TEM_POPPLER, "sem pdftotext ou pdfinfo")
class SemPypdf(Pasta):
    def test_o_registro_para_antes_de_tocar_na_copia_e_diz_as_saidas(self):
        self.obtido()
        with mock.patch.dict(sys.modules, {"pypdf": None}), \
                self.assertRaisesRegex(RuntimeError, "pypdf(.|\n)*--manter-capa"):
            self.registrar()
        self.assertEqual(self.arquivo.read_bytes(), COM_CAPA)
        self.assertFalse(self.original.parent.exists())
        self.assertFalse(self.arquivo.with_suffix(".txt").exists())

    def test_o_abrir_fica_com_a_capa_e_diz_por_que(self):
        with mock.patch.dict(sys.modules, {"pypdf": None}):
            r = acesso.abrir("10.1/x", self.pasta, buscar=falso_buscar(), obter=falso_obter(), agora=QUANDO)
        self.assertEqual((r["status"], r["copia_de_leitura"]), ("aberto", None))
        self.assertEqual(Path(r["arquivo"]).read_bytes(), COM_CAPA)
        self.assertIn("pypdf", r["diario"][-1])


def falso_buscar():
    oa = {"doi": "https://doi.org/10.1/x", "open_access": {"is_oa": True},
          "best_oa_location": {"is_oa": True, "pdf_url": "https://rep/x.pdf", "version": "publishedVersion"}}
    return lambda url, **kw: (200, oa) if "api.openalex.org" in url else (404, None)


def falso_obter():
    return lambda url, **kw: (200, COM_CAPA, url, {}) if url == "https://rep/x.pdf" else (404, b"", url, {})


@unittest.skipUnless(TEM_POPPLER and TEM_PYPDF, "sem pdftotext, pdfinfo ou pypdf")
class CapaRetiradaNoAbrir(Pasta):
    def test_o_abrir_tambem_tira_a_capa(self):
        r = acesso.abrir("10.1/x", self.pasta, buscar=falso_buscar(), obter=falso_obter(), agora=QUANDO)
        self.assertEqual((self.pasta / "originais" / "10-1-x.pdf").read_bytes(), COM_CAPA)
        self.assertEqual((r["sha256"], r["paginas"], r["copia_de_leitura"]["paginas"]), (sha256(COM_CAPA), 3, 2))
        self.assertNotIn("See discussions", Path(r["texto"]).read_text(encoding="utf-8"))
        self.assertIn("capa do ResearchGate (p. 1 do PDF obtido) retirada", r["diario"][-1])

    def test_com_manter_capa_o_abrir_nao_corta(self):
        r = acesso.abrir("10.1/x", self.pasta, buscar=falso_buscar(), obter=falso_obter(), agora=QUANDO,
                         manter_capa=True)
        self.assertIsNone(r["copia_de_leitura"])
        self.assertFalse((self.pasta / "originais").exists())


@unittest.skipUnless(TEM_POPPLER and TEM_PYPDF, "sem pdftotext, pdfinfo ou pypdf")
class Cli(Pasta):
    def rodar(self, *argv):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            codigo = artigo.main(list(argv))
        return codigo, saida.getvalue()

    def test_registrar_tira_a_capa_e_o_paragrafo_diz_isso(self):
        self.obtido()
        with mock.patch.object(artigo, "_metadados", return_value=ParagrafoFonte.RESULTADO["meta"]):
            codigo, saida = self.rodar("registrar", DOI, "--arquivo", str(self.arquivo), "--url", URL,
                                       "--origem", ORIGEM, "--etiqueta", "C", "--versao", "publicada")
        self.assertEqual(codigo, 0)
        self.assertIn(f"A cópia de leitura é o PDF obtido sem a p. 1, a capa do ResearchGate, e tem 2 páginas", saida)
        gravado = json.loads((self.pasta / f"{procedencia.slug_de_doi(DOI)}.procedencia.json").read_text(encoding="utf-8"))
        self.assertEqual((gravado["sha256"], gravado["copia_de_leitura"]["pdf_obtido"]), (sha256(COM_CAPA), str(self.original)))

    def test_registrar_com_manter_capa(self):
        self.obtido()
        with mock.patch.object(artigo, "_metadados", return_value=ParagrafoFonte.RESULTADO["meta"]):
            codigo, _ = self.rodar("registrar", DOI, "--arquivo", str(self.arquivo), "--url", URL,
                                   "--origem", ORIGEM, "--etiqueta", "C", "--manter-capa")
        self.assertEqual(codigo, 0)
        self.assertEqual(self.arquivo.read_bytes(), COM_CAPA)
        self.assertFalse(self.original.parent.exists())

    def test_abrir_com_manter_capa(self):
        abrir_sem_rede = functools.partial(acesso.abrir, buscar=falso_buscar(), obter=falso_obter())
        with mock.patch.object(acesso, "abrir", abrir_sem_rede):
            codigo, _ = self.rodar("abrir", "10.1000/x", "--destino", str(self.pasta), "--manter-capa")
        self.assertEqual(codigo, 0)
        self.assertEqual((self.pasta / "10-1000-x.pdf").read_bytes(), COM_CAPA)
        self.assertFalse((self.pasta / "originais").exists())


if __name__ == "__main__":
    unittest.main()
