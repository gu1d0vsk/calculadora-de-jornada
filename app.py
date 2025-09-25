import streamlit as st
import datetime

# Função para formatar a entrada de hora (HHMM ou HH:MM)
def formatar_hora_input(input_str):
    input_str = input_str.strip()
    if ':' in input_str:
        return input_str
    
    if len(input_str) == 3:
        input_str = '0' + input_str
    if len(input_str) != 4 or not input_str.isdigit():
        raise ValueError("Formato de hora inválido.")
    
    hora_formatada = f"{input_str[:2]}:{input_str[2:]}"
    return hora_formatada

# Função para calcular o tempo no núcleo
def calcular_tempo_nucleo(entrada, saida, saida_almoco, retorno_almoco):
    nucleo_inicio = entrada.replace(hour=9, minute=0, second=0, microsecond=0)
    nucleo_fim = entrada.replace(hour=18, minute=0, second=0, microsecond=0)
    inicio_trabalho_nucleo = max(entrada, nucleo_inicio)
    fim_trabalho_nucleo = min(saida, nucleo_fim)
    if inicio_trabalho_nucleo >= fim_trabalho_nucleo:
        return 0
    tempo_bruto_nucleo_segundos = (fim_trabalho_nucleo - inicio_trabalho_nucleo).total_seconds()
    tempo_bruto_nucleo_minutos = tempo_bruto_nucleo_segundos / 60
    tempo_almoco_nucleo_minutos = 0
    if saida_almoco and retorno_almoco:
        inicio_almoco_nucleo = max(saida_almoco, nucleo_inicio)
        fim_almoco_nucleo = min(retorno_almoco, nucleo_fim)
        if inicio_almoco_nucleo < fim_almoco_nucleo:
            tempo_almoco_nucleo_segundos = (fim_almoco_nucleo - inicio_almoco_nucleo).total_seconds()
            tempo_almoco_nucleo_minutos = tempo_almoco_nucleo_segundos / 60
    tempo_liquido_nucleo = tempo_bruto_nucleo_minutos - tempo_almoco_nucleo_minutos
    return max(0, tempo_liquido_nucleo)

# --- Criação da Interface do Web App com Streamlit ---
st.set_page_config(page_title="Calculadora de Jornada", layout="wide")
st.title("Calculadora de Jornada")
st.subheader("Informe seus horários para calcular a jornada")

# Campos de entrada
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        entrada_str = st.text_input("Entrada (HHMM ou HH:MM):", key="entrada")
        saida_almoco_str = st.text_input("Saída Almoço (HHMM ou HH:MM):", key="saida_almoco")
    with col2:
        retorno_almoco_str = st.text_input("Volta Almoço (HHMM ou HH:MM):", key="retorno_almoco")
        saida_real_str = st.text_input("Saída (HHMM ou HH:MM):", key="saida_real")

# Botão de cálculo
if st.button("Calcular"):
    try:
        hora_entrada = datetime.datetime.strptime(formatar_hora_input(entrada_str), "%H:%M")

        # Determina a duração do almoço/intervalo para as previsões
        duracao_almoço_previsao = 30
        if saida_almoco_str and retorno_almoco_str:
            saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
            retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
            duracao_almoço_previsao = (retorno_almoco - saida_almoco).total_seconds() / 60
            if duracao_almoço_previsao < 0:
                st.error("O tempo de retorno do almoço deve ser depois do tempo de saída.")
                st.stop()

        # --- Parte 1: Cálculo das previsões ---
        minutos_intervalo_5h = max(15, duracao_almoço_previsao)
        hora_nucleo_inicio = hora_entrada.replace(hour=9, minute=0, second=0, microsecond=0)
        if hora_entrada.time() < datetime.time(9, 0):
            hora_saida_5h = hora_nucleo_inicio + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
        else:
            hora_saida_5h = hora_entrada + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
        
        minutos_intervalo_demais = max(30, duracao_almoço_previsao)
        hora_saida_8h = hora_entrada + datetime.timedelta(hours=8, minutes=minutos_intervalo_demais)
        hora_saida_10h = hora_entrada + datetime.timedelta(hours=10, minutes=minutos_intervalo_demais)
        
        termo_5h = "intervalo" if (hora_saida_5h - hora_entrada).total_seconds()/60 < 360 else "almoço"
        termo_8h = "intervalo" if (hora_saida_8h - hora_entrada).total_seconds()/60 < 360 else "almoço"
        termo_10h = "intervalo" if (hora_saida_10h - hora_entrada).total_seconds()/60 < 360 else "almoço"
        
        st.header("Previsões de Saída")
        st.markdown(f"""
        - Mínimo: **{hora_saida_5h.strftime('%H:%M')}** ({minutos_intervalo_5h:.0f}min de {termo_5h})
        - Zerado: **{hora_saida_8h.strftime('%H:%M')}** ({minutos_intervalo_demais:.0f}min de {termo_8h})
        - Máximo: **{hora_saida_10h.strftime('%H:%M')}** ({minutos_intervalo_demais:.0f}min de {termo_10h})
        """)
        
        # --- Parte 2: Resumo do dia (se houver dados de saída) ---
        if saida_almoco_str and retorno_almoco_str and saida_real_str:
            saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
            retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
            hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
            
            duracao_almoco_minutos_real = (retorno_almoco - saida_almoco).total_seconds() / 60
            trabalho_bruto_minutos = (hora_saida_real - hora_entrada).total_seconds() / 60
            
            if trabalho_bruto_minutos < 360:
                duracao_almoço_para_calculo = max(15, duracao_almoco_minutos_real)
            else:
                duracao_almoço_para_calculo = max(30, duracao_almoco_minutos_real)
                
            trabalho_liquido_minutos = trabalho_bruto_minutos - duracao_almoço_para_calculo
            
            horas_trabalhadas = int(trabalho_liquido_minutos // 60)
            minutos_trabalhados = int(trabalho_liquido_minutos % 60)
            
            saldo_banco_horas_minutos = trabalho_liquido_minutos - 480
            saldo_horas = int(abs(saldo_banco_horas_minutos) // 60)
            saldo_minutos = int(abs(saldo_banco_horas_minutos) % 60)
            saldo_texto = f"{saldo_horas}h e {saldo_minutos}min"
            
            saldo_string = f"Saldo no banco de horas: Ganhei {saldo_texto}" if saldo_banco_horas_minutos >= 0 else f"Saldo no banco de horas: Perdi {saldo_texto}"
            
            min_intervalo_real = 15 if trabalho_liquido_minutos < 360 else 30
            termo_intervalo_real = "intervalo" if trabalho_liquido_minutos < 360 else "almoço"
            
            tempo_nucleo_minutos = calcular_tempo_nucleo(hora_entrada, hora_saida_real, saida_almoco, retorno_almoco)
            
            aviso_nao_autorizado = ""
            if duracao_almoco_minutos_real < min_intervalo_real:
                aviso_nao_autorizado += f"- {termo_intervalo_real.capitalize()} inferior a {min_intervalo_real} minutos."
            if trabalho_liquido_minutos > 600:
                aviso_nao_autorizado += "\n- Jornada maior que 10h."
            if hora_saida_real.time() > datetime.time(20, 0):
                aviso_nao_autorizado += "\n- Saída depois das 20h."

            if aviso_nao_autorizado:
                st.header("‼️ PERMANÊNCIA NÃO AUTORIZADA ‼️")
                st.markdown(f"**Motivos:**{aviso_nao_autorizado}")
            
            st.header("Resumo do seu dia")
            st.markdown(f"""
            - Você trabalhou: **{horas_trabalhadas}h e {minutos_trabalhados}min**
            - Tempo de {termo_intervalo_real}: **{duracao_almoco_minutos_real:.0f}min**
            - {saldo_string}
            - Tempo no núcleo (9h-18h): **{int(tempo_nucleo_minutos // 60)}h e {int(tempo_nucleo_minutos % 60)}min**
            """)

            if tempo_nucleo_minutos < 300:
                st.warning("Não cumpriu as 5h no núcleo.")
    except ValueError as e:
        st.error(f"Erro no formato da hora. O formato deve ser HHMM ou HH:MM.")
