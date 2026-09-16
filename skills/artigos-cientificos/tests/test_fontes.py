import unittest

import _caminho  # noqa: F401
import fontes

CROSSREF = {
    "DOI": "10.1007/S10648-025-10003-9",
    "title": ["Increasing Video Lecture Playback Speed Can Impair Test Performance – A Meta-Analysis"],
    "author": [{"given": "Emily", "family": "Tharumalingam"}, {"given": "Brady R. T.", "family": "Roberts"},
               {"given": "Jonathan M.", "family": "Fawcett"}, {"given": "Evan F.", "family": "Risko"}],
    "container-title": ["Educational Psychology Review"],
    "issued": {"date-parts": [[2025, 4, 1]]},
    "volume": "37", "journal-issue": {"issue": "2"}, "article-number": "35",
    "type": "journal-article", "publisher": "Springer Science and Business Media LLC",
    "is-referenced-by-count": 4,
    "license": [{"URL": "https://www.springernature.com/gp/researchers/text-and-data-mining"}],
    "link": [{"URL": "https://link.springer.com/content/pdf/10.1007/s10648-025-10003-9.pdf",
              "content-type": "application/pdf"},
             {"URL": "https://link.springer.com/article/10.1007/s10648-025-10003-9/fulltext.html",
              "content-type": "text/html"}],
}

OPENALEX = {
    "doi": "https://doi.org/10.7717/peerj.4375", "title": "The state of OA",
    "publication_year": 2018, "cited_by_count": 1169, "type": "article",
    "open_access": {"is_oa": True, "oa_status": "gold", "oa_url": "https://peerj.com/articles/4375"},
    "best_oa_location": {"is_oa": True, "pdf_url": "https://peerj.com/articles/4375.pdf",
                         "version": "publishedVersion", "license": "cc-by",
                         "source": {"display_name": "PeerJ", "type": "journal"}},
    "locations": [
        {"is_oa": True, "pdf_url": "https://peerj.com/articles/4375.pdf", "version": "publishedVersion"},
        {"is_oa": True, "pdf_url": "https://europepmc.org/articles/pmc5815332?pdf=render",
         "version": "publishedVersion", "source": {"type": "repository"}},
        {"is_oa": False, "pdf_url": "https://editora.example/pago.pdf"},
        {"is_oa": True, "landing_page_url": "https://arxiv.org/abs/1801.01234", "pdf_url": None},
    ],
    "primary_location": {"source": {"display_name": "PeerJ"}},
    "authorships": [{"author": {"display_name": "Heather Piwowar"}}, {"author": {"display_name": "Jason Priem"}}],
    "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/29456894",
            "pmcid": "https://www.ncbi.nlm.nih.gov/pmc/articles/5815332"},
    "biblio": {"volume": "6", "issue": None, "first_page": "e4375", "last_page": None},
}

UNPAYWALL = {
    "oa_status": "green",
    "best_oa_location": {"url_for_pdf": "https://dash.harvard.edu/x.pdf",
                         "url_for_landing_page": "https://dash.harvard.edu/handle/x",
                         "version": "acceptedVersion", "license": "cc-by", "host_type": "repository"},
    "oa_locations": [
        {"url_for_pdf": "https://dash.harvard.edu/x.pdf", "version": "acceptedVersion"},
        {"url_for_pdf": None, "url_for_landing_page": "https://editora.example/artigo",
         "version": "publishedVersion", "host_type": "publisher"},
    ],
}


class ExtrairIdentificadores(unittest.TestCase):
    def test_doi_dentro_de_url_e_com_pontuacao_final(self):
        self.assertEqual(fontes.extrair_doi("veja https://doi.org/10.1007/s10648-025-10003-9."),
                         "10.1007/s10648-025-10003-9")

    def test_doi_em_maiusculas_vira_minusculas(self):
        self.assertEqual(fontes.extrair_doi("DOI: 10.1007/S10648-025-10003-9"), "10.1007/s10648-025-10003-9")

    def test_sem_doi(self):
        self.assertIsNone(fontes.extrair_doi("velocidade de videoaula"))

    def test_arxiv(self):
        self.assertEqual(fontes.extrair_arxiv_id("https://arxiv.org/abs/2301.08243v2"), "2301.08243v2")
        self.assertEqual(fontes.extrair_arxiv_id("10.48550/arxiv.1706.03762"), "1706.03762")
        self.assertEqual(fontes.extrair_arxiv_id("nada"), "")


class Crossref(unittest.TestCase):
    def test_normaliza_o_registro(self):
        reg = fontes.normalizar_crossref(CROSSREF)
        self.assertEqual(reg.doi, "10.1007/s10648-025-10003-9")
        self.assertEqual(reg.autores[0], "Emily Tharumalingam")
        self.assertEqual((reg.periodico, reg.ano, reg.volume, reg.numero, reg.paginas),
                         ("Educational Psychology Review", 2025, "37", "2", "35"))
        self.assertEqual(reg.fonte, "crossref")

    def test_so_o_link_pdf_vira_candidato(self):
        cands = fontes.candidatos_crossref(CROSSREF)
        self.assertEqual([c.url for c in cands],
                         ["https://link.springer.com/content/pdf/10.1007/s10648-025-10003-9.pdf"])
        self.assertEqual(cands[0].degrau, "crossref-tdm")

    def test_url_com_email_entra_no_polite_pool(self):
        self.assertIn("mailto=a%40b.c", fontes.crossref_url("10.1/x", "a@b.c"))
        self.assertNotIn("mailto", fontes.crossref_url("10.1/x"))


class OpenAlex(unittest.TestCase):
    def test_normaliza_ids_e_biblio(self):
        reg = fontes.normalizar_openalex(OPENALEX)
        self.assertEqual((reg.doi, reg.pmid, reg.pmcid), ("10.7717/peerj.4375", "29456894", "PMC5815332"))
        self.assertEqual((reg.volume, reg.numero, reg.paginas), ("6", "", "e4375"))
        self.assertEqual(reg.oa_status, "gold")
        self.assertEqual(reg.arxiv_id, "1801.01234")

    def test_candidatos_sem_repetir_e_sem_os_fechados(self):
        cands = fontes.candidatos_openalex(OPENALEX)
        urls = [c.url for c in cands]
        self.assertEqual(urls, ["https://peerj.com/articles/4375.pdf",
                                "https://europepmc.org/articles/pmc5815332?pdf=render",
                                "https://peerj.com/articles/4375"])
        self.assertEqual(cands[-1].tipo, "landing")

    def test_busca_leva_filtro_de_ano(self):
        url = fontes.openalex_busca_url("playback speed", desde=2020, n=7)
        self.assertIn("from_publication_date%3A2020-01-01", url)
        self.assertIn("per-page=7", url)


class Unpaywall(unittest.TestCase):
    def test_pdf_antes_da_pagina_e_sem_repetir(self):
        cands = fontes.candidatos_unpaywall(UNPAYWALL)
        self.assertEqual([(c.url, c.tipo) for c in cands], [
            ("https://dash.harvard.edu/x.pdf", "pdf"),
            ("https://dash.harvard.edu/handle/x", "landing"),
            ("https://editora.example/artigo", "landing"),
        ])
        self.assertEqual(cands[0].versao, "acceptedVersion")


class OutrasFontes(unittest.TestCase):
    def test_semantic_scholar(self):
        self.assertEqual(fontes.candidatos_s2({"openAccessPdf": {"url": "https://x/y.pdf"}})[0].degrau,
                         "semantic-scholar")
        self.assertEqual(fontes.candidatos_s2({"openAccessPdf": None}), [])
        self.assertEqual(fontes.ids_s2({"externalIds": {"ArXiv": "2301.1", "PubMedCentral": "PMC1"}}),
                         {"arxiv_id": "2301.1", "pmid": "", "pmcid": "PMC1"})

    def test_europepmc(self):
        obj = {"resultList": {"result": [{"id": "1"}, {"id": "2", "pmcid": "PMC7029759"}]}}
        self.assertEqual(fontes.pmcid_de_europepmc(obj), "PMC7029759")
        cands = fontes.candidatos_europepmc("PMC7029759")
        self.assertEqual([c.tipo for c in cands], ["pdf", "xml"])
        self.assertEqual(fontes.candidatos_europepmc(""), [])

    def test_arxiv(self):
        self.assertEqual(fontes.candidatos_arxiv("2301.08243")[0].url, "https://arxiv.org/pdf/2301.08243")

    def test_semantic_scholar_normaliza_metadados(self):
        reg = fontes.normalizar_s2({"title": "Attention Is All You Need", "year": 2017, "venue": "NeurIPS",
                                    "authors": [{"name": "Ashish Vaswani"}], "citationCount": 100000,
                                    "externalIds": {"ArXiv": "1706.03762", "DOI": "10.48550/arXiv.1706.03762"}})
        self.assertEqual((reg.doi, reg.ano, reg.periodico, reg.autores, reg.fonte),
                         ("10.48550/arxiv.1706.03762", 2017, "NeurIPS", ("Ashish Vaswani",), "semantic-scholar"))
        self.assertIn("arXiv:1706.03762", fontes.s2_arxiv_url("1706.03762"))

    def test_arxiv_atom_vira_registro_e_a_entrada_error_nao(self):
        atom = (b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">'
                b'<entry><id>http://arxiv.org/abs/1706.03762v7</id><title>Attention Is All\n  You Need</title>'
                b'<published>2017-06-12T17:57:34Z</published><author><name>Ashish Vaswani</name></author>'
                b'<author><name>Noam Shazeer</name></author><arxiv:doi>10.48550/arXiv.1706.03762</arxiv:doi></entry></feed>')
        reg = fontes.normalizar_arxiv_atom(atom)
        self.assertEqual((reg.titulo, reg.ano, reg.autores, reg.arxiv_id, reg.fonte),
                         ("Attention Is All You Need", 2017, ("Ashish Vaswani", "Noam Shazeer"), "1706.03762v7", "arxiv"))
        erro = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Error</title></entry></feed>'
        self.assertIsNone(fontes.normalizar_arxiv_atom(erro))
        self.assertIsNone(fontes.normalizar_arxiv_atom(b"<html>"))

    def test_pmcid_ganha_prefixo(self):
        self.assertEqual(fontes.normalizar_pmcid("5815332"), "PMC5815332")
        self.assertEqual(fontes.normalizar_pmcid("pmc5815332"), "PMC5815332")
        self.assertEqual(fontes.normalizar_pmcid(None), "")


class Http(unittest.TestCase):
    def test_user_agent_so_leva_email_quando_ha(self):
        self.assertIn("mailto:a@b.c", fontes.user_agent("a@b.c"))
        self.assertNotIn("mailto", fontes.user_agent(None))

    def test_email_so_vai_para_crossref_openalex_e_unpaywall(self):
        for url in ("https://api.crossref.org/works/10.1/x", "https://api.openalex.org/works/doi:10.1/x",
                    "https://api.unpaywall.org/v2/10.1/x?email=a@b.c"):
            self.assertEqual(fontes.email_para(url, "a@b.c"), url and "a@b.c")
        for url in ("https://api.semanticscholar.org/graph/v1/paper/DOI:10.1/x", "https://arxiv.org/pdf/1",
                    "https://link.springer.com/content/pdf/x.pdf", "https://www.ebi.ac.uk/europepmc/x",
                    "https://api.crossref.org.evil.example/works/x"):
            self.assertIsNone(fontes.email_para(url, "a@b.c"))
        self.assertIsNone(fontes.email_para("https://api.crossref.org/works/x", None))

    def test_http_get_nao_manda_email_a_outros_hosts(self):
        import urllib.request
        vistos = []

        class Resposta:
            status = 200
            headers = {}

            def read(self):
                return b"{}"

            def geturl(self):
                return "https://x"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def abrir_falso(req, timeout=0):
            vistos.append(req.get_header("User-agent"))
            return Resposta()
        original = urllib.request.urlopen
        urllib.request.urlopen = abrir_falso
        try:
            fontes.http_get("https://api.semanticscholar.org/x", email="a@b.c")
            fontes.http_get("https://api.openalex.org/x", email="a@b.c")
        finally:
            urllib.request.urlopen = original
        self.assertNotIn("mailto", vistos[0])
        self.assertIn("mailto:a@b.c", vistos[1])


if __name__ == "__main__":
    unittest.main()
