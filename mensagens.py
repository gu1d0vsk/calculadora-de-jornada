import datetime
import pytz

def obter_mensagem_do_dia():
    """Retorna uma mensagem engraçada baseada no dia da semana."""
    fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.date.today().weekday() # Segunda é 0 e Domingo é 6
    mensagens = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo"
    }
    return mensagens.get(hoje, "Calculadora de Jornada")
