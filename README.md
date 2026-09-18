# J.A.R.V.I.S. Operator

Operador **local e real**. Vê a tela, move o mouse, clica, digita, abre apps, lê a web, controla volume/janelas e executa o que você pedir.

Isto **não** é um chat holográfico fingindo que clicou. Um site no navegador **não consegue** controlar o mouse da sua máquina. Este processo roda **no seu computador**.

Não é um produto da Marvel. É uma homenagem de engenharia.

## Windows (CMD)

Precisa de [Python 3.11+](https://www.python.org/downloads/) (marque *Add python.exe to PATH*) e [Git](https://git-scm.com/download/win).

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/sites-art77/jarvis-operator.git
cd jarvis-operator
install.cmd
```

O `install.cmd` cria o venv, instala as libs, abre o `.env` e **move o mouse de verdade** (`--self-test`).

Cole no `.env`:

```
NVIDIA_API_KEY=nvapi-...
```

Chave em [build.nvidia.com](https://build.nvidia.com). Nunca commite o `.env`.

Depois:

```bat
rodar.cmd
rodar.cmd "abra o bloco de notas e escreva olá senhor"
python -m jarvis --self-test
```

Failsafe: jogue o mouse no **canto superior esquerdo** para abortar.

## Linux / macOS

```bash
git clone https://github.com/sites-art77/jarvis-operator.git
cd jarvis-operator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m jarvis --self-test
python -m jarvis "abra o navegador e pesquise o clima no Rio de Janeiro"
```

macOS: Ajustes → Privacidade → Acessibilidade (habilite o Terminal).  
Linux: X11 (Wayland puro às vezes bloqueia captura).

## Cérebro

| Chave no `.env` | Papel |
|---|---|
| `NVIDIA_API_KEY` | Visão da tela + raciocínio e ferramentas ([build.nvidia.com](https://build.nvidia.com)) |
| `XAI_API_KEY` | Opcional: voz (TTS/STT). Se não houver NVIDIA, o Grok assume o cérebro |

## O que ele faz de verdade

- Screenshot + visão (Nemotron VL na NVIDIA, com reserva Grok se houver chave)
- Mouse: mover, clique, duplo, direito, arrastar, scroll
- Teclado: texto, atalhos, teclas
- Apps, pastas, arquivos, shell (com bloqueio de wipe/shutdown)
- Abrir URL no navegador **e** ler página com `fetch_url`
- Clipboard, notificações, volume, mídia
- Listar e focar janelas
- Loop autônomo: observa → pensa → age → observa de novo

```bash
python -m jarvis --voice --listen 6   # voz exige XAI_API_KEY também
```

## Segurança

- Chaves só no `.env`. Nunca no git.
- Wipe de disco, shutdown e fork bomb são bloqueados.
- `fetch_url` recusa localhost e IPs privados.
- Não rode como Administrador / root.

## Testes (sem display)

```bash
pip install pytest
pytest -q
```

## Limitações honestas

- Não veste armadura nem dispara mísseis.
- Anti-cheat em tela cheia pode recusar o controle.
- Wayland puro às vezes bloqueia captura — use X11 ou o portal.
- Cada passo gasta cota da chave NVIDIA (e xAI, se houver).
