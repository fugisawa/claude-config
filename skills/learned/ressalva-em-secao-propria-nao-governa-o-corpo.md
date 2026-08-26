---
name: ressalva-em-secao-propria-nao-governa-o-corpo
description: Colofão, seção de limitações e ressalva de método NÃO protegem o corpo — o mesmo autor escreve as duas partes em registros opostos, porque ensinar quer confiança e auditar quer cautela, e afirma no corpo mais do que admite na ressalva
metadata:
  pattern: code_review
  origin: manual_estudo, 19/08/2026 — duas ocorrências no mesmo arquivo, ambas achadas pelo revisor e nenhuma pelo autor
  confidence: alta (e testou-se que não vira verificação automática)
---

**O padrão.** Um documento declara em seção própria o que não foi conferido — colofão,
seção de limitações, nota de método. Isso parece resolver a honestidade do texto, e não
resolve: **a ressalva não governa o corpo.** O leitor lê o corpo; a ressalva ele lê depois,
se ler.

A causa não é desleixo, e é isso que torna a lição útil: **as duas seções são escritas em
registros opostos.** Ensinar quer confiança — frase afirmativa, sem hedge, porque hedge em
material didático atrapalha. Auditar quer cautela — "não foi aberto", "não se confirmou".
O mesmo autor, na mesma sessão, afirma no corpo mais do que admite na ressalva, **sem
perceber**, porque cada parte está certa dentro do próprio registro.

**Custo medido**, duas ocorrências no mesmo arquivo:

- o corpo dizia que uma objeção *"não existe"*, enquanto o colofão dizia *"busca não prova
  inexistência"*;
- o corpo autorizava citar uma controvérsia *"sem ressalva de procedência"*, enquanto o
  colofão declarava que **o livro não foi aberto**.

## O gatilho

Todo documento que tenha colofão, seção de fontes ou declaração do que não foi conferido —
quer dizer, todo artefato que se leva a sério. O risco cresce com o tamanho do intervalo
entre escrever o corpo e escrever a ressalva.

## O remédio, e ele é procedimental porque não vira verificação

**Isto foi testado e não automatiza:** exigiria casar linguagem natural com linguagem
natural, comparando o que o corpo afirma com o que a ressalva nega. O que funcionou, e foi
por acidente nas duas vezes:

> **Dê o colofão ao revisor explicitamente, como trecho a revisar** — e peça que ele o leia
> **contra o corpo**, e não isolado.

O revisor lê as duas partes sem o compromisso de ensinar, e é essa neutralidade que expõe a
divergência. Foi assim que as duas foram pegas, e nenhuma delas pelo autor.

Corolário barato: quando a ressalva disser *"não foi aberto"* ou *"não se confirmou"*,
**procure no corpo a afirmação correspondente** e veja se ela carrega a mesma dúvida. Se
não carregar, o corpo é que muda — nunca a ressalva, porque a ressalva é a que mede.

Relacionado: [[fronteira-de-arquivo-nao-cria-dono-da-coerencia]] ·
[[negative-finding-vs-broken-probe]] · [[aviso-por-item-nao-diz-ausencia-total]]
