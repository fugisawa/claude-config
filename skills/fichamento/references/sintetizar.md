# Modo sintetizar: o que várias leituras, juntas, dizem ao argumento

O único modo que não abre fonte: lê os blocos já gravados nas seções `## Do modelo` e `## Do
autor` de várias notas e os confronta com o argumento. Serve para o autor escrever uma seção
com o que tem, e para ver o que falta. Ele não escreve a seção.

## Passos

1. **Declare o recorte**: as notas (uma lista de FT), ou um estágio do desenho, ou uma seção
   do argumento; e o alvo, que é sempre uma parte de `docs/argumento.md`.
2. **Leia só as notas**, nunca as fontes. O que não estiver numa nota não entra na síntese;
   se faltar, a síntese diz que falta e propõe o modo (`responder` ou `verificar`) que o
   traria. Blocos do autor têm precedência sobre blocos do modelo quando divergem. A parte
   gerada da nota (as AF do registro) conta como leitura, e se cita como "AF-NNN do registro";
   fonte que nunca passou por modo nenhum entra só por essas AF, e a síntese diz isso.
3. **Organize por afirmação do alvo**, e não por fonte: para cada afirmação, o que sustenta
   (fonte, página, veredito ou rótulo do bloco de origem), o que contradiz, o que restringe, e
   a lacuna.
4. **Diga a força**, com a escala do registro: quantas fontes lidas no texto completo
   sustentam, quantas restringem, quantas contradizem; o que está só em bloco `explorar`
   (candidato) e ainda não foi verificado.
5. **Feche com o que falta**: as afirmações do alvo sem fonte nas notas, e as perguntas ao
   autor.

## Modelo do bloco

Grava-se na nota de síntese `docs/leituras/sintese-<recorte>.md`, criada por este modo com as duas
marcas (`fichar.py gravar sintese-<recorte> sintetizar <bloco>` procura exatamente esse nome).
Títulos de linha da tabela do argumento e nomes de seção vão em itálico, não entre aspas: o
validador lê aspas duplas como citação de fonte, que exige página ou seção.

```markdown
**Recorte.** <notas | estágio | seção> · **Alvo.** <parte do argumento>

**Por afirmação do alvo.**

*<afirmação 1>*
- sustenta: FT-x (p. N, veredito do bloco `verificar` de AAAA-MM-DD); FT-y (p. M, rótulo `sustenta`)
- restringe: FT-z (p. K) — <em quê>
- contradiz: <FT (p.)> ou "nenhuma nas notas lidas"
- candidato não verificado: FT-w (bloco `explorar`, p. J)
- lacuna: <o que a afirmação pede e nenhuma nota traz>

*<afirmação 2>* …

**Força, em números:** <n> fontes lidas sustentam · <n> restringem · <n> contradizem · <n> só candidatas

**O que falta ler ou verificar:** <lista com o modo sugerido>

**Perguntas ao autor:**
1. <…>
2. <…>
```

A nota de síntese segue o mesmo contrato das outras: o bloco vai para `## Do modelo`, e a
seção `## Do autor` é dele. Como `fichar.py gravar` exige a nota com a seção do autor, crie a
nota de síntese com as duas marcas antes de gravar.
