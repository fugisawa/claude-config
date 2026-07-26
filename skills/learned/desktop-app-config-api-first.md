---
name: desktop-app-config-api-first
description: Configurar/operar app desktop do usuário (Anki, e similares com API local) — API primeiro porque rótulo de menu varia com versão/idioma (nunca ditar caminho de UI de memória); print do usuário guia o resto; diálogo de opções ABERTO sobrescreve writes da API no Salvar (reassertar depois + read-back); testes contra app localizado não hardcodeiam nomes default
metadata:
  pattern: workarounds
  origin: manual_estudo, setup da coleção Anki nova via AnkiConnect (26/07/2026)
  confidence: alta (ciclo completo vivido, com o clobber flagrado por read-back)
---

**O caso:** configurar o preset FSRS do Anki do usuário. Instruções de UI de memória falharam duas vezes ("não existe opção criar perfil" — ficava dentro de outro menu; "meu Anki está em português e em versão diferente das suas instruções"). A API resolveu 90%; o resto saiu por print.

**O padrão (na ordem):**
1. **API primeiro.** Tudo que for DADO de configuração, escrever pela API local (AnkiConnect: `getDeckConfig`→mutar→`saveDeckConfig`) — imune a idioma, versão e layout. Só recorrer à UI para o que a API não alcança (toggles globais, diálogos de confirmação).
2. **Nunca ditar rótulos de menu de memória.** Para os passos de UI restantes: pedir **print do usuário** e apontar no layout DELE ("troque o campo X que está mostrando Y") — ou descrever pela função ("ícone de engrenagem ao lado do deck"), nunca pelo texto exato do menu.
3. **Diálogo aberto = clobber.** Janela de opções aberta carrega o estado de quando abriu; o Salvar do usuário **sobrescreve writes da API feitos enquanto ela estava aberta** (flagrado: bury siblings voltou a false). Sequência correta: usuário salva a UI → **reassertar via API depois** → verificar por read-back. Nunca o inverso.
4. **Ações que a API recusa têm significado.** Ex.: AnkiConnect `sync` falha com "status 2" quando houve mudança de schema (note type novo) — não é bug, é o app exigindo o clique humano de direção (upload×download destrutivo). Reconhecer e devolver ao usuário com a escolha certa já apontada.
5. **Testes de integração contra app localizado:** nunca hardcodear nomes de entidades default ("Basic" não existe em PT-BR — é "Básico"); resolver dinamicamente (listar e escolher) ou o teste quebra em metade das máquinas.

**Bônus de segurança:** perfil/coleção errada é o risco nº 1 — antes de escrever, ler o estado (decks/contagens) e confirmar que é a coleção esperada; `getProfiles`/`loadProfile` existem, mas criar perfil é UI-only.
