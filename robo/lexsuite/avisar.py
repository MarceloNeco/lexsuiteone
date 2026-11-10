"""Avisos: e-mail no fim de cada rodada e Telegram na hora (monitor).

Senha e token NUNCA ficam em arquivo: o robô lê das variáveis de ambiente
LEXSUITE_SMTP_SENHA (no Gmail, uma "senha de app", não a senha da conta) e
LEXSUITE_TELEGRAM_TOKEN (o código que o @BotFather entrega). Sem a variável,
o robô só pula aquele aviso e diz por quê.
"""

import datetime as dt
import html
import json
import os
import smtplib
import ssl
import time
import urllib.error
import urllib.request
from email.message import EmailMessage

from . import config


def enviar(cfg, assunto, html, anexos=()):
    senha = os.environ.get("LEXSUITE_SMTP_SENHA")
    if not cfg.get("ativo") or not senha:
        return "E-mail não enviado (desligado na config ou sem a variável LEXSUITE_SMTP_SENHA)."
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = assunto, cfg["de"], ", ".join(cfg["para"])
    msg.set_content("Abra este e-mail num programa que mostre HTML.")
    msg.add_alternative(html, subtype="html")
    for caminho in anexos:
        with open(caminho, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream",
                               filename=os.path.basename(caminho))
    with smtplib.SMTP(cfg.get("servidor", "smtp.gmail.com"), int(cfg.get("porta", 587)), timeout=60) as s:
        s.starttls(context=ssl.create_default_context())
        s.login(cfg["de"], senha)
        s.send_message(msg)
    return f"E-mail enviado para {', '.join(cfg['para'])}."


def resumo_html(painel):
    e = html.escape  # nomes de empresa vêm de fora: nunca entram no HTML sem limpeza
    leads = painel.get("leads") or []
    altas = [l for l in leads if l.get("faixa") == "Alta"]
    linhas = "".join(
        f"<tr><td>{e(str(l['faixa']))}</td><td>{l['nota']}</td><td>{e(', '.join(l['empresas']))}</td>"
        f"<td>{e(l['processo'])}</td><td>{e(l['rito'])}</td></tr>" for l in leads[:15])
    v = painel.get("vara_stats") or {}
    return f"""<div style="font-family:Arial,sans-serif;max-width:640px">
<h2 style="margin:0">LexSuiteONE · JUDICIAL</h2>
<p>{e(v.get('vara', ''))} ({e(v.get('tribunal', ''))}) — atualizado em {e(painel.get('gerado_em', ''))}</p>
<p><b>{len(leads)}</b> ações novas contra empresas · <b>{len(altas)}</b> com prioridade alta.</p>
<table border="1" cellpadding="6" style="border-collapse:collapse;font-size:13px">
<tr><th>Prioridade</th><th>Nota</th><th>Empresa(s)</th><th>Processo</th><th>Rito</th></tr>{linhas}</table>
<p style="color:#666;font-size:12px">Fonte: DJEN e DataJud (CNJ), dados públicos. Pessoas físicas não aparecem.</p></div>"""


# --- Monitor ---------------------------------------------------------------

def _data_br(iso):
    try:
        return config.data_curta(str(iso)[:10])
    except ValueError:
        return ""


def telegram(cfg, textos):
    """Manda cada texto como uma mensagem do bot. Devolve (enviadas, recado)."""
    token = os.environ.get("LEXSUITE_TELEGRAM_TOKEN")
    if not cfg.get("ativo") or not cfg.get("chat_id"):
        return 0, "Telegram desligado na config."
    if not token:
        return 0, "Telegram não enviado: falta a variável LEXSUITE_TELEGRAM_TOKEN."
    enviadas = 0
    for n, texto in enumerate(textos):
        if n:
            time.sleep(3)  # grupos aceitam ~20 mensagens por minuto
        corpo = json.dumps({"chat_id": cfg["chat_id"], "text": texto[:4096], "parse_mode": "HTML",
                            "disable_web_page_preview": True}).encode("utf-8")
        for tentativa in (1, 2):
            req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=corpo,
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30):  # nosec B310 - URL fixa https da API do Telegram
                    enviadas += 1
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and tentativa == 1:
                    try:
                        espera = int(json.loads(e.read().decode("utf-8"))["parameters"]["retry_after"])
                    except (ValueError, KeyError, TypeError):
                        espera = 30
                    time.sleep(min(espera, 60))
                    continue
                # Nunca mostrar o endereço do pedido: ele contém o token.
                return enviadas, f"Telegram recusou (HTTP {e.code}). Confira o chat_id e se o bot está no grupo."
            except (urllib.error.URLError, TimeoutError):
                return enviadas, "Telegram fora do ar ou sem internet; tento de novo na próxima rodada."
    return enviadas, f"Telegram: {enviadas} mensagem(ns) enviada(s)."


def agrupar(blocos, limite=3800, max_mensagens=10):
    """Junta os avisos em poucas mensagens (cada uma até ~3.800 letras), urgentes primeiro."""
    msgs, atual = [], ""
    for b in blocos:
        if atual and len(atual) + len(b) + 2 > limite:
            msgs.append(atual)
            atual = ""
        atual = (atual + "\n\n" + b) if atual else b
    if atual:
        msgs.append(atual)
    if len(msgs) > max_mensagens:
        resto = len(msgs) - max_mensagens + 1
        msgs = msgs[:max_mensagens - 1] + [f"… e mais {resto} mensagem(ns) de avisos. Veja o e-mail ou a caixa de publicações."]
    return msgs


def descobrir_chats():
    """Lista os grupos/conversas em que o bot já recebeu mensagem (para achar o chat_id)."""
    token = os.environ.get("LEXSUITE_TELEGRAM_TOKEN")
    if not token:
        return None, "Falta a variável LEXSUITE_TELEGRAM_TOKEN."
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30) as r:  # nosec B310 - URL fixa https
            dados = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"Telegram recusou (HTTP {e.code}). Confira o token."
    except (urllib.error.URLError, TimeoutError):
        return None, "Sem resposta do Telegram."
    chats = {}
    for u in dados.get("result") or []:
        for chave in ("message", "my_chat_member", "channel_post", "edited_message"):
            chat = (u.get(chave) or {}).get("chat")
            if chat:
                chats[chat["id"]] = chat.get("title") or chat.get("first_name") or chat.get("username") or ""
    return chats, ""


def texto_telegram(item, com_trecho=True):
    e = html.escape
    linhas = [f"<b>{e(item['urgencia'].upper())} · {e(item['ato'])}</b>",
              f"<code>{e(item.get('processo') or '')}</code> · {e(item.get('tribunal') or '')}",
              e(item.get("orgao") or "")]
    if item.get("cliente"):
        linhas.append(f"Cliente: {e(item['cliente'])}")
    datas = f"Disponibilizada {_data_br(item.get('data'))} · publicação {_data_br(item.get('publicacao'))}"
    if item.get("vencimento"):
        datas += f" · prazo de {item['dias_prazo']} dias vence ~{_data_br(item['vencimento'])}"
    elif item.get("inicio_prazo"):
        datas += f" · prazos começam {_data_br(item['inicio_prazo'])}"
    linhas.append(datas)
    if com_trecho and item.get("trecho"):
        linhas.append(f"<i>{e(item['trecho'][:350])}</i>")
    if item.get("link"):
        linhas.append(f'<a href="{e(item["link"], quote=True)}">Abrir publicação</a>')
    return "\n".join(l for l in linhas if l)


def monitor_html(novas, com_trecho=True):
    e = html.escape
    cores = {"Urgente": "#a3302a", "Alta": "#a87a2e", "Normal": "#4a5568"}
    blocos = []
    for i in novas:
        prazo = (f"prazo de {i['dias_prazo']} dias · vence ~{_data_br(i['vencimento'])}" if i.get("vencimento")
                 else f"prazos começam {_data_br(i.get('inicio_prazo'))}" if i.get("inicio_prazo") else "")
        link = f'<a href="{e(i["link"], quote=True)}">Abrir publicação</a>' if i.get("link") else ""
        trecho_html = (f'<div style="color:#333;font-size:13px;margin-top:6px">{e(i["trecho"])}</div>'
                       if com_trecho and i.get("trecho") else "")
        blocos.append(f"""<div style="border-left:4px solid {cores.get(i['urgencia'], '#4a5568')};padding:8px 12px;margin:10px 0;background:#f7f7f9">
<b style="color:{cores.get(i['urgencia'], '#4a5568')}">{e(i['urgencia'])}</b> · <b>{e(i['ato'])}</b><br>
<span style="font-family:monospace">{e(i.get('processo') or '')}</span> · {e(i.get('tribunal') or '')} · {e(i.get('orgao') or '')}<br>
{('Cliente: ' + e(i['cliente']) + '<br>') if i.get('cliente') else ''}
Disponibilizada {_data_br(i.get('data'))} · publicação {_data_br(i.get('publicacao'))}{(' · ' + prazo) if prazo else ''}<br>
<span style="color:#666;font-size:12px">Por que avisou: {e('; '.join(i.get('motivos') or []))}</span> {link}{trecho_html}</div>""")
    return f"""<div style="font-family:Arial,sans-serif;max-width:680px">
<h2 style="margin:0">LexSuiteONE · Monitor de publicações</h2>
<p>{len(novas)} publicação(ões) nova(s) no DJEN nos processos acompanhados.</p>{''.join(blocos)}
<p style="color:#666;font-size:12px">Datas de publicação e prazo são estimativas em dias úteis (feriados nacionais e
forenses; sem feriados locais). Confira sempre no processo. Fonte: DJEN (CNJ).</p></div>"""
