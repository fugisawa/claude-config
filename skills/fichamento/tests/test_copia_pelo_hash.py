"""Testes do fichar.py para a cópia que o recibo não aponta (defeito de 29/09/2026).

O localizar achava a cópia só pelo DOI da referência, procurando o recibo da artigos-cientificos com o mesmo
DOI. A fonte sem DOI (o relatório de Treverton, a lei de 2004, a página da IARPA, a tese de Coulthart, o livro
de Kahneman, Sibony e Sunstein) não tem recibo, porque o `artigo.py registrar` exige um DOI, e o script
respondia "sem cópia local" com a cópia na pasta. O parágrafo Fonte: do registro guarda os 12 primeiros dígitos
do SHA-256 do arquivo baixado, e é por eles que o script acha a cópia agora.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fichar  # noqa: E402

FICHA = """# R

## Fontes

### FT-relatorio — Teste (2009)
- **Referência:** Ana Teste, 2009, *Um relatório*, Instituto de Teste, Estocolmo, 21 páginas. {identificador} (registro: página de créditos, 2026-09-26)
- **Versão da cópia:** {versao}

{fonte}

#### AF-001
- **Situação:** texto completo
"""
FONTE_COM_COPIA = ('Fonte: Teste (2009), "Um relatório", *Instituto de Teste*, ISBN 978-0-00-000000-0. Cópia obtida em '
                   'https://exemplo.org/relatorio.pdf, por repositório do instituto (rota A, licenciada), versão publicada, 4 páginas, '
                   'SHA-256 {sha}…; valores conferidos no texto em 2026-09-26.')
FONTE_SEM_COPIA = ('Fonte: Teste (2009), "Um relatório", *Instituto de Teste*, ISBN 978-0-00-000000-0. ⚑ Texto integral não obtido '
                   'por via legal em 2026-09-26: fechado no OpenAlex e no Unpaywall. Os valores citados seguem não conferidos em fonte primária.')
TXT = "Um relatório\n\nSUMMARY\n\nPuzzles have an answer in principle.\n\fMysteries are contingent.\n\fComplexities are the third class.\n\f"


def _pdf_minimo(paginas):
    """Um PDF válido com uma linha de texto em cada página, para o pdftotext ter o que extrair."""
    objetos = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % (4 + 2 * i) for i in range(len(paginas))) + b"] /Count %d >>" % len(paginas),
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, linha in enumerate(paginas):
        conteudo = b"BT /F1 12 Tf 72 720 Td (" + linha.encode("latin-1") + b") Tj ET"
        objetos.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (5 + 2 * i))
        objetos.append(b"<< /Length %d >>\nstream\n" % len(conteudo) + conteudo + b"\nendstream")
    pdf, posicoes = bytearray(b"%PDF-1.4\n"), []
    for n, objeto in enumerate(objetos, 1):
        posicoes.append(len(pdf)); pdf += b"%d 0 obj\n" % n + objeto + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1) + b"".join(b"%010d 00000 n \n" % p for p in posicoes)
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    return bytes(pdf)


class CopiaPeloHash(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        self.copias = self.raiz / "fontes" / "copias"; self.copias.mkdir(parents=True)
        self._copia("aaa-outra-fonte.pdf", b"%PDF-1.4 outra fonte")   # vem antes na ordem alfabética e não é a do registro
        self._copia("aaa-outra-fonte.txt", b"Outra fonte.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _copia(self, nome, conteudo):
        caminho = self.copias / nome; caminho.write_bytes(conteudo)
        return caminho

    def _registro(self, sha, versao="PDF da versão publicada.", doi=""):
        fonte = FONTE_SEM_COPIA if sha is None else FONTE_COM_COPIA.format(sha=sha)
        identificador = f"DOI {doi}" if doi else "ISBN 978-0-00-000000-0"   # a obra sem DOI, como a maioria dos relatórios e livros
        (self.raiz / "fontes" / "registro.md").write_text(FICHA.format(identificador=identificador, versao=versao, fonte=fonte), encoding="utf-8")

    @staticmethod
    def _sha(caminho):
        return hashlib.sha256(caminho.read_bytes()).hexdigest()[:12]   # como o registro o escreve: 12 dígitos e reticências

    def _rodar(self, *args):
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            try:
                codigo = fichar.main(["--raiz", str(self.raiz), *args])
            except SystemExit as recusa:
                codigo = recusa.code
        return codigo, saida.getvalue(), erro.getvalue()

    def test_sem_doi_acha_a_copia_pelo_sha256_do_paragrafo_fonte(self):
        pdf = self._copia("relatorio-wayback.pdf", b"%PDF-1.4 o relatorio")   # como Treverton (2009): o PDF baixado e o texto ao lado
        ao_lado = self._copia("relatorio-wayback.txt", TXT.encode())
        pagina = self._copia("pagina-do-programa.txt", b"Summary\n\nThe program ended.\n")   # como a página da IARPA: o texto é a cópia
        for baixado, texto in ((pdf, ao_lado), (pagina, pagina)):
            with self.subTest(copia=baixado.name):
                self._registro(self._sha(baixado))
                f = fichar.localizar("FT-relatorio", self.raiz)
                self.assertEqual(f.txt, texto); self.assertEqual(f.aviso, "")

    def test_comando_localizar_diz_que_arquivo_o_hash_identificou(self):
        pdf = self._copia("relatorio-wayback.pdf", b"%PDF-1.4 o relatorio")
        self._copia("relatorio-wayback.txt", TXT.encode())
        self._registro(self._sha(pdf))
        codigo, saida, _ = self._rodar("localizar", "FT-relatorio")
        d = json.loads(saida)   # sem recibo, a procedência é nula, e é a cópia que diz de onde o texto veio
        self.assertEqual(codigo, 0); self.assertIsNone(d["procedencia"])
        self.assertEqual(d.get("copia"), "fontes/copias/relatorio-wayback.pdf"); self.assertEqual(d["txt"], "fontes/copias/relatorio-wayback.txt")

    def test_hash_sem_arquivo_aqui_manda_trazer_a_copia(self):
        self._registro("0123456789ab")   # o registro guarda o hash, e a cópia ficou na outra máquina
        f = fichar.localizar("FT-relatorio", self.raiz)
        self.assertIsNone(f.txt); self.assertIn("SHA-256 0123456789ab", f.aviso); self.assertIn("traga a cópia da outra máquina", f.aviso)
        codigo, _, erro = self._rodar("localizar", "FT-relatorio")
        self.assertEqual(codigo, 2); self.assertIn("traga a cópia da outra máquina", erro)
        self.assertNotIn("abra pela skill", erro)   # uma nova abertura pode trazer outra versão da fonte

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "o root lê o arquivo sem permissão")
    def test_arquivo_ilegivel_na_pasta_nao_derruba_a_busca(self):
        self._copia("aaa-parcial.pdf", b"%PDF-1.4 sincronizando").chmod(0)   # como o arquivo que o Syncthing ainda está gravando
        pdf = self._copia("relatorio-wayback.pdf", b"%PDF-1.4 o relatorio")
        texto = self._copia("relatorio-wayback.txt", TXT.encode())
        self._registro(self._sha(pdf))
        self.assertEqual(fichar.localizar("FT-relatorio", self.raiz).txt, texto)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "o root lê o arquivo sem permissão")
    def test_hash_nao_achado_cita_o_arquivo_que_nao_se_leu(self):
        self._copia("aaa-parcial.pdf", b"%PDF-1.4 sincronizando").chmod(0)   # a cópia procurada pode ser ele
        self._registro("0123456789ab")
        self.assertIn("aaa-parcial.pdf", fichar.localizar("FT-relatorio", self.raiz).aviso)

    def test_fonte_sem_hash_continua_sem_copia_local(self):
        self._registro(None)   # como Bennett e Waltz (2007), cujo texto não se obteve: o parágrafo Fonte: não guarda hash
        self.assertIsNone(fichar.localizar("FT-relatorio", self.raiz).txt)
        codigo, _, erro = self._rodar("localizar", "FT-relatorio")
        self.assertEqual(codigo, 2); self.assertIn("sem cópia local", erro)

    @unittest.skipUnless(shutil.which("pdftotext"), "o teste precisa do pdftotext")
    def test_pdf_sem_texto_extraido_ganha_o_txt_na_primeira_vez(self):
        pdf = self._copia("livro-copia-do-autor.pdf", _pdf_minimo(["Primeira pagina do livro", "Segunda pagina do livro"]))   # como o de Kahneman, Sibony e Sunstein
        self._registro(self._sha(pdf))
        f = fichar.localizar("FT-relatorio", self.raiz)
        self.assertEqual(f.txt, self.copias / "livro-copia-do-autor.txt"); self.assertEqual(f.aviso, "")
        texto = f.txt.read_text(encoding="utf-8")
        self.assertEqual(fichar.total_de_paginas(texto), 2); self.assertIn("Segunda pagina do livro", fichar.paginas(texto)[1])

    @unittest.skipUnless(shutil.which("pdftotext"), "o teste precisa do pdftotext")
    def test_comando_diz_quando_grava_o_texto_extraido(self):
        pdf = self._copia("livro-copia-do-autor.pdf", _pdf_minimo(["Uma pagina"]))
        self._registro(self._sha(pdf))
        _, _, erro = self._rodar("localizar", "FT-relatorio")   # quem só queria o DOI fica sabendo que um arquivo foi gravado
        self.assertIn("pdftotext -layout", erro); self.assertIn("fontes/copias/livro-copia-do-autor.txt", erro)
        _, _, erro = self._rodar("localizar", "FT-relatorio")   # na segunda vez o texto já existe, e nada se grava
        self.assertNotIn("pdftotext", erro)

    @unittest.skipUnless(shutil.which("pdftotext"), "o teste precisa do pdftotext")
    def test_copia_cujo_texto_nao_se_extrai_avisa_e_nao_deixa_txt(self):
        sem_programas = {"PATH": str(self.raiz / "pasta-sem-programas")}   # a máquina sem o poppler-utils
        casos = (("livro.pdf", b"isto nao e um PDF", {}, "o pdftotext não o extraiu"),
                 ("livro.pdf", _pdf_minimo(["Uma pagina"]), sem_programas, "o pdftotext não está instalado"),
                 ("pagina.html", b"<html><body>Summary</body></html>", {}, "só extrai o texto de PDF"))
        for nome, conteudo, ambiente, motivo in casos:
            with self.subTest(motivo=motivo):
                copia = self._copia(nome, conteudo); self._registro(self._sha(copia))
                with mock.patch.dict(os.environ, ambiente):
                    f = fichar.localizar("FT-relatorio", self.raiz)
                self.assertIsNone(f.txt); self.assertIn(copia.name, f.aviso); self.assertIn(motivo, f.aviso)
                self.assertFalse(copia.with_suffix(".txt").exists())   # o .txt vazio passaria por texto nas próximas vezes
                copia.unlink()

    def test_copia_achada_pelo_hash_segue_a_declaracao_da_versao_da_copia(self):
        pdf = self._copia("relatorio-wayback.pdf", b"%PDF-1.4 o relatorio")   # como Treverton (2009): capa, créditos e o texto da p. 5 em diante
        paginas = ["Um relatório\n", "Published by: Instituto de Teste\n", "Um relatório\n\nPuzzles.\n", "Mysteries.\n", "Complexities.\n"]
        self._copia("relatorio-wayback.txt", "\f".join(paginas + [""]).encode())
        self._registro(self._sha(pdf), versao="PDF da versão publicada, com a paginação da publicação; a página 3 do PDF é a página 5")
        f = fichar.localizar("FT-relatorio", self.raiz)
        self.assertEqual([fichar.pagina_impressa(i, f) for i in range(5)],
                         ["p. 1 do PDF", "p. 2 do PDF", "p. 5 da cópia", "p. 6 da cópia", "p. 7 da cópia"])
        self.assertEqual(f.aviso, "")

    def test_pagina_copiada_pelo_navegador_fica_sem_paginacao(self):
        pagina = self._copia("pagina-do-programa.txt", b"Summary\n\nThe program ended.\n\nPrime Performers\n\nTwo teams.\n")   # como a página da IARPA
        self._registro(self._sha(pagina), versao="texto do elemento principal da página; as localizações citam o título da seção")
        self.assertEqual(fichar.pagina_impressa(0, fichar.localizar("FT-relatorio", self.raiz)), "sem paginação")

    def test_janela_corrida_sai_do_pdf_achado_pelo_hash(self):
        pdf = self._copia("relatorio-wayback.pdf", b"%PDF-1.4 o relatorio")
        self._copia("relatorio-wayback.txt", TXT.encode())
        self._copia("relatorio-wayback.corrido.txt", b"Um relatorio\n\nA coluna da direita, lida na ordem.\n\f")   # já extraído: o teste não roda o pdftotext
        self._registro(self._sha(pdf))
        codigo, saida, erro = self._rodar("janela", "FT-relatorio", "--corrido", "--termo", "coluna da direita")
        self.assertEqual(codigo, 0, erro); self.assertIn("A coluna da direita, lida na ordem.", saida)

    def test_janela_corrida_recusa_a_copia_que_ja_e_texto(self):
        pagina = self._copia("pagina-do-programa.txt", b"Summary\n\nThe program ended.\n")   # não há PDF de onde extrair o texto corrido
        self._registro(self._sha(pagina))
        codigo, _, _ = self._rodar("janela", "FT-relatorio", "--corrido", "--termo", "program")
        self.assertIn("não é PDF", str(codigo))

    def test_com_doi_vale_o_hash_quando_o_recibo_nao_da_o_texto(self):
        texto = self._copia("relatorio-editora.txt", TXT.encode())   # como Kyllonen e col. (2019), cujo texto veio da página da editora
        recibo = self.copias / "10-1000-relatorio.procedencia.json"
        for tentativa in (True, False):   # o recibo da tentativa que não abriu; nenhum recibo, como o do National Research Council (2011)
            with self.subTest(recibo="da tentativa" if tentativa else "nenhum"):
                if tentativa:
                    recibo.write_text(json.dumps({"doi": "10.1000/relatorio", "status": "nao_aberto", "arquivo": "", "texto": ""}), encoding="utf-8")
                else:
                    recibo.unlink()
                self._registro(self._sha(texto), doi="10.1000/relatorio")
                f = fichar.localizar("FT-relatorio", self.raiz)
                self.assertEqual(f.txt, texto); self.assertEqual(f.aviso, "")

    def test_texto_declarado_que_falta_nao_cede_o_lugar_ao_hash(self):
        pdf = self._copia("publicada.pdf", b"%PDF-1.4 a versao publicada")   # o PDF chegou a esta máquina, e o texto que o recibo declara não
        (self.copias / "10-1000-relatorio.procedencia.json").write_text(
            json.dumps({"doi": "10.1000/relatorio", "arquivo": "publicada.pdf", "texto": "publicada-lida.txt"}), encoding="utf-8")
        self._registro(self._sha(pdf), doi="10.1000/relatorio")
        f = fichar.localizar("FT-relatorio", self.raiz)   # como Steyvers e col. (2025): nenhum outro texto substitui o que o recibo declara
        self.assertIsNone(f.txt); self.assertIn("publicada-lida.txt", f.aviso)
        self.assertFalse((self.copias / "publicada.txt").exists())   # nem um extraído agora do PDF


# ------------------------------------------------ o DOI da referência (defeito de 29/09/2026)
# O _doi_de parava no primeiro parêntese e guardava a vírgula do fim: o DOI de Cheng e col. (1986) virava
# "10.1016/0010-0285(86", e o de Lahneman e Arcos (2014), "10.5040/9798216385714,". Com o DOI cortado, Cheng e col.
# e Fong, Krantz e Nisbett (1986) não achavam o recibo, e o script dizia "sem cópia local" com o recibo e o texto
# na pasta.

REFERENCIA = """# R

## Fontes

### FT-teste-1986 — Teste (1986)
- **Referência:** Ana Teste, 1986, "Um artigo", *Cognitive Psychology* 18(3), 293–328. DOI {doi}{depois}

Fonte: x
"""


class DoiDaReferencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.raiz = Path(self.tmp.name).resolve()
        self.copias = self.raiz / "fontes" / "copias"; self.copias.mkdir(parents=True)
        (self.copias / "artigo.txt").write_text(TXT, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_doi_com_parentese_ou_pontuacao_no_fim_acha_o_recibo(self):
        casos = (("10.1016/0010-0285(86)90002-2", " (registro: Crossref, 2026-09-28)"),   # como Cheng e col. (1986)
                 ("10.5040/9798216385714", ", ISBN 9781442228979 (registro: Crossref, 2026-09-28)"),   # como Lahneman e Arcos (2014)
                 ("10.4324/9780203797327", "; capítulo 3 (registro: Crossref, 2026-09-28)"))
        for doi, depois in casos:
            with self.subTest(doi=doi):
                (self.raiz / "fontes" / "registro.md").write_text(REFERENCIA.format(doi=doi, depois=depois), encoding="utf-8")
                (self.copias / "artigo.procedencia.json").write_text(
                    json.dumps({"doi": doi, "arquivo": "artigo.pdf", "texto": "artigo.txt"}), encoding="utf-8")
                f = fichar.localizar("FT-teste-1986", self.raiz)
                self.assertEqual(f.doi, doi); self.assertEqual(f.txt, self.copias / "artigo.txt")


if __name__ == "__main__":
    unittest.main()
