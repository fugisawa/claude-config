import json
import tempfile
import unittest
from pathlib import Path

import _caminho  # noqa: F401
import acesso
import fontes
from fontes import Candidato
from _jats import ARTICLESET, SO_A_FOLHA_DE_ROSTO

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
        (corpo, final, formato), recusa = acesso.baixar_ou_recusa(Candidato("https://rep.edu/handle/1", "unpaywall", tipo="landing"), obter=obter)
        self.assertEqual((formato, final, recusa), ("pdf", "https://rep.edu/files/artigo.pdf", ""))
        self.assertTrue(corpo.startswith(b"%PDF"))

    def test_html_sem_pdf_e_recusado_com_a_linha_do_diario(self):
        obter = falso_obter({"https://ed/x": (200, b"<html>paywall</html>", "https://ed/x")})
        self.assertEqual(acesso.baixar_ou_recusa(Candidato("https://ed/x", "crossref-tdm"), obter=obter),
                         (None, "crossref-tdm: nada legível em https://ed/x"))

    def test_xml_conta_como_texto_quando_traz_o_corpo(self):
        obter = falso_obter({"https://epmc/xml": (200, b"<article><body><p>oi</p></body></article>", "https://epmc/xml")})
        self.assertEqual(acesso.baixar_ou_recusa(Candidato("https://epmc/xml", "europepmc", tipo="xml"), obter=obter)[0][2], "xml")


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

    def test_email_so_acompanha_as_consultas_de_crossref_openalex_e_unpaywall(self):
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


DOI_PMC = "10.1177/0956797613497022"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=4076289"
EPMC_PDF = "https://europepmc.org/articles/PMC4076289?pdf=render"
EPMC_XML = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4076289/fullTextXML"
OPENALEX_FECHADO_COM_PMCID = {"doi": f"https://doi.org/{DOI_PMC}", "open_access": {"is_oa": False, "oa_status": "closed"},
                              "ids": {"pmcid": "https://www.ncbi.nlm.nih.gov/pmc/articles/4076289"}}


class Efetch(unittest.TestCase):
    """O degrau de 02/10/2026: o manuscrito de Reyna e col. (2014), PMC4076289, que o Europe PMC não serviu (500 no
    REST, 403 no site) e o efetch do NCBI devolveu inteiro, num `<pmc-articleset>`."""
    def buscar(self):
        return falso_buscar({"api.openalex.org": (200, OPENALEX_FECHADO_COM_PMCID)})

    def test_o_pmcid_rende_o_candidato_do_efetch_depois_dos_do_europepmc(self):
        cands, _, diario = acesso.coletar(DOI_PMC, None, buscar=self.buscar())
        self.assertEqual([c.url for c in cands], [EPMC_PDF, EPMC_XML, EFETCH])
        self.assertEqual((cands[-1].degrau, cands[-1].tipo), ("ncbi-efetch", "xml"))
        self.assertIn("ncbi-efetch: PMCID PMC4076289", diario)

    def test_sem_pmcid_o_degrau_e_pulado_e_o_diario_diz(self):
        _, _, diario = acesso.coletar("10.1/x", None, buscar=falso_buscar({}))
        self.assertEqual(diario[-1], "ncbi-efetch: sem PMCID")

    def test_o_xml_sem_corpo_nao_abre_e_o_diario_diz_por_que(self):
        obter = falso_obter({EPMC_XML: (500, b"", EPMC_XML), EFETCH: (200, SO_A_FOLHA_DE_ROSTO, EFETCH)})
        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir(DOI_PMC, Path(pasta), buscar=self.buscar(), obter=obter)
            self.assertEqual(r["status"], "nao_aberto")
            self.assertIn(f"europepmc: nada legível em {EPMC_XML}", r["diario"])
            self.assertIn(f"ncbi-efetch: XML sem o corpo do artigo em {EFETCH}", r["diario"])
            self.assertEqual(list(Path(pasta).iterdir()), [])

    def test_o_manuscrito_abre_como_xml_na_versao_aceita_e_a_escada_nao_poe_o_email_no_que_grava(self):
        chamadas = []

        def obter(url, **kw):
            chamadas.append((url, kw.get("email")))
            return (200, ARTICLESET, EFETCH, {}) if url == EFETCH else (404, b"", url, {})
        with tempfile.TemporaryDirectory() as pasta:
            r = acesso.abrir(DOI_PMC, Path(pasta), email="a@b.c", buscar=self.buscar(), obter=obter,
                             agora="2026-10-02T12:00:00-03:00")
            self.assertEqual((r["status"], r["formato"], r["degrau"], r["versao"], r["etiqueta"]),
                             ("aberto", "xml", "ncbi-efetch", "acceptedVersion", "A"))
            self.assertEqual((r["url"], r["url_final"]), (EFETCH, EFETCH))
            self.assertIn((EFETCH, "a@b.c"), chamadas, "o e-mail de cortesia vai no pedido")
            self.assertNotIn("a@b.c", json.dumps(r), "e a escada não o escreve em candidato, endereço nem diário; "
                             "o endereço que o http_get devolve sem ele é prova de test_fontes")
            self.assertTrue(Path(r["texto"]).read_text(encoding="utf-8").startswith("Developmental Reversals"))
            self.assertEqual(r["diario"][-2:], [
                f"ncbi-efetch: aberto como xml a partir de {EFETCH}",
                "ncbi-efetch: o XML se declara manuscrito do autor (NIHMS581621); a versão lida é a aceita, não a publicada"])


if __name__ == "__main__":
    unittest.main()
