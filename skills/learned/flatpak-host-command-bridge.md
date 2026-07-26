---
name: flatpak-host-command-bridge
description: App Flatpak reclama que um binário do host "não foi encontrado" (pdflatex, pandoc, etc.) — o sandbox não enxerga /usr/bin nem ~/.local/bin do host; resolver com wrapper flatpak-spawn --host em ~/.var/app/<id>/data/bin + overrides de PATH e TMPDIR compartilhado (sem TMPDIR a ponte falha silenciosamente quando há troca de arquivos temporários)
metadata:
  pattern: workarounds
  origin: ghostwriter Flatpak sem pdflatex, export PDF (26/07/2026)
  confidence: alta (ponte testada ponta a ponta, PDF gerado de dentro do sandbox)
---

**O caso:** ghostwriter (Flatpak) exporta PDF via pandoc embutido, que chama `pdflatex` —
inexistente no sandbox, embora instalado no host. Instalar TeX dentro do Flatpak era
inviável (app não declara extension point de texlive; `--filesystem=host-os` quebra em
glibc/libs/texmf). A ponte delega a execução ao host.

**O padrão (4 passos):**
1. **Wrapper** em `~/.var/app/<app-id>/data/bin/<binário>` — diretório de dados do app:
   mesmo caminho absoluto dentro e fora do sandbox, sobrevive a updates, sem permissão extra:
   ```sh
   #!/bin/sh
   exec flatpak-spawn --host /usr/bin/pdflatex "$@"
   ```
2. **Permissão D-Bus** que habilita o `flatpak-spawn --host`:
   `flatpak override --user <app-id> --talk-name=org.freedesktop.Flatpak`
3. **PATH e TMPDIR**:
   `flatpak override --user <app-id> --env=PATH=/app/bin:/usr/bin:<home>/.var/app/<app-id>/data/bin --env=TMPDIR=<home>/.var/app/<app-id>/cache/tmp`
   (criar o dir do TMPDIR). Wrappers por ÚLTIMO no PATH: binários do runtime têm precedência.
   **TMPDIR é o detalhe que faz funcionar**: processo do sandbox e binário do host trocam
   arquivos temporários; o /tmp do sandbox é privado, mas `~/.var/app/...` é o mesmo path
   dos dois lados. Sem isso, pandoc grava o .tex num /tmp que o pdflatex do host não vê.
4. **Reiniciar o app** (override só vale para instância nova) e verificar sem UI:
   `flatpak run --command=sh <app-id> -c 'command -v <binário> && <binário> --version'`

**Ressalvas:** `--talk-name=org.freedesktop.Flatpak` = o app pode executar QUALQUER comando
no host (furo deliberado no sandbox; comunicar ao usuário). Reverter tudo:
`flatpak override --user --reset <app-id>`. Inspecionar: `flatpak override --user <app-id> --show`.
Exemplo vivo nesta máquina: `~/.var/app/org.kde.ghostwriter/data/bin/`.
