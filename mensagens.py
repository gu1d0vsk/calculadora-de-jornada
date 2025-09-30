import datetime

def obter_mensagem_do_dia():
    """Retorna uma mensagem engraçada baseada no dia da semana."""
    hoje = datetime.date.today().weekday() # Segunda é 0 e Domingo é 6
    mensagens = {
        0: "Segundou, EBA!!",
        1: "Terça-feira 📌",
        2: "Quarta-feira, semana praticamente encerrada.",
        3: "Quinta-feira 📆",
        4: "Sextou! Quem fez, fez.",
        5: "Sábado",
        6: "Domingo"
    }
    return mensagens.get(hoje, "Calculadora de Jornada")
