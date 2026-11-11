"""Rodar sozinho: uma tarefa do Agendador do Windows (schtasks), criada pela tela sem a pessoa abrir nada.

Horários e dias vêm do config.json (radar.horarios, radar.dias). A tarefa usa "executar assim que possível se um
horário foi perdido": num computador de casa, desligado ou dormindo na hora marcada, a leitura acontece quando ele
voltar. Se o Windows recusar esse formato (XML), cai no jeito antigo: uma tarefa simples por horário, sem compensar.
Ao terminar uma leitura, notificar() mostra um aviso no canto da tela do Windows.
"""

import datetime as dt
import os
import re
import subprocess  # nosec B404 - só schtasks e powershell, sem shell, com argumentos fixos
import tempfile

# Padrão (decisão de 08/Nov): o Diário de Justiça Eletrônico Nacional sai a partir das 19h; às 20h a leitura já pega o
# dia, e às 8h pega o que entrou tarde da noite, antes de o escritório começar. Horas cheias são fáceis de lembrar.
PADRAO = ("20:00", "08:00")
MAXIMO = 6
DIAS = ("todos", "uteis")
TAREFA = "LexSuiteONE Radar"
ANTIGAS = ("LexSuiteONE Radar (noite)", "LexSuiteONE Radar (manha)")
HORA = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
DIAS_UTEIS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def escape(texto):
    """Escapa texto para dentro do XML da tarefa."""
    return str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _rodar(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=30, shell=False, stdin=subprocess.DEVNULL,  # nosec B603
                       creationflags=SEM_JANELA)  # 0.7.29: chamado do pythonw, o schtasks piscaria uma janela preta
    return r.returncode == 0, (r.stderr or r.stdout or "").strip()[:200]


def disponivel():
    return os.name == "nt"


def validar(horarios):
    """Lista de "HH:MM" válidos, sem repetir, em ordem do dia, no máximo MAXIMO. Vazia ou inválida: o padrão."""
    vistos = set()
    for h in horarios if isinstance(horarios, (list, tuple)) else []:
        m = HORA.match(str(h or "").strip())
        if m:
            vistos.add(f"{int(m.group(1)):02d}:{m.group(2)}")
    lista = sorted(vistos)[:MAXIMO]
    return lista or list(PADRAO)


def validar_dias(dias):
    return dias if dias in DIAS else "todos"


def do_config(cfg):
    r = (cfg or {}).get("radar") or {}
    return validar(r.get("horarios")), validar_dias(r.get("dias"))


def origem_da_leitura(cfg, agora=None, tolerancia_min=15):
    """Para o histórico de leituras: "agendamento" se a leitura começou até 15 minutos depois de um horário marcado;
    senão "fora do horário" (computador ligado depois do horário, leitura de recuperação, ou rodada à mão)."""
    agora = agora or dt.datetime.now()
    horarios, _ = do_config(cfg)
    for h in horarios:
        hh, mm = (int(x) for x in h.split(":"))
        for dia in (agora.date(), agora.date() - dt.timedelta(days=1)):
            marcado = dt.datetime.combine(dia, dt.time(hh, mm))
            if dt.timedelta(0) <= agora - marcado <= dt.timedelta(minutes=tolerancia_min):
                return "agendamento"
    return "fora do horário"


def horario_perdido(cfg, agora=None, tolerancia_min=15, ultima_leitura=""):
    """0.7.15: se a leitura começou mais de 15 minutos depois de um horário marcado (computador desligado ou em repouso
    na hora), devolve esse horário ("08:00"); senão "". Olha o último horário marcado antes de agora (hoje ou ontem)."""
    agora = agora or dt.datetime.now()
    horarios, dias = do_config(cfg)
    ultimo = None
    for dia in (agora.date(), agora.date() - dt.timedelta(days=1)):
        if dias == "uteis" and dia.weekday() >= 5:
            continue
        for h in horarios:
            hh, mm = (int(x) for x in h.split(":"))
            marcado = dt.datetime.combine(dia, dt.time(hh, mm))
            if marcado <= agora and (ultimo is None or marcado > ultimo):
                ultimo = marcado
    if ultimo is None or agora - ultimo <= dt.timedelta(minutes=tolerancia_min) or agora - ultimo > dt.timedelta(hours=20):
        return ""
    if ultima_leitura and str(ultima_leitura)[:19] >= ultimo.isoformat(timespec="seconds"):
        return ""  # já houve leitura depois do horário marcado: não é atraso
    return ultimo.strftime("%H:%M")


def proxima(horarios, dias="todos", agora=None):
    """Data e hora da próxima leitura automática (datetime local), ou None se não houver horário."""
    agora = agora or dt.datetime.now()
    horarios = validar(horarios)
    for d in range(0, 8):
        dia = agora.date() + dt.timedelta(days=d)
        if dias == "uteis" and dia.weekday() >= 5:
            continue
        for h in horarios:
            hh, mm = (int(x) for x in h.split(":"))
            quando = dt.datetime.combine(dia, dt.time(hh, mm))
            if quando > agora:
                return quando
    return None


def tem_noite(horarios):
    """True se algum horário é depois das 19h (quando o Diário do dia já saiu)."""
    return any(h >= "19:00" for h in validar(horarios))


def executavel_oculto(pasta):
    """0.7.29 (dono: sem janela preta): o pythonw.exe do Python portátil da pasta (ou o que vem junto do Python em uso),
    ou "" se não houver. Com ele, a leitura automática e a tela rodam sem janela de prompt de comando."""
    import sys
    for c in (os.path.join(pasta, "python", "pythonw.exe"), os.path.join(os.path.dirname(sys.executable or ""), "pythonw.exe")):
        if c and os.path.isfile(c):
            return c
    return ""


def acao_oculta(pasta):
    """(comando, argumentos) da leitura automática sem janela, ou None se não houver pythonw."""
    exe = executavel_oculto(pasta)
    if not exe:
        return None
    return exe, f'"{os.path.join(pasta, "lexsuite_robo.py")}" radar --agendado'


def xml_tarefa(bat, horarios, dias="todos", hoje=None, oculta=None):
    """O XML da tarefa (formato do Agendador do Windows), com um gatilho por horário. 0.7.29: com `oculta`
    ((pythonw, argumentos)), a tarefa chama o Python sem janela, direto, em vez do RODAR.bat."""
    hoje = hoje or dt.date.today()
    gatilhos = []
    for h in validar(horarios):
        quando = f"{hoje.isoformat()}T{h}:00"
        if validar_dias(dias) == "uteis":
            agenda = ("<ScheduleByWeek><WeeksInterval>1</WeeksInterval><DaysOfWeek>"
                      + "".join(f"<{d} />" for d in DIAS_UTEIS) + "</DaysOfWeek></ScheduleByWeek>")
        else:
            agenda = "<ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>"
        gatilhos.append(f"<CalendarTrigger><StartBoundary>{quando}</StartBoundary><Enabled>true</Enabled>{agenda}</CalendarTrigger>")
    pasta = os.path.dirname(bat)
    return ('<?xml version="1.0" encoding="UTF-16"?>\n'
            '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">'
            "<RegistrationInfo><Description>RADAR JUDICIAL (LexSuiteONE): leitura automática do Diário.</Description></RegistrationInfo>"
            f"<Triggers>{''.join(gatilhos)}</Triggers>"
            '<Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>'
            "<Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>"
            "<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>"
            "<AllowHardTerminate>true</AllowHardTerminate><StartWhenAvailable>true</StartWhenAvailable>"
            "<RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>"
            "<IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>"
            "<AllowStartOnDemand>true</AllowStartOnDemand><Enabled>true</Enabled><Hidden>false</Hidden>"
            "<RunOnlyIfIdle>false</RunOnlyIfIdle><WakeToRun>false</WakeToRun><ExecutionTimeLimit>PT4H</ExecutionTimeLimit>"
            "<Priority>7</Priority></Settings>"
            f'<Actions Context="Author"><Exec><Command>{escape(oculta[0] if oculta else bat)}</Command>'
            f'<Arguments>{escape(oculta[1] if oculta else "--agendado")}</Arguments>'
            f"<WorkingDirectory>{escape(pasta)}</WorkingDirectory></Exec></Actions></Task>")


def _simples(nome_hora):
    return f"{TAREFA} {nome_hora.replace(':', 'h')}"


def agendado():
    """True se a tarefa (nova, simples ou antiga) existe."""
    if not disponivel():
        return False
    ok, _ = _rodar(["schtasks", "/query", "/tn", TAREFA])
    if ok:
        return True
    ok, saida = _rodar(["schtasks", "/query", "/fo", "csv", "/nh"])
    return ok and TAREFA in saida


def _apagar_tudo():
    _rodar(["schtasks", "/delete", "/f", "/tn", TAREFA])
    for nome in ANTIGAS:
        _rodar(["schtasks", "/delete", "/f", "/tn", nome])
    saida = _saida_inteira(["schtasks", "/query", "/fo", "csv", "/nh"])  # 0.7.29: a lista inteira (antes, só 200 letras)
    for nome in set(re.findall(r'"\\?(' + re.escape(TAREFA) + r' \d\dh\d\d)"', saida)):
        _rodar(["schtasks", "/delete", "/f", "/tn", nome])


def descricao(horarios, dias="todos"):
    h = [x.replace(":", "h") for x in validar(horarios)]
    lista = h[0] if len(h) == 1 else ", ".join(h[:-1]) + " e " + h[-1]
    return ("de segunda a sexta" if validar_dias(dias) == "uteis" else "todo dia") + " às " + lista


def agendar(pasta_robo, horarios=None, dias="todos"):
    """Cria (ou recria) a leitura automática que roda o RODAR.bat desta pasta. Devolve (ok, mensagem)."""
    if not disponivel():
        return False, "Agendamento automático só no Windows."
    bat = os.path.join(pasta_robo, "RODAR.bat")
    if not os.path.exists(bat):
        return False, "RODAR.bat não encontrado na pasta do programa."
    horarios, dias = validar(horarios), validar_dias(dias)
    _apagar_tudo()
    arq = None
    try:
        fd, arq = tempfile.mkstemp(suffix=".xml", prefix="lexsuite-tarefa-")
        with os.fdopen(fd, "w", encoding="utf-16") as f:
            f.write(xml_tarefa(bat, horarios, dias, oculta=acao_oculta(pasta_robo)))
        ok, msg = _rodar(["schtasks", "/create", "/f", "/tn", TAREFA, "/xml", arq])
    except OSError as e:
        ok, msg = False, str(e)
    finally:
        if arq:
            try:
                os.remove(arq)
            except OSError:
                pass
    if ok:
        return True, f"Agendado: {descricao(horarios, dias)}. Se o computador estiver desligado na hora, a leitura acontece quando ele ligar."
    # Jeito antigo (sem compensar horário perdido): uma tarefa por horário.
    oc = acao_oculta(pasta_robo)
    tr = f'"{oc[0]}" {oc[1]}' if oc and len(f'"{oc[0]}" {oc[1]}') <= 260 else f'"{bat}" --agendado'  # o /tr aceita até 261 letras
    for h in horarios:
        args = ["schtasks", "/create", "/f", "/tn", _simples(h), "/st", h, "/tr", tr]
        args[5:5] = ["/sc", "weekly", "/d", "MON,TUE,WED,THU,FRI"] if dias == "uteis" else ["/sc", "daily"]
        ok2, msg2 = _rodar(args)
        if not ok2:
            return False, f"Não consegui criar a leitura automática ({msg2 or msg}). Tente o AGENDAR.bat como administrador."
    return True, f"Agendado: {descricao(horarios, dias)}, com o computador ligado na hora."


def migrar_antigas(pasta_robo, cfg):
    """Quem tinha as duas tarefas antigas (19h40 e 7h10, até a 0.7.8) passa para a tarefa nova, com os horários do
    config (o padrão novo, se não houver). Devolve a mensagem, ou "" se não havia nada a migrar."""
    if not disponivel():
        return ""
    ok, _ = _rodar(["schtasks", "/query", "/tn", ANTIGAS[0]])
    if not ok:
        return ""
    horarios, dias = do_config(cfg)
    return agendar(pasta_robo, horarios, dias)[1]


def _saida_inteira(args):
    """A saída inteira de um comando (o _rodar corta em 200 letras), em texto, seja UTF-16 ou não."""
    try:
        r = subprocess.run(args, capture_output=True, timeout=30, shell=False, stdin=subprocess.DEVNULL, creationflags=SEM_JANELA)  # nosec B603
    except (OSError, subprocess.SubprocessError):
        return ""
    if r.returncode != 0:
        return ""
    bruto = r.stdout or b""
    if bruto.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in bruto[:200]:
        return bruto.decode("utf-16", "replace")
    try:
        return bruto.decode("utf-8")
    except UnicodeDecodeError:
        return bruto.decode("cp850", "replace")


def comando_da_tarefa(xml):
    """O <Command> do XML de uma tarefa (o XML do schtasks não muda com o idioma do Windows)."""
    m = re.search(r"<Command>(.*?)</Command>", str(xml or ""), re.S)
    return m.group(1).strip() if m else ""


def migrar_para_oculta(pasta_robo, cfg):
    """0.7.29: a leitura automática criada até a 0.7.28 chama o RODAR.bat (abre janela preta). Se houver o pythonw,
    recria a tarefa, com os mesmos horários do config, chamando o Python sem janela. Lê o comando pelo XML da tarefa
    (igual em qualquer idioma do Windows): qualquer comando que não seja o pythonw é recriado. Tarefa do próprio
    usuário, sem administrador. Devolve a mensagem, ou "" se não havia o que migrar."""
    if not disponivel() or not acao_oculta(pasta_robo):
        return ""
    nomes = [TAREFA] + sorted(set(re.findall(r'"\\?(' + re.escape(TAREFA) + r' \d\dh\d\d)"',
                                             _saida_inteira(["schtasks", "/query", "/fo", "csv", "/nh"]))))
    for nome in nomes:
        cmd = comando_da_tarefa(_saida_inteira(["schtasks", "/query", "/tn", nome, "/xml"]))
        if cmd and "pythonw" not in cmd.lower():
            horarios, dias = do_config(cfg)
            return agendar(pasta_robo, horarios, dias)[1]
    return ""


def caixa_erro(titulo, texto):
    """0.7.29: caixa de aviso do Windows (sem janela preta, um erro antes de a tela abrir não teria onde aparecer)."""
    if not disponivel():
        return False
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, str(texto), str(titulo), 0x10 | 0x40000)  # erro + sempre na frente
        return True
    except (OSError, AttributeError):
        return False


def desagendar():
    if not disponivel():
        return False, "Agendamento automático só no Windows."
    _apagar_tudo()
    return True, "Leitura automática desligada."


# Aviso no canto da tela do Windows ao terminar uma leitura. O texto vai por variável de ambiente (nada é montado no
# comando), e o PowerShell roda escondido, sem esperar.
_AVISO_PS = ("Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; "
             "$n = New-Object System.Windows.Forms.NotifyIcon; $n.Icon = [System.Drawing.SystemIcons]::Information; "
             "$n.BalloonTipTitle = $env:LEXSUITE_AVISO_TITULO; $n.BalloonTipText = $env:LEXSUITE_AVISO_TEXTO; "
             "$n.Visible = $true; $n.ShowBalloonTip(15000); Start-Sleep -Seconds 16; $n.Dispose()")


def notificar(titulo, texto):
    """Mostra o aviso e devolve True se conseguiu disparar. Fora do Windows não faz nada."""
    if not disponivel():
        return False
    env = dict(os.environ, LEXSUITE_AVISO_TITULO=str(titulo)[:60], LEXSUITE_AVISO_TEXTO=str(texto)[:250])
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", _AVISO_PS],  # nosec B603 B607
                         env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except OSError:
        return False


def texto_aviso(situacao, marca_curto="RADAR"):
    """Texto do aviso a partir da situação devolvida por radar.executar."""
    s = situacao or {}
    novas = int(s.get("novas") or 0)
    if not novas:
        return "Leitura terminada: nenhuma ação nova contra empresas nos tribunais acompanhados."
    frase = "1 ação nova contra empresa" if novas == 1 else f"{novas} ações novas contra empresas"
    return f"Leitura terminada: {frase}. Abra o {marca_curto} para ver a lista."
