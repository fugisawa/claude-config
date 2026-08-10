"""Testes do doctor_ambiente — seam: scan(texto_da_declaracao, probe) -> Report.

O probe é INJETADO. Um doctor que medisse a máquina de dentro do teste só
passaria na máquina em que foi escrito — que é exatamente o defeito que ele
existe para pegar.

Valores esperados escritos à mão, nunca recalculados pela lógica sob teste.
"""
import unittest

from doctor_ambiente import Severity, _dono, scan

# Declaração de duas máquinas: uma medida, uma pendente. É a forma real do
# arquivo docs/ambiente-por-maquina.md.
DECL = """
# Ambiente por máquina

Prosa que o parser deve ignorar por completo.

## Máquina A — trabalho

```decl
machine-id: 19aeb4de
rotulo: trabalho · Dell OptiPlex 7070
medido-em: 2026-08-10
node-interativo: nvm v24
node-nao-interativo: brew v26
node-apt: apt v20
presentes: bat, fd, rg, nvm, uv, bun
ausentes: batcat, conda, magick
```

## Máquina B — casa

```decl
machine-id: pendente
rotulo: casa
```
"""

PROBE_A = {
    "machine_id": "19aeb4de",
    "node": {
        "interativo": ("nvm", 24),
        "nao-interativo": ("brew", 26),
        "apt": ("apt", 20),
    },
    "comandos": {
        "bat": True, "fd": True, "rg": True, "nvm": True, "uv": True, "bun": True,
        "batcat": False, "conda": False, "magick": False,
    },
}


def probe_com(**mudancas):
    """PROBE_A com alterações pontuais — sem mutar o original."""
    novo = {**PROBE_A, "node": dict(PROBE_A["node"]), "comandos": dict(PROBE_A["comandos"])}
    for chave, valor in mudancas.items():
        if chave in ("node", "comandos"):
            novo[chave] = {**novo[chave], **valor}
        else:
            novo[chave] = valor
    return novo


class ScanTest(unittest.TestCase):
    def codes(self, report, severity):
        return sorted(f.code for f in report.findings if f.severity is severity)

    def test_declaracao_que_bate_nao_tem_erro(self):
        report = scan(DECL, PROBE_A)
        self.assertEqual(self.codes(report, Severity.ERROR), [])
        self.assertTrue(report.ok)
        self.assertEqual(report.item_count, 2)

    def test_maquina_nao_declarada_e_erro(self):
        # Clone numa máquina nova: rodar sem declaração é o caso que o CLAUDE.md
        # antigo tratava como "esta máquina" e nunca detectava.
        report = scan(DECL, probe_com(machine_id="ffffffff"))
        self.assertEqual(self.codes(report, Severity.ERROR), ["maquina-nao-declarada"])
        self.assertFalse(report.ok)

    def test_comando_que_apareceu_e_divergencia(self):
        # O defeito real de 10/08: a declaração dizia que batcat não existe.
        report = scan(DECL, probe_com(comandos={"batcat": True}))
        self.assertEqual(self.codes(report, Severity.ERROR), ["fato-divergente"])
        detalhe = next(f.detail for f in report.findings if f.code == "fato-divergente")
        self.assertIn("batcat", detalhe)

    def test_comando_que_sumiu_e_divergencia(self):
        report = scan(DECL, probe_com(comandos={"nvm": False}))
        self.assertEqual(self.codes(report, Severity.ERROR), ["fato-divergente"])
        detalhe = next(f.detail for f in report.findings if f.code == "fato-divergente")
        self.assertIn("nvm", detalhe)

    def test_troca_de_major_do_node_e_divergencia(self):
        report = scan(DECL, probe_com(node={"interativo": ("nvm", 26)}))
        self.assertEqual(self.codes(report, Severity.ERROR), ["fato-divergente"])

    def test_troca_de_dono_do_node_e_divergencia(self):
        # Mesmo major, outro provedor: muda qual binário responde.
        report = scan(DECL, probe_com(node={"interativo": ("brew", 24)}))
        self.assertEqual(self.codes(report, Severity.ERROR), ["fato-divergente"])

    def test_patch_diferente_NAO_e_divergencia(self):
        # A decisão central do desenho: declarar comportamento, não leitura.
        # v24.18.0 → v24.19.1 não muda nada para quem lê a instrução, e
        # reprovar isso faria o gancho apanhar --no-verify em uma semana.
        report = scan(DECL, PROBE_A)
        self.assertTrue(report.ok)
        self.assertEqual(self.codes(report, Severity.ERROR), [])

    def test_secao_pendente_avisa_mas_nao_reprova(self):
        report = scan(DECL, PROBE_A)
        self.assertEqual(self.codes(report, Severity.WARN), ["secao-pendente"])
        self.assertTrue(report.ok, "pendência da outra máquina não pode travar esta")

    def test_machine_id_duplicado_e_erro(self):
        duplicada = DECL + "\n```decl\nmachine-id: 19aeb4de\nrotulo: copia\n```\n"
        report = scan(duplicada, PROBE_A)
        self.assertIn("declaracao-duplicada", self.codes(report, Severity.ERROR))

    def test_prosa_fora_do_bloco_e_ignorada(self):
        ruido = DECL.replace("Prosa que o parser deve ignorar por completo.",
                             "machine-id: 00000000\npresentes: coisa-que-nao-existe")
        report = scan(ruido, PROBE_A)
        self.assertEqual(report.item_count, 2)
        self.assertEqual(self.codes(report, Severity.ERROR), [])


class DonoTest(unittest.TestCase):
    """Caminhos reais desta máquina, colados à mão do `readlink -f`."""

    def test_nvm(self):
        self.assertEqual(_dono("/home/fugisawa/.nvm/versions/node/v24.18.0/bin/node"), "nvm")

    def test_linuxbrew(self):
        self.assertEqual(_dono("/home/linuxbrew/.linuxbrew/bin/node"), "brew")

    def test_apt(self):
        self.assertEqual(_dono("/usr/bin/node"), "apt")

    def test_desconhecido_nao_vira_apt_por_engano(self):
        # "outro" precisa existir: classificar errado é pior que não classificar,
        # porque a divergência sairia como fato e não como dúvida.
        self.assertEqual(_dono("/opt/algum/node"), "outro")

    def test_nome_pelado_nao_e_classificado(self):
        # O sintoma de 10/08: nvm preguiçoso devolve "node" pelado antes da
        # primeira chamada. Isso não pode virar um dono plausível.
        self.assertEqual(_dono("node"), "outro")


if __name__ == "__main__":
    unittest.main()
