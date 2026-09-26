# Modo responder: o que esta fonte diz sobre esta pergunta

O modo mais curto. Uma pergunta, uma fonte, um trecho. Serve para quando o autor quer saber se
pode escrever uma frase, e não para explorar nem para julgar o método.

## Passos

1. **Reescreva a pergunta como alegação atômica.** Uma afirmação testável por vez; se a
   pergunta trouxer duas, divida e responda às duas em blocos separados. Escreva a alegação no
   topo do bloco, na forma exata em que a testou.
2. **Vá à seção provável**, não à ordem do artigo: resultados ou discussão para achado
   empírico, método para procedimento e amostra, introdução para definição, conclusão para o
   que os autores dizem ter mostrado. Use `fichar.py janela --secao` e depois `--termo` com as
   palavras da alegação e os seus sinônimos no idioma da fonte.
3. **Decida o rótulo** pelo que o trecho diz, não pelo que o resumo diz:
   - `sustenta`: a fonte afirma a alegação, com número ou frase que a contém;
   - `refuta`: a fonte afirma o contrário ou o resultado contradiz;
   - `misto`: parte a favor, parte contra, ou sustenta uma versão mais estreita;
   - `insuficiente`: a fonte toca no assunto, mas o trecho não decide;
   - `não consta`: a fonte não trata disso. É resposta válida e frequente.
4. **Copie o trecho literal**, curto, com a página, e diga em uma frase o que o cerca
   (condição, amostra, medida), porque o trecho fora do contexto é a forma mais comum de erro
   de citação.
5. **Faça a pergunta de verificação:** releia o trecho e responda, contra ele, "o trecho diz
   isto mesmo?". Se a resposta for "só em parte", o rótulo desce para `misto` ou
   `insuficiente`.
6. **Valide e grave.** O bloco só vale com pelo menos um trecho ancorado em página ou com
   "não consta".

## Modelo do bloco

```markdown
**Pergunta.** <a pergunta do autor, como veio>

**Alegação testada.** <a forma atômica>

**Rótulo:** sustenta | refuta | misto | insuficiente | não consta

**Trecho.** "<literal, curto>" (p. N)

**Contexto do trecho.** <condição, amostra, medida, em uma ou duas frases, com página>

**Verificação.** <a pergunta de verificação e a resposta contra o próprio trecho>

**O que a fonte não diz.** <o que a pergunta pedia e a fonte não traz, se for o caso>

**Perguntas ao autor:**
1. <o que ele precisa abrir ou decidir>
2. <…>
```

## Erros que este modo evita, e por quê

- **Ler o resumo.** O resumo de Weijers & Dierynck dizia 217 auditores; o corpo dava 163, 132 e
  78, e a soma explicava o número. O resumo de Chang e col. dizia "6 a 11%"; o corpo dava 10%,
  11% e 12%. Os dois casos estão no registro do projeto que originou esta skill.
- **Trecho sem condição.** "Reduziu o excesso de confiança" era verdade só para um dos dois
  tipos de estímulo em Stone & Opel; a página e a condição mudam a frase que o autor pode
  escrever.
- **Rótulo binário forçado.** Metade das divergências do projeto eram "afirmação restringida",
  e não "certa" ou "errada".
