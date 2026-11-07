"""Rodar sozinho: tarefas do Agendador do Windows (schtasks), criadas pela tela sem a pessoa abrir nada."""

import os
import subprocess  # nosec B404 - só schtasks, sem shell, com argumentos fixos

TAREFAS = (("LexSuiteONE Radar (noite)", "19:40"), ("LexSuiteONE Radar (manha)", "07:10"))


def _rodar(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=30, shell=False)  # nosec B603
    return r.returncode == 0, (r.stderr or r.stdout or "").strip()[:200]


def disponivel():
    return os.name == "nt"


def agendado():
    """True se a tarefa da noite existe."""
    if not disponivel():
        return False
    ok, _ = _rodar(["schtasks", "/query", "/tn", TAREFAS[0][0]])
    return ok


def agendar(pasta_robo):
    """Cria (ou recria) as duas tarefas diárias que rodam o RODAR.bat desta pasta. Devolve (ok, mensagem)."""
    if not disponivel():
        return False, "Agendamento automático só no Windows."
    bat = os.path.join(pasta_robo, "RODAR.bat")
    if not os.path.exists(bat):
        return False, "RODAR.bat não encontrado na pasta do robô."
    for nome, hora in TAREFAS:
        ok, msg = _rodar(["schtasks", "/create", "/f", "/tn", nome, "/sc", "daily", "/st", hora, "/tr", f'"{bat}" --agendado'])
        if not ok:
            return False, f"Não consegui criar a tarefa ({msg}). Tente o AGENDAR.bat como administrador."
    return True, "Agendado: todo dia às 19:40 e às 07:10, com o computador ligado."


def desagendar():
    if not disponivel():
        return False, "Agendamento automático só no Windows."
    for nome, _ in TAREFAS:
        _rodar(["schtasks", "/delete", "/f", "/tn", nome])
    return True, "Agendamento removido."
