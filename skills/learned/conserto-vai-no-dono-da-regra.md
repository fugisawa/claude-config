---
name: conserto-vai-no-dono-da-regra
description: Quando um valor derivado diverge do disco, a primeira pergunta é se o DERIVADOR sabe derivar aquilo — não se alguém o contornou; consertar o arquivo que doeu deixa o derivador incompleto e o defeito volta no próximo caso que ele não cobre
metadata:
  pattern: error_resolution
  origin: manual_estudo, 19/08/2026 — três ocorrências no mesmo dia
  confidence: alta (uma delas tinha diagnóstico pronto e errado: "alguém digitou o destino à mão")
---

**O padrão.** Um valor que deveria ser derivado aparece divergindo do disco. A reação
natural é corrigir o valor. A reação certa é perguntar **se o derivador sabe derivar aquele
caso** — porque, se não souber, corrigir o valor conserta uma ocorrência e deixa a fábrica
produzindo as próximas.

**Custo medido, três ocorrências num dia:**

- uma guarda de contagem de páginas estava **cega para duas disciplinas inteiras**, e o que
  se ia fazer era acertar os números à mão;
- a lista de conectivos de um derivador de caminhos não tinha os plurais (`nas`, `nos`), de
  modo que certos nomes saíam errados — e o sintoma parecia digitação;
- uma sessão diagnosticou *"alguém digitou o destino à mão"* quando **o derivador é que
  estava incompleto**. O diagnóstico era coerente, específico e falso.

## O gatilho

Sempre que aparecer divergência entre um valor e a fonte dele, e a palavra "alguém"
entrar no diagnóstico. *"Alguém digitou"*, *"alguém esqueceu"*, *"alguém contornou"* são
hipóteses sobre pessoas — e a hipótese sobre a **ferramenta** é mais barata de testar:
rode o derivador sobre o caso e veja o que ele devolve.

## O remédio

1. **Rode o derivador sobre o caso divergente**, isolado. Se ele devolve o valor certo, aí
   sim alguém contornou. Se devolve o errado, o conserto é dele.
2. **Meça o alcance antes de consertar.** Um derivador incompleto costuma estar incompleto
   para uma classe, e não para um caso — foi assim que "duas disciplinas cegas" apareceu.
3. **Conserte o derivador e regenere**, em vez de corrigir a saída. Saída corrigida à mão é
   a segunda cópia da regra, e ela diverge calada na próxima rodada.

## O que isto NÃO é

Não é [[a-segunda-copia-da-regra-diverge-calada]], que é sobre **não escrever** a cópia — a
divergência já existe quando esta lição dispara. E não é
[[measurement-broke-not-the-code]], que dispara quando uma métrica despenca depois de mudar
a representação; ali o código está certo e o medidor mudou de unidade. Aqui o derivador
está **incompleto**, e o valor errado é a consequência correta de uma regra que não cobre o
caso.

Relacionado: [[a-segunda-copia-da-regra-diverge-calada]] · [[measurement-broke-not-the-code]] ·
[[guarda-nao-pode-derivar-do-guardado]] · [[comando-verde-que-fez-menos-do-que-anuncia]]
