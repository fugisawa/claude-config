"""O registro da cópia manual: a página HTML com o texto já extraído, o .txt que não se sobrescreve sem
aviso, o recibo da tentativa que falhou antes e o de outro DOI com o mesmo nome de arquivo. Os três primeiros
casos são os de 28/09/2026: Mandel e Barnes (2014), lidos na página do PubMed Central, e Marrin (2012), que
chegou por pedido depois de a escada falhar."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _caminho  # noqa: F401
import acesso
import artigo
import fontes
import procedencia

DOI = "10.1073/pnas.1406138111"
OUTRO_DOI_DO_MESMO_NOME = "10.1073/pnas/1406138111"   # só a pontuação muda, e o nome do recibo é o mesmo
PMC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4121776/"
QUANDO = "2026-09-28T14:45:00-03:00"
TENTADO = "2026-09-25T17:23:42-03:00"
HTML = (b'<!DOCTYPE html>\n<html lang="en"><head><title>Accuracy of forecasts in strategic intelligence - PMC</title>'
        b'</head><body><article><h1>Accuracy of forecasts in strategic intelligence</h1>'
        b'<p>The accuracy of 1,514 strategic intelligence forecasts ...</p></article></body></html>\n')
SHA256_DO_HTML = "75b3f3214ad0a60fa0dfb973d0af0b5b2e67c25d1de04e03879d3af9531384e7"
TEXTO_COMPLETO = "Accuracy of forecasts in strategic intelligence\n\nResults\nThe forecasts were well calibrated.\n"
# o XML que o PMC servia ao lado da página: só a folha de rosto, sem o corpo do artigo
SO_A_FOLHA_DE_ROSTO = (b"<article><front><article-meta><title-group><article-title>Accuracy of forecasts in strategic "
                       b"intelligence</article-title></title-group></article-meta></front></article>")
DIARIO_DA_FALHA = ["crossref: metadados obtidos", "europepmc: PMCID PMC4121776",
                   "europepmc: nada legível em https://europepmc.org/articles/PMC4121776?pdf=render"]
META = {"titulo": "Accuracy of forecasts in strategic intelligence", "autores": ["David R. Mandel", "Alan Barnes"],
        "periodico": "Proceedings of the National Academy of Sciences", "ano": 2014, "volume": "111",
        "numero": "30", "paginas": "10984-10989"}


def recibo_da_falha() -> dict:
    """O recibo que o `abrir` grava quando nenhum degrau abre."""
    return procedencia.registro_de_procedencia(
        {"doi": DOI, "status": "nao_aberto", "meta": META, "tentado_em": TENTADO, "diario": DIARIO_DA_FALHA},
        pendencias=["pedido ao autor rascunhado em 2026-09-25"], reavaliar_em="2026-10-25")


class Pasta(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta)

    def registrar(self, arquivo, **kw):
        return acesso.registrar_manual(DOI, arquivo, url=PMC, origem="PubMed Central", etiqueta="A",
                                       versao="publicada", agora=QUANDO, **kw)


class PaginaHtml(Pasta):
    def test_entra_com_o_texto_ja_extraido_que_fica_como_estava(self):
        for sufixo in (".html", ".htm"):
            with self.subTest(sufixo=sufixo):
                html = self.pasta / f"mandel-barnes-2014-pmc{sufixo}"
                html.write_bytes(HTML)
                txt = self.pasta / "mandel-barnes-2014-pmc.txt"
                txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
                r = self.registrar(html, texto=txt)
                self.assertEqual((r["status"], r["formato"], r["texto"], r["paginas"]),
                                 ("aberto", "html", str(txt), None))
                self.assertEqual(r["sha256"], SHA256_DO_HTML)
                self.assertEqual(txt.read_text(encoding="utf-8"), TEXTO_COMPLETO)

    def test_nao_extrai_texto_nenhum_da_pagina(self):
        html = self.pasta / "pagina.html"
        html.write_bytes(HTML)
        txt = self.pasta / "extraido-a-mao.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        self.registrar(html, texto=txt)
        self.assertEqual(sorted(p.name for p in self.pasta.iterdir()), ["extraido-a-mao.txt", "pagina.html"])

    def test_sem_o_texto_ou_com_texto_que_nao_existe_e_recusada(self):
        html = self.pasta / "pagina.html"
        html.write_bytes(HTML)
        with self.assertRaisesRegex(RuntimeError, "--texto"):
            self.registrar(html)
        with self.assertRaisesRegex(RuntimeError, "nao-existe.txt"):
            self.registrar(html, texto=self.pasta / "nao-existe.txt")

    def test_texto_vazio_ou_que_e_a_propria_pagina_e_recusado(self):
        html = self.pasta / "pagina.html"
        html.write_bytes(HTML)
        vazio = self.pasta / "pagina.txt"
        vazio.write_text("", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "vazio"):
            self.registrar(html, texto=vazio)
        with self.assertRaisesRegex(RuntimeError, "a própria cópia"):
            self.registrar(html, texto=html)

    def test_o_texto_ja_extraido_so_vale_para_pagina_html(self):
        xml = self.pasta / "copia.xml"
        xml.write_bytes(SO_A_FOLHA_DE_ROSTO)
        txt = self.pasta / "outro.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "HTML"):
            self.registrar(xml, texto=txt)


class TextoQueJaExiste(Pasta):
    def setUp(self):
        super().setUp()
        self.xml = self.pasta / "mandel-barnes-2014-pmc.xml"
        self.xml.write_bytes(SO_A_FOLHA_DE_ROSTO)
        self.txt = self.pasta / "mandel-barnes-2014-pmc.txt"
        self.txt.write_text(TEXTO_COMPLETO, encoding="utf-8")

    def test_nao_se_sobrescreve_sem_aviso(self):
        with self.assertRaisesRegex(RuntimeError, "mandel-barnes-2014-pmc.txt"):
            self.registrar(self.xml)
        self.assertEqual(self.txt.read_text(encoding="utf-8"), TEXTO_COMPLETO)

    def test_se_sobrescreve_quando_se_pede(self):
        r = self.registrar(self.xml, sobrescrever_texto=True)
        self.assertEqual(r["texto"], str(self.txt))
        self.assertEqual(self.txt.read_text(encoding="utf-8"), "Accuracy of forecasts in strategic intelligence")


class ReciboAnterior(Pasta):
    def setUp(self):
        super().setUp()
        self.html = self.pasta / "mandel-barnes-2014-pmc.html"
        self.html.write_bytes(HTML)
        self.txt = self.pasta / "mandel-barnes-2014-pmc.txt"
        self.txt.write_text(TEXTO_COMPLETO, encoding="utf-8")

    def test_o_da_tentativa_que_falhou_da_o_diario_e_a_data_da_tentativa(self):
        r = self.registrar(self.html, texto=self.txt, anterior=recibo_da_falha())
        self.assertEqual(r["diario"], DIARIO_DA_FALHA + [f"manual: PubMed Central, em {PMC}"])
        self.assertEqual((r["tentado_em"], r["baixado_em"]), (TENTADO, QUANDO))

    def test_o_de_copia_ja_aberta_nao_se_emenda(self):
        aberto = {**recibo_da_falha(), "status": "aberto", "diario": ["manual: site do autor, em https://autor/x.pdf"]}
        r = self.registrar(self.html, texto=self.txt, anterior=aberto)
        self.assertEqual(r["diario"], [f"manual: PubMed Central, em {PMC}"])
        self.assertEqual(r["tentado_em"], QUANDO)


class CliRegistrar(Pasta):
    def rodar(self, *argv):
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.object(artigo, "_metadados", return_value=META), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            codigo = artigo.main(["registrar", DOI, "--url", PMC, "--origem", "PubMed Central", "--etiqueta", "A",
                                  "--versao", "publicada", *argv])
        return codigo, saida.getvalue(), erro.getvalue()

    def recibo(self) -> Path:
        return self.pasta / f"{procedencia.slug_de_doi(DOI)}.procedencia.json"

    def test_pagina_html_com_o_texto_e_o_recibo_da_tentativa_que_falhou(self):
        html = self.pasta / "mandel-barnes-2014-pmc.html"
        html.write_bytes(HTML)
        txt = self.pasta / "mandel-barnes-2014-pmc.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        procedencia.gravar(self.pasta, procedencia.slug_de_doi(DOI), recibo_da_falha())
        codigo, saida, _ = self.rodar("--arquivo", str(html), "--texto", str(txt), "--conferido-em", "2026-09-25")
        self.assertEqual(codigo, 0)
        gravado = json.loads(self.recibo().read_text(encoding="utf-8"))
        self.assertEqual((gravado["status"], gravado["formato"], gravado["texto"]), ("aberto", "html", str(txt)))
        self.assertEqual(gravado["diario"], DIARIO_DA_FALHA + [f"manual: PubMed Central, em {PMC}"])
        self.assertEqual(gravado["tentado_em"], TENTADO)
        self.assertIn("SHA-256 75b3f3214ad0…; valores conferidos no texto em 2026-09-25.", saida)

    def test_sobrescrever_o_texto_pela_cli_deixa_aviso(self):
        xml = self.pasta / "mandel-barnes-2014-pmc.xml"
        xml.write_bytes(SO_A_FOLHA_DE_ROSTO)
        txt = self.pasta / "mandel-barnes-2014-pmc.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        codigo, _, erro = self.rodar("--arquivo", str(xml))
        self.assertEqual(codigo, 1)
        self.assertIn("--sobrescrever-texto", erro)
        self.assertFalse(self.recibo().exists())
        codigo, _, erro = self.rodar("--arquivo", str(xml), "--sobrescrever-texto")
        self.assertEqual(codigo, 0)
        self.assertIn("aviso:", erro)
        self.assertIn("mandel-barnes-2014-pmc.txt", erro)

    def test_o_recibo_anterior_se_le_no_destino_quando_ele_nao_e_a_pasta_da_copia(self):
        copias, recibos = self.pasta / "copias", self.pasta / "recibos"
        copias.mkdir()
        recibos.mkdir()
        html = copias / "mandel-barnes-2014-pmc.html"
        html.write_bytes(HTML)
        txt = copias / "mandel-barnes-2014-pmc.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        procedencia.gravar(recibos, procedencia.slug_de_doi(DOI), recibo_da_falha())
        codigo, _, _ = self.rodar("--arquivo", str(html), "--texto", str(txt), "--destino", str(recibos))
        self.assertEqual(codigo, 0)
        gravado = json.loads((recibos / f"{procedencia.slug_de_doi(DOI)}.procedencia.json").read_text(encoding="utf-8"))
        self.assertEqual((gravado["tentado_em"], gravado["diario"][:3]), (TENTADO, DIARIO_DA_FALHA))
        self.assertEqual(sorted(p.name for p in copias.iterdir()), ["mandel-barnes-2014-pmc.html", "mandel-barnes-2014-pmc.txt"])

    def test_registro_recusado_nao_consulta_a_rede_e_o_aceito_consulta(self):
        html = self.pasta / "pagina.html"
        html.write_bytes(HTML)
        txt = self.pasta / "pagina-texto.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        consultas = []

        def http_json(url, **kw):
            consultas.append(url)
            return 404, None
        argv = ["registrar", DOI, "--arquivo", str(html), "--url", PMC, "--origem", "PubMed Central", "--etiqueta", "A"]
        with mock.patch.object(fontes, "http_json", http_json), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(artigo.main(argv), 1)          # página HTML sem --texto
            self.assertEqual(consultas, [])
            self.assertEqual(artigo.main(argv + ["--texto", str(txt)]), 0)
        self.assertTrue(consultas)

    def test_recibo_anterior_ilegivel_para_o_registro_e_fica_como_estava(self):
        html = self.pasta / "pagina.html"
        html.write_bytes(HTML)
        txt = self.pasta / "pagina.txt"
        txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        self.recibo().write_text("{ recibo cortado", encoding="utf-8")
        codigo, _, erro = self.rodar("--arquivo", str(html), "--texto", str(txt))
        self.assertEqual(codigo, 1)
        self.assertIn(self.recibo().name, erro)
        self.assertEqual(self.recibo().read_text(encoding="utf-8"), "{ recibo cortado")


class ReciboDeOutroDoi(Pasta):
    """Dois DOIs que só diferem na pontuação, como 10.1073/pnas.1406138111 e 10.1073/pnas/1406138111, dão o mesmo
    nome de recibo. Sem a recusa, o `registrar` de um herdaria o diário da tentativa do outro, ou gravaria o seu
    recibo no lugar do da cópia do outro; o `abrir` já recusava o recibo de outro DOI desde 28/09/2026. O DOI que
    só difere na caixa é o mesmo DOI."""
    def setUp(self):
        super().setUp()
        self.html = self.pasta / "mandel-barnes-2014-pmc.html"
        self.html.write_bytes(HTML)
        self.txt = self.pasta / "mandel-barnes-2014-pmc.txt"
        self.txt.write_text(TEXTO_COMPLETO, encoding="utf-8")
        self.consultas = []

    def rodar(self, doi, *argv):
        """O `registrar` pela linha de comando, com a rede falsa: cada consulta às APIs fica em `consultas`."""
        def http_json(url, **kw):
            self.consultas.append(url)
            return 404, None
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.object(fontes, "http_json", http_json), contextlib.redirect_stdout(saida), \
                contextlib.redirect_stderr(erro):
            codigo = artigo.main(["registrar", doi, "--url", PMC, "--origem", "PubMed Central", "--etiqueta", "A",
                                  "--versao", "publicada", *argv])
        return codigo, saida.getvalue(), erro.getvalue()

    def test_recibo_de_outro_doi_com_o_mesmo_nome_de_arquivo_nao_passa_o_diario(self):
        recibo = procedencia.gravar(self.pasta, procedencia.slug_de_doi(DOI), recibo_da_falha())
        antes = recibo.read_bytes()
        codigo, _, erro = self.rodar(OUTRO_DOI_DO_MESMO_NOME, "--arquivo", str(self.html), "--texto", str(self.txt))
        self.assertEqual(codigo, 1)
        self.assertEqual(recibo.read_bytes(), antes)
        for trecho in (recibo.name, DOI, "--destino"):
            self.assertIn(trecho, erro)
        self.assertEqual(self.consultas, [])

    def test_recibo_de_outro_doi_com_o_mesmo_nome_de_arquivo_da_copia_aberta_fica_como_estava(self):
        recibos = self.pasta / "recibos"
        codigo, _, _ = self.rodar(DOI, "--arquivo", str(self.html), "--texto", str(self.txt), "--destino", str(recibos))
        self.assertEqual(codigo, 0)
        recibo = recibos / f"{procedencia.slug_de_doi(DOI)}.procedencia.json"
        antes, self.consultas = recibo.read_bytes(), []
        xml = self.pasta / "outro-artigo.xml"
        xml.write_bytes(SO_A_FOLHA_DE_ROSTO)
        codigo, _, erro = self.rodar(OUTRO_DOI_DO_MESMO_NOME, "--arquivo", str(xml), "--destino", str(recibos))
        self.assertEqual(codigo, 1)
        self.assertEqual(recibo.read_bytes(), antes)
        self.assertIn(str(recibo), erro)
        self.assertFalse(xml.with_suffix(".txt").exists())
        self.assertEqual(self.consultas, [])

    def test_recibo_do_mesmo_doi_em_outra_caixa_passa_o_diario(self):
        # o recibo escrito à mão pode trazer o DOI como a editora o imprime, e a linha de comando o põe em minúsculas
        recibo = procedencia.gravar(self.pasta, procedencia.slug_de_doi(DOI),
                                    {**recibo_da_falha(), "doi": "10.1073/PNAS.1406138111"})
        codigo, _, _ = self.rodar(DOI, "--arquivo", str(self.html), "--texto", str(self.txt))
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(recibo.read_text(encoding="utf-8"))["diario"],
                         DIARIO_DA_FALHA + [f"manual: PubMed Central, em {PMC}"])


if __name__ == "__main__":
    unittest.main()
