import streamlit as st
import datetime

# --- Funções de Lógica ---

def formatar_hora_input(input_str):
    """Formata a entrada de hora (HHMM ou HH:MM) para o formato HH:MM."""
    input_str = input_str.strip()
    if ':' in input_str:
        return input_str
    
    if len(input_str) == 3:
        input_str = '0' + input_str
    if len(input_str) != 4 or not input_str.isdigit():
        raise ValueError("Formato de hora inválido.")
    
    return f"{input_str[:2]}:{input_str[2:]}"

def calcular_tempo_nucleo(entrada, saida, saida_almoco, retorno_almoco):
    """Calcula o tempo trabalhado dentro do horário núcleo (9h às 18h)."""
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

# --- Interface do Web App com Streamlit ---
st.set_page_config(page_title="Calculadora de Jornada", layout="centered")

# Injeção de CSS para customização
st.markdown("""
<style>
    /* Limita a largura do container principal */
    .main .block-container {
        max-width: 800px;
    }
    /* Estiliza o título principal customizado */
    .main-title {
        
        font-size: 2.5rem !important;
        font-weight: bold;
    }
    /* Estiliza o subtítulo customizado */
    .sub-title {
        color: gray;
        font-size: 1.5rem !important;
    }
    /* Estiliza o botão de cálculo */
    div[data-testid="stButton"] > button {
        background-color: rgb(92, 228, 136);
        color: #FFFFFF;
    }
    /* Arredonda as caixas de input de texto */
    div[data-testid="stTextInput"] input {
        border-radius: 1.5rem !important;}
        .st-aw {
    border-bottom-right-radius: 1.5rem;
}
.st-av {
    border-top-right-radius: 1.5rem;
}
.st-au {
    border-bottom-left-radius: 1.5rem;
}
.st-at {
    border-top-left-radius: 1.5rem;
}
    

""", unsafe_allow_html=True)


st.markdown('<p class="main-title">Calculadora de Jornada de Trabalho</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Informe seus horários para calcular a jornada diária</p>', unsafe_allow_html=True)

# Layout dos campos de entrada otimizado para desktop e mobile
with st.container():
    entrada_str = st.text_input("Entrada", key="entrada")
    col1, col2 = st.columns(2)
    with col1:
        saida_almoco_str = st.text_input("Saída Almoço", key="saida_almoco")
    with col2:
        retorno_almoco_str = st.text_input("Volta Almoço", key="retorno_almoco")
    saida_real_str = st.text_input("Saída", key="saida_real")


if st.button("Calcular"):
    if not entrada_str:
        st.warning("Por favor, preencha pelo menos o horário de entrada.")
    else:
        try:
            hora_entrada = datetime.datetime.strptime(formatar_hora_input(entrada_str), "%H:%M")

            # --- Parte 1: Cálculo das previsões ---
            st.header("Previsões de Saída")
            duracao_almoço_previsao = 0
            if saida_almoco_str and retorno_almoco_str:
                saida_almoco_prev = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                retorno_almoco_prev = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                duracao_almoço_previsao = (retorno_almoco_prev - saida_almoco_prev).total_seconds() / 60

            minutos_intervalo_5h = max(15, duracao_almoço_previsao)
            hora_nucleo_inicio = hora_entrada.replace(hour=9, minute=0)
            hora_base_5h = max(hora_entrada, hora_nucleo_inicio)
            hora_saida_5h = hora_base_5h + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
            
            minutos_intervalo_demais = max(30, duracao_almoço_previsao)
            hora_saida_8h = hora_entrada + datetime.timedelta(hours=8, minutes=minutos_intervalo_demais)
            hora_saida_10h = hora_entrada + datetime.timedelta(hours=10, minutes=minutos_intervalo_demais)
            
            st.markdown(f"""
            - **Mínimo (5h no núcleo):** {hora_saida_5h.strftime('%H:%M')} (com {minutos_intervalo_5h:.0f}min de intervalo)
            - **Jornada Padrão (8h):** {hora_saida_8h.strftime('%H:%M')} (com {minutos_intervalo_demais:.0f}min de almoço)
            - **Máximo (10h):** {hora_saida_10h.strftime('%H:%M')} (com {minutos_intervalo_demais:.0f}min de almoço)
            """)
            
            # --- Parte 2: Resumo do dia (se houver dados de saída) ---
            if saida_real_str:
                hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
                
                if hora_saida_real < hora_entrada:
                    st.error("Verifique a ordem dos horários. A Saída deve ser depois da Entrada.")
                    st.stop()

                saida_almoco = None
                retorno_almoco = None
                duracao_almoco_minutos_real = 0

                if saida_almoco_str and retorno_almoco_str:
                    saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                    retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                    if retorno_almoco < saida_almoco:
                        st.error("A volta do almoço deve ser depois da saída para o almoço.")
                        st.stop()
                    duracao_almoco_minutos_real = (retorno_almoco - saida_almoco).total_seconds() / 60

                trabalho_bruto_minutos = (hora_saida_real - hora_entrada).total_seconds() / 60
                
                # Calcula o tempo de trabalho real (descontando o intervalo tirado) para determinar o intervalo obrigatório
                tempo_trabalhado_efetivo = trabalho_bruto_minutos - duracao_almoco_minutos_real

                # Define o intervalo mínimo e o termo apropriado com base na jornada efetivamente trabalhada
                if tempo_trabalhado_efetivo > 360: # Acima de 6h de trabalho
                    min_intervalo_real = 30
                    termo_intervalo_real = "almoço"
                elif tempo_trabalhado_efetivo > 240: # De 4h a 6h de trabalho
                    min_intervalo_real = 15
                    termo_intervalo_real = "intervalo"
                else: # Até 4h de trabalho
                    min_intervalo_real = 0
                    termo_intervalo_real = "intervalo"

                # Para o cálculo do saldo, deduzimos o maior valor entre o intervalo tirado e o obrigatório.
                duracao_almoço_para_calculo = max(min_intervalo_real, duracao_almoco_minutos_real)
                    
                trabalho_liquido_minutos = trabalho_bruto_minutos - duracao_almoço_para_calculo
                
                horas_trabalhadas = int(trabalho_liquido_minutos // 60)
                minutos_trabalhados = int(trabalho_liquido_minutos % 60)
                
                saldo_banco_horas_minutos = trabalho_liquido_minutos - 480  # 8 horas = 480 minutos

                # Exibição do resumo
                st.header("Resumo do Dia")
                
                saldo_horas = int(abs(saldo_banco_horas_minutos) // 60)
                saldo_minutos = int(abs(saldo_banco_horas_minutos) % 60)
                saldo_texto = f"{saldo_horas}h e {saldo_minutos}min"
                saldo_string = f"Saldo positivo de {saldo_texto}" if saldo_banco_horas_minutos >= 0 else f"Saldo negativo de {saldo_texto}"
                
                tempo_nucleo_minutos = calcular_tempo_nucleo(hora_entrada, hora_saida_real, saida_almoco, retorno_almoco)
                
                # Monta a string do resumo dinamicamente
                resumo_texto = f"""
                - **Tempo total trabalhado:** {horas_trabalhadas}h e {minutos_trabalhados}min
                """
                if duracao_almoco_minutos_real > 0:
                    resumo_texto += f"- **Tempo de {termo_intervalo_real}:** {duracao_almoco_minutos_real:.0f}min\n"
                
                resumo_texto += f"""
                - **Saldo do dia:** {saldo_string}
                - **Tempo no núcleo (9h-18h):** {int(tempo_nucleo_minutos // 60)}h e {int(tempo_nucleo_minutos % 60)}min
                """
                st.markdown(resumo_texto)


                if tempo_nucleo_minutos < 300: # 5 horas = 300 minutos
                    st.warning("Atenção: Não cumpriu as 5h obrigatórias no período núcleo.")

                # Avisos de permanência não autorizada
                aviso_nao_autorizado = ""
                if min_intervalo_real > 0 and duracao_almoco_minutos_real < min_intervalo_real:
                    aviso_nao_autorizado += f"\n- {termo_intervalo_real.capitalize()} foi inferior a {min_intervalo_real} minutos."
                if trabalho_liquido_minutos > 600: # 10 horas = 600 minutos
                    aviso_nao_autorizado += "\n- Jornada de trabalho excedeu 10 horas."
                if hora_saida_real.time() > datetime.time(20, 0):
                    aviso_nao_autorizado += "\n- Saída registrada após as 20h."

                if aviso_nao_autorizado:
                    st.error(f"‼️ ATENÇÃO: POSSÍVEL PERMANÊNCIA NÃO AUTORIZADA ‼️\n**Motivos:**{aviso_nao_autorizado}")

        except ValueError as e:
            st.error(f"Erro no formato da hora. Use HHMM ou HH:MM.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
