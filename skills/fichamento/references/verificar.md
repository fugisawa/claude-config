# Modo verificar: provar, desprovar ou descartar uma alegação nesta fonte

O modo meticuloso. Uma alegação, como o manuscrito ou o argumento a escreve, e uma fonte que
supostamente a sustenta. Sai um veredito em graus, a evidência a favor e contra com página, a
gravidade de qualquer erro de citação, o nível em que a checagem parou, e a proposta de AF que o
autor pode colar no registro. É o único modo que produz algo destinado ao registro, e ainda
assim como proposta.

## Passos

1. **Escreva a alegação como está** (no manuscrito, no argumento ou no acervo) e, abaixo, a
   **versão mais forte** dela, a que os autores da fonte assinariam. Testa-se a forte, não o
   espantalho. Postura: caridosa, mas não crédula.
2. **Classifique a fonte e escolha a lista.** O critério é "a alegação é sustentada pela
   evidência adequada ao tipo", e não "há tabela".

   | Tipo de fonte | Lista de apreciação | O que se procura |
   |---|---|---|
   | experimento com sorteio | RoB 2: sorteio, desvio do protocolo, dado ausente, medida do desfecho, seleção do resultado relatado | o efeito, o intervalo, o `p`, o `k`, o modelo |
   | observacional ou quase-experimento | ROBINS-I: confusão, seleção, classificação, desvio, dado ausente, medida, seleção do relatado | o que controla o que; a direção plausível do viés |
   | revisão sistemática ou meta-análise | PRISMA como lista de relato: busca, critérios, `k`, heterogeneidade, viés de publicação | o número agregado com o `k` e o intervalo; a errata |
   | levantamento por questionário | STROBE como lista de relato: amostra, taxa de resposta, instrumento | o `N`, quem respondeu, o que foi medido e não só relatado |
   | ensaio, texto normativo, relatório oficial | Toulmin (alegação, dado, garantia, apoio, ressalva) + questões críticas de Walton para o esquema usado (autoridade, analogia, causa, sinal, abdução) | se o dado existe, se a garantia é dita, se a ressalva é reconhecida |
   | qualquer tipo, alegação causal | severidade (Mayo): que erro o desenho detectaria, e se o detectaria caso a alegação fosse falsa; melhor explicação (Lipton): a escolhida é a mais provável entre as rivais examinadas? | as rivais que a fonte examina e as que ignora |

3. **Procure a evidência a favor**, por página, nas seções que o tipo indica. Anote os
   companheiros do número: modelo, `k` ou `N`, intervalo, `p`, condição.
4. **Procure a evidência contra**, com o mesmo esforço: a ressalva dos autores, a condição em
   que o efeito some, a tabela que diverge do texto, o resultado secundário que contradiz. Um
   bloco sem nenhuma linha "contra" ou "ressalva" é suspeito de leitura seletiva. Evidência de
   fora da fonte (outro estudo que contradiz) entra só como pista, marcada ⚑ e sem ser aberta;
   abri-la é outra corrida da `artigos-cientificos` e outro fichamento.
5. **Se a alegação cita outra fonte por dentro desta** (citação de citação), declare o
   **nível em que a checagem parou**:
   - `E`, existência: a fonte citada existe e o DOI resolve (`artigo.py resolver`);
   - `S`, superfície: título, autores e ano batem com o que a fonte que cita diz;
   - `I`, integridade: a fonte citada trata do assunto pelo qual foi citada;
   - `G`, granular: a fonte citada diz, com o número e o sentido, o que a citação lhe atribui.
   Só `G` autoriza o manuscrito a repetir a citação. As divergências achadas no projeto de
   origem eram todas do nível `G`: fonte real, número errado. Abrir a citada é outra corrida da
   `artigos-cientificos`; este modo declara até onde foi.
6. **Rotule a gravidade** de qualquer erro de citação encontrado entre a alegação e a fonte:
   `maior` (a fonte não sustenta, é irrelevante ou contradiz) ou `menor` (imprecisão sem
   contradição: número arredondado, condição omitida). Nunca "certo/errado".
7. **Dê o veredito em cinco graus**, e diga o que mudaria:
   `sustentada` · `sustentada com ressalva` (a fonte sustenta uma forma mais estreita, e o bloco
   diz qual) · `indeterminada` (a fonte não decide) · `enfraquecida` (a fonte pesa contra sem
   refutar) · `refutada`. Passe a própria refutação pelo mesmo teste: se você diz que a fonte
   contradiz, cite a página em que contradiz.
8. **Escreva a proposta de AF** no formato exato do registro do projeto (abaixo), com o destino
   sugerido (`usar`, `restringir`, `cortar`) e a razão quando for `restringir` ou `cortar`. A
   afirmação da AF é a que a fonte sustenta, não a que o autor queria.
9. **Valide, resolva os DOIs mencionados, grave.** Os sete vetores de ataque que o registro do
   projeto usa como lembrete: número trocado, atribuição trocada, resumo contra corpo, texto
   contra tabela, condição omitida, versão errada da fonte, citação de segunda mão.

## Modelo do bloco

Aspas duplas no bloco são lidas pelo validador como citação literal, que exige página ou seção; nas
linhas de alegação, de versão mais forte e de razão, escreva sem aspas ou em itálico.

```markdown
**Alegação, como está.** <literal>
**Versão mais forte.** <a que os autores assinariam>

**Tipo de fonte e lista usada.** <tipo> · <lista>

**A favor.**
- <evidência com companheiros do número> (p. N)

**Contra ou ressalva.**
- <evidência, ressalva dos autores, condição em que some> (p. N)

**Citação de citação.** <se houver: fonte citada, DOI, e> **Nível da checagem:** E | S | I | G

**Erro de citação.** nenhum | menor: <qual> | maior: <qual>

**Veredito:** sustentada | sustentada com ressalva | indeterminada | enfraquecida | refutada
**O que mudaria esta avaliação:** <o dado, a página ou a condição que a inverteria>

**Proposta de AF** (para o autor colar no registro, sob a FT):
```
#### AF-NNN
- **Afirmação:** <a que a fonte sustenta>
- **Seção do manuscrito:** <n>
- **Origem:** <análise §x; argumento §y>
- **O que a fonte diz:** "<literal>" (p. N); "<literal>" (p. M)
- **Situação:** texto completo
- **Destino:** usar | restringir | cortar
- **Razão:** <obrigatória se restringir ou cortar>
```

**Perguntas ao autor:**
1. <…>
2. <…>
```

## Fronteira com o parecerista

O agente `parecerista-2-critico` ataca o manuscrito inteiro, com as suas seções, o seu
encadeamento e o seu enquadramento. Este modo ataca **uma alegação numa fonte**. Quando o
veredito for `refutada` ou `enfraquecida` numa alegação central do argumento, o autor decide se
manda o argumento ao parecerista; este modo não o faz sozinho.
