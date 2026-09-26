---
name: verificacao-cara-nao-descobre-um-defeito-por-vez
description: Quando a verificação custa minutos, usá-la para descobrir o que falta paga o custo inteiro por defeito encontrado — o gancho responde "posso publicar?" e não "o que está inconsistente?", então antes da segunda tentativa rode todas as guardas baratas de uma vez e feche a cascata de derivados até o ponto fixo; e enquanto um gancho roda não se cria vigia, não se edita a árvore que ele mede e não se lança outro gancho no mesmo clone
metadata:
  pattern: error_resolution
  origin: manual_estudo, 08/09/2026 — segundo episódio; o primeiro, de 26/08/2026 (21 reprovações seguidas), está registrado em estudo/tests/varredura.py e foi lido 41 minutos depois da primeira reprovação
  confidence: alta (dois episódios medidos no mesmo projeto, 21 e 5 reprovações; no segundo, 42 minutos de gancho reprovado em 74 minutos de sessão, e nada publicado)
---

**Estende [[conserto-vai-no-dono-da-regra]] e [[predicado-de-estado-alheio-precisa-de-observavel]], e corrige um conselho de [[arvore-suja-pode-nao-ser-sua]].** Aquela manda, diante de suíte vermelha, *"rode de novo em vez de editar"*. Isso é barato quando a rodada custa segundos. Quando ela custa 391 s, rodar de novo é o defeito.

**O padrão.** Uma verificação tem dois usos, e eles pedem instrumentos opostos. O primeiro é decidir se algo pode ser publicado: para isso ela é binária, roda uma vez por publicação e pode custar o que custar. O segundo é descobrir o que ainda está errado: para isso ela é o pior instrumento possível quando é cara, porque devolve **um** defeito por rodada e cobra a rodada inteira por cada um. O erro é usar o gancho do primeiro tipo como se fosse do segundo. Uma alteração de uma linha num JSON de parâmetros move uma cascata — três Markdown gerados, um HTML que os embute, quatro PDFs que saem dele, e um `--verify` de ritmo que, aplicado, reabre a cascata desde o começo. Cada reprovação do gancho ensinou um elo, e a cascata tinha cinco.

**O episódio de 08/09/2026, medido no transcript.**

1. Cinco reprovações completas de gancho, 677 + 392 + 391 + 381 + 686 s = 42 minutos, cada uma revelando o elo seguinte: a procedência que não nomeava o lote; três derivados e o HTML; os três derivados de novo, porque só o HTML tinha sido regenerado; o ritmo que pedia `--aplicar`; e um teste da própria sessão. O laço que roda as dezesseis guardas do pre-commit sem a suíte custa 2m57 e só foi executado 42 minutos depois da primeira reprovação, logo após a primeira bronca.
2. Dezessete laços `until … sleep` para vigiar oito comandos, dezesseis em segundo plano; cinco ficaram órfãos por 32 a 59 minutos, dois deles com o alvo morto havia 55 minutos, e somaram 219 minutos-processo competindo por CPU com o gancho que vigiavam. Dois eram imortais por construção: `pgrep -f 'git commit'` casa o próprio script que pergunta — às 02:23:42 ele disse "git ainda rodando" quatro segundos depois de o commit ter terminado.
3. Dois commits lançados em paralelo, duas vezes, no mesmo clone que outra sessão já ocupava: `index.lock` fatal, e o commit sobrevivente saiu com a lista de arquivos incompleta, o que custou mais 391 s.
4. Dois scripts encadearam commit e push sem guarda, com um `grep -iE 'reprovad|erro |FAIL'` entre o comando e a decisão; o filtro não casa `fatal:` nem `error:`, o HEAD não se moveu, e o script imprimiu "empurrando 9 commits". Os três scripts anteriores da mesma sessão tinham a guarda; ela caiu sob pressão.
5. Um arquivo de teste escrito na árvore enquanto o pre-push rodava a suíte nela: o gancho o descobriu na versão de catorze segundos e reprovou. Onze minutos por um arquivo que não estava no commit.
6. Três agentes lançados para implementar antes de haver medição, e os três mortos em 34 s, 10 min e 2 min — enquanto a sessão fazia à mão o que tinha pedido a eles.

**O procedimento, que começa antes da segunda tentativa.**

1. Leia o custo do gancho antes de tentar de novo — ele imprime o próprio tempo. Acima de um minuto, ele deixa de ser lugar de descobrir.
2. Rode **todas** as guardas baratas, e não as três que doeram; a lista completa mora no projeto (aqui, `ARQUITETURA.md` e o próprio `githooks/pre-commit`). Leia a primeira reprovação como amostra de uma cascata, e não como o defeito.
3. Regenere os derivados **até o ponto fixo**, porque regenerar um suja outro; aplique o que pede `--aplicar` ou decida explicitamente que não aplica. No `manual_estudo` isso é um comando, `python3 estudo/fechar.py` (08/09/2026): ele regenera e reconstrói alternando até a árvore parar de mudar de **conteúdo**, roda as dezessete guardas sem a suíte em ~70 s, e **reprova se reescreveu arquivo que já estava sujo antes** — porque arquivo sujo tem dono, e num clone com duas sessões o comando de conveniência vira a segunda escrevendo no da primeira. Onde não houver o comando, o procedimento é o mesmo à mão.
4. Só então uma tentativa — uma por clone, contando a outra sessão. Enquanto ela roda, a árvore é do gancho: nenhuma edição, nenhum segundo commit, nenhum vigia novo. A notificação de fim já existe.
5. Se um vigia for indispensável, ele mede um observável que pode tornar-se falso: PID guardado no lançamento ou `pgrep -x` do binário, nunca `pgrep -f` com o padrão dentro do próprio script.
6. Publicação encadeada segue por `&&` ou por teste de efeito (`git log -1` mudou?). Filtro de saída nunca fica entre o comando e a decisão — o que ele descarta é o motivo.
7. Abra o registro do episódio anterior e o acervo `learned/` na primeira reprovação, e não depois da cobrança: neste episódio ambos foram lidos segundos depois das broncas, e nenhum minuto antes.

**O que não se conclui daqui.** Que o gancho está errado ou que se deve pulá-lo com `--no-verify`: as cinco reprovações estavam certas sobre o disco. Nem que reduzir o custo do gancho resolve o método — o custo foi cortado na mesma noite com cache, e a lição vale igual a 30 s, porque o que muda com o custo é só o tamanho da conta, e não quem a paga.
