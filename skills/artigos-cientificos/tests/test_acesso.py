import tempfile
import unittest
from pathlib import Path

import _caminho  # noqa: F401
import acesso
import fontes
from fontes import Candidato

PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj << >> endobj\n%%EOF\n"
HTML_COM_META = (b"<html><head><meta content=\"/files/artigo.pdf\" name=\"citation_pdf_url\">"
                 b"</head><body>resumo</body></html>")


def falso_obter(respostas):
    """Constrói um `http_get` de mentira a partir de {url: (status, corpo, url_final)}."""
    chamadas = []

    def obter(url, **kw):
        chamadas.append(url)
        status, corpo, final = respostas.get(url, (404, b"", url))
        return status, corpo, final, {}
    obter.chamadas = chamadas
    return obter


class Ordenar(unittest.TestCase):
    def test_pdf_publicado_vem_antes_de_tudo(self):
        cands = [
            Candidato("https://a/landing", "unpaywall", "publishedVersion", tipo="landing"),
            Candidato("https://b/aceito.pdf", "unpaywall", "acceptedVersion"),
            Candidato("https://c/publicado.pdf", "semantic-scholar", "publishedVersion"),
            Candidato("https://d/xml", "europepmc", "publishedVersion", tipo="xml"),
            Candidato("https://c/publicado.pdf", "openalex", "publishedVersion"),
        ]
        ordenados = acesso.ordenar(cands)
        self.assertEqual([c.url for c in ordenados],
                         ["https://c/publicado.pdf", "https://b/aceito.pdf", "https://d/xml", "https://a/landing"])
        self.assertEqual(ordenados[0].degrau, "semantic-scholar", "a primeira ocorrência da URL é a que fica")

    def test_mesma_versao_desempata_pelo_degrau(self):
        cands = [Candidato("https://s2.pdf", "semantic-scholar"), Candidato("https://un.pdf", "unpaywall")]
        self.assertEqual(acesso.ordenar(cands)[0].degrau, "unpaywall")


class PdfNaPagina(unittest.TestCase):
    def test_meta_nas_duas_ordens_de_atributo_e_url_relativa(self):
        self.assertEqual(acesso.pdf_url_na_pagina(HTML_COM_META.decode(), "https://rep.edu/handle/1"),
                         "https://rep.edu/files/artigo.pdf")
        html = '<meta name="citation_pdf_url" content="https://x/y.pdf">'
        self.assertEqual(acesso.pdf_url_na_pagina(html, "https://x/"), "https://x/y.pdf")
        self.assertEqual(acesso.pdf_url_na_pagina("<html></html>", "https://x/"), "")

    def test_eh_pdf(self):
        self.assertTrue(acesso.eh_pdf(PDF))
        self.assertFalse(acesso.eh_pdf(b"<html>"))


class Baixar(unittest.TestCase):
    def test_pagina_de_pouso_leva_ao_pdf_pelo_meta(self):
        obter = falso_obter({
            "https://rep.edu/handle/1": (200, HTML_COM_META, "https://rep.edu/handle/1"),
            "https://rep.edu/files/artigo.pdf": (200, PDF, "https://rep.edu/files/artigo.pdf"),
        })
        corpo, final, formato = acesso.baixar(Candidato("https://rep.edu/handle/1", "unpaywall", tipo="landing"), obter=obter)
        self.assertEqual((formato, final), ("pdf", "https://rep.edu/files/artigo.pdf"))
        self.assertTrue(corpo.startswith(b"%PDF"))

    def test_html_sem_pdf_devolve_none(self):
        obter = falso_obter({"https://ed/x": (200, b"<html>paywall</html>", "https://ed/x")})
        self.assertIsNone(acesso.baixar(Candidato("https://ed/x", "crossref-tdm"), obter=obter))

    def test_xml_conta_como_texto(self):
        obter = falso_obter({"https://epmc/xml": (200, b"<article><body><p>oi</p></body></article>", "https://epmc/xml")})
        self.assertEqual(acesso.baixar(Candidato("https://epmc/xml", "europepmc", tipo="xml"), obter=obter)[2], "xml")


def falso_buscar(respostas):
    def buscar(url, **kw):
        for trecho, resposta in respostas.items():
            if trecho in url:
                return resposta
        return 404, None
    return buscar


class Coletar(unittest.TestCase):
    def test_sem_email_pula_unpaywall_e_ainda_acha_pelo_openalex(self):
        buscar = falso_buscar({
            "api.crossref.org": (200, {"message": {"DOI": "10.1/x", "title": ["T"], "author": []}}),
            "api.openalex.org": (200, {"doi": "https://doi.org/10.1/x", "open_access": {"is_oa": True, "oa_status": "green"},
                                       "best_oa_location": {"is_oa": True, "pdf_url": "https://rep/x.pdf", "version": "acceptedVersion"}}),
        })
        cands, meta, diario = acesso.coletar("10.1/x", None, buscar=buscar)
        self.assertEqual([c.url for c in cands], ["https://rep/x.pdf"])
        self.assertEqual(meta.fonte, "crossref")
        self.assertTrue(any("unpaywall: pulado" in l for l in diario))
        self.assertTrue(any("semantic-scholar: sem registro" in l for l in diario))

    def test_com_email_consulta_unpaywall(self):
        buscar = falso_buscar({"api.unpaywall.org": (200, {"oa_status": "gold", "best_oa_location": {"url_for_pdf": "https://u/x.pdf"}})})
        cands, meta, diario = acesso.coletar("10.1/x", "a@b.c", buscar=buscar)
        self.assertEqual(cands[0].degrau, "unpaywall")
        self.assertIsNone(meta)

    def test_email_so_acompanha_as_tres_apis_de_cortesia(self):
        chamadas = []

        def buscar(url, **kw):
            chamadas.append((url, kw.get("email")))
            return 404, None
        acesso.coletar("10.1/x", "a@b.c", buscar=buscar, obter=falso_obter({}))
        com = {u for u, e in chamadas if e}
        sem = {u for u, e in chamadas if not e}
        self.assertTrue(all(any(h in u for h in ("crossref", "openalex", "unpaywall")) for u in com), com)
        self.assertTrue(any("semanticscholar" in u for u in sem) and any("europepmc" in u for u in sem))


    def test_doi_do_arxiv_rende_candidato_mesmo_sem_registro_nas_apis(self):
        buscar = falso_buscar({"api.semanticscholar.org/graph/v1/paper/arXiv:1706.03762": (
            200, {"title": "Attention", "year": 2017, "externalIds": {"ArXiv": "1706.03762"}})})
        cands, meta, diario = acesso.coletar("10.48550/arxiv.1706.03762", None, buscar=buscar)
        self.assertEqual([c.url for c in cands], ["https://arxiv.org/pdf/1706.03762"])
        self.assertEqual(meta.titulo, "Attention")
        self.assertTrue(any("metadados pelo arXiv" in l for l in diario))


    def test_semantic_scholar_em_429_cai_para_o_atom_do_arxiv(self):
        buscar = falso_buscar({"api.semanticscholar.org": (429, None)})
        atom = (b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/1706.03762</id>'
                b'<title>Attention</title><published>2017-06-12T00:00:00Z</published></entry></feed>')
        obter = falso_obter({"https://export.arxiv.org/api/query?id_list=1706.03762": (200, atom, "https://export.arxiv.org/api/query?id_list=1706.03762")})
        cands, meta, diario = acesso.coletar("10.48550/arxiv.1706.03762", None, buscar=buscar, obter=obter)
        self.assertEqual((meta.titulo, meta.ano, meta.fonte), ("Attention", 2017, "arxiv"))
        self.assertEqual([c.degrau for c in cands], ["arxiv"])


class Abrir(unittest.TestCase):
    def test_grava_pdf_texto_e_devolve_resultado(self):
        buscar = falso_buscar({
            "api.crossref.org": (200, {"message": {"DOI": "10.1/x", "title": ["T"], "author": [{"family": "Silva"}],
                                                   "container-title": ["Rev"], "issued": {"date-parts": [[2024]]}}}),
            "api.openalex.org": (200, {"doi": "https://doi.org/10.1/x", "open_access": {"is_oa": True},
                                       "best_oa_location": {"is_oa": True, "pdf_url": "https://rep/x.pdf", "version": "publishedVersion", "license": "cc-by"}}),
        })
        obter = falso_obter({"https://rep/x.pdf": (200, PDF, "https://rep/x.pdf")})

        def extrair(arquivo, formato):
            destino = arquivo.with_suffix(".txt")
            destino.write_text("texto extraído", encoding="utf-8")
            return destino

        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir("10.1/x", Path(pasta), buscar=buscar, obter=obter, extrair=extrair, agora="2026-09-16T12:00:00-03:00")
            self.assertEqual(r["status"], "aberto")
            self.assertTrue(Path(r["arquivo"]).read_bytes().startswith(b"%PDF"))
            self.assertEqual(Path(r["texto"]).read_text(encoding="utf-8"), "texto extraído")
            self.assertEqual((r["degrau"], r["versao"], r["licenca"]), ("openalex", "publishedVersion", "cc-by"))
            self.assertEqual(len(r["sha256"]), 64)
            self.assertEqual(r["meta"]["autores"], ["Silva"])

    def test_sem_candidato_nao_abre_e_nao_grava(self):
        buscar = falso_buscar({})
        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir("10.1/x", Path(pasta), buscar=buscar, obter=falso_obter({}))
            self.assertEqual(r["status"], "nao_aberto")
            self.assertEqual(list(Path(pasta).iterdir()), [])

    def test_listar_nao_baixa(self):
        buscar = falso_buscar({"api.openalex.org": (200, {"best_oa_location": {"is_oa": True, "pdf_url": "https://rep/x.pdf"}})})
        obter = falso_obter({})
        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir("10.1/x", Path(pasta), buscar=buscar, obter=obter, apenas_listar=True)
            self.assertEqual(r["status"], "listado")
            self.assertEqual(obter.chamadas, [])
            self.assertEqual(len(r["candidatos"]), 1)


if __name__ == "__main__":
    unittest.main()
