"""A conferência que atravessa a quebra de linha, o hífen de fim de linha e as colunas do PDF."""
import contextlib
import io
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import _caminho  # noqa: F401
import artigo
import leitura
import texto


ESQUERDA = ["plots watered by the drip system yielded about",
            "twice as much grain as the flooded ones, but",
            "the count of plots without irriga-",
            "tion was too small to test. Soil type, the",
            "second factor, also mattered for the yield",
            "of the eastern fields, and the effect held when",
            "the plots were weighed as a whole rather than",
            "as the sum of their rows. The harvests were",
            "weighed twice by independent teams, and the",
            "agreement between them was high throughout."]
DIREITA = ["the unirrigated plots did not differ from",
           "the irrigated ones (sandy soils, k = 21,",
           "d = .58; clay soils, k",
           "= 12, d = .61). Plots with heavy clay",
           "showed larger effects than those with",
           "sandy soil, and roughly half of the plots",
           "had been fertilized the year before the",
           "trial. A few post hoc analyses examined",
           "rainfall as a continuous moderator with a",
           "weighted least squares regression model."]
# como o `pdftotext -layout` imprime duas colunas: cada linha física leva um pedaço de cada uma
DUAS_COLUNAS = "".join(f"{e:<52}{d}".rstrip() + "\n" for e, d in zip(ESQUERDA, DIREITA))


TRES = (["Birds were counted at dawn on each", "transect, and the counts rose in the", "second spring after the hedges",
         "were planted. Small finches gained", "the most, while larger species", "showed no change in most years.",
         "Hedge age mattered as much as the", "hedge length did in every site", "we surveyed for this report."],
        ["The counters met weekly to settle", "disagreements, and the review of", "the field notes took place after",
         "the first forty visits had been", "logged twice by each counter.", "Agreement was high for the common",
         "species and lower for the rare", "ones, which were recorded in too", "many different ways across sites."],
        ["Future work should follow hedges", "in sites where the crops change", "from one season to the next,",
         "since the sites here repeated", "the same crop. Long gaps between", "planting and the first count",
         "were rare, and their effect", "remains an open question for", "the next round of surveys."])
TRES_COLUNAS = "".join(f"{a:<38}{b:<38}{c}".rstrip() + "\n" for a, b, c in zip(*TRES))

COM_TITULO_E_RODAPE = (
    "            IRRIGATION AND YIELD: WHAT THIRTY FIELD TRIALS SAY ABOUT DRIP SYSTEMS\n\n"
    + "".join(f"{e:<52}{d}".rstrip() + "\n" for e, d in zip(
        ESQUERDA[:-1] + ["across all of the trials, the effect was"],
        ["larger for wheat than for barley, and"] + DIREITA[1:]))
    + "\n          Downloaded from the publisher by a university library on 3 March 2019\n")

# A legenda da figura, mais larga que a coluna, atravessa a calha bem onde uma frase da coluna da
# direita passa de linha: pelo desenho da página não há como saber que "accu-" continua em "racy".
LEGENDA_ESQ = ["Two groups trained for six weeks, one",
               "with a coach and one alone, and both",
               "kept a log of every error they made.",
               "The logs were coded blind to the group",
               "by two raters who met every Friday.",
               "Figure 2. Mean change in error rate by condition and week, with standard errors",
               "shown for each group; the dashed line marks the end of the training period.",
               "Errors fell in both groups, but the",
               "coached group kept its gains longer",
               "after the training period was over."]
LEGENDA_DIR = ["Training effects were measured by",
               "the change in errors from the first",
               "week to the last, and the transfer",
               "test came a month later. Across the",
               "samples, the effect of the intervention on accu-",
               "",
               "",
               "racy was small in both groups, and",
               "the transfer test showed no sign of",
               "a difference between the groups."]
COM_LEGENDA_LARGA = "".join((f"{e:<52}{d}" if d else e).rstrip() + "\n" for e, d in zip(LEGENDA_ESQ, LEGENDA_DIR))
# a mesma página como o `pdftotext -raw` a devolve: cada coluna inteira, na ordem em que foi desenhada
COM_LEGENDA_LARGA_EM_ORDEM = "\n".join(LEGENDA_ESQ + [d for d in LEGENDA_DIR if d]) + "\n"


def conferir(arquivo: Path, *expressoes: str) -> tuple[int, str]:
    """`artigo.py conferir`, com o código de saída e o que ele imprimiu."""
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        codigo = artigo.main(["conferir", str(arquivo), *expressoes])
    return codigo, saida.getvalue()


def pdf_de(textos: list[tuple[int, int, str]]) -> bytes:
    """Um PDF de uma página com cada (x, y, texto) em Helvetica 10, desenhados na ordem da lista."""
    fluxo = "BT /F1 10 Tf " + " ".join(f"1 0 0 1 {x} {y} Tm ({s}) Tj" for x, y, s in textos) + " ET"
    objetos = ["<< /Type /Catalog /Pages 2 0 R >>",
               "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R"
               " /Resources << /Font << /F1 5 0 R >> >> >>",
               f"<< /Length {len(fluxo)} >>\nstream\n{fluxo}\nendstream",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    pdf, posicoes = "%PDF-1.4\n", []
    for n, corpo in enumerate(objetos, 1):
        posicoes.append(len(pdf))
        pdf += f"{n} 0 obj\n{corpo}\nendobj\n"
    xref = len(pdf)
    pdf += (f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n" + "".join(f"{p:010d} 00000 n \n" for p in posicoes)
            + f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n")
    return pdf.encode("latin-1")


class AtravessaQuebraDeLinha(unittest.TestCase):
    def test_expressao_que_atravessa_a_quebra_de_linha(self):
        txt = ("Results\n"
               "the count of plots without\n"
               "irrigation was too small to test, so the\n"
               "estimate is fragile.\n")
        achados = texto.procurar(txt, ["the count of plots without irrigation was too small to test"],
                                 atravessa_linhas=True)
        self.assertEqual([(a.linha, a.texto, a.continuacao, a.antes, a.depois) for a in achados],
                         [(2, "the count of plots without", ((3, "irrigation was too small to test, so the"),),
                           ("Results",), ("estimate is fragile.",))])
        colado = "the pooled effectsizes\nyieldsa mean of .41\n"   # o pdftotext perdeu o espaço entre as palavras
        achados = texto.procurar(colado, ["effect sizes yields a mean"], atravessa_linhas=True)
        self.assertEqual([a.linha for a in achados], [1])

    def test_hifen_de_fim_de_linha_e_desfeito_como_o_tipografo_quis(self):
        txt = ("the yield rose when the irrigation perfor-\n"
               "mance was measured with a self-\n"
               "report scale. Addi\u00ad\n"            # hífen discricionário (U+00AD) no fim da linha
               "tional factors emerged after COVID-\n"
               "19 (Field Studies 12, pp. 231\u2013\n"
               "245).\n")
        casos = {"irrigation performance was measured": 1,
                 "measured with a self-report scale": 2,          # o hífen do composto é opcional
                 "Additional factors": 3,
                 "after COVID-19": 4,                             # antes de algarismo o hífen fica
                 "pp. 231-245": 5,
                 "irrigation perfor-\nmance was measured": 1}     # expressão colada com a quebra do .txt
        for expressao, linha in casos.items():
            with self.subTest(expressao=expressao):
                self.assertEqual([a.linha for a in texto.procurar(txt, [expressao], atravessa_linhas=True)], [linha])


class Normalizacao(unittest.TestCase):
    def test_ligadura_e_hifen_discricionario_no_meio_da_linha(self):
        txt = "the e\ufb00ect was signi\ufb01cant: an improve\u00adment of 12% in accuracy\n"
        for expressao in ("effect was significant", "an improvement of 12%"):
            with self.subTest(expressao=expressao):
                self.assertEqual([a.linha for a in texto.procurar(txt, [expressao])], [1])


class Colunas(unittest.TestCase):
    def test_emenda_coluna_por_coluna_e_nao_linha_por_linha(self):
        esq = texto.procurar(DUAS_COLUNAS, ["the count of plots without irrigation was too small to test"],
                             atravessa_linhas=True)
        self.assertEqual([(a.linha, a.texto, a.continuacao, a.antes, a.depois) for a in esq],
                         [(3, "the count of plots without irriga-",
                           ((4, "tion was too small to test. Soil type, the"),),
                           ("twice as much grain as the flooded ones, but",),
                           ("second factor, also mattered for the yield",))])
        dir_ = texto.procurar(DUAS_COLUNAS, ["clay soils, k = 12, d = .61"], atravessa_linhas=True)
        self.assertEqual([(a.linha, a.texto, a.continuacao) for a in dir_],
                         [(3, "d = .58; clay soils, k", ((4, "= 12, d = .61). Plots with heavy clay"),))])

    def test_tres_colunas(self):
        achados = texto.procurar(TRES_COLUNAS, ["the review of the field notes took place"], atravessa_linhas=True)
        self.assertEqual([(a.linha, a.texto, a.continuacao) for a in achados],
                         [(2, "disagreements, and the review of", ((3, "the field notes took place after"),))])

    def test_do_pe_de_uma_coluna_ao_topo_da_seguinte_sem_o_rodape_no_meio(self):
        achados = texto.procurar(COM_TITULO_E_RODAPE, ["the effect was larger for wheat than for barley"],
                                 atravessa_linhas=True)
        self.assertEqual([(a.linha, a.texto, a.continuacao) for a in achados],
                         [(12, "across all of the trials, the effect was",
                           ((3, "larger for wheat than for barley, and"),))])


class OrdemDeLeitura(unittest.TestCase):
    FRASE = "the effect of the intervention on accuracy was small"

    def test_a_ordem_de_leitura_do_pdf_acha_o_que_o_desenho_da_pagina_esconde(self):
        self.assertEqual(texto.procurar(COM_LEGENDA_LARGA, [self.FRASE], atravessa_linhas=True), [])
        achados = texto.procurar(COM_LEGENDA_LARGA, [self.FRASE], atravessa_linhas=True,
                                 ordem_de_leitura=COM_LEGENDA_LARGA_EM_ORDEM)
        self.assertEqual([(a.linha, a.texto, a.continuacao) for a in achados],
                         [(5, "samples, the effect of the intervention on accu-",
                           ((8, "racy was small in both groups, and"),))])

    def test_so_vale_o_que_esta_no_txt(self):
        outro = COM_LEGENDA_LARGA.replace("racy was small", "racy was large")
        self.assertEqual(texto.procurar(outro, [self.FRASE], atravessa_linhas=True,
                                        ordem_de_leitura=COM_LEGENDA_LARGA_EM_ORDEM), [])


class Relatorio(unittest.TestCase):
    def test_numera_cada_linha_que_a_ocorrencia_ocupa(self):
        expressao = "the count of plots without irrigation was too small to test"
        achados = texto.procurar(DUAS_COLUNAS, [expressao], atravessa_linhas=True)
        self.assertEqual(texto.relatorio(achados, [expressao]).splitlines(), [
            f"\u2713 {expressao!r}: 1 ocorrência(s)",
            "      twice as much grain as the flooded ones, but",
            "      3 the count of plots without irriga-",
            "      4 tion was too small to test. Soil type, the",
            "      second factor, also mattered for the yield"])


class Conferir(unittest.TestCase):
    def test_acha_o_que_atravessa_a_linha_na_coluna_e_devolve_0(self):
        with tempfile.TemporaryDirectory() as pasta:
            txt = Path(pasta) / "artigo.txt"
            txt.write_text(DUAS_COLUNAS, encoding="utf-8")
            codigo, saida = conferir(txt, "the count of plots without irrigation was too small to test",
                                     "clay soils, k = 12, d = .61")
            self.assertEqual(codigo, 0)
            self.assertIn("      4 tion was too small to test. Soil type, the", saida)
            codigo, saida = conferir(txt, "the count of plots without irrigation was too large to test")
            self.assertEqual(codigo, 2)
            self.assertIn("não encontrado", saida)


@unittest.skipUnless(shutil.which("pdftotext"), "sem pdftotext (poppler-utils)")
class ConferirComOPdfAoLado(unittest.TestCase):
    def test_o_pdf_ao_lado_do_txt_da_a_ordem_de_leitura(self):
        # a página de COM_LEGENDA_LARGA desenhada de verdade: a coluna da esquerda inteira, depois a da direita
        desenho = ([(50, 700 - 14 * i, e) for i, e in enumerate(LEGENDA_ESQ)]
                   + [(330, 700 - 14 * i, d) for i, d in enumerate(LEGENDA_DIR) if d])
        with tempfile.TemporaryDirectory() as pasta:
            pdf = Path(pasta) / "artigo.pdf"
            pdf.write_bytes(pdf_de(desenho))
            self.assertEqual(conferir(pdf, OrdemDeLeitura.FRASE)[0], 0)   # extrai o .txt e lê o PDF
            txt = pdf.with_suffix(".txt")
            codigo, saida = conferir(txt, OrdemDeLeitura.FRASE)
            self.assertEqual(codigo, 0)
            self.assertIn("racy was small in both groups, and", saida)
            pdf.rename(Path(pasta) / "outro.pdf")
            self.assertEqual(conferir(txt, OrdemDeLeitura.FRASE)[0], 2)   # sem o PDF, as colunas escondem a frase


class ConferirComPdftotextQueTrava(unittest.TestCase):
    def test_nao_espera_para_sempre_e_avisa_que_seguiu_so_no_txt(self):
        with tempfile.TemporaryDirectory() as pasta:
            binarios = Path(pasta) / "bin"
            binarios.mkdir()
            falso = binarios / "pdftotext"
            falso.write_text("#!/bin/sh\nexec sleep 5\n")   # exec: o kill do timeout pega o próprio sleep
            falso.chmod(0o755)
            txt = Path(pasta) / "artigo.txt"
            txt.write_text(DUAS_COLUNAS, encoding="utf-8")
            (Path(pasta) / "artigo.pdf").write_bytes(b"%PDF-1.4\n")
            erro = io.StringIO()
            with mock.patch.dict(os.environ, {"PATH": f"{binarios}{os.pathsep}{os.environ['PATH']}"}), \
                    mock.patch.object(leitura, "TEMPO_MAX_DO_PDFTOTEXT", 0.5), contextlib.redirect_stderr(erro):
                inicio = time.monotonic()
                codigo, _ = conferir(txt, "the count of plots without irrigation was too small to test")
                demora = time.monotonic() - inicio
        self.assertLess(demora, 3)
        self.assertEqual(codigo, 0)                      # o que o .txt sozinho acha continua achado
        self.assertIn("artigo.pdf", erro.getvalue())


if __name__ == "__main__":
    unittest.main()
