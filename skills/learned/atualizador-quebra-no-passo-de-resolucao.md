---
name: atualizador-quebra-no-passo-de-resolucao
description: Toda ferramenta de "baixar a última versão e instalar" tem um passo de RESOLUÇÃO que depende de superfície de terceiro — o HTML de uma página, o redirecionamento de uma API — e é nele que ela quebra calada; de onde o operador olha, a falha é indistinguível de "já está em dia", e o diagnóstico barato é rodar a resolução SOZINHA, que costuma ser read-only e ter comando próprio
metadata:
  pattern: error_resolution
  origin: sessão 05/09/2026 — Antigravity e Cursor, dois produtos independentes, quebrados no mesmo passo no mesmo dia
  confidence: alta (dois casos medidos; o IDE ficou três meses e quatro versões atrasado enquanto avisava todo dia)
---

**O padrão.** Instalar "a última versão" é uma cadeia de quatro passos — resolver a origem,
baixar, instalar, conferir — e o primeiro é o único que depende de uma superfície que você
não controla. Página oficial, endpoint de API, layout de um pacote JavaScript: qualquer um
muda sem aviso, e quando muda o atualizador não instala nada. O que o operador vê não é um
erro; é o app continuar pedindo atualização depois de ele ter "atualizado".

## Dois produtos, o mesmo passo, o mesmo dia

| Ferramenta | O que ela resolvia | Como quebrou |
|---|---|---|
| instalador do Antigravity | raspava um pacote `main-*.js` da página oficial atrás das URLs dos tarballs | a página virou build Astro e não publica mais esse pacote — as URLs passaram para o próprio HTML |
| wrapper do Cursor | `curl -s` na API de download, e `jq` no corpo | a API responde 3xx; **sem `-L`** o corpo é o literal `Redirecting...`, 15 bytes, que o `jq` não lê |

Os dois **existiam, rodavam e imprimiam**. Nenhum instalava. O Antigravity IDE ficou três
meses e quatro versões para trás; o marcador do Cursor está parado em `0.49.6` desde
maio/2025, com um binário `3.19.x` no disco, o que data quando o caminho de atualização
morreu.

## O que custou, e o que denunciou

O sintoma foi lido ao contrário durante meses. O app avisava "update available" todo dia, e o
aviso **estava certo** — quem estava errado era o atualizador. No Linux esse aviso é só aviso:
o botão abre a página de download e nunca troca arquivo em `/opt`. Um detector correto rodando
de graça, todo dia, foi tratado como ruído porque a ação seguinte a ele não funcionava.

## O gatilho

Diante de "eu atualizo e ele continua pedindo atualização", não comece pelo app nem pelo
aviso. **Rode o passo de resolução sozinho** — ele quase sempre tem comando próprio, é
read-only e custa segundos:

- `--print-downloads`, `--dry-run`, `--check-only` no instalador;
- o `curl` cru no endpoint que o script consulta, comparado com o que o script recebe.

Se a resolução devolve vazio ou erro, achou. Se devolve certo, o defeito está adiante.

## E a conferência que faltava nos dois

Compare a versão **medida no artefato** contra a publicada, e meça **de novo** depois de
instalar. Marcador não serve de fonte: o `.antigravity-linux-version` declarava `2.1.4`
enquanto o disco tinha outro produto, compilado quatro meses antes — e o instalador, que
comparava marcador contra origem, via igualdade e pulava a instalação achando-se em dia.

Onde a versão real mora costuma ser um arquivo interno: `package.json` dentro do `app.asar`
de um Electron, `product.json` de um fork do VS Code, `package.json` extraído de dentro do
AppImage. Ler qualquer um deles custa milissegundos.

**Parentesco.** Este é o caso particular de
[[o-medidor-olha-o-lugar-errado]] em que o proxy conveniente é o arquivo de marcador, e de
[[comando-verde-que-fez-menos-do-que-anuncia]] em que o comando nem verde estava — ele
imprimia o erro, e ninguém lia a saída de um comando que "já se sabia" o que fazia.
