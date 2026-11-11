"""Saúde do robô sem IA: olha o resultado de cada rodada e diz se alguma fonte mudou ou parou.
É o sensor que decide quando chamar a manutenção (gente ou IA). Cada aviso vai para o banco e para a aba Saúde."""

import datetime as dt

from . import prazos


def avaliar(pubs, novos, receita_consultas=0, receita_falhas=0, hoje=None, ja_conferidos=0):
    """Devolve uma lista de {fonte, situacao (ok | atenção | erro), detalhe}. 0.7.29: `ja_conferidos` = Diários do período
    que já tinham sido lidos numa leitura anterior; sem publicação nova por isso não é alarme."""
    hoje = hoje or dt.date.today()
    saida = []
    n = len(pubs or [])
    if n == 0 and ja_conferidos:
        saida.append({"fonte": "DJEN", "situacao": "ok",
                      "detalhe": f"Nada novo: os {ja_conferidos} Diário(s) do período já tinham sido conferidos numa leitura anterior."})
    elif n == 0:
        saida.append({"fonte": "DJEN", "situacao": "atenção" if prazos.dia_util(hoje) else "ok",
                      "detalhe": "Nenhuma publicação lida. Em dia útil, confira se o Diário saiu e se o computador está no Brasil."})
    else:
        sem_campos = sum(1 for p in pubs if not p.get("processo") or not p.get("texto"))
        taxa = sem_campos / n
        if taxa > 0.2:
            saida.append({"fonte": "DJEN", "situacao": "erro",
                          "detalhe": f"{taxa:.0%} das publicações sem número de processo ou sem texto: o formato do DJEN pode ter mudado."})
        else:
            saida.append({"fonte": "DJEN", "situacao": "ok", "detalhe": f"{n} publicações lidas; campos esperados presentes."})
        taxa_novas = len(novos or []) / n
        if taxa_novas > 0.3:
            saida.append({"fonte": "Regra de ação nova", "situacao": "atenção",
                          "detalhe": f"{taxa_novas:.0%} das publicações viraram ação nova: a regra está frouxa."})
        elif not novos and n > 1000:
            saida.append({"fonte": "Regra de ação nova", "situacao": "atenção",
                          "detalhe": "Nenhuma ação nova em um Diário grande: a regra pode ter parado de casar."})
        else:
            saida.append({"fonte": "Regra de ação nova", "situacao": "ok", "detalhe": f"{len(novos or [])} ações novas em {n} publicações."})
    if receita_consultas:
        taxa = receita_falhas / receita_consultas
        saida.append({"fonte": "Receita (CNPJ)", "situacao": "erro" if taxa > 0.5 else "atenção" if taxa > 0.2 else "ok",
                      "detalhe": f"{receita_consultas} consultas, {receita_falhas} sem resposta."})
    return saida


def registrar(banco, avaliacoes, aviso=print):
    for a in avaliacoes:
        banco.registrar("saude", a)
        if a["situacao"] != "ok":
            aviso(f"  Saúde [{a['situacao']}] {a['fonte']}: {a['detalhe']}")
