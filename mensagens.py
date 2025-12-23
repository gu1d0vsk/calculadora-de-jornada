import datetime
import pytz

def obter_mensagem_do_dia():
    """Retorna uma mensagem engraçada baseada no dia da semana."""
    fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.date.today().weekday() # Segunda é 0 e Domingo é 6
    mensagens = {
        0: "Boas Festas!!🎉🍾",
        1: "Boas Festas!!🎉🍾",
        2: "Boas Festas!!🎉🍾",
        3: "Boas Festas!!🎉🍾",
        4: "Boas Festas!!🎉🍾",
        5: "Boas Festas!!🎉🍾",
        6: "Boas Festas!!🎉🍾"
    }
    return mensagens.get(hoje, "Calculadora de Jornada")
