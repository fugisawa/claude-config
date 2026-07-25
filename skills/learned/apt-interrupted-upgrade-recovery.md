---
name: apt-interrupted-upgrade-recovery
description: "Ubuntu com 'package system is broken' / dependências insatisfeitas bizarras ('Depends X (= v) but v is installed'): diagnosticar pelo term.log ANTES de agir; causa típica nesta máquina = repo CUDA NVIDIA (pin 600) × archive Ubuntu; NÃO desabilitar repos de terceiros no meio do voo; recuperar com dpkg --configure -a → apt-get -f install"
metadata:
  pattern: error_resolution
  origin: upgrade NVIDIA 535→580 interrompido (25/07/2026) — apt full-upgrade morreu com conflitos de arquivo
  confidence: alta (diagnóstico + conserto completos na mesma sessão, verificados)
---

**O caso:** `apt full-upgrade` do driver NVIDIA morreu no meio, deixando ~40 pacotes `iU`
(descompactados, não configurados) e mensagens absurdas tipo "Depends: X (= v) but v is
installed". O guia genérico ("disable third-party repos, apt-get install -f") estava
meio certo e meio errado: o repo terceiro ERA o causador, mas desabilitá-lo naquele
momento teria estragado o conserto.

**Diagnóstico (nesta ordem, tudo read-only, sem sudo):**
1. `tail -60 /var/log/apt/term.log` — o erro REAL do dpkg (aqui: "a tentar sobre-escrever
   '/usr/bin/nvidia-bug-report.sh', que também está no pacote nvidia-utils-535"). A
   mensagem de "unmet dependencies" da GUI é sintoma, não causa.
2. `/var/log/apt/history.log` — qual comando iniciou e quais pacotes estavam na transação.
3. `dpkg -l | grep -Ev '^(ii|rc|hi)'` — estados quebrados (`iU`=unpacked, `iF`=half-conf).
   Cuidado: `iF` durante processamento de triggers é transitório — a fonte da verdade é
   `grep -A2 '^Package: X$' /var/lib/dpkg/status`.
4. `apt-cache policy <pacotes>` + `ls /etc/apt/preferences.d/` — mistura de origens?
   Nesta máquina: repo CUDA (`developer.download.nvidia.com`, **pin 600**) fornece
   driver `-1ubuntu1` que conflita com o empacotamento `-0ubuntu0.24.04.x` do archive
   (arquivos mudam de pacote sem Breaks/Replaces cruzados).

**Por que NÃO desabilitar o repo terceiro no meio do voo:** os pacotes meio-instalados
são as versões DELE; sem o repo, o apt perde a fonte exata das dependências que faltam.
Primeiro deixar o sistema consistente, DEPOIS discutir pin/remoção do repo.

**Conserto (ordem canônica):**
`sudo dpkg --configure -a` → `sudo apt-get -f install`. No caso NVIDIA, o -f install
bastou porque os pacotes 535 transicionais `.2` (vazios) já tinham sido descompactados —
o conflito de arquivo se auto-resolveu. Fallback (só se ainda reclamar de sobre-escrever):
`apt-get -o Dpkg::Options::="--force-overwrite" -f install`.

**Verificação pós-conserto:** `dpkg -l` sem estados anômalos; `apt-get -o
Debug::NoLocking=1 check` (funciona sem root — `apt-get check` puro falha no lock);
`dkms status` cobre `uname -r`; initrds regenerados (`ls -la /boot/initrd.img-*`,
tamanhos ~íntegros). `nvidia-smi` com "Driver/library version mismatch" é ESPERADO até
reboot (userland novo + módulo antigo carregado) — não é um problema a consertar.

**Codificado nos dotfiles (v7.1):** `apt_state_ok`/`apt_recover`/`APT_OPTS` em
`~/dotfiles/system-maintenance/lib/common.sh`; o `update` faz preflight e o
`sm-health` diário denuncia estado quebrado.
