"""O pedido ao autor: redige no idioma certo, cabe em 120 palavras, sugere o destinatário e nunca envia."""
import contextlib
import datetime as dt
import inspect
import io
import json
import unittest

import _caminho  # noqa: F401
import artigo
import fontes
import pedido

HOJE = dt.date(2026, 9, 16)
META_EN = {
    "doi": "10.1007/s10648-025-10003-9",
    "titulo": "Increasing Video Lecture Playback Speed Can Impair Test Performance – a Meta-Analysis",
    "autores": ["Emily Tharumalingam", "Brady R. T. Roberts"], "periodico": "Educational Psychology Review",
    "ano": 2025, "editora": "Springer Science and Business Media LLC",
    "correspondente": "Emily Tharumalingam", "pais_correspondente": "CA", "correspondente_marcado": True,
}
META_BR = {
    "doi": "10.1590/1807-0191201925197",
    "titulo": "Democracia, instituições de controle e justiça sob a ótica do pluralismo estatal",
    "autores": ["Rogério Bastos Arantes", "Thiago Moreira"], "periodico": "Opinião Pública", "ano": 2019,
    "editora": "FapUNIFESP (SciELO)", "correspondente": "Rogério Bastos Arantes", "pais_correspondente": "BR",
    "correspondente_marcado": False,
}


class Idioma(unittest.TestCase):
    def test_lusofono_em_portugues_e_o_resto_em_ingles(self):
        self.assertEqual([pedido.idioma_para(p) for p in ("BR", "pt", "US", "", "CA")],
                         ["pt", "pt", "en", "en", "en"])


class Redigir(unittest.TestCase):
    def test_em_ingles_cabe_no_limite_e_traz_doi_motivo_e_promessa(self):
        r = pedido.montar(META_EN, tema="playback speed of video lectures", hoje=HOJE)
        self.assertEqual(r["idioma"], "en")
        self.assertLessEqual(r["palavras"], pedido.LIMITE_DE_PALAVRAS)
        self.assertTrue(r["cabe_no_limite"])
        self.assertTrue(r["body"].startswith("Dear Dr. Tharumalingam,"))
        for trecho in ("doi:10.1007/s10648-025-10003-9", "playback speed of video lectures",
                       "will not redistribute", "sharing policies", "Daniel Fugisawa"):
            self.assertIn(trecho, r["body"])
        self.assertEqual(r["subject"], f'Request for a copy of "{META_EN["titulo"]}"')
        self.assertNotIn("Share Link", r["body"], "Springer não tem Share Link")
        self.assertEqual(r["destinatario"]["criterio"], "autor de correspondência marcado pelo OpenAlex")

    def test_em_portugues_e_com_o_primeiro_autor_quando_o_openalex_nao_marca(self):
        r = pedido.montar(META_BR, tema="controle externo pelos tribunais de contas", hoje=HOJE)
        self.assertEqual(r["idioma"], "pt")
        self.assertTrue(r["body"].startswith("Prezado(a) Prof(a). Arantes,"))
        self.assertIn("doi:10.1590/1807-0191201925197", r["body"])
        self.assertLessEqual(r["palavras"], pedido.LIMITE_DE_PALAVRAS)
        self.assertTrue(r["destinatario"]["criterio"].startswith("primeiro autor"))
        self.assertEqual(r["subject"], f'Pedido de cópia do artigo "{META_BR["titulo"]}"')

    def test_idioma_forcado_e_assinatura_propria(self):
        r = pedido.montar(META_BR, tema="x", idioma="en", assinatura="D. F.", hoje=HOJE)
        self.assertTrue(r["body"].startswith("Dear Dr. Arantes,"))
        self.assertTrue(r["body"].endswith("D. F."))

    def test_elsevier_pede_o_share_link_como_alternativa(self):
        r = pedido.montar({**META_EN, "editora": "Elsevier BV"}, tema="x", hoje=HOJE)
        self.assertIn("published version (or a Share Link)?", r["body"])

    def test_titulo_longo_cai_para_a_forma_compacta_e_ainda_cabe(self):
        longo = {**META_EN, "titulo": " ".join(["palavra"] * 40)}
        r = pedido.montar(longo, tema="x", hoje=HOJE)
        self.assertNotIn("sharing policies", r["body"])
        self.assertTrue(r["cabe_no_limite"], r["palavras"])

    def test_sem_autor_a_saudacao_e_generica(self):
        r = pedido.montar({"doi": "10.1/x", "titulo": "T"}, tema="x", hoje=HOJE)
        self.assertTrue(r["body"].startswith("Dear author,"))
        self.assertIn("autor não identificado", r["pendencia"])

    def test_sem_email_o_to_fica_vazio_e_com_email_vai(self):
        self.assertEqual(pedido.montar(META_EN, tema="x", hoje=HOJE)["to"], [])
        self.assertEqual(pedido.montar(META_EN, tema="x", para="a@b.c", hoje=HOJE)["to"], ["a@b.c"])

    def test_pendencia_tem_janela_de_30_dias(self):
        self.assertEqual(pedido.pendencia("Ana Silva", HOJE),
                         "pedido ao autor rascunhado em 2026-09-16 para Ana Silva; "
                         "sem resposta, não repetir antes de 2026-10-16")

    def test_nunca_envia(self):
        r = pedido.montar(META_EN, tema="x", hoje=HOJE)
        self.assertIn("`create_draft`", r["aviso"])
        self.assertIn("Nunca `send_message`", r["aviso"])
        for modulo in (pedido, artigo):
            self.assertNotIn("send_message(", inspect.getsource(modulo))


class Correspondente(unittest.TestCase):
    def test_marcado_pelo_openalex_com_pais(self):
        obj = {"doi": "https://doi.org/10.1/x", "title": "T", "authorships": [
            {"author": {"display_name": "Ana Silva"}, "countries": ["BR"], "is_corresponding": False},
            {"author": {"display_name": "Bob Jones"}, "countries": ["US"], "is_corresponding": True}]}
        reg = fontes.normalizar_openalex(obj)
        self.assertEqual((reg.correspondente, reg.pais_correspondente, reg.correspondente_marcado),
                         ("Bob Jones", "US", True))
        self.assertEqual(reg.autores, ("Ana Silva", "Bob Jones"))

    def test_sem_marca_fica_o_primeiro_autor_e_o_pais_vem_da_instituicao(self):
        obj = {"doi": "https://doi.org/10.1/x", "authorships": [
            {"author": {"display_name": "Ana Silva"}, "institutions": [{"country_code": "BR"}]}]}
        reg = fontes.normalizar_openalex(obj)
        self.assertEqual((reg.correspondente, reg.pais_correspondente, reg.correspondente_marcado),
                         ("Ana Silva", "BR", False))
        vazio = fontes.normalizar_openalex({"doi": "https://doi.org/10.1/x"})
        self.assertEqual((vazio.correspondente, vazio.pais_correspondente), ("", ""))


class CliPedido(unittest.TestCase):
    def _capturar(self, argv):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            codigo = artigo.main(argv)
        return codigo, saida.getvalue()

    def test_pedido_devolve_o_que_o_create_draft_precisa(self):
        original = artigo._metadados
        artigo._metadados = lambda doi, email: META_EN
        try:
            codigo, saida = self._capturar(["pedido", "10.1007/s10648-025-10003-9", "--tema", "x", "--json"])
            self.assertEqual(codigo, 0)
            r = json.loads(saida)
            self.assertEqual(set(r) >= {"to", "subject", "body", "pendencia", "aviso"}, True)
            codigo, saida = self._capturar(["pedido", "10.1007/s10648-025-10003-9", "--tema", "x",
                                            "--idioma", "pt", "--para", "a@b.c"])
            self.assertEqual(codigo, 0)
            self.assertIn("to:      a@b.c", saida)
            self.assertIn("Prezado(a) Prof(a). Tharumalingam,", saida)
            artigo._metadados = lambda doi, email: None
            self.assertEqual(self._capturar(["pedido", "10.1000/x", "--tema", "x"])[0], 2)
        finally:
            artigo._metadados = original


if __name__ == "__main__":
    unittest.main()
