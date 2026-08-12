"""Testes do doctor_rules — seam: scan(declaradas, locais, plugins, ligados) -> erros.

As quatro listas são INJETADAS. Este doctor guarda uma divergência que é real
entre as duas máquinas (o plugin ECC existe em casa e não no trabalho, medido em
11/08/2026); um teste que lesse o disco passaria de um lado e reprovaria do
outro, exatamente o defeito que ele existe para pegar.

Valores esperados escritos à mão, nunca recalculados pela lógica sob teste.
"""
import unittest

from doctor_rules import scan

ECC = "everything-claude-code@everything-claude-code"

# Estado saudável: um agente local, um servido pelo plugin, plugin ligado.
LOCAIS = {"code-reviewer"}
PLUGINS = {"planner": ECC, "tdd-guide": ECC}
LIGADOS = {ECC: True}


class TestCoerente(unittest.TestCase):
    def test_tabela_que_bate_com_o_disco_nao_acusa_nada(self):
        erros = scan([("code-reviewer", "local"), ("planner", "ecc")], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(erros, [])


class TestProvedorErrado(unittest.TestCase):
    def test_declarar_local_o_que_vem_do_plugin(self):
        erros = scan([("planner", "local")], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(len(erros), 1)
        self.assertIn("declarado `local`", erros[0])
        self.assertIn(ECC, erros[0])

    def test_declarar_plugin_o_que_e_local(self):
        erros = scan([("code-reviewer", "ecc")], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(len(erros), 1)
        self.assertIn("não está instalado", erros[0])

    def test_apelido_de_provedor_desconhecido(self):
        erros = scan([("planner", "marketplace-inventado")], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(len(erros), 1)
        self.assertIn("desconhecido", erros[0])


class TestAgenteAusente(unittest.TestCase):
    def test_agente_que_nao_existe_em_lugar_nenhum(self):
        erros = scan([("fantasma", "local")], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(len(erros), 1)
        self.assertIn("não existe em lugar nenhum", erros[0])

    def test_plugin_ausente_nesta_maquina_pede_decisao_e_nao_silencio(self):
        """O caso do trabalho: o plugin simplesmente não está no disco."""
        erros = scan([("planner", "ecc")], LOCAIS, {}, {})
        self.assertEqual(len(erros), 1)
        self.assertIn("NESTA máquina", erros[0])


class TestPluginDesligado(unittest.TestCase):
    def test_instalado_porem_false(self):
        erros = scan([("planner", "ecc")], LOCAIS, PLUGINS, {ECC: False})
        self.assertEqual(len(erros), 1)
        self.assertIn("NÃO habilitado", erros[0])

    def test_instalado_porem_sem_entrada_e_o_defeito_de_11_08_2026(self):
        """`ecc@ecc` substituiu o id real, e o plugin ficou sem entrada nenhuma."""
        erros = scan([("planner", "ecc")], LOCAIS, PLUGINS, {"ecc@ecc": False})
        self.assertEqual(len(erros), 1)
        self.assertIn("sem entrada em enabledPlugins", erros[0])


class TestTabelaSumida(unittest.TestCase):
    def test_sem_coluna_provider_reprova_em_vez_de_passar_vazio(self):
        """Guarda da guarda: tabela ilegível não pode virar 'zero problemas'."""
        erros = scan([], LOCAIS, PLUGINS, LIGADOS)
        self.assertEqual(len(erros), 1)
        self.assertIn("passaria em silêncio", erros[0])


class TestVariosDeUmaVez(unittest.TestCase):
    def test_cada_linha_rende_seu_proprio_erro(self):
        erros = scan(
            [("code-reviewer", "local"), ("planner", "local"), ("fantasma", "local")],
            LOCAIS,
            PLUGINS,
            LIGADOS,
        )
        self.assertEqual(len(erros), 2)


if __name__ == "__main__":
    unittest.main()
