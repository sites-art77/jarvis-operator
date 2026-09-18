# J.A.R.V.I.S. Operator

Operador **local e real**. Vê a tela (visão NVIDIA Nemotron ou Grok), move o mouse, clica, digita, abre apps, lê a web, controla volume/janelas e executa o que você pedir. Isto **não** é um chat holográfico fingindo que clicou.

Um site no navegador **não consegue** controlar o mouse da sua máquina. Este processo roda **no seu computador**.

Não é um produto da Marvel. É uma homenagem de engenharia.

## Cérebro

| Chave no `.env` | Papel |
|---|---|
| `NVIDIA_API_KEY` | Visão da tela + raciocínio e ferramentas ([build.nvidia.com](https://build.nvidia.com)) |
| `XAI_API_KEY` | Opcional: voz (TTS/STT). Se não houver NVIDIA, o Grok assume o cérebro |

Padrão: se a chave NVIDIA existir, ela é usada. Nunca cole a chave no git nem no chat.

## O que ele faz de verdade

- Screenshot + visão (Nemotron VL na NVIDIA, ou Grok)
- Mouse: mover, clique, duplo, direito, arrastar, scroll
- Teclado: texto, atalhos, teclas
- Apps, pastas, arquivos, shell (com bloqueio de wipe/shutdown)
- Abrir URL no navegador **e** ler página com `fetch_url`
- Clipboard, notificações, volume, mídia
- Listar e focar janelas
- Loop autônomo: observa → pensa → age → observa de novo

Failsafe: jogue o mouse no **canto superior esquerdo** para abortar.

## Instalação

```bash
git clone https://github.com/sites-art77/jarvis-operator.git
cd jarvis-operator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

No `.env` local:

```
NVIDIA_API_KEY=nvapi-...
```

macOS: Ajustes → Privacidade → Acessibilidade (habilite o Terminal).  
Linux: X11/Wayland, `python3-tk`.

## Uso

```bash
python -m jarvis "abra o navegador e pesquise o clima no Rio de Janeiro"
python -m jarvis
python -m jarvis --voice --listen 6   # voz exige XAI_API_KEY também
```

## Segurança

- Chaves só no `.env`. Nunca no git.
- Wipe de disco, shutdown e fork bomb são bloqueados.
- `fetch_url` recusa localhost e IPs privados.
- Não rode como root.

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
