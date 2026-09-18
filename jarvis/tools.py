def _fn(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    parameters: dict = {"type": "object", "properties": properties}
    if required:
        parameters["required"] = required
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": parameters},
    }


TOOLS = [
    _fn("mouse_move", "Move o cursor real. x e y em percentual da tela (0-100).", {"x": {"type": "number"}, "y": {"type": "number"}, "duration": {"type": "number"}}, ["x", "y"]),
    _fn("click", "Move (se x,y) e clica de verdade. button: left|right|middle. clicks: 1-3 (2 = duplo).", {"x": {"type": "number"}, "y": {"type": "number"}, "button": {"type": "string"}, "clicks": {"type": "integer"}}),
    _fn("drag", "Arrasta o botão esquerdo até x,y percentuais.", {"x": {"type": "number"}, "y": {"type": "number"}}, ["x", "y"]),
    _fn("scroll", "Roda o mouse. Positivo sobe, negativo desce.", {"amount": {"type": "integer"}}, ["amount"]),
    _fn("type_text", "Digita no campo focado, tecla a tecla.", {"text": {"type": "string"}}, ["text"]),
    _fn("hotkey", "Atalho. Ex.: keys=['ctrl','c'] ou ['cmd','space'].", {"keys": {"type": "array", "items": {"type": "string"}}}, ["keys"]),
    _fn("press", "Pressiona uma tecla (enter, tab, esc, backspace, delete, up, down, volumedown...).", {"key": {"type": "string"}}, ["key"]),
    _fn("open_app", "Abre um aplicativo instalado (Firefox, Chrome, Code, Calculator, etc.).", {"name": {"type": "string"}}, ["name"]),
    _fn("open_url", "Abre uma URL no navegador padrão.", {"url": {"type": "string"}}, ["url"]),
    _fn("fetch_url", "Baixa o texto de uma página http(s) pública e devolve o conteúdo (não abre janela).", {"url": {"type": "string"}}, ["url"]),
    _fn("open_path", "Abre um arquivo ou pasta no sistema.", {"path": {"type": "string"}}, ["path"]),
    _fn("list_dir", "Lista arquivos de uma pasta real.", {"path": {"type": "string"}}, ["path"]),
    _fn("read_file", "Lê um arquivo de texto do disco.", {"path": {"type": "string"}}, ["path"]),
    _fn("write_file", "Escreve um arquivo de texto no disco.", {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
    _fn("run_command", "Executa um comando no shell. Comandos catastróficos são bloqueados.", {"command": {"type": "string"}}, ["command"]),
    _fn("clipboard_get", "Lê a área de transferência.", {}),
    _fn("clipboard_set", "Coloca texto na área de transferência.", {"text": {"type": "string"}}, ["text"]),
    _fn("screenshot_save", "Salva um JPEG da tela no disco.", {"path": {"type": "string"}}),
    _fn("system_info", "SO, CPU, disco livre, hostname.", {}),
    _fn("notify", "Mostra uma notificação nativa do sistema.", {"title": {"type": "string"}, "message": {"type": "string"}}, ["message"]),
    _fn("volume", "Controle de volume. action: up|down|mute.", {"action": {"type": "string"}}, ["action"]),
    _fn("media", "Controle de mídia. action: play_pause|next|prev|stop.", {"action": {"type": "string"}}, ["action"]),
    _fn("window_list", "Lista janelas visíveis.", {}),
    _fn("window_focus", "Traz uma janela para frente pelo título (trecho).", {"title": {"type": "string"}}, ["title"]),
    _fn("wait", "Espera a UI responder, em segundos (0.2 a 8).", {"seconds": {"type": "number"}}, ["seconds"]),
]

TOOL_NAMES = tuple(item["function"]["name"] for item in TOOLS)
