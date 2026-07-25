---
name: browser-login-session-pairing
description: Automação de site logado no Chrome — "estou logado" do usuário ≠ sessão no browser que a extensão controla; resolver com list/switch_browser, checar o SUBDOMÍNIO certo antes de concluir deslogado, e NUNCA autenticar (estacionar na tela de login e devolver ao usuário)
metadata:
  pattern: workarounds
  origin: manual_estudo, montagem de simulados no QConcursos via Chrome (24/07/2026)
  confidence: alta (fluxo completo executado, com os 3 modos de falha vividos)
---

**O caso:** usuário disse "loguei o QConcursos no Chrome", mas a aba controlada mostrava
"Entrar". Três causas distintas se empilharam e cada uma tem remédio próprio.

**O padrão (na ordem de diagnóstico):**
1. **Perfil/instância errada do Chrome.** A extensão pode estar pareada com OUTRO Chrome
   (2+ conectados). Sinal: usuário vê tudo logado, agente vê tudo deslogado.
   Remédio: `list_connected_browsers` → AskUserQuestion com TODOS os browsers + opção de
   broadcast → `switch_browser` (usuário clica Connect no Chrome certo e pode nomeá-lo).
   Depois do switch: `tabs_context_mcp` de novo (grupo de abas muda).
2. **Subdomínio errado.** Plataformas dividem sessão por host (QC: `www.` deslogado
   enquanto `elite.`/`app.` redirecionam para a área logada). Antes de concluir "não está
   logado", navegar para o host da ÁREA DE MEMBRO e olhar o header (avatar vs "Entrar").
   URLs antigas de memória dão 404 — navegar pela UI, não por URL decorada.
3. **Login de fato pendente.** Regra dura: o agente NUNCA preenche senha nem clica
   "Entrar", mesmo com credencial salva no gerenciador. Remédio: estacionar a aba na
   tela de login, dizer ao usuário exatamente onde ela está, e pedir o clique. Retomar
   só após verificar o header logado.
4. **Sessão num perfil SEM extensão (vivido 25/07/2026).** Todos os browsers conectados
   à extensão estavam deslogados — a sessão paga vivia num 3º perfil do Chrome onde a
   extensão não está instalada. Sinal: switch_browser/select_browser não resolve; login
   continua aparecendo no browser escolhido pelo usuário. Remédio: TIME-BOX a automação
   (2–3 tentativas) e cair para o input alternativo — **screenshots/prints do próprio
   usuário como fonte primária** (ele está logado no perfil dele; um print custa 10s).
   Não é derrota: para leitura de dados, print do usuário ≥ automação.

**Bônus de SPA com filtros (mesmo caso):** o estado-verdade são os CHIPS/URL de filtro
(conferir `subject_ids`/`board_ids` na URL vale como QA), botões se REPOSICIONAM após
re-render (re-screenshot antes de clicar de novo), dropdowns custom são instáveis
(preferir botões diretos quando existir equivalente).
