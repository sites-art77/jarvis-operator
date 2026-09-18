# J.A.R.V.I.S. Operator

Operador **local e real**. Vê a tela, move o mouse, clica, digita, abre aplicativos, lê e escreve arquivos, roda comandos e fala. O cérebro é o Grok (xAI). Isto **não** é um chat holográfico fingindo que clicou.

Um site no navegador **não consegue** controlar o mouse da sua máquina. Por isso este repositório existe: o processo roda **no seu computador**, com as permissões do seu usuário.

Não é um produto da Marvel. É uma homenagem de engenharia.

## O que ele faz de verdade

- Captura screenshot da tela
- Move o cursor (coordenadas percentuais 0–100)
- Clique, duplo clique, clique direito, arrastar, scroll
- Digita e dispara atalhos (`ctrl+c`, `cmd+space`, Enter…)
- Abre apps, URLs e pastas do sistema
- Lê / escreve arquivos
- Executa comandos no shell (com bloqueio de wipe de disco, shutdown, fork bomb)
- Voz: escuta o microfone (STT xAI) e responde falando (TTS xAI)
- Loop autônomo: observa → pensa → age → observa de novo, até concluir

Failsafe do `pyautogui`: jogue o mouse no **canto superior esquerdo** para abortar.

## Requisitos

- Python 3.11+
- Chave em [console.x.ai](https://console.x.ai)
- Permissão de acessibilidade (macOS: Ajustes → Privacidade → Acessibilidade, habilite o Terminal/iTerm)
- Linux: servidor gráfico (X11/Wayland), `python3-tk`, e um capturador (`gnome-screenshot` ou equivalente)

## Instalação

```bash
git clone https://github.com/sites-art77/jarvis-operator.git
cd jarvis-operator
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edite .env e cole XAI_API_KEY
```

## Uso

Uma ordem e ele opera sozinho:

```bash
python -m jarvis "abra o navegador e pesquise o clima no Rio de Janeiro"
```

REPL:

```bash
python -m jarvis
```

Voz (fala → executa → responde falando):

```bash
python -m jarvis --voice --listen 6
```

## Segurança

- `XAI_API_KEY` fica só no `.env` local. Nunca no git.
- Comandos que apagam o sistema, formatam disco ou desligam a máquina são **bloqueados**.
- `rm -rf` em pastas de projeto pede confirmação no terminal.
- Escrita recusada em `C:\Windows` e `/etc/passwd`.
- Ele age com o mesmo poder do seu usuário. Não rode como root.

## Testes (sem display)

```bash
pip install pytest
pytest -q
```

Os testes cobrem o filtro de segurança e o parser. O mouse exige o seu desktop.

## Limitações honestas

- Não veste armadura, não dispara mísseis, não liga a casa sem você integrar isso.
- Jogos em tela cheia com anti-cheat podem recusar o controle.
- Wayland puro às vezes bloqueia captura/clique — use X11 ou as permissões do portal.
- Cada passo gasta cota da sua chave xAI (visão + texto).
