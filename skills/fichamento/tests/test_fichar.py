"""Testes do fichar.py, sem rede e sem git: localizar, página impressa, janelas, gravar e validar."""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fichar  # noqa: E402

REGISTRO = """# R

## Fontes

### FT-teste-2020 — Teste (2020)
- **Referência:** Ana Teste, 2020, "Um artigo", *Periódico* 1(1), 469-480. DOI 10.1000/teste (registro: Crossref, 2026-09-26)
- **Tipo e revisão:** artigo revisado por pares

Fonte: x

#### AF-001
- **Situação:** texto completo

### FT-prova-2011 — Prova (2011)
- **Referência:** B, 2011, "Outro", *P* 2(2), 542-554. DOI 10.1000/prova (registro: Crossref, 2026-09-26)
- **Versão da cópia:** prova tipográfica da editora, sem a paginação do periódico

Fonte: y
"""
TXT = "Title Page\n\nABSTRACT\n\nWe found that training did not improve accuracy.\n\fMETHOD\n\nParticipants\n\nForty-four investigators took part, d = -0.129.\n\fRESULTS\n\nThe effect was significant, p < .01.\n"

NOTA = "---\nft: FT-teste-2020\n---\n# Teste (2020)\n\nA parte até \"## Do modelo\" é gerada; \"## Do autor\" é sua.\n\n## O que o registro já tem\n\n- x\n\n## Do autor\n\n### O que este texto diz\n\nMeu texto.\n"

BLOCO_OK = """**Pergunta.** O treino melhora a acurácia?

**Rótulo:** refuta

**Trecho.** "training did not improve accuracy" (p. 469)

**Perguntas ao autor:**
1. Quer a tabela 1?
2. Vale abrir o método?
"""


class Fichar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name)
        (self.raiz / "fontes" / "copias").mkdir(parents=True); (self.raiz / "docs" / "leituras").mkdir(parents=True)
        (self.raiz / "fontes" / "registro.md").write_text(REGISTRO, encoding="utf-8")
        txt = self.raiz / "fontes" / "copias" / "teste.txt"; txt.write_text(TXT, encoding="utf-8")
        json.dump({"doi": "10.1000/teste", "arquivo": str(self.raiz / "fontes" / "copias" / "teste.pdf")},
                  open(self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json", "w"))
        self.nota = self.raiz / "docs" / "leituras" / "FT-teste-2020.md"; self.nota.write_text(NOTA, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_localizar_acha_txt_e_intervalo(self):
        f = fichar.localizar("FT-teste-2020", self.raiz)
        self.assertEqual(f.doi, "10.1000/teste"); self.assertEqual(f.paginas, (469, 480)); self.assertTrue(f.txt and f.txt.name == "teste.txt")

    def test_sem_copia_local(self):
        f = fichar.localizar("FT-prova-2011", self.raiz)
        self.assertIsNone(f.txt)

    def test_pagina_impressa_e_da_copia(self):
        f = fichar.localizar("FT-teste-2020", self.raiz)
        self.assertEqual(fichar.pagina_impressa(2, f), "p. 471")
        p = fichar.localizar("FT-prova-2011", self.raiz)
        self.assertEqual(fichar.pagina_impressa(2, p), "p. 3 da cópia")

    def test_mapa_e_janelas(self):
        f = fichar.localizar("FT-teste-2020", self.raiz); txt = f.txt.read_text()
        titulos = [t for _, _, t in fichar.mapa(txt, f)]
        self.assertIn("METHOD", titulos); self.assertIn("RESULTS", titulos)
        self.assertIn("Forty-four", fichar.janela_pagina(txt, 1))
        j = fichar.janela_termo(txt, ["d = -0,129"], fonte=f)
        self.assertIn("p. 470", j); self.assertIn("0.129", j)
        self.assertIn("não consta", fichar.janela_termo(txt, ["unicórnio"], fonte=f))
        self.assertIn("p < .01", fichar.janela_secao(txt, "RESULTS", f))

    def test_validar_pega_citacao_sem_pagina_e_bloco_do_resumo(self):
        erros = fichar.validar(BLOCO_OK, "responder"); self.assertEqual(erros, [], erros)
        ruim = BLOCO_OK.replace(" (p. 469)", "")
        self.assertTrue(any("sem página" in e for e in fichar.validar(ruim, "responder")))
        self.assertTrue(any("resumo" in e for e in fichar.validar("**Rótulo:** sustenta\n\n**Perguntas ao autor:**\n1. a\n2. b\n", "responder")))
        self.assertTrue(any("Veredito" in e for e in fichar.validar(BLOCO_OK, "verificar")))
        self.assertTrue(any("Perguntas ao autor" in e for e in fichar.validar(BLOCO_OK.replace("2. Vale abrir o método?\n", ""), "responder")))

    def test_gravar_cria_secao_e_preserva_autor(self):
        c = fichar.gravar(self.nota, "responder", BLOCO_OK, quando="2026-09-26")
        t = self.nota.read_text()
        self.assertIn("## Do modelo", t); self.assertLess(t.index("## Do modelo"), t.index("## Do autor"))
        self.assertIn(c, t); self.assertIn("Meu texto.", t); self.assertIn("_ferramenta: Claude Code; skill fichamento_", t)
        fichar.gravar(self.nota, "verificar", "**Veredito:** refutada (p. 470)\n\n**Perguntas ao autor:**\n1. a\n2. b\n", quando="2026-09-27")
        t2 = self.nota.read_text()
        self.assertEqual(len(re.findall(r"(?m)^## Do modelo$", t2)), 1); self.assertLess(t2.index("### responder"), t2.index("### verificar"))
        self.assertIn("Meu texto.", t2)


if __name__ == "__main__":
    unittest.main()


TXT_HIFEN = "Intro\n\fWe saw an even greater increase in confi-\ndence, leading to increased overconfidence for easy items.\n\fEnd\n"


class FicharDefeitosDoS4(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name)
        (self.raiz / "fontes" / "copias").mkdir(parents=True)
        (self.raiz / "fontes" / "registro.md").write_text(REGISTRO, encoding="utf-8")
        (self.raiz / "fontes" / "copias" / "teste.txt").write_text(TXT_HIFEN, encoding="utf-8")
        json.dump({"doi": "10.1000/teste", "arquivo": str(self.raiz / "fontes" / "copias" / "teste.pdf")},
                  open(self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json", "w"))
        self.f = fichar.localizar("FT-teste-2020", self.raiz)

    def tearDown(self):
        self.tmp.cleanup()

    def test_termo_quebrado_por_hifen_de_fim_de_linha(self):
        j = fichar.janela_termo(TXT_HIFEN, ["greater increase in confidence"], fonte=self.f)
        self.assertIn("texto emendado", j); self.assertIn("p. 470", j)

    def test_pagina_da_linha_que_abre_com_form_feed(self):
        j = fichar.janela_termo(TXT_HIFEN, ["We saw"], fonte=self.f)
        self.assertIn("[p. 470", j)   # a linha começa com \f: pertence à página nova, não à anterior

    def test_pagina_impressa_e_indice(self):
        self.assertEqual(fichar.indice_de_pagina(470, self.f, 3), 1)   # impressa
        self.assertEqual(fichar.indice_de_pagina(2, self.f, 3), 1)     # índice, fora do intervalo impresso

    def test_trema_e_aspas_em_palavra_solta(self):
        txt = "Intro\n\fK¨ohnken (1987) found d = -0.159.\n"
        j = fichar.janela_termo(txt, ["Köhnken"], fonte=self.f)
        self.assertIn("p. 470", j)
        bloco = "**Alegação, como está.** treino \"aumentou\" o viés \"sem melhorar a sensibilidade\"\n\n**Veredito:** sustentada com ressalva\n**Nível da checagem:** S\n**O que mudaria esta avaliação:** x\n\n**A favor.**\n- \"training and prior experience appeared to increase\" (p. 469)\n\n**Perguntas ao autor:**\n1. a\n2. b\n"
        self.assertEqual(fichar.validar(bloco, "verificar"), [])

    def test_subsecao_vale_como_pagina_em_versao_sem_paginacao(self):
        bloco = "**Pergunta.** x\n\n**Rótulo:** sustenta\n\n**Trecho.** \"payoffs and base rate influence bias in the model\" (seção Overview of SDT)\n\n**Perguntas ao autor:**\n1. a\n2. b\n"
        self.assertEqual(fichar.validar(bloco, "responder"), [])

    def test_doi_com_parentese_nao_e_truncado(self):
        b = "Ver Lichtenstein & Fischhoff (1977), DOI 10.1016/0030-5073(77)90001-0. E (10.1037/h0022125)."
        self.assertEqual(fichar.dois_mencionados(b), ["10.1016/0030-5073(77)90001-0", "10.1037/h0022125"])


# ------------------------------------------------ capa antes do artigo (defeito de 28/09/2026)
# A cópia de Tannenbaum e Cerasoli (2013) abre com a capa da SAGE, e a p. 231 é a segunda página
# do PDF: o fichar.py supunha que a primeira página da cópia era a primeira impressa e rotulava
# tudo uma página acima. Aqui a p. 469 do FT-teste-2020 é a segunda página da cópia, e a capa
# cita o artigo pela primeira página, como a da SAGE ("2013 55: 231").

TXT_CAPA = "\f".join([
    "Periódico: The Journal\n\nUm artigo\n\nPeriódico 2020 1: 469 originally published online\n\nDownloaded on May 1, 2020\n",
    "Um artigo\n\nAna Teste\n\nABSTRACT\n\nWe found that training did not improve accuracy.\n\nVol. 1, No. 1, 2020, pp. 469-480\n",
    "470\t\tPeriódico\n\nMETHOD\n\nForty-four investigators took part, d = -0.129.\n",
    "Um artigo                                        471\n\nRESULTS\n\nThe effect was significant, p < .01.\n",
    "472\t\tPeriódico\n\nDISCUSSION\n\nTraining is not enough.\n",
])


class FicharCapaAntesDoArtigo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        (self.raiz / "fontes" / "copias").mkdir(parents=True)
        (self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/teste", "arquivo": str(self.raiz / "fontes" / "copias" / "teste.pdf")}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _fonte(self, txt, registro=REGISTRO):
        (self.raiz / "fontes" / "registro.md").write_text(registro, encoding="utf-8")
        (self.raiz / "fontes" / "copias" / "teste.txt").write_text(txt, encoding="utf-8")
        return fichar.localizar("FT-teste-2020", self.raiz)

    def test_capa_desloca_a_pagina_impressa(self):
        f = self._fonte(TXT_CAPA)
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 469")   # a segunda página da cópia abre o artigo
        self.assertEqual(fichar.pagina_impressa(3, f), "p. 471")
        self.assertIn("[p. 470,", fichar.janela_termo(TXT_CAPA, ["Forty-four"], fonte=f))

    def test_capa_nao_ganha_pagina_impressa(self):
        f = self._fonte(TXT_CAPA)
        self.assertEqual(fichar.pagina_impressa(0, f), "p. 1 da cópia")   # e não "p. 468", que não existe

    def test_pagina_depois_do_artigo_e_da_copia(self):
        artigo = ["Um artigo\n\nABSTRACT\n\nx\n"] + [f"{p}\t\tPeriódico\n\ntexto\n" for p in range(470, 481)]
        f = self._fonte("\f".join(["Capa\n"] + artigo + ["Material suplementar\n"]))
        self.assertEqual(fichar.pagina_impressa(12, f), "p. 480")
        self.assertEqual(fichar.pagina_impressa(13, f), "p. 14 da cópia")   # o artigo acaba na p. 480

    def test_indice_de_pagina_com_capa(self):
        f = self._fonte(TXT_CAPA)
        self.assertEqual(fichar.indice_de_pagina(471, f, 5), 3)   # --pagina 471 abre a página de RESULTS
        self.assertEqual(fichar.indice_de_pagina(1, f, 5), 0)     # índice fora do intervalo: a capa

    def test_janela_secao_com_capa(self):
        f = self._fonte(TXT_CAPA)
        j = fichar.janela_secao(TXT_CAPA, "RESULTS", f)
        self.assertTrue(j.startswith("[p. 471] RESULTS"), j); self.assertIn("p < .01", j)

    def test_indicio_fraco_nao_desloca(self):
        solto = TXT.replace("The effect was significant", "470 of the analysts improved; the effect was significant")
        self.assertEqual(fichar.pagina_impressa(2, self._fonte(solto)), "p. 471")   # um número só não é cabeçalho
        empate = "\f".join(["a\n", "b\n", "470 x\n", "471 x\n", "472 x\n", "470 y\n", "471 y\n", "472 y\n"])   # votos em 1 e em 4, três a três
        self.assertEqual(fichar.pagina_impressa(2, self._fonte(empate)), "p. 471")

    def _registro_com_versao(self, versao):
        return REGISTRO.replace("- **Tipo e revisão:** artigo", f"- **Versão da cópia:** {versao}\n- **Tipo e revisão:** artigo", 1)

    def test_registro_declara_a_pagina_do_pdf(self):
        sem_cabecalho = "Repositório institucional\n\nUm artigo\n\f" + TXT   # a capa e três páginas sem número impresso
        self.assertEqual(fichar.pagina_impressa(1, self._fonte(sem_cabecalho)), "p. 470")   # sem indício, vale o de sempre
        for frase in ("a página 2 do PDF é a página 469 do periódico", "a página impressa é a do PDF mais 467"):
            f = self._fonte(sem_cabecalho, self._registro_com_versao(f"PDF da versão publicada, com a capa do repositório; {frase}"))
            self.assertEqual(fichar.pagina_impressa(1, f), "p. 469", frase); self.assertEqual(f.aviso, "", frase)
        menos = self._registro_com_versao("PDF com a capa da editora; a página impressa é a do PDF menos 1").replace("469-480", "1-8")
        self.assertEqual(fichar.pagina_impressa(1, self._fonte(sem_cabecalho, menos)), "p. 1")   # artigo paginado de 1 a 8

    def test_registro_prevalece_e_a_divergencia_aparece(self):
        f = self._fonte(TXT_CAPA, self._registro_com_versao("PDF da versão publicada; a página 1 do PDF é a página 469"))
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 470")   # as AF citam pela regra do registro, e o bloco concorda com elas
        self.assertIn("na página 2", f.aviso); self.assertIn("vale o registro", f.aviso)

    def _rodar(self, *args):
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            fichar.main(["--raiz", str(self.raiz), *args])
        return saida.getvalue(), erro.getvalue()

    def test_localizar_e_mapa_dizem_onde_comeca_o_artigo(self):
        self._fonte(TXT_CAPA)
        self.assertEqual(json.loads(self._rodar("localizar", "FT-teste-2020")[0])["deslocamento"], 1)
        self.assertIn("a p. 469 é a 2ª delas", self._rodar("mapa", "FT-teste-2020")[0].splitlines()[1])

    def test_aviso_de_divergencia_sai_no_terminal(self):
        self._fonte(TXT_CAPA, self._registro_com_versao("PDF da versão publicada; a página 1 do PDF é a página 469"))
        self.assertIn("vale o registro", self._rodar("mapa", "FT-teste-2020")[1])

    def test_sem_intervalo_a_declaracao_nao_da_pagina_impressa(self):
        sem_intervalo = self._registro_com_versao("PDF da versão publicada; a página 2 do PDF é a página 1").replace(" 469-480.", "")
        f = self._fonte(TXT_CAPA, sem_intervalo)   # a referência sem intervalo, como a de FT-schoenegger-2024
        self.assertIsNone(f.paginas); self.assertEqual(fichar.pagina_impressa(1, f), "p. 2 da cópia")

    def test_dois_numeros_alinhados_por_acaso_nao_bastam(self):
        negativo = "\f".join(["Capa\n\nPeriódico, pp. 469 a 480\n", "471\n\nTABLE 1 Participant ID\n", "472\n\nTABLE 1 (cont.)\n"])
        self.assertEqual(fichar.pagina_impressa(1, self._fonte(negativo)), "p. 470")   # dois votos em -1 não são cabeçalho
        positivo = "\f".join(["Title Page\n", "METHOD\n", "470 participants\n", "471 participants\n"])
        self.assertEqual(fichar.pagina_impressa(2, self._fonte(positivo)), "p. 471")   # nem dois votos em 1

    def test_versao_sem_paginacao_nao_avisa(self):
        prova = self._registro_com_versao("prova tipográfica da editora, sem a paginação do periódico; a página 1 do PDF é a página 469")
        f = self._fonte(TXT_CAPA, prova)   # os cabeçalhos discordam da declaração, mas o rótulo é sempre 'da cópia'
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 2 da cópia"); self.assertEqual(f.aviso, "")

    def test_pagina_a_mais_sem_indicio_avisa(self):
        sem_cabecalho = "Repositório institucional\n\nUm artigo\n\f" + TXT   # quatro páginas com texto
        f = self._fonte(sem_cabecalho, REGISTRO.replace("469-480", "469-471"))   # um artigo de três páginas
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 470")   # o rótulo segue o de sempre; o aviso diz por quê
        self.assertIn("4 páginas com texto", f.aviso); self.assertIn('"a página N do PDF é a página 469"', f.aviso)
        self.assertEqual(self._fonte(sem_cabecalho).aviso, "")   # com o intervalo de 12 páginas, nada sobra

    def test_copia_que_comeca_depois_da_primeira_pagina(self):
        truncada = self._registro_com_versao("PDF da versão publicada, sem a primeira página; a página 1 do PDF é a página 470")
        f = self._fonte(TXT, truncada)   # deslocamento -1: a cópia não traz número de página, e só o registro o dá
        self.assertEqual(fichar.pagina_impressa(0, f), "p. 470"); self.assertEqual(fichar.indice_de_pagina(470, f, 3), 0)
