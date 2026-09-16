---
name: proxy-documental-mede-se-a-distancia
description: Quando o documento-alvo está indisponível e você adota outro como referência, meça a distância textual entre os dois antes de descontar a confiança — em domínio de texto padronizado o substituto costuma ser cópia literal do alvo, e o desconto aplicado por precaução é que vira o erro
metadata:
  pattern: knowledge_management
  origin: manual_estudo, disciplinas/afo — editais TCU × TCE-RR × SEFAZ-AM, sessão 11/08/2026
  confidence: alta (a propagação de texto foi medida em quatro editais; o desconto indevido que ela causou custou 28 dias em três arquivos)
---

**O padrão.** Documento-alvo indisponível leva a adotar um parecido como referência, e o reflexo
que parece prudente é descontar a confiança — "serve, mas não é o alvo". Esse desconto é uma
**estimativa da distância entre os dois, feita sem medir a distância**. Em domínio de texto
padronizado a distância costuma ser zero: editais, contratos, licitações, termos de referência,
normas infralegais e templates de configuração se copiam entre órgãos, entre versões e entre
fornecedores. Medir custa um `diff` do trecho que interessa. Estimar custa a confiança do
documento inteiro, e às vezes custa uma lacuna inventada que gera trabalho depois.

**O caso.** Uma rodada de pesquisa de 14/07/2026 não achou o edital do TCU e adotou o do TCE-RR
como substituto, com a ressalva escrita no corpo: *"o conteúdo do TCE-RR ainda é o padrão-ouro
comparável (mesma lógica de banca/estrutura FGV) mas **não deve ser citado como 'edital do
TCU'**"*. O bloco de Administração Financeira e Orçamentária do TCE-RR 2024 é **cópia literal do
bloco do TCU 2021**, item por item, incluindo a numeração. A ressalva dizia o contrário do que os
arquivos mostravam, e ficou de pé **28 dias em três arquivos**, junto com uma lacuna declarada
("não obtive o edital do TCU") que também não existia. Desfazer as duas custou baixar os dois
PDFs e comparar os blocos.

O mesmo texto está ainda no TCU 2015 e no SEFAZ-AM 2022, este com duas adaptações de ente. Ou
seja: a propagação não foi coincidência de dois documentos, e sim um modelo circulando entre
quatro, por cima de uma troca de banca (Cebraspe em 2015, FGV em 2021).

**Como aplicar.**

- **Identifique o arquivo pelo conteúdo, nunca pelo nome nem pela busca que o trouxe.** No caso
  acima o PDF se chamava `auditor_federal_de_controle_externo_-_area_de_controle_externoaufc-ce_
  tipo_1.pdf`, estava hospedado no site da FGV e foi rotulado de "TCE-RR, erro de indexação". Ele
  era a **prova do TCU**. Um `head -30` mostra a capa e um `grep -ci roraima` devolve zero.
- **Compare o trecho que você vai usar, não o documento todo.** A pergunta não é "os dois editais
  são iguais", e sim "o bloco que eu vou citar é o mesmo".
- **A medida serve nas duas direções.** Distância zero converte proxy em citação direta, e você
  passa a dizer de quem é o texto. Distância grande te diz **quanto** descontar, em vez de
  descontar por impressão.
- **Distância zero é achado, não só conforto.** Aqui ela respondeu a pergunta que decidia o
  estudo: o programa da matéria é do órgão, sobreviveu à troca de banca e vem sendo copiado por
  outros — logo a banca indefinida move o estilo da questão, e não o conteúdo a estudar. Quem só
  quisesse "poder citar" teria parado antes de ver isso.

**Sinal de alerta.** Qualquer frase sua com "comparável", "serve como proxy", "mesma lógica",
"padrão-ouro aproximado" ou "estrutura equivalente" **sem um número ao lado**. Todas descrevem
uma distância. Se você não a mediu, não a conhece — e a versão prudente da frase pode estar tão
errada quanto a otimista.

**Parente próximo, e o contraste.** [[a-segunda-copia-da-regra-diverge-calada]] trata do caso
inverso e interno: cópia que **você** faz de uma regra sua diverge em silêncio, e por isso não se
faz a segunda. Aqui a cópia é de terceiro, **não** divergiu, e o defeito foi não medir. Uma manda
não criar cópia; a outra manda medir a cópia alheia antes de julgá-la. Ver também
[[negative-finding-vs-broken-probe]], que cobre o outro lado do mesmo episódio — a lacuna
declarada que ninguém reverifica.
