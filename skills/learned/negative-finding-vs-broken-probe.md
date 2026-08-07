---
name: negative-finding-vs-broken-probe
description: Antes de registrar "isto não existe / não funciona", separar a OBSERVAÇÃO da CONCLUSÃO — sonda quebrada parece ausência, e conclusão negativa documentada é auto-realizável porque ninguém reteste o que já está escrito como impossível
metadata:
  pattern: error_resolution
  origin: manual_estudo + skill legislacao-br, sessão 07/08/2026
  confidence: alta (dois casos medidos na mesma sessão, um deles custou a rota inteira)
---

**O caso:** a skill `legislacao-br` afirmava, com medição datada, que "não existe API pública de
texto consolidado — o campo de texto vem vazio", e concluía: *"não gaste tempo tentando automatizar
por API — já foi tentado e medido."* A observação estava certa: o `contentUrl` que a API anuncia
responde **404**. A conclusão estava errada: o texto existe, e o path anunciado é que está
malformado (falta `/public/`). Inserir seis caracteres devolve 200 com 962 KB. A mesma entrada
dizia que o Planalto estava bloqueado por WAF — também falso; responde 200 com User-Agent de
navegador. Duas rotas fechadas por engano, e a instrução explícita de *não tentar* garantia que
ninguém descobrisse.

**O padrão:** uma sonda que falha tem duas leituras — "a coisa não existe" e "meu acesso a ela está
errado" — e elas são indistinguíveis no resultado. 404, timeout, campo vazio e resposta vazia são
todos ambíguos. O perigo não é errar a leitura uma vez; é **escrever a leitura errada como fato**,
porque conclusão negativa é auto-realizável: quem lê "já foi tentado e medido" não repete o teste.

**Como aplicar:**
- Ao registrar achado negativo, escreva o que você **observou** (`GET <url> → 404`) separado do que
  você **concluiu** (`logo não há texto`). A observação envelhece bem; a conclusão, não.
- Antes de concluir ausência, teste ao menos uma variação do ACESSO: outro path, outro header,
  outro user-agent, outro campo do mesmo payload. O 404 aqui morava a um `/public/` de distância.
- Marque conclusão negativa com data e com o custo de reverificar. Se reverificar é barato (um
  `curl`), ela não deveria virar instrução de "não tente".
- Ao herdar um "isso não funciona" de doc própria, trate como hipótese datada, não como parede —
  principalmente se a fonte for de terceiros e o registro tiver mais de uma semana.

**Sinal de alerta:** qualquer frase sua do tipo "já foi tentado, não insista". Ela economiza minutos
e pode custar a solução inteira. Prefira "testado em DD/MM, falhou assim; se precisar, retestar
custa X".
