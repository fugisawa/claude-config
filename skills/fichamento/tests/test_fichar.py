"""Testes do fichar.py, sem rede e sem git: localizar, página impressa, janelas, gravar e validar."""
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
