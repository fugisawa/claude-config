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
        (self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/teste", "arquivo": str(self.raiz / "fontes" / "copias" / "teste.pdf")}), encoding="utf-8")
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
        (self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/teste", "arquivo": str(self.raiz / "fontes" / "copias" / "teste.pdf")}), encoding="utf-8")
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

    def test_sem_intervalo_a_declaracao_vale_e_a_divergencia_aparece(self):
        sem_intervalo = self._registro_com_versao("PDF da versão publicada; a página 2 do PDF é a página 1").replace(" 469-480.", "")
        f = self._fonte(TXT_CAPA, sem_intervalo)   # a referência sem intervalo, como a de FT-schoenegger-2024, e a cópia imprime 470 a 472
        self.assertIsNone(f.paginas); self.assertEqual(fichar.pagina_impressa(1, f), "p. 1 da cópia")   # e não a posição, "p. 2 da cópia"
        self.assertIn("vale o registro", f.aviso)   # até 29/09/2026 a declaração sem intervalo era ignorada

    def test_dois_numeros_alinhados_por_acaso_nao_bastam(self):
        negativo = "\f".join(["Capa\n\nPeriódico, pp. 469 a 480\n", "471\n\nTABLE 1 Participant ID\n", "472\n\nTABLE 1 (cont.)\n"])
        self.assertEqual(fichar.pagina_impressa(1, self._fonte(negativo)), "p. 470")   # dois votos em -1 não são cabeçalho
        positivo = "\f".join(["Title Page\n", "METHOD\n", "470 participants\n", "471 participants\n"])
        self.assertEqual(fichar.pagina_impressa(2, self._fonte(positivo)), "p. 471")   # nem dois votos em 1

    def test_prova_segue_a_declaracao_com_o_rotulo_da_copia(self):
        prova = self._registro_com_versao("prova tipográfica da editora, sem a paginação do periódico; a página 1 do PDF é a página 469")
        f = self._fonte(TXT_CAPA, prova)   # até 29/09/2026 a prova ficava na posição, "p. 2 da cópia", sem aviso
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 470 da cópia")   # o número que o registro declara, e não o do periódico, "p. 470"
        self.assertIn("vale o registro", f.aviso)   # os cabeçalhos põem a p. 470 na página 3 do PDF

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


# ------------------------------------------------ o texto que o recibo declara (defeito de 28/09/2026)
# O recibo da artigos-cientificos grava "arquivo" e "texto" como o comando os recebeu: só o nome,
# relativo à pasta do recibo; relativo à raiz do projeto; ou absoluto, às vezes com a pasta pessoal
# da outra máquina. O fichar.py ignorava o campo "texto", resolvia o nome solto contra a raiz e usava
# o caminho da outra máquina como estava: dizia "sem cópia local" com o texto ao lado do recibo, ou
# caía no texto com o nome do DOI, que no caso de Steyvers e col. (2025) é a pré-publicação do arXiv,
# e não a versão publicada que o recibo declara.

OUTRA_MAQUINA = "/outra-maquina/analista_intel/fontes/copias/"   # como /home/danielfugisawa/… no recibo de Heuer (1981)


class FicharTextoDoRecibo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        self.copias = self.raiz / "fontes" / "copias"; self.copias.mkdir(parents=True)
        (self.raiz / "fontes" / "registro.md").write_text(REGISTRO, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _recibo(self, arquivo, texto):
        (self.copias / "10-1000-teste.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/teste", "arquivo": arquivo, "texto": texto}), encoding="utf-8")

    def test_nome_solto_e_relativo_a_pasta_do_recibo(self):
        (self.copias / "teste-manual.txt").write_text(TXT, encoding="utf-8")
        self._recibo("teste-manual.pdf", "teste-manual.txt")   # como o recibo de Kalyuga e col. (2003)
        self.assertEqual(fichar.localizar("FT-teste-2020", self.raiz).txt, self.copias / "teste-manual.txt")

    def test_caminho_relativo_a_raiz_do_projeto(self):
        (self.copias / "teste-manual.txt").write_text(TXT, encoding="utf-8")
        self._recibo("fontes/copias/teste-manual.pdf", "fontes/copias/teste-manual.txt")   # como o recibo de Dhami, Belton e Mandel (2019)
        self.assertEqual(fichar.localizar("FT-teste-2020", self.raiz).txt, self.copias / "teste-manual.txt")

    def test_caminho_absoluto_da_outra_maquina(self):
        (self.copias / "teste-manual.txt").write_text(TXT, encoding="utf-8")
        self._recibo(OUTRA_MAQUINA + "teste-manual.pdf", OUTRA_MAQUINA + "teste-manual.txt")
        self.assertEqual(fichar.localizar("FT-teste-2020", self.raiz).txt, self.copias / "teste-manual.txt")

    def test_texto_do_recibo_vence_o_texto_com_o_nome_do_doi(self):
        (self.copias / "teste-publicada.txt").write_text(TXT, encoding="utf-8")
        (self.copias / "10-1000-teste.txt").write_text("arXiv:2401.13835v2\n", encoding="utf-8")   # a pré-publicação
        self._recibo("teste-publicada.pdf", "teste-publicada.txt")   # como o recibo de Steyvers e col. (2025)
        self.assertEqual(fichar.localizar("FT-teste-2020", self.raiz).txt, self.copias / "teste-publicada.txt")

    def test_texto_declarado_que_falta_nao_cede_o_lugar_a_outro(self):
        (self.copias / "10-1000-teste.txt").write_text("arXiv:2401.13835v2\n", encoding="utf-8")
        self._recibo("teste-publicada.pdf", "teste-publicada.txt")   # o texto declarado ainda não chegou a esta máquina
        f = fichar.localizar("FT-teste-2020", self.raiz)
        self.assertIsNone(f.txt); self.assertIn("teste-publicada.txt", f.aviso)

    def test_texto_declarado_que_falta_manda_trazer_e_nao_reabrir(self):
        self._recibo("teste-publicada.pdf", "teste-publicada.txt")
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            codigo = fichar.main(["--raiz", str(self.raiz), "localizar", "FT-teste-2020"])
        self.assertEqual(codigo, 2); self.assertIn("traga a cópia da outra máquina", erro.getvalue())
        self.assertNotIn("abra pela skill", erro.getvalue())   # o abrir de Steyvers e col. (2025) trouxe a pré-publicação

    def test_recibo_sem_o_campo_texto_usa_o_pdf_com_txt(self):
        (self.copias / "teste-manual.txt").write_text(TXT, encoding="utf-8")
        (self.copias / "10-1000-teste.procedencia.json").write_text(   # recibo que só nomeia o PDF
            json.dumps({"doi": "10.1000/teste", "arquivo": OUTRA_MAQUINA + "teste-manual.pdf"}), encoding="utf-8")
        self.assertEqual(fichar.localizar("FT-teste-2020", self.raiz).txt, self.copias / "teste-manual.txt")

    def test_texto_corrido_acha_o_pdf_do_recibo(self):
        (self.copias / "teste-manual.pdf").write_bytes(b"%PDF-1.4\n")
        (self.copias / "teste-manual.txt").write_text(TXT, encoding="utf-8")
        (self.copias / "teste-manual.corrido.txt").write_text(TXT, encoding="utf-8")   # já extraído: o teste não roda o pdftotext
        for pasta in ("", "fontes/copias/", OUTRA_MAQUINA):
            with self.subTest(pasta=pasta or "nome solto"):
                self._recibo(pasta + "teste-manual.pdf", pasta + "teste-manual.txt")
                f = fichar.localizar("FT-teste-2020", self.raiz)
                self.assertEqual(fichar.texto_corrido(f), self.copias / "teste-manual.corrido.txt")


# ------------------------------------------------ cópia sem paginação (defeito de 28/09/2026)
# O texto que vem do XML JATS do PubMed Central e do Europe PMC, ou de uma página HTML, não tem form
# feed: a cópia inteira é uma página só, e o fichar.py a numerava pelo intervalo do registro. Toda
# linha de Reyna e col. (2014) saía "p. 76", toda linha de Lynn e Barrett (2014) saía "p. 1663", e o
# registro dessas fontes cita a seção.

TXT_JATS = ("Introduction\n\nWe asked whether training improves accuracy.\n\nMethod\n\n"
            "Forty-four investigators took part, d = -0.129.\n\nResults\n\nThe effect was significant, p < .01.\n")


class FicharCopiaSemPaginacao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        self.copias = self.raiz / "fontes" / "copias"; self.copias.mkdir(parents=True)
        (self.raiz / "fontes" / "registro.md").write_text(REGISTRO, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _copia(self, txt, formato):
        (self.copias / "teste.txt").write_text(txt, encoding="utf-8")
        (self.copias / "10-1000-teste.procedencia.json").write_text(json.dumps(
            {"doi": "10.1000/teste", "arquivo": "teste." + formato, "texto": "teste.txt", "formato": formato}), encoding="utf-8")

    def _rodar(self, *args):
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            fichar.main(["--raiz", str(self.raiz), *args])
        return saida.getvalue(), erro.getvalue()

    def test_xml_e_html_nao_ganham_pagina_impressa(self):
        for formato in ("xml", "html"):   # como os recibos de Reyna e col. (2014) e de Mandel e Barnes (2014)
            with self.subTest(formato=formato):
                self._copia(TXT_JATS, formato)
                saida = self._rodar("janela", "FT-teste-2020", "--termo", "Forty-four")[0]
                self.assertIn("[sem paginação, linha 7] Forty-four", saida); self.assertNotIn("p. 469", saida)
                saida = self._rodar("janela", "FT-teste-2020", "--secao", "Results")[0]
                self.assertTrue(saida.startswith("[sem paginação] Results"), saida)

    def _registro(self, registro):
        (self.raiz / "fontes" / "registro.md").write_text(registro, encoding="utf-8")
        return fichar.localizar("FT-teste-2020", self.raiz)

    def test_texto_sem_form_feed_nao_ganha_pagina_impressa(self):
        self._copia(TXT_JATS, "pdf")   # o recibo diz PDF, mas o texto não veio do pdftotext, que fecha toda página com form feed
        self.assertEqual(fichar.pagina_impressa(0, self._registro(REGISTRO)), "sem paginação")   # e não "p. 469", num intervalo de doze

    def test_artigo_de_uma_pagina_sem_form_feed_guarda_a_pagina(self):
        self._copia(TXT_JATS, "pdf")   # a única página da cópia é a única do artigo
        self.assertEqual(fichar.pagina_impressa(0, self._registro(REGISTRO.replace("469-480", "469-469"))), "p. 469")

    def test_texto_sem_form_feed_nem_intervalo_nao_ganha_pagina_da_copia(self):
        self._copia(TXT_JATS, "pdf")   # como a transcrição por OCR de Moore e Hoffman (2019), cujo intervalo o registro não dá ao script
        f = self._registro(REGISTRO.replace(" 469-480.", ""))
        self.assertIsNone(f.paginas); self.assertEqual(fichar.pagina_impressa(0, f), "sem paginação")   # e não "p. 1 da cópia", num PDF de 24 páginas

    def test_mapa_diz_que_a_copia_nao_tem_paginacao(self):
        self._copia(TXT_JATS, "xml")
        linhas = self._rodar("mapa", "FT-teste-2020")[0].splitlines()
        self.assertTrue(linhas[1].startswith("sem paginação: o recibo declara a cópia em XML"), linhas[1])
        self.assertIn('"(seção …)"', linhas[1]); self.assertIn("   sem paginação  L5     Method", linhas)

    def test_localizar_diz_que_a_copia_nao_tem_paginacao(self):
        self._copia(TXT_JATS, "html")
        d = json.loads(self._rodar("localizar", "FT-teste-2020")[0])
        self.assertEqual(d.get("sem_paginas"), "o recibo declara a cópia em HTML, que não tem página")
        self._copia(TXT, "pdf")   # a cópia paginada não ganha a chave, e o localizar dela sai como antes
        self.assertNotIn("sem_paginas", json.loads(self._rodar("localizar", "FT-teste-2020")[0]))

    def test_janela_por_pagina_recusa_a_copia_sem_paginacao(self):
        self._copia(TXT_JATS, "xml")   # --pagina 469 devolvia o texto inteiro, com o rótulo "p. 469"
        with self.assertRaises(SystemExit) as recusa:
            fichar.indice_de_pagina(469, fichar.localizar("FT-teste-2020", self.raiz), 1)
        self.assertIn("--termo", str(recusa.exception)); self.assertIn("--secao", str(recusa.exception))

    def test_rotulo_sem_paginacao_nao_e_ancora(self):
        copiado = BLOCO_OK.replace("(p. 469)", "(sem paginação)")   # o rótulo da janela não substitui a seção no bloco
        self.assertTrue(any("sem página" in e for e in fichar.validar(copiado, "responder")))
        self.assertEqual(fichar.validar(BLOCO_OK.replace("(p. 469)", "(seção Results)"), "responder"), [])

    def test_manuscrito_sem_form_feed_tambem_e_sem_paginacao(self):
        self._copia(TXT_JATS, "pdf")   # o rótulo 'da cópia' daria "p. 1 da cópia" a toda linha de um manuscrito de várias páginas
        manuscrito = REGISTRO.replace("- **Tipo e revisão:** artigo", "- **Versão da cópia:** manuscrito aceito, sem a paginação do periódico\n- **Tipo e revisão:** artigo", 1)
        self.assertEqual(fichar.pagina_impressa(0, self._registro(manuscrito)), "sem paginação")


# ------------------------------------------------ numeração impressa na própria cópia (defeito de 28/09/2026)
# Quando o registro cita a numeração impressa na própria cópia, e não a do periódico, o rótulo é "p. N da cópia",
# com o número impresso na página, que é o que o registro cita, e a página fora dessa numeração, como a capa, leva
# "p. N do PDF", com a posição da página no arquivo; o autor decidiu assim em 28/09/2026, e provas e manuscritos
# continuam rotulados pela posição no PDF, como se apresentou a ele. A regra nasceu de um defeito. A cópia de
# Colson e Cooke (2018) é a publicação antecipada da Oxford University Press, paginada de 1 a 21, e a de
# Tofel-Grehl e Feldon (2013) é a publicação antecipada paginada de 1 a 12. A Versão da cópia das duas diz que as
# páginas citadas são as da cópia, e não as do fascículo (113–132 e 293–304), mas o fichar.py só reconhecia a
# versão sem a paginação do periódico quando o campo começava por "prova", "manuscrito" ou "pré", e rotulava pelo
# fascículo: a p. 5 da cópia saía "p. 117".

TXT_ANTECIPADO = "\f".join([
    "1\n\nUm artigo\n\nAna Teste\n\nABSTRACT\n\nWe found that training did not improve accuracy.\n",
    "2\t\tAna Teste\n\nMETHOD\n\nForty-four investigators took part, d = -0.129.\n",
    "Um artigo\t\t3\n\nRESULTS\n\nThe effect was significant, p < .01.\n",
    "4\t\tAna Teste\n\nDISCUSSION\n\nTraining is not enough.\n",
]) + "\f"
ANTECIPADO = ("PDF da publicação antecipada online, paginado de 1 a 4; a paginação do fascículo é 469–480, "
              "e as páginas citadas abaixo são as da cópia.")

TXT_REIMPRESSAO = "\f".join([
    "HISTORICAL REVIEW PROGRAM\n\nRELEASE IN FULL\n\nTITLE: Um artigo\n",
    "Um artigo\n\nABSTRACT\n\nWe found that training did not improve accuracy.\n\n35\n",
    "Um artigo\n\nMETHOD\n\nForty-four investigators took part, d = -0.129.\n\n36\n",
    "Um artigo\n\nRESULTS\n\nThe effect was significant, p < .01.\n\n37\n",
    "Um artigo\n\nDISCUSSION\n\nTraining is not enough.\n\n38\n",
]) + "\f"
REIMPRESSAO = ("reimpressão integral do artigo em outra revista, pp. 35–38; o texto é o publicado, mas a paginação é a "
               "da reimpressão, e as localizações abaixo citam a página da reimpressão.")

TXT_REPETIDO = "\f".join(["Repositório institucional\n\nUm artigo\n"] +
                         [f"{n}\t\tAna Teste\n\nTexto da seção.\n" for n in (1, 2, 3, 3, 4, 5, 6)]) + "\f"
REPETIDO = ("manuscrito aceito, com a capa do repositório; a página 2 do PDF é a página 1, e a página 5 do PDF é a página 3, "
            "que se repete; as localizações citam a página impressa no manuscrito")   # como Costa, Miranda e Melo (2022), cuja página da tabela 2 repete o 12


class FicharNumeracaoDaCopia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        (self.raiz / "fontes" / "copias").mkdir(parents=True)
        (self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/teste", "arquivo": "teste.pdf", "texto": "teste.txt"}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _fonte(self, txt, versao, sem_intervalo=False):
        registro = REGISTRO.replace("- **Tipo e revisão:** artigo", f"- **Versão da cópia:** {versao}\n- **Tipo e revisão:** artigo", 1)
        if sem_intervalo:   # como a Science Advances, que identifica o artigo por um número, e o relatório lido no lugar de um livro
            registro = registro.replace("*Periódico* 1(1), 469-480. DOI", "*Periódico* 1(1), e123. DOI", 1)
        (self.raiz / "fontes" / "registro.md").write_text(registro, encoding="utf-8")
        (self.raiz / "fontes" / "copias" / "teste.txt").write_text(txt, encoding="utf-8")
        return fichar.localizar("FT-teste-2020", self.raiz)

    def _rodar(self, *args):
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            fichar.main(["--raiz", str(self.raiz), *args])
        return saida.getvalue(), erro.getvalue()

    def test_publicacao_antecipada_cita_a_pagina_da_copia(self):
        f = self._fonte(TXT_ANTECIPADO, ANTECIPADO)   # como Colson e Cooke (2018): o PDF começa no artigo
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 2 da cópia")   # e não "p. 470", do fascículo
        self.assertIn("[p. 2 da cópia,", fichar.janela_termo(TXT_ANTECIPADO, ["Forty-four"], fonte=f))

    def test_reimpressao_com_capa_cita_o_numero_impresso(self):
        f = self._fonte(TXT_REIMPRESSAO, REIMPRESSAO)   # como Betts (1978): a folha da CIA e a reimpressão de 1979, pp. 35–54
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 35 da cópia")   # e não "p. 470", nem a posição, "p. 2 da cópia"
        self.assertEqual(fichar.pagina_impressa(0, f), "p. 1 do PDF")      # a folha não tem número impresso
        self.assertEqual(fichar.indice_de_pagina(37, f, 6), 3)              # --pagina 37 abre a página de RESULTS

    def test_primeira_pagina_sem_numero_impresso(self):
        sem_numero = TXT_ANTECIPADO.replace("1\n\nUm artigo", "Um artigo", 1)   # como Tofel-Grehl e Feldon (2013): a p. 1 não imprime o número
        self.assertEqual(fichar.pagina_impressa(0, self._fonte(sem_numero, ANTECIPADO)), "p. 1 da cópia")   # e não "p. 1 do PDF"

    def test_ultima_pagina_sem_numero_impresso(self):
        sem_numero = TXT_ANTECIPADO.replace("4\t\tAna Teste", "Ana Teste", 1)   # como Harrison e col. (2020), cuja p. 13 não traz o número na camada de texto
        self.assertEqual(fichar.pagina_impressa(3, self._fonte(sem_numero, ANTECIPADO)), "p. 4 da cópia")   # e não "p. 4 do PDF"

    def test_declaracao_diz_onde_a_numeracao_comeca(self):
        com_capa = "Repositório institucional\n\nUm artigo\n\f" + TXT   # a capa e três páginas sem número impresso
        antiga = ("PDF da publicação antecipada, com a capa do repositório; a página 2 do PDF é a página 1, e as localizações "
                  "citam a paginação 1–3 da cópia, e não a 469–480 do fascículo")   # como Mellers e col. (2014) até 28/09/2026
        f = self._fonte(com_capa, antiga)
        self.assertEqual([fichar.pagina_impressa(i, f) for i in range(4)], ["p. 1 do PDF", "p. 1 da cópia", "p. 2 da cópia", "p. 3 da cópia"])
        self.assertEqual(f.aviso, "")

    def test_declaracao_prevalece_sobre_os_cabecalhos_e_avisa(self):
        f = self._fonte(TXT_ANTECIPADO, ANTECIPADO + " A página 2 do PDF é a página 1.")   # os cabeçalhos põem a p. 1 na 1ª página do PDF
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 1 da cópia")   # as AF citam pela regra do registro, e o bloco concorda com elas
        self.assertIn("na página 1 do PDF", f.aviso); self.assertIn("vale o registro", f.aviso)

    def test_sem_indicio_rotula_pela_posicao_e_avisa(self):
        f = self._fonte(TXT, ANTECIPADO)   # nem número impresso no cabeçalho e no pé, nem declaração
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 2 da cópia")   # supõe-se que o PDF começa no artigo
        self.assertIn("a numeração impressa começa", f.aviso); self.assertIn('"a página 2 do PDF é a página 1"', f.aviso)

    def test_versao_que_cita_o_fasciculo_continua_no_fasciculo(self):
        com_capa = "Repositório institucional\n\nUm artigo\n\f" + TXT
        convertida = ("PDF diagramado pela editora, com a paginação provisória 1–3 da publicação antecipada; na cópia, a capa é a p. 1 "
                      "do PDF, e a p. 1 provisória é a p. 2 do PDF. O fascículo tem as mesmas páginas, e as localizações citam a página "
                      "do fascículo, que é a provisória mais 468. Assim, a página 2 do PDF é a página 469. Até 2026-09-28 as localizações "
                      "citavam a paginação provisória, e o autor mandou convertê-las nessa data.")   # como Mellers e col. (2014) desde 28/09/2026
        f = self._fonte(com_capa, convertida)
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 469"); self.assertIsNone(f.paginas_da_copia)

    def test_versao_anterior_a_publicacao_com_capa_cita_o_numero_impresso(self):
        com_capa = "Repositório institucional\n\nUm artigo\n\f" + TXT_ANTECIPADO   # a capa e a numeração de 1 a 4 no cabeçalho
        for versao in ("manuscrito aceito, com a folha da editora antes do texto, e as localizações citam a página impressa no manuscrito",   # como Brem e col. (2018)
                       "prova tipográfica da editora, com a capa do repositório, sem a paginação do periódico",
                       "pré-publicação, com a capa do repositório"):
            with self.subTest(versao=versao.split(",")[0]):   # até 29/09/2026 as três ficavam na posição: "p. 2 da cópia" na p. 1
                f = self._fonte(com_capa, versao)
                self.assertEqual([fichar.pagina_impressa(i, f) for i in range(3)], ["p. 1 do PDF", "p. 1 da cópia", "p. 2 da cópia"])

    # A decisão do autor de 29/09/2026 estendeu a regra do número impresso às provas, aos manuscritos e às
    # pré-publicações, e a conferência do mesmo dia achou a declaração ignorada quando a referência não traz o
    # intervalo de páginas: a Versão da cópia de Schoenegger e col. (2024) diz "a página 2 do PDF é a página 1",
    # e o script rotulava a p. 1 do artigo como "p. 2 da cópia", a posição no PDF.

    def test_referencia_sem_intervalo_le_a_declaracao(self):
        com_capa = "Repositório institucional\n\nUm artigo\n\f" + TXT   # a capa e três páginas sem número impresso
        publicada = "PDF da versão publicada, com a capa do repositório; a página 2 do PDF é a página 1, e as localizações citam a página do artigo"
        f = self._fonte(com_capa, publicada, sem_intervalo=True)
        self.assertEqual([fichar.pagina_impressa(i, f) for i in range(4)], ["p. 1 do PDF", "p. 1 da cópia", "p. 2 da cópia", "p. 3 da cópia"])
        self.assertEqual(fichar.indice_de_pagina(3, f, 5), 3)   # --pagina 3 abre a última página, e não a 3ª do PDF

    def test_numeracao_que_se_repete_pede_duas_declaracoes(self):
        f = self._fonte(TXT_REPETIDO, REPETIDO)
        self.assertEqual([fichar.pagina_impressa(i, f) for i in range(8)],
                         ["p. 1 do PDF", "p. 1 da cópia", "p. 2 da cópia", "p. 3 da cópia", "p. 3 da cópia", "p. 4 da cópia", "p. 5 da cópia", "p. 6 da cópia"])
        self.assertEqual(f.aviso, "")   # os cabeçalhos concordam com a segunda declaração, que vale da página 5 do PDF em diante
        self.assertEqual(fichar.indice_de_pagina(5, f, 9), 6)   # --pagina 5 abre a 7ª página do PDF

    def test_segunda_declaracao_que_discorda_dos_cabecalhos_avisa(self):
        continua = "\f".join(["Repositório institucional\n\nUm artigo\n"] +
                             [f"{n}\t\tAna Teste\n\nTexto da seção.\n" for n in (1, 2, 3, 4, 5, 6)]) + "\f"   # a numeração não se repete
        digitada = ("manuscrito aceito, com a capa do repositório; a página 2 do PDF é a página 1, e a página 5 do PDF é a página 10, "
                    "que se repete")   # engano de digitação: a página 5 do PDF traz o 4
        f = self._fonte(continua, digitada)
        self.assertEqual(fichar.pagina_impressa(4, f), "p. 10 da cópia")   # vale o registro, como na primeira declaração
        self.assertIn("p. 10 da cópia na página 5 do PDF", f.aviso); self.assertIn("vale o registro", f.aviso)   # até aqui o aviso só olhava a primeira

    def test_numero_que_a_numeracao_salta_e_recusado(self):
        salta = "\f".join(["Repositório institucional\n\nUm artigo\n"] +
                          [f"{n}\t\tAna Teste\n\nTexto da seção.\n" for n in (1, 2, 3, 7, 8, 9)]) + "\f"   # a numeração pula do 3 para o 7
        f = self._fonte(salta, "manuscrito aceito, com a capa do repositório; a página 2 do PDF é a página 1, e a página 5 do PDF é a página 7")
        self.assertEqual(f.aviso, ""); self.assertEqual(fichar.indice_de_pagina(7, f, 8), 4)   # --pagina 7 abre a 5ª página do PDF
        with self.assertRaises(SystemExit) as recusa:   # até aqui abria em silêncio a posição 4, que traz o 3 impresso
            fichar.indice_de_pagina(4, f, 8)
        self.assertIn("p. 4", str(recusa.exception))

    def test_manuscrito_sem_numero_impresso_fica_na_posicao_e_avisa_sem_atribuir_frase_ao_registro(self):
        f = self._fonte(TXT, "manuscrito do autor, gerado de TeX, sem a paginação do periódico")   # como Laskov e col. (2005): nenhuma página traz número
        self.assertEqual(fichar.pagina_impressa(1, f), "p. 2 da cópia")   # a posição, como antes de 29/09/2026
        self.assertNotIn("diz que as páginas citadas são as impressas", f.aviso)   # a Versão da cópia deste não diz isso
        self.assertIn('"a página 2 do PDF é a página 1"', f.aviso)

    def test_mapa_e_localizar_mostram_a_segunda_correspondencia(self):
        self._fonte(TXT_REPETIDO, REPETIDO)
        d = json.loads(self._rodar("localizar", "FT-teste-2020")[0])
        self.assertEqual(d.get("correspondencias"), [[2, 1], [5, 3]])   # posição no PDF e número impresso de cada trecho
        linha = self._rodar("mapa", "FT-teste-2020")[0].splitlines()[1]   # quem abre a cópia fica sabendo que o 3 se repete
        self.assertIn("posição 5 do PDF", linha); self.assertIn("p. 3 da cópia", linha)

    def test_copia_sem_paginacao_nao_ganha_numeracao_da_copia(self):
        (self.raiz / "fontes" / "copias" / "10-1000-teste.procedencia.json").write_text(json.dumps(
            {"doi": "10.1000/teste", "arquivo": "teste.xml", "texto": "teste.txt", "formato": "xml"}), encoding="utf-8")
        f = self._fonte(TXT_JATS, ANTECIPADO)   # o XML não tem página, diga a Versão da cópia o que disser
        self.assertEqual(fichar.pagina_impressa(0, f), "sem paginação"); self.assertEqual(f.aviso, "")

    def test_mapa_e_localizar_dizem_onde_a_numeracao_da_copia_comeca(self):
        self._fonte(TXT_REIMPRESSAO, REIMPRESSAO)
        d = json.loads(self._rodar("localizar", "FT-teste-2020")[0])
        self.assertEqual(d.get("paginas_da_copia"), [35, 38]); self.assertEqual(d["deslocamento"], 1)
        linhas = self._rodar("mapa", "FT-teste-2020")[0].splitlines()
        self.assertIn("a p. 35 da cópia é a 2ª delas", linhas[1]); self.assertIn("'do PDF'", linhas[1])
        self.assertIn("  p. 36 da cópia  L3     METHOD", linhas)

    def test_mapa_conta_as_paginas_do_pdf(self):
        self._fonte(TXT_REIMPRESSAO, REIMPRESSAO)   # o pdftotext fecha toda página com form feed, até a última
        linha = self._rodar("mapa", "FT-teste-2020")[0].splitlines()[1]
        self.assertTrue(linha.startswith("5 páginas no PDF;"), linha)   # e não 6, que conta o vazio depois do último form feed

    def test_janela_por_pagina_diz_a_posicao_no_pdf(self):
        self._fonte(TXT_REIMPRESSAO, REIMPRESSAO)
        saida = self._rodar("janela", "FT-teste-2020", "--pagina", "37")[0]
        self.assertTrue(saida.startswith("[p. 37 da cópia; posição 4 no PDF]\n"), saida)   # e não "índice 4 na cópia", outro número da cópia

    def test_janela_por_pagina_recusa_a_pagina_depois_da_ultima(self):
        with self.assertRaises(SystemExit) as recusa:   # cinco páginas; o form feed da última não abre uma sexta
            fichar.janela_pagina(TXT_REIMPRESSAO, 5)
        self.assertIn("o PDF tem 5 páginas", str(recusa.exception))
