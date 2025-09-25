import streamlit as st
import datetime

# --- Configuração da Página e Estilos ---
st.set_page_config(page_title="Calculadora de Jornada")

st.markdown("""
    <style>
    .reportview-container .main {
        background-color: #262730;
        color: white;
        max-width: 800px;
        margin: auto;
    }
    .stApp {
        background-color: #262730;
    }
    .st-bu, .st-b5 {
        border-radius: 15px;
        padding: 20px;
    }
    .st-bx, .st-b_ {
        border-radius: 15px;
    }
    .st-dp, .st-dq {
        border-radius: 15px;
    }
    .st-dg, .st-dh {
        color: #f77f00;
        font-weight: bold;
    }
    .st-c4 {
        border: 2px solid #5a5a66;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 20px;
        width: 100%;
    }
    .st-c5 {
        background-color: #2f2f3f;
    }
    .st-c6 {
        border: 2px solid #5a5a66;
        border-radius: 15px;
    }
    /* Estilo para aumentar a fonte dos campos de texto e labels */
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    .stTextInput>label {
        font-size: 18px !important;
    }
    .stMarkdown p {
        font-size: 16px;
    }
    /* Estilo para a cor dos títulos principais */
    h1 {
        color: rgb(255, 75, 75);
    }
    /* Estilo para a cor do botão */
    .stButton>button {
        background-color: rgb(92, 228, 136);
        color: black;
        border: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Funções de Lógica ---
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

# --- Interface e Lógica Principal ---
st.title("Calculadora de Horários de Trabalho")
st.markdown("Calcule seu horário de trabalho ideal e acompanhe a conformidade com as políticas da empresa")

col_entrada, col_previsao = st.columns(2)

with col_entrada:
    st.markdown("## ✍️ Entrada de Horários")
    with st.container(border=True):
        hora_entrada_str = st.text_input("Horário de Entrada", placeholder="HH:MM ou HHMM")
        
        st.markdown("---")
        
        saida_almoco_str = st.text_input("Início do Almoço", placeholder="HH:MM ou HHMM")
        retorno_almoco_str = st.text_input("Fim do Almoço", placeholder="HH:MM ou HHMM")
        
        st.markdown("---")
        
        saida_real_str = st.text_input("Horário de Saída", placeholder="HH:MM ou HHMM")
        st.markdown("<small><i>Opcional - para calcular o resumo real de trabalho</i></small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Calcular Horários", use_container_width=True):
            st.session_state.calcular = True
        
if 'calcular' not in st.session_state:
    st.session_state.calcular = False

with col_previsao:
    st.markdown("## 📈 Previsões de Horário")
    with st.container(border=True):
        if st.session_state.calcular:
            try:
                hora_entrada = datetime.datetime.strptime(formatar_hora_input(hora_entrada_str), "%H:%M")

                duracao_almoço_previsao = 0
                if saida_almoco_str and retorno_almoco_str:
                    saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                    retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                    duracao_almoço_previsao = (retorno_almoco - saida_almoco).total_seconds() / 60
                    if duracao_almoço_previsao < 0:
                        st.error("O tempo de retorno do almoço deve ser depois do tempo de saída.")
                        st.stop()

                minutos_intervalo_5h = max(15, duracao_almoço_previsao)
                hora_nucleo_inicio = hora_entrada.replace(hour=9, minute=0, second=0, microsecond=0)
                if hora_entrada.time() < datetime.time(9, 0):
                    hora_saida_5h = hora_nucleo_inicio + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
                else:
                    hora_saida_5h = hora_entrada + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
                
                minutos_intervalo_demais = max(30, duracao_almoço_previsao)
                hora_saida_8h = hora_entrada + datetime.timedelta(hours=8, minutes=minutos_intervalo_demais)
                hora_saida_10h = hora_entrada + datetime.timedelta(hours=10, minutes=minutos_intervalo_demais)

                st.markdown(f"**Mínimo (5h)**\n{hora_saida_5h.strftime('%H:%M')}\n<small>{minutos_intervalo_5h:.0f}min de intervalo</small>", unsafe_allow_html=True)
                st.markdown(f"**Equilibrado (8h)**\n{hora_saida_8h.strftime('%H:%M')}\n<small>{minutos_intervalo_demais:.0f}min de almoço</small>", unsafe_allow_html=True)
                st.markdown(f"**Máximo (10h)**\n{hora_saida_10h.strftime('%H:%M')}\n<small>{minutos_intervalo_demais:.0f}min de almoço</small>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                st.subheader("Conformidade de Horário Central")
                if saida_almoco_str and retorno_almoco_str and saida_real_str:
                    saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                    retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                    hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
                    
                    tempo_nucleo_minutos = calcular_tempo_nucleo(hora_entrada, hora_saida_real, saida_almoco, retorno_almoco)
                    
                    if tempo_nucleo_minutos >= 300: # 5 horas
                        st.success("✅ 5 horas cumpridas")
                    else:
                        st.warning(f"⚠️ **{int(tempo_nucleo_minutos // 60)}h e {int(tempo_nucleo_minutos % 60)}min** - Não cumpriu o mínimo de 5h no núcleo.")

                else:
                    st.info("Aguardando cálculo")
            
            except ValueError:
                st.error("Formato de hora inválido.")

# --- Footer com cards de informação ---
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.info("ℹ️ **Horário Central**\nMínimo de 5 horas entre 9:00 e 18:00 obrigatório diariamente", icon=None)

with col_footer2:
    st.success("✅ **Horário Flexível**\nInicie entre 7:00 e 10:00, jornada equilibrada de 8 horas", icon=None)

with col_footer3:
    st.warning("⚠️ **Política de Intervalo**\nMínimo 15min para turnos <6h, 30min para turnos longos", icon=None)
