import streamlit as st
import datetime
import time
from eventos import *
from mensagens import obter_mensagem_do_dia
import requests
import pytz
import streamlit.components.v1 as components
import numpy as np

# --- Funções de Lógica ---

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_weather_forecast(exit_time):
    try:
        lat = -22.93
        lon = -43.17
        fuso_horario_brasil = "America/Sao_Paulo"
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability&timezone={fuso_horario_brasil}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        hourly_data = data['hourly']
        times = hourly_data['time']
        probabilities = hourly_data['precipitation_probability']
        fuso = pytz.timezone(fuso_horario_brasil)
        hoje = datetime.datetime.now(fuso).date()
        hora_saida = exit_time.time()
        timestamp_completo = datetime.datetime.combine(hoje, hora_saida)
        target_time_str = timestamp_completo.strftime('%Y-%m-%dT%H:00')
        if target_time_str in times:
            index = times.index(target_time_str)
            rain_prob = probabilities[index]
            if rain_prob >= 40:
                return f"☔ Leve o guarda-chuva! Há {rain_prob}% de chance de chuva por volta das {exit_time.strftime('%H:%M')}."
        return ""
    except Exception as e:
        print(f"Erro ao buscar previsão do tempo: {e}")
        return ""

def get_weather_icon(wmo_code):
    if wmo_code == 0: return "☀️"
    elif wmo_code in [1, 2, 3]: return "🌥️"
    elif wmo_code in [45, 48]: return "🌫️"
    elif wmo_code in [51, 53, 55, 56, 57]: return "🌦️"
    elif wmo_code in [61, 63, 65, 66, 67]: return "🌧️"
    elif wmo_code in [71, 73, 75, 77]: return "❄️"
    elif wmo_code in [80, 81, 82]: return "🌧️"
    elif wmo_code in [95, 96, 99]: return "⛈️"
    else: return "🌡️"

@st.cache_data(ttl=10800) # Cache de 3 horas
def get_daily_weather():
    try:
        lat = -22.93
        lon = -43.17
        fuso_horario_brasil = "America/Sao_Paulo"
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max&hourly=uv_index&timezone={fuso_horario_brasil}&forecast_days=1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily_data = data['daily']
        temp_min = daily_data['temperature_2m_min'][0]
        temp_max = daily_data['temperature_2m_max'][0]
        weather_code = daily_data['weather_code'][0]
        rain_prob = daily_data['precipitation_probability_max'][0]
        icon = get_weather_icon(weather_code)
        
        hourly_data = data['hourly']
        uv_index_midday = hourly_data['uv_index'][12]
        
        forecast_parts = [
            f"{icon} Hoje no Rio: Mínima de {temp_min:.0f}°C e Máxima de {temp_max:.0f}°C",
            f"💧 {rain_prob:.0f}%"
        ]
        
        uv_value = uv_index_midday
        if uv_value <= 2: uv_text = f"😎 UV ao meio-dia: {uv_value:.1f} (Baixo)"
        elif uv_value <= 5: uv_text = f"🙂 UV ao meio-dia: {uv_value:.1f} (Moderado)"
        elif uv_value <= 7: uv_text = f"🥵 UV ao meio-dia: {uv_value:.1f} (Alto)"
        elif uv_value <= 10: uv_text = f"⚠️ UV ao meio-dia: {uv_value:.1f} (Muito Alto)"
        else: uv_text = f"‼️ UV ao meio-dia: {uv_value:.1f} (Extremo)"
        
        forecast_parts.append(uv_text)
        return " | ".join(forecast_parts)
    except Exception as e:
        print(f"Erro ao buscar previsão diária: {e}")
        return ""

def verificar_eventos_proximos():
    fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.datetime.now(fuso_horario_brasil).date()
    mensagens = []
    eventos_agrupados = {}
    
    # LISTA UNIFICADA
    todos_os_dicionarios = [FERIADOS, DATAS_PAGAMENTO_VA_VR, DATAS_LIMITE_BENEFICIOS, DATAS_PAGAMENTO_SALARIO, DATAS_PAGAMENTO_13, DATAS_ADIANTAMENTO_SALARIO, CESTA_NATALINA]
    
    for d in todos_os_dicionarios:
        for data, nome in d.items():
            if data not in eventos_agrupados:
                eventos_agrupados[data] = []
            eventos_agrupados[data].append(nome)
            
    for data_evento, lista_nomes in sorted(eventos_agrupados.items()):
        delta = data_evento - hoje
        if 0 <= delta.days <= 12:
            if any("Crédito" in s or "Pagamento" in s or "13º" in s or "Adiantamento" in s or "Cesta" in s for s in lista_nomes): emoji = "💰"
            elif any("Data limite" in s for s in lista_nomes): emoji = "❗️"
            else: emoji = "🗓️"
            
            # Limpa os nomes (tira parenteses e espaços)
            partes_evento = [nome.split('(')[0].strip() for nome in lista_nomes]

            # Junta os nomes com vírgula e "e"
            if len(partes_evento) == 1: 
                texto_eventos = partes_evento[0]
            else: 
                texto_eventos = ", ".join(partes_evento[:-1]) + " e " + partes_evento[-1]
            
            # Formata a mensagem de forma concisa
            if delta.days == 0:
                mensagem = f"{emoji} Hoje: {texto_eventos}"
            elif delta.days == 1:
                mensagem = f"{emoji} Amanhã: {texto_eventos}"
            else:
                mensagem = f"{emoji} {delta.days} dias: {texto_eventos}"
                
            mensagens.append(mensagem)
    return mensagens

def gerar_contagem_regressiva_home_office():
    try:
        fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
        hoje = datetime.datetime.now(fuso_horario_brasil).date()
        data_home_office = datetime.date(2026, 2, 1)
        
        dias_restantes = (data_home_office - hoje).days
        if dias_restantes < 0: return ""

        # --- Cálculo de Dias Úteis ---
        # Definimos o feriado de São Sebastião (RJ) e outros que desejar
        feriados_rj = [
            '2026-01-01', # Ano Novo
            '2026-01-20', # São Sebastião (RJ)
        ]
        
        # O numpy.busday_count calcula dias úteis entre datas (exclui o dia final)
        dias_uteis = int(np.busday_count(hoje, data_home_office, holidays=feriados_rj))
        
        texto_dias = "dia" if dias_restantes == 1 else "dias"
        texto_uteis = "dia útil" if dias_uteis == 1 else "úteis"
        
        return f"<strong>Integra II:</strong> {dias_restantes} {texto_dias} ({dias_uteis} {texto_uteis}) para o home office"
    except Exception as e:
        print(f"Erro ao gerar contagem regressiva: {e}")
        return ""

def formatar_hora_input(input_str):
    input_str = input_str.strip()
    if ':' in input_str: return input_str
    if len(input_str) == 3: input_str = '0' + input_str
    if len(input_str) != 4 or not input_str.isdigit(): raise ValueError("Formato de hora inválido.")
    return f"{input_str[:2]}:{input_str[2:]}"

def calcular_tempo_nucleo(entrada, saida, saida_almoco, retorno_almoco):
    nucleo_inicio = entrada.replace(hour=9, minute=0, second=0, microsecond=0)
    nucleo_fim = entrada.replace(hour=18, minute=0, second=0, microsecond=0)
    inicio_trabalho_nucleo = max(entrada, nucleo_inicio)
    fim_trabalho_nucleo = min(saida, nucleo_fim)
    if inicio_trabalho_nucleo >= fim_trabalho_nucleo: return 0
    tempo_bruto_nucleo_segundos = (fim_trabalho_nucleo - inicio_trabalho_nucleo).total_seconds()
    tempo_almoco_no_nucleo_segundos = 0
    
    if saida_almoco and retorno_almoco:
        inicio_almoco_sobreposicao = max(inicio_trabalho_nucleo, saida_almoco)
        fim_almoco_sobreposicao = min(fim_trabalho_nucleo, retorno_almoco)
        if fim_almoco_sobreposicao > inicio_almoco_sobreposicao:
            tempo_almoco_no_nucleo_segundos = (fim_almoco_sobreposicao - inicio_almoco_sobreposicao).total_seconds()
            
    tempo_liquido_nucleo_segundos = tempo_bruto_nucleo_segundos - tempo_almoco_no_nucleo_segundos
    return max(0, tempo_liquido_nucleo_segundos / 60)

def formatar_duracao(minutos):
    if minutos < 0: minutos = 0
    horas = int(minutos // 60)
    mins = int(minutos % 60)
    return f"{horas}h {mins}min"

# --- Interface do Web App com Streamlit ---
st.set_page_config(page_title="Calculadora de Jornada", page_icon="🧮", layout="centered")

#----------------------
page_bg_img = """
<style>
[data-testid="stApp"] {
    background-image: linear-gradient(rgb(2, 45, 44) 0%, rgb(0, 21, 21) 100%);
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0); /* Deixa a barra superior transparente */
}

/* Força texto claro (já que o fundo é escuro) */
.stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span {
    color: #e0e0e0 !important;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
# --- 1. RENDERIZAÇÃO DOS INPUTS E BOTÕES ---
mensagem_do_dia = obter_mensagem_do_dia()
st.markdown(f'<p class="main-title">{mensagem_do_dia}</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Informe seus horários para calcular a jornada diária</p>', unsafe_allow_html=True)

mensagens_eventos = verificar_eventos_proximos()

col_buffer_1, col_main, col_buffer_2 = st.columns([1, 6, 1])
with col_main:
    entrada_str = st.text_input("Entrada", key="entrada", help="formatos aceitos:\nHMM, HHMM ou HH:MM")
    usar_intervalo_auto = st.checkbox("Intervalo Automático (Mínimo)", value=True, help="Calcula o desconto automático (30min ou 15min) sem precisar digitar os horários de almoço.")
    
    if not usar_intervalo_auto:
        col1, col2 = st.columns(2)
        with col1: saida_almoco_str = st.text_input("Saída para o Almoço", key="saida_almoco")
        with col2: retorno_almoco_str = st.text_input("Volta do Almoço", key="retorno_almoco")
    else:
        saida_almoco_str, retorno_almoco_str = "", ""

    saida_real_str = st.text_input("Saída", key="saida_real")
    col_calc, col_events = st.columns(2)
    with col_calc: calculate_clicked = st.button("Calcular", use_container_width=True)
    with col_events:
        event_button_text = "Próximos Eventos 🗓️" if mensagens_eventos else "Próximos Eventos"
        events_clicked = st.button(event_button_text, use_container_width=True)

# --- 2. LÓGICA DE ESTADO ---
if 'show_events' not in st.session_state: st.session_state.show_events = False
if 'show_results' not in st.session_state: st.session_state.show_results = False

if events_clicked: st.session_state.show_events = not st.session_state.show_events
if calculate_clicked: st.session_state.show_results = True
if st.session_state.show_results and not entrada_str:
    st.warning("Por favor, preencha pelo menos o horário de entrada.")
    st.session_state.show_results = False

# --- 3. LÓGICA DE CSS DINÂMICO OTIMIZADO PARA MOBILE ---
has_active_content = st.session_state.show_results or st.session_state.show_events

if not has_active_content:
    # Estado Inicial
    layout_css = """
    div.block-container {
        transform: translateY(17vh); /* Desktop: Centraliza bem */
        transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), opacity 0.4s ease-in-out;
    }
    @media (max-width: 640px) {
        div.block-container {
            transform: translateY(10vh); /* Mobile: Sobe mais para não ficar "caído" */
        }
    }
    """
else:
    # Estado Ativo: Posição original (0)
    layout_css = """
    div.block-container {
        transform: translateY(0);
        transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1);
    }
    
    /* Reduz foco da área de input */
    .main-title, .sub-title, div[data-testid="stTextInput"], div[data-testid="stButton"], div[data-testid="stCheckbox"] {
        opacity: 0.5;
        transform: scale(0.98);
        transition: all 0.2s ease-in-out;
    }
    
    /* Restaura foco ao passar o mouse */
    .main-title:hover, .sub-title:hover, div[data-testid="stTextInput"]:hover, div[data-testid="stButton"]:hover, div[data-testid="stCheckbox"]:hover {
        opacity: 1;
        transform: scale(1);
    }
    """

st.markdown(f"""
  
<style>

    /* --- CSS "NUCLEAR" PARA LIMPAR A INTERFACE DO STREAMLIT --- */
    
    /* Esconde o rodapé padrão "Made with Streamlit" */
    footer {{visibility: hidden;}}
    
    /* Esconde o menu de 3 pontos no topo direito (Opcional - remove se quiser manter o menu) */
    #MainMenu {{visibility: hidden;}}
    
    /* Esconde a barra colorida no topo da tela */
    header {{visibility: hidden;}}
    
    /* Tenta esconder o botão de deploy/gerenciar app (A Coroa) */
    .stDeployButton {{display:none;}}
    
    /* Esconde ícones de status de execução */
    [data-testid="stStatusWidget"] {{display:none;}}

    /* --------------------------------------------------------- */

    /* Injeta o CSS dinâmico de animação que você já tinha */
    {layout_css}

    /* CSS GERAL DO SEU APP */
    .main .block-container {{ max-width: 800px; padding-bottom: 5rem; }} /* Padding extra pro footer não cobrir */
    .main-title {{ font-size: 2.2rem !important; font-weight: bold; text-align: center; }}
    .sub-title {{ color: gray; text-align: center; font-size: 1.25rem !important; }}
    
    /* --- BOTÕES COM NEON (Efeito Hover) --- */
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div[data-testid="stButton"] > button {{ 
        background-color: rgb(221, 79, 5) !important; color: #FFFFFF !important; border-radius: 4rem; border-color: transparent;
        transition: all 0.3s ease; 
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div[data-testid="stButton"] > button:hover {{
        box-shadow: 0 0 12px rgba(221, 79, 5, 0.8), 0 0 20px rgba(221, 79, 5, 0.4); transform: scale(1.02);
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div[data-testid="stButton"] > button {{ 
        background-color: rgb(0, 80, 81) !important; color: #FFFFFF !important; border-radius: 4rem; border-color: transparent;
        transition: all 0.3s ease;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div[data-testid="stButton"] > button:hover {{
        box-shadow: 0 0 12px rgba(0, 80, 81, 0.8), 0 0 20px rgba(0, 80, 81, 0.4); transform: scale(1.02);
    }}
div[data-testid="stTextInput"] input {{ border-radius: 1.5rem !important; text-align: center; font-weight: 600; }}
        .main div[data-testid="stTextInput"] > label {{ text-align: center !important; width: 100%; display: block; }}
    .st-b7 {{  background-color: rgba(12, 19, 14, 0.31) !important; }}


    /* Animação de entrada dos resultados */
    .results-container, .event-list-container.visible {{ animation: fadeIn 0.4s ease-out forwards; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .event-list-item {{ background-color: #cacaca3b00; padding: 10px; border-radius: 1.5rem; margin-bottom: 5px; text-align: center; }}
    body.dark .event-list-item {{ background-color: #cacaca3b00; color: #fafafa; }}
    .custom-warning, .custom-error {{ border-radius: 1.5rem; padding: 1rem; margin-top: 1rem; text-align: center; }}
    .custom-warning {{ background-color: rgba(255, 170, 0, 0); border: 1px solid #ffaa0000; color: rgb(247, 185, 61); }}
    .custom-error {{ background-color: rgba(255, 108, 108, 0.15); border: 1px solid rgb(255, 108, 108); color: rgb(255, 75, 75); }}
    .custom-error p {{ margin: 0.5rem 0 0 0; }}
    div[data-testid="stHeading"] a {{ display: none !important; }}
    div[data-testid="stMetric"] {{ background-color: transparent !important; padding: 0 !important; }}
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] p,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: inherit !important; }}
    .section-container {{ text-align: center; margin-top: 1.5rem; }}
    .metric-custom {{ background-color: #F0F2F6; border-radius: 4rem; padding: 1rem; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; color: #31333f; }}
    .metric-almoco {{ background-color: #F0F2F6; }}
    .metric-saldo-pos {{ background-color: rgb(84, 198, 121); }}
    .metric-saldo-neg {{ background-color: rgb(255, 108, 108); }}
    .metric-minimo {{ background-color: rgb(57, 94, 94); }}
    .metric-padrao {{ background-color: rgb(0, 80, 81); }} 
    .metric-maximo {{ background-color: rgb(221, 79, 5); }} 
    .metric-custom .label {{ font-size: 0.875rem; margin-bottom: 0.25rem; color: #5a5a5a; }}
    .metric-custom .value {{ font-size: 1.5rem; font-weight: 900; color: #31333f; }}
    .metric-custom .details {{ font-size: 0.75rem; margin-top: 0.25rem; color: #5a5a5a; }}
    .metric-saldo-pos .value, .metric-saldo-neg .value, .metric-minimo .value, .metric-padrao .value, .metric-maximo .value {{ color: #FFFFFF; }}
    .metric-saldo-pos .label, .metric-saldo-neg .label, .metric-minimo .label, .metric-padrao .label, .metric-maximo .label, .metric-minimo .details, .metric-padrao .details, .metric-maximo .details {{ color: rgba(255, 255, 255, 0.85); }}
    .predictions-grid-container {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }}
    .summary-grid-container {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }}
    
    .predictions-wrapper {{ transition: opacity 0.4s ease-out, transform 0.4s ease-out, padding 0.4s ease-out; }}
    .predictions-wrapper.de-emphasized {{ opacity: 0.5; transform: scale(0.98); padding-bottom: 1rem; margin-bottom: 1rem; }}

    div[data-testid="stCheckbox"] {{ display: flex; justify-content: center; margin-top: 0px; padding-bottom: 0px; }}
    div[data-testid="stCheckbox"] label span p {{ font-size: 0.85rem !important; color: #555; }}

    @media (max-width: 640px) {{
        .predictions-grid-container {{ grid-template-columns: repeat(2, 1fr); }}
        .predictions-grid-container .metric-minimo {{ order: 2; }}
        .predictions-grid-container .metric-padrao {{ order: 1; grid-column: 1 / -1; }}
        .predictions-grid-container .metric-maximo {{ order: 3; }}
        .summary-grid-container {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    /* Estilos gerais para classes instáveis do Streamlit */
   
    ._link_gzau3_10 {{   display: none !important;}}
    ##._link_gzau3_10 {{   display: none !important;}}
    ##._profileContainer_gzau3_53 {{   display: none !important;}}
    .st-emotion-cache-yfw52f hr {{    display: none !important;}}
    .st-bv {{    font-weight: 800;}} .st-ay {{    font-size: 1.3rem;}} .st-aw {{    border-bottom-right-radius: 1.5rem;}} .st-av {{    border-top-right-radius: 1.5rem;}} .st-au {{    border-bottom-left-radius: 1.5rem;}} .st-at {{    border-top-left-radius: 1.5rem;}}
      .st-b6 {{  border-bottom-color: rgba(38, 39, 48, 0) !important;}} .st-b5 {{  border-top-color: rgba(38, 39, 48, 0) !important;}} .st-b4 {{  border-right-color: rgba(38, 39, 48, 0) !important;}} .st-b3 {{  border-left-color: rgba(38, 39, 48, 0) !important;}}
    .st-emotion-cache-yinll1 svg, .st-emotion-cache-ubko3j svg {{ display: none; }} 
    .st-emotion-cache-467cry hr:not([size]) {{    display: none;}} .st-emotion-cache-zh2fnc {{    place-items: center; width: auto !important;}} .st-emotion-cache-3uj0rx hr:not([size]) {{ display: none;}} .st-emotion-cache-14vh5up, a._container_gzau3_1._viewerBadge_nim44_23, .st-emotion-cache-scp8yw.e3g0k5y6, img._profileImage_gzau3_78._lightThemeShadow_gzau3_95, ._container_gzau3_1, ._profileImage_gzau3_78, .st-emotion-cache-1sss6mo {{    display: none !important;}}
</style>
""", unsafe_allow_html=True)

# --- 4. RENDERIZAÇÃO DOS CONTEÚDOS ---

events_placeholder = st.empty()
if st.session_state.show_events:
    with events_placeholder.container():
        if mensagens_eventos:
            event_html = "<div class='event-list-container visible'>"
            for evento in mensagens_eventos:
                event_html += f"<div class='event-list-item'>{evento}</div>"
            event_html += "</div>"
            st.markdown(event_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum evento próximo nos próximos 12 dias.")
        st.components.v1.html("""<script>setTimeout(function() { const eventsEl = window.parent.document.querySelector('.event-list-container'); if (eventsEl) { eventsEl.scrollIntoView({ behavior: 'smooth', block: 'center' }); } }, 50);</script>""", height=0)

results_placeholder = st.empty()
if st.session_state.show_results:
    if entrada_str:
        try:
            hora_entrada = datetime.datetime.strptime(formatar_hora_input(entrada_str), "%H:%M")
            
            limite_inicio_jornada_previsao = hora_entrada.replace(hour=7, minute=0, second=0, microsecond=0)
            entrada_valida_previsao = max(hora_entrada, limite_inicio_jornada_previsao)
            
            predictions_container_class = "predictions-wrapper"
            limite_saida = hora_entrada.replace(hour=20, minute=0, second=0, microsecond=0)
            duracao_almoço_previsao = 0
            
            if not usar_intervalo_auto and saida_almoco_str and retorno_almoco_str:
                saida_almoco_prev = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                retorno_almoco_prev = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                duracao_almoço_previsao = (retorno_almoco_prev - saida_almoco_prev).total_seconds() / 60
            
            hora_nucleo_inicio = hora_entrada.replace(hour=9, minute=0)
            tempo_antes_nucleo_min = 0
            if entrada_valida_previsao < hora_nucleo_inicio:
                tempo_antes_nucleo_min = (hora_nucleo_inicio - entrada_valida_previsao).total_seconds() / 60

            jornada_total_minima_min = (5 * 60) + tempo_antes_nucleo_min
            if jornada_total_minima_min > 360: intervalo_obrigatorio_5h = 30
            else: intervalo_obrigatorio_5h = 15

            minutos_intervalo_5h = max(intervalo_obrigatorio_5h, duracao_almoço_previsao)
            hora_base_5h = max(entrada_valida_previsao, hora_nucleo_inicio)
            hora_saida_5h_calculada = hora_base_5h + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
            hora_saida_5h = min(hora_saida_5h_calculada, limite_saida)
            
            minutos_intervalo_demais = max(30, duracao_almoço_previsao)
            hora_saida_8h_calculada = entrada_valida_previsao + datetime.timedelta(hours=8, minutes=minutos_intervalo_demais)
            hora_saida_8h = min(hora_saida_8h_calculada, limite_saida)
            hora_saida_10h_calculada = entrada_valida_previsao + datetime.timedelta(hours=10, minutes=minutos_intervalo_demais)
            hora_saida_10h = min(hora_saida_10h_calculada, limite_saida)

            duracao_5h_min = (hora_saida_5h - entrada_valida_previsao).total_seconds() / 60 - minutos_intervalo_5h
            duracao_8h_min = (hora_saida_8h - entrada_valida_previsao).total_seconds() / 60 - minutos_intervalo_demais
            duracao_10h_min = (hora_saida_10h - entrada_valida_previsao).total_seconds() / 60 - minutos_intervalo_demais
            
            texto_desc_5h = f"({formatar_duracao(duracao_5h_min)})" if hora_saida_5h_calculada > limite_saida else "(5h no núcleo)"
            texto_desc_8h = f"({formatar_duracao(duracao_8h_min)})" if hora_saida_8h_calculada > limite_saida else "(8h)"
            texto_desc_10h = f"({formatar_duracao(duracao_10h_min)})" if hora_saida_10h_calculada > limite_saida else "(10h)"

            if minutos_intervalo_5h >= 30: termo_intervalo_5h = "almoço"
            else: termo_intervalo_5h = "intervalo"
            
            predictions_html = f"""<div class='section-container'><h3>Previsões de Saída</h3><div class="predictions-grid-container"><div class="metric-custom metric-minimo"><div class="label">Mínimo {texto_desc_5h}</div><div class="value">{hora_saida_5h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_5h:.0f}min de {termo_intervalo_5h}</div></div><div class="metric-custom metric-padrao"><div class="label">Jornada Padrão {texto_desc_8h}</div><div class="value">{hora_saida_8h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_demais:.0f}min de almoço</div></div><div class="metric-custom metric-maximo"><div class="label">Máximo {texto_desc_10h}</div><div class="value">{hora_saida_10h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_demais:.0f}min de almoço</div></div></div></div>"""
            
            footnote, warnings_html = "", ""
            if saida_real_str:
                predictions_container_class += " de-emphasized"
                hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
                if hora_saida_real < hora_entrada: raise ValueError("A Saída deve ser depois da Entrada.")
                
                limite_inicio_jornada = hora_entrada.replace(hour=7, minute=0, second=0, microsecond=0)
                limite_fim_jornada = hora_entrada.replace(hour=20, minute=0, second=0, microsecond=0)
                entrada_valida = max(hora_entrada, limite_inicio_jornada)
                saida_valida = min(hora_saida_real, limite_fim_jornada)
                
                duracao_almoco_minutos_real = 0
                saida_almoco, retorno_almoco = None, None
                almoco_valido_minutos, desconto_ausencia = 0, 0

                if not usar_intervalo_auto:
                    if saida_almoco_str and retorno_almoco_str:
                        saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                        retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                        if retorno_almoco < saida_almoco: raise ValueError("A volta do almoço deve ser depois da saída para o almoço.")
                        
                        duracao_almoco_minutos_real = (retorno_almoco - saida_almoco).total_seconds() / 60
                        janela_inicio = saida_almoco.replace(hour=11, minute=0, second=0)
                        janela_fim = saida_almoco.replace(hour=16, minute=0, second=0)
                        inicio_valido = max(saida_almoco, janela_inicio)
                        fim_valido = min(retorno_almoco, janela_fim)
                        if fim_valido > inicio_valido: almoco_valido_minutos = (fim_valido - inicio_valido).total_seconds() / 60
                        desconto_ausencia = duracao_almoco_minutos_real - almoco_valido_minutos
                else:
                    trabalho_bruto_temp = 0
                    if saida_valida > entrada_valida:
                         trabalho_bruto_temp = (saida_valida - entrada_valida).total_seconds() / 60
                    
                    if trabalho_bruto_temp <= 240:
                        almoco_valido_minutos = 0
                    elif (trabalho_bruto_temp - 15) <= 360: 
                        almoco_valido_minutos = 15 
                    else:
                        almoco_valido_minutos = 30
                    
                    duracao_almoco_minutos_real = almoco_valido_minutos

                almoco_fisico_minutos = duracao_almoco_minutos_real
                trabalho_bruto_minutos = 0
                if saida_valida > entrada_valida: trabalho_bruto_minutos = (saida_valida - entrada_valida).total_seconds() / 60
                
                tempo_trabalhado_efetivo = trabalho_bruto_minutos - almoco_fisico_minutos
                if tempo_trabalhado_efetivo > 360: min_intervalo_real, termo_intervalo_real = 30, "almoço"
                elif tempo_trabalhado_efetivo > 240: min_intervalo_real, termo_intervalo_real = 15, "intervalo"
                else: min_intervalo_real, termo_intervalo_real = 0, "intervalo"
                
                valor_almoco_display = f"{duracao_almoco_minutos_real:.0f}min"
                if desconto_ausencia > 0:
                     valor_almoco_display = f"{almoco_valido_minutos:.0f}min (+{desconto_ausencia:.0f}min fora)"
                     footnote = f"<p style='font-size: 0.75rem; color: #ff4b4b; text-align: center; margin-top: 1rem;'>*Atenção: {desconto_ausencia:.0f} minutos do seu intervalo foram fora da janela permitida (11h-16h) e contaram como ausência.</p>"
                elif min_intervalo_real > 0 and almoco_valido_minutos < min_intervalo_real:
                    valor_almoco_display = f"{almoco_valido_minutos:.0f}min*"
                    footnote = f"<p style='font-size: 0.75rem; color: gray; text-align: center; margin-top: 1rem;'>*Seu tempo de {termo_intervalo_real} válido foi menor que o mínimo de {min_intervalo_real} minutos. Para os cálculos, foi considerado o valor mínimo obrigatório.</p>"
                elif usar_intervalo_auto and duracao_almoco_minutos_real > 0:
                     valor_almoco_display = f"{duracao_almoco_minutos_real:.0f}min <span style='font-size: 0.85rem; font-weight: 400; color: #5a5a5a;'>(Auto)</span>"

                desconto_intervalo_oficial = max(min_intervalo_real, almoco_valido_minutos)
                trabalho_liquido_minutos = trabalho_bruto_minutos - desconto_intervalo_oficial - desconto_ausencia
                saldo_banco_horas_minutos = trabalho_liquido_minutos - 480
                tempo_nucleo_minutos = calcular_tempo_nucleo(entrada_valida, saida_valida, saida_almoco, retorno_almoco)
                
                if usar_intervalo_auto and duracao_almoco_minutos_real > 0:
                    tempo_bruto_nucleo = tempo_nucleo_minutos
                    tempo_fora_nucleo = trabalho_bruto_minutos - tempo_bruto_nucleo
                    intervalo_restante = max(0, duracao_almoco_minutos_real - tempo_fora_nucleo)
                    tempo_nucleo_minutos = max(0, tempo_bruto_nucleo - intervalo_restante)

                if tempo_nucleo_minutos < 300: warnings_html += '<div class="custom-warning">Atenção: Não cumpriu as 5h obrigatórias no período núcleo.</div>'
                lista_de_permanencia = []
                if hora_entrada.time() < datetime.time(7, 0): lista_de_permanencia.append("A entrada foi registrada antes das 7h")
                if desconto_ausencia > 0: lista_de_permanencia.append(f"Parte do intervalo ({desconto_ausencia:.0f}min) realizado fora do horário permitido (11h às 16h)")
                if min_intervalo_real > 0 and almoco_valido_minutos < min_intervalo_real:
                     if desconto_ausencia == 0: lista_de_permanencia.append(f"O {termo_intervalo_real} foi inferior a {min_intervalo_real} minutos")
                if trabalho_liquido_minutos > 600: lista_de_permanencia.append("A jornada de trabalho excedeu 10 horas")
                if hora_saida_real.time() > datetime.time(20, 0): lista_de_permanencia.append("A saída foi registrada após as 20h")
                if lista_de_permanencia:
                    motivo_header = "Motivo" if len(lista_de_permanencia) == 1 else "Motivos"
                    motivos_texto = "<br>".join(lista_de_permanencia)
                    warnings_html += f"""<div class="custom-error"><b>‼️ PERMANÊNCIA NÃO AUTORIZADA ‼️</b><p><b>{motivo_header}:</b></p><p>{motivos_texto}</p></div>"""
                weather_warning = get_weather_forecast(saida_valida)
                if weather_warning: warnings_html += f'<div class="custom-warning">{weather_warning}</div>'
            
            with results_placeholder.container():
                final_predictions_html = f'<div class="{predictions_container_class}">{predictions_html}</div>'
                st.markdown(f'<div class="results-container">{final_predictions_html}</div>', unsafe_allow_html=True)
                if saida_real_str:
                    st.markdown("<div class='section-container'><h3>Resumo do Dia</h3></div>", unsafe_allow_html=True)
                    saldo_css_class = "metric-saldo-pos" if saldo_banco_horas_minutos >= 0 else "metric-saldo-neg"
                    sinal = "+" if saldo_banco_horas_minutos >= 0 else "-"
                    summary_grid_html = f"""<div class="summary-grid-container"><div class="metric-custom"><div class="label">Total Trabalhado</div><div class="value">{formatar_duracao(trabalho_liquido_minutos)}</div></div><div class="metric-custom"><div class="label">Tempo no Núcleo</div><div class="value">{formatar_duracao(tempo_nucleo_minutos)}</div></div><div class="metric-custom metric-almoco"><div class="label">Tempo de {termo_intervalo_real}</div><div class="value">{valor_almoco_display}</div></div><div class="metric-custom {saldo_css_class}"><div class="label">Saldo do Dia</div><div class="value">{sinal} {formatar_duracao(abs(saldo_banco_horas_minutos))}</div></div></div>"""
                    st.markdown(summary_grid_html, unsafe_allow_html=True)
                    st.markdown(footnote, unsafe_allow_html=True)
                st.markdown(warnings_html, unsafe_allow_html=True)
            st.components.v1.html("""<script>setTimeout(function() { const resultsEl = window.parent.document.querySelector('.results-container'); if (resultsEl) { resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' }); } }, 100);</script>""", height=0)

        except ValueError as e:
            st.error(f"Erro: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
        finally:
            st.session_state.show_results = False

# --- CÁLCULO DOS DADOS DO RODAPÉ ---
daily_forecast = get_daily_weather()
contagem_regressiva = gerar_contagem_regressiva_home_office()

# Monta o conteúdo HTML do rodapé combinando as variáveis
footer_items = []
if daily_forecast:
    # Remove tags P e centralização que possam vir da função original se houver, 
    # ou usa o texto cru. Como sua função retorna texto puro com pipes, está ótimo.
    footer_items.append(f"<span>{daily_forecast}</span>")

if contagem_regressiva:
    footer_items.append(f"<span>{contagem_regressiva}</span>")

# Une os itens com um separador visual
footer_content = " <span style='opacity: 0.3; margin: 0 8px;'>|</span> ".join(footer_items)

# Se não tiver nada, coloca um espaço vazio para não quebrar o layout
if not footer_content:
    footer_content = "&nbsp;"

# --- INJEÇÃO DO RODAPÉ (AGORA NO TOPO/CABEÇALHO) VIA JAVASCRIPT ---
import streamlit.components.v1 as components

js_footer = f"""
<script>
    function injectHeader() {{
        var headerId = "header-fixo-js";
        
        // Remove cabeçalho antigo para atualizar se houver reload
        var oldHeader = window.parent.document.getElementById(headerId);
        if (oldHeader) {{ oldHeader.remove(); }}

        // Cria o elemento
        var header = window.parent.document.createElement("div");
        header.id = headerId;
        
        // Injeta o conteúdo gerado no Python
        header.innerHTML = `{footer_content}`;
        
        // --- ESTILOS CSS PARA O TOPO ---
        header.style.position = "fixed";
        header.style.top = "0";          // Fixa no topo
        header.style.left = "0";
        header.style.width = "100%";
        header.style.textAlign = "center";
        
        // Visual
        header.style.backgroundColor = "rgba(240, 242, 246, 0.05)"; // Mais opaco para não misturar com o texto rolando por baixo
        header.style.color = "#555";
        header.style.padding = "10px 10px";
        header.style.fontSize = "0.75rem";
        header.style.borderBottom = "1px solid rgba(0,0,0,0)"; // Borda em baixo agora
        
        // Comportamento
        header.style.zIndex = "2147483647"; // Máximo z-index para ficar sobre tudo
        header.style.backdropFilter = "blur(0)"; // Blur mais forte
        header.style.display = "flex";
        header.style.justifyContent = "center";
        header.style.alignItems = "center";
        header.style.flexWrap = "wrap";
        header.style.lineHeight = "1.4";
        header.style.fontFamily = "sans-serif";
    
        // Injeta no corpo da página
        window.parent.document.body.appendChild(header);
        
        // --- AJUSTE DE ESPAÇAMENTO DO CONTEÚDO PRINCIPAL ---
        // Empurra o conteúdo para baixo para não ficar escondido atrás da barra
        var mainContainer = window.parent.document.querySelector('.main .block-container');
        if (mainContainer) {{
            mainContainer.style.marginTop = "0rem"; // Espaço extra no topo
            mainContainer.style.paddingTop = "0rem";
        }}
        
        // Remove as linhas horizontais extras
        var hrs = window.parent.document.querySelectorAll('.st-emotion-cache-yfw52f hr');
        hrs.forEach(hr => hr.style.display = 'none');
    }}
    
    // Executa
    injectHeader();
</script>
"""

components.html(js_footer, height=0)

components.html(
    """
    <script>
        const removeStreamlitElements = () => {
            const footer = window.parent.document.querySelector('footer');
            if (footer) { footer.style.display = 'none'; }

            const badge = window.parent.document.querySelector('div[class*="viewerBadge"]');
            if (badge) { badge.style.display = 'none'; }
        }
        removeStreamlitElements();
        const observer = new MutationObserver(() => {
            removeStreamlitElements();
        });
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
)

components.html(js_footer, height=0)

components.html(
    """
    <script>
        const removeStreamlitElements = () => {
            // Alvo: O rodapé padrão (onde fica o "Made with Streamlit")
            const footer = window.parent.document.querySelector('footer');
            if (footer) {
                footer.style.display = 'none';
            }

            // Alvo: O botão vermelho específico "Hosted with Streamlit" (caso seja separado do footer)
            // Eles costumam mudar a classe, mas geralmente está numa div com 'viewerBadge'
            const badge = window.parent.document.querySelector('div[class*="viewerBadge"]');
            if (badge) {
                badge.style.display = 'none';
            }
            
            // Opcional: Remover o menu de hamburguer do topo (caso queira limpar tudo)
            // const header = window.parent.document.querySelector('header');
            // if (header) {
            //    header.style.display = 'none';
            // }
        }

        // Tenta rodar assim que carrega
        removeStreamlitElements();

        // Como o Streamlit as vezes recarrega elementos, vamos garantir com um observer
        const observer = new MutationObserver(() => {
            removeStreamlitElements();
        });
        
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
)
