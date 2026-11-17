"""O leitor de JATS, que dá o texto de conferência das cópias lidas em XML. O caso é o de 02/10/2026: o XML de
Reyna e col. (2014), obtido pelo efetch do NCBI (PMC4076289), vinha num `<pmc-articleset>`, e o texto extraído
só trazia o corpo; as duas citações da AF-029 estavam no resumo, e o `conferir` não as achava. O texto começa
pelo título e pelos parágrafos do resumo, e só então vem o corpo. As fixtures estão em `_jats.py`."""
import unittest

import _caminho  # noqa: F401
import leitura
from _jats import (ARTICLESET, ARTIGO, CABECALHO, MANUSCRITO_DO_EUROPEPMC, NIHMS, PMCID_INEXISTENTE,
                   SO_A_FOLHA_DE_ROSTO, TEXTO_DO_ARTIGO, VERSAO_DA_EDITORA_COM_NIHMS)


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

    def test_namespace_padrao_nao_esconde_as_tags(self):
        xml = (b'<article xmlns="https://jats.nlm.nih.gov/ns"><front><article-meta><title-group><article-title>T'
               b'</article-title></title-group></article-meta></front><body><p>corpo</p></body></article>')
        self.assertEqual(leitura.jats_para_texto(xml), "T\n\ncorpo")

    def test_sem_artigo_nem_titulo_resumo_ou_corpo_vem_o_documento_inteiro(self):
        self.assertEqual(leitura.jats_para_texto(b"<doc><x>texto </x><y>solto</y></doc>"), "texto solto")
        self.assertEqual(leitura.jats_para_texto(b"<article><front><p>nota </p></front></article>"), "nota")


class TituloEResumo(unittest.TestCase):
    def test_o_texto_comeca_pelo_titulo_e_pelos_paragrafos_do_resumo(self):
        self.assertEqual(leitura.jats_para_texto(ARTIGO), TEXTO_DO_ARTIGO)

    def test_o_resto_da_frente_e_o_fundo_ficam_de_fora(self):
        texto = leitura.jats_para_texto(ARTIGO)
        for fora in ("Psychological science", "Reyna", "framing", "References", "Another title", "PMC4076289",
                     "pmc-prop-manuscript", "yes"):
            self.assertNotIn(fora, texto)

    def test_resumo_estruturado_da_um_paragrafo_por_secao(self):
        xml = (b'<article><front><article-meta><title-group><article-title>T</article-title></title-group>'
               b'<abstract><sec><title>Background</title><p>why</p></sec><sec><title>Methods</title><p>how</p></sec>'
               b'</abstract></article-meta></front><body><p>corpo</p></body></article>')
        self.assertEqual(leitura.jats_para_texto(xml), "T\n\nBackground\n\nwhy\n\nMethods\n\nhow\n\ncorpo")

    def test_sem_corpo_o_texto_e_o_titulo_e_o_resumo(self):
        self.assertEqual(leitura.jats_para_texto(SO_A_FOLHA_DE_ROSTO), TEXTO_DO_ARTIGO.split("\n\nRisky")[0])


class PmcArticleset(unittest.TestCase):
    def test_o_articleset_do_efetch_e_aceito_como_involucro(self):
        self.assertEqual(leitura.jats_para_texto(ARTICLESET), TEXTO_DO_ARTIGO)

    def test_so_o_artigo_com_corpo_passa_sem_recusa(self):
        self.assertEqual(leitura.recusa_do_jats(ARTICLESET), "")
        self.assertEqual(leitura.recusa_do_jats(ARTIGO), "")

    def test_sem_o_corpo_do_artigo_a_recusa_diz_isso(self):
        for xml in (SO_A_FOLHA_DE_ROSTO, PMCID_INEXISTENTE,
                    b"<article><front/><body/></article>",
                    b"<article><front/><body> \n </body></article>",
                    b"<article><front/><sub-article><body><p>parecer</p></body></sub-article></article>",
                    b"<html><body><p>pagina de desafio</p></body></html>"):
            self.assertEqual(leitura.recusa_do_jats(xml), "XML sem o corpo do artigo", xml)

    def test_xml_ilegivel_tem_recusa_propria(self):
        self.assertEqual(leitura.recusa_do_jats(b"<a><b>"), "XML ilegível")
        entidade_do_dtd = CABECALHO + b"<pmc-articleset><article><body><p>a&nbsp;b</p></body></article></pmc-articleset>"
        self.assertEqual(leitura.recusa_do_jats(entidade_do_dtd), "XML ilegível")


class Manuscrito(unittest.TestCase):
    def test_o_manuscrito_do_autor_e_o_que_o_pmc_declara(self):
        self.assertEqual(leitura.manuscrito_do_jats(ARTICLESET), "NIHMS581621")
        self.assertEqual(leitura.manuscrito_do_jats(MANUSCRITO_DO_EUROPEPMC), "NIHMS581621")

    def test_o_nihms_que_sobra_na_versao_da_editora_nao_e_marca(self):
        self.assertEqual(leitura.manuscrito_do_jats(VERSAO_DA_EDITORA_COM_NIHMS), "")
        self.assertEqual(leitura.manuscrito_do_jats(MANUSCRITO_DO_EUROPEPMC.replace(b"<meta-value>yes", b"<meta-value>no")), "")
        self.assertEqual(leitura.manuscrito_do_jats(b"<a><b>"), "")

    def test_manuscrito_declarado_sem_identificador(self):
        self.assertEqual(leitura.manuscrito_do_jats(ARTIGO.replace(NIHMS, b"")), "sem identificador")


if __name__ == "__main__":
    unittest.main()
