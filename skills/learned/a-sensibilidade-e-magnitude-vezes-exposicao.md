---
name: a-sensibilidade-e-magnitude-vezes-exposicao
description: Num modelo por trechos, a sensibilidade de um parâmetro não é o tamanho do ajuste e sim o tamanho vezes o número de períodos em que ele incide — raciocinar pelo valor em vez de pela integral aponta a alavanca errada, e a única defesa é variar um parâmetro por vez no modelo real em vez de estimar
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, 31/08/2026 — recomendação de planejamento com um número errado por 2,6× e uma inferência de alavanca invertida
  confidence: alta (medido rodando o próprio módulo do projeto, com os dois parâmetros variados isoladamente)
---

**O padrão.** Num cronograma, orçamento ou curva por trechos, cada parâmetro governa **um
trecho**, e o efeito dele no total é o valor **vezes a extensão do trecho**. Quem olha só o
valor conclui que o parâmetro maior é a alavanca maior, e isso é falso sempre que os trechos
tiverem tamanhos diferentes.

**O caso.** Uma curva de horas de estudo por semana: piso de 22 h por **4 semanas**, rampa de
8, platô de 35 h daí em diante — o platô cobrindo **treze semanas ou mais** do horizonte.
Variando um de cada vez sobre as mesmas 719 horas de conteúdo:

| mexer no **platô** (35) | semanas | mexer no **piso** (22) | semanas |
|---|---:|---|---:|
| 35 | 25 | 22 | 25 |
| 31 | 27 | 20 | 25 |
| 28 | 28 | 18 | 26 |
| 25 | 30 | 16 | 26 |

Baixar o platô em 10 custa **5 semanas**; baixar o piso em 6 custa **1**. A razão é aritmética
e não tem mistério depois de dita: 6 h × 4 semanas = 24 h, e 7 h × 13 semanas passa de 90.
**É exposição, não tamanho.**

**Os dois erros que isso produziu, e eles são de sinais opostos.**

A sessão parceira estimou que baixar o platô consumiria **7 semanas de folga**, "e é honesto
que consuma". Ela pegou a diferença entre as 26 semanas de conteúdo e as 33 do horizonte,
chamou de margem e supôs proporcionalidade ao patamar. O valor real era **3** — errado por
2,6× —, e a diferença muda o tom da recomendação: pagar três semanas por honestidade
metodológica se defende sozinho, pagar sete exige argumento.

Depois, corrigida, ela inferiu a regra oposta e igualmente falsa: *"mexer no piso seria a
alavanca forte"*. A minha própria observação a induziu — eu tinha escrito que o platô "morde
só a cauda", querendo dizer que a alavanca é **menor do que o número do patamar sugere**, e ela
leu como "o platô é fraco". Os dados desfazem as duas.

**O procedimento, e ele custa um laço.** Não estime sensibilidade: **varie um parâmetro por
vez no modelo real** e leia o resultado. No caso foram dez linhas chamando a própria função da
curva do projeto. Estimativa de sensibilidade em modelo por trechos é onde a intuição erra com
mais confiança, porque a aritmética é simples o bastante para dar a impressão de que se pode
fazê-la de cabeça.

**O corolário que sobrevive ao caso.** Antes de discutir qual botão girar, pergunte **por
quantos períodos cada botão vale**. Num modelo com piso curto e platô longo, quase toda a massa
está no platô, e uma discussão sobre o piso é uma discussão sobre a margem de erro.

Isto é primo de [[o-medidor-olha-o-lugar-errado]] pelo lado do diagnóstico — lá o instrumento
mede a coisa errada, aqui o raciocínio pesa a coisa errada —, e o remédio é o mesmo: trocar a
inferência por uma medição barata que já estava disponível.
