import streamlit as st
import datetime
import time
from eventos import *
from mensagens import obter_mensagem_do_dia
import requests
import pytz

# --- Funções de Lógica ---

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_weather_forecast(exit_time):
    """Busca a previsão de chuva para um horário específico no Rio de Janeiro."""
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

# NOVA FUNÇÃO DE ÍCONE
def get_weather_icon(wmo_code):
    """Converte o código WMO em um emoji de ícone de tempo."""
    if wmo_code == 0:
        return "☀️"  # Céu limpo
    elif wmo_code in [1, 2, 3]:
        return "🌥️"  # Principalmente limpo, parcialmente nublado, encoberto
    elif wmo_code in [45, 48]:
        return "🌫️"  # Nevoeiro
    elif wmo_code in [51, 53, 55, 56, 57]:
        return "🌦️"  # Chuvisco
    elif wmo_code in [61, 63, 65, 66, 67]:
        return "🌧️"  # Chuva
    elif wmo_code in [71, 73, 75, 77]:
        return "❄️"  # Neve
    elif wmo_code in [80, 81, 82]:
        return "🌧️"  # Pancadas de chuva
    elif wmo_code in [95, 96, 99]:
        return "⛈️"  # Trovoada
    else:
        return "🌡️" # Padrão

# FUNÇÃO DE CLIMA DIÁRIO ATUALIZADA
@st.cache_data(ttl=10800) # Cache de 3 horas
def get_daily_weather():
    """Busca a previsão de temperatura, chuva, UV e ícone para o dia no Rio de Janeiro."""
    try:
        lat = -22.93
        lon = -43.17
        fuso_horario_brasil = "America/Sao_Paulo"
        
        # URL ATUALIZADA para incluir chance de chuva e índice UV
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max,uv_index_max&timezone={fuso_horario_brasil}&forecast_days=1"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extraindo todos os dados
        daily_data = data['daily']
        temp_min = daily_data['temperature_2m_min'][0]
        temp_max = daily_data['temperature_2m_max'][0]
        weather_code = daily_data['weather_code'][0]
        rain_prob = daily_data['precipitation_probability_max'][0]
        uv_index = daily_data['uv_index_max'][0]

        icon = get_weather_icon(weather_code)

        # Construindo o texto parte por parte
        forecast_parts = [
            f"{icon} Hoje no Rio: Mínima de {temp_min:.0f}°C e Máxima de {temp_max:.0f}°C",
            f"💧 {rain_prob:.0f}%"
        ]

        # Adiciona o alerta de UV apenas se for alto (>= 6)
        if uv_index >= 6:
            forecast_parts.append(f"🥵 UV Alto ({uv_index:.1f})")

        # Juntando tudo com um separador
        return " | ".join(forecast_parts)
        
    except Exception as e:
        print(f"Erro ao buscar previsão diária: {e}")
        return ""

def obter_artigo(nome_evento):
    nome_lower = nome_evento.lower()
    femininas = ["confraternização", "paixão", "independência", "república", "consciência", "compensação", "volta", "saída", "data", "parcela", "cesta", "jornada"]
    if any(palavra in nome_lower for palavra in femininas):
        return "a"
    return "o"

def verificar_eventos_proximos():
    fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.datetime.now(fuso_horario_brasil).date()
    mensagens = []
    eventos_agrupados = {}
    todos_os_dicionarios = [FERIADOS_2025, DATAS_PAGAMENTO_VA_VR, DATAS_LIMITE_BENEFICIOS, DATAS_PAGAMENTO_SALARIO, DATAS_PAGAMENTO_13, DATAS_ADIANTAMENTO_SALARIO, CESTA_NATALINA]
    for d in todos_os_dicionarios:
        for data, nome in d.items():
            if data not in eventos_agrupados:
                eventos_agrupados[data] = []
            eventos_agrupados[data].append(nome)
    for data_evento, lista_nomes in sorted(eventos_agrupados.items()):
        delta = data_evento - hoje
        if 0 <= delta.days <= 12:
            if any("Crédito" in s or "Pagamento" in s or "13º" in s or "Adiantamento" in s or "Cesta" in s for s in lista_nomes):
                emoji = "💰"
            elif any("Data limite" in s for s in lista_nomes):
                emoji = "❗️"
            else:
                emoji = "🗓️"
            nomes_com_artigo = []
            for nome in lista_nomes:
                nome_limpo = nome.split('(')[0].strip()
                artigo = obter_artigo(nome_limpo)
                nomes_com_artigo.append(f"{artigo} {nome_limpo}")
            nome_evento_final = " e ".join(nomes_com_artigo)
            if delta.days == 0:
                mensagem = f"{emoji} Hoje é {nome_evento_final}!"
            elif delta.days == 1:
                mensagem = f"{emoji} Amanhã é {nome_evento_final}!"
            else:
                mensagem = f"{emoji} Faltam {delta.days} dias para {nome_evento_final}!"
            mensagens.append(mensagem)
    return mensagens

def formatar_hora_input(input_str):
    input_str = input_str.strip()
    if ':' in input_str:
        return input_str
    if len(input_str) == 3:
        input_str = '0' + input_str
    if len(input_str) != 4 or not input_str.isdigit():
        raise ValueError("Formato de hora inválido.")
    return f"{input_str[:2]}:{input_str[2:]}"

def calcular_tempo_nucleo(entrada, saida, saida_almoco, retorno_almoco):
    nucleo_inicio = entrada.replace(hour=9, minute=0, second=0, microsecond=0)
    nucleo_fim = entrada.replace(hour=18, minute=0, second=0, microsecond=0)
    inicio_trabalho_nucleo = max(entrada, nucleo_inicio)
    fim_trabalho_nucleo = min(saida, nucleo_fim)
    if inicio_trabalho_nucleo >= fim_trabalho_nucleo:
        return 0
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
    if minutos < 0:
        minutos = 0
    horas = int(minutos // 60)
    mins = int(minutos % 60)
    return f"{horas}h {mins}min"

# --- Interface do Web App com Streamlit ---
st.set_page_config(page_title="Calculadora de Jornada", layout="centered")

# Injeção de CSS para customização
st.markdown("""
<style>
    /* Diminui o padding superior da página */
    div.block-container { padding-top: 4rem; }
    /* Limita a largura do container principal */
    .main .block-container { max-width: 800px; }
    /* Estiliza o título principal customizado */
    .main-title { font-size: 2.2rem !important; font-weight: bold; text-align: center; }
    /* Estiliza o subtítulo customizado */
    .sub-title { color: gray; text-align: center; font-size: 1.25rem !important; }
    /* Estilos para os botões */
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div[data-testid="stButton"] > button { background-color: rgb(221, 79, 5) !important; color: #FFFFFF !important; border-radius: 4rem; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div[data-testid="stButton"] > button { background-color: rgb(0, 80, 81) !important; color: #FFFFFF !important; border-radius: 4rem; }
    /* Arredonda as caixas de input e centraliza os labels */
    div[data-testid="stTextInput"] input { border-radius: 1.5rem !important; text-align: center; font-weight: 600; }
    .main div[data-testid="stTextInput"] > label { text-align: center !important; width: 100%; display: block; }
    /* Animação de fade-in para os resultados */
    .results-container { animation: fadeIn 0.5s ease-out forwards; }
    /* Animação para a lista de eventos (APENAS FADE-IN) */
    .event-list-container.visible { animation: fadeIn 0.5s ease-out forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    /* Estilos para a lista de eventos */
    .event-list-item { background-color: #cacaca3b00; padding: 10px; border-radius: 1.5rem; margin-bottom: 5px; text-align: center; }
    body.dark .event-list-item { background-color: #cacaca3b00; color: #fafafa; }
    /* Estilos para alertas customizados */
    .custom-warning, .custom-error { border-radius: 1.5rem; padding: 1rem; margin-top: 1rem; text-align: center; }
    .custom-warning { background-color: rgba(255, 170, 0, 0); border: 1px solid #ffaa0000; color: rgb(247, 185, 61); }
    .custom-error { background-color: rgba(255, 108, 108, 0.15); border: 1px solid rgb(255, 108, 108); color: rgb(255, 75, 75); }
    .custom-error p { margin: 0.5rem 0 0 0; }
    /* Oculta o ícone de âncora/link nos cabeçalhos de forma mais específica */
    div[data-testid="stHeading"] a { display: none !important; }
    /* Remove estilos padrão que podem causar conflito */
    div[data-testid="stMetric"] { background-color: transparent !important; padding: 0 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] p,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: inherit !important; }
    /* Estilo para centralizar texto dentro das seções de resultado */
    .section-container { text-align: center; }
    /* Estilos para a métrica customizada */
    .metric-custom { background-color: #F0F2F6; border-radius: 4rem; padding: 1rem; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; color: #31333f; }
    .metric-almoco { background-color: #F0F2F6; }
    .metric-saldo-pos { background-color: rgb(84, 198, 121); }
    .metric-saldo-neg { background-color: rgb(255, 108, 108); }
    .metric-minimo { background-color: rgb(57, 94, 94); }
    .metric-padrao { background-color: rgb(0, 80, 81); } 
    .metric-maximo { background-color: rgb(221, 79, 5); } 
    .metric-custom .label { font-size: 0.875rem; margin-bottom: 0.25rem; color: #5a5a5a; }
    .metric-custom .value { font-size: 1.5rem; font-weight: 900; color: #31333f; }
    .metric-custom .details { font-size: 0.75rem; margin-top: 0.25rem; color: #5a5a5a; }
    /* Cor de texto branca para caixas coloridas */
    .metric-saldo-pos .value, .metric-saldo-neg .value, .metric-minimo .value, .metric-padrao .value, .metric-maximo .value { color: #FFFFFF; }
    .metric-saldo-pos .label, .metric-saldo-neg .label, .metric-minimo .label, .metric-padrao .label, .metric-maximo .label, .metric-minimo .details, .metric-padrao .details, .metric-maximo .details { color: rgba(255, 255, 255, 0.85); }
    /* Grids de métricas */
    .predictions-grid-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
    .summary-grid-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }
    /* Responsividade */
    @media (max-width: 640px) {
        .predictions-grid-container { grid-template-columns: repeat(2, 1fr); }
        .predictions-grid-container .metric-minimo { order: 2; }
        .predictions-grid-container .metric-padrao { order: 1; grid-column: 1 / -1; }
        .predictions_grid-container .metric-maximo { order: 3; }
        .summary-grid-container { grid-template-columns: repeat(2, 1fr); }
    }
    /* Estilos gerais para classes instáveis do Streamlit */
    .st-bv {    font-weight: 800;}
    .st-ay {    font-size: 1.3rem;}
    .st-aw {    border-bottom-right-radius: 1.5rem;}
    .st-av {    border-top-right-radius: 1.5rem;}
    .st-au {    border-bottom-left-radius: 1.5rem;}
    .st-at {    border-top-left-radius: 1.5rem;}
    .st-emotion-cache-yinll1 svg { display: none; } 
    .st-emotion-cache-ubko3j svg { display: none; }

</style>
""", unsafe_allow_html=True)


mensagem_do_dia = obter_mensagem_do_dia()
st.markdown(f'<p class="main-title">{mensagem_do_dia}</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Informe seus horários para calcular a jornada diária</p>', unsafe_allow_html=True)

mensagens_eventos = verificar_eventos_proximos()

col_buffer_1, col_main, col_buffer_2 = st.columns([1, 6, 1])
with col_main:
    entrada_str = st.text_input("Entrada", key="entrada", help="formatos aceitos:\nHMM, HHMM ou HH:MM")
    col1, col2 = st.columns(2)
    with col1:
        saida_almoco_str = st.text_input("Saída para o Almoço", key="saida_almoco")
    with col2:
        retorno_almoco_str = st.text_input("Volta do Almoço", key="retorno_almoco")
    saida_real_str = st.text_input("Saída", key="saida_real")
    col_calc, col_events = st.columns(2)
    with col_calc:
        calculate_clicked = st.button("Calcular", use_container_width=True)
    with col_events:
        event_button_text = "Próximos Eventos 🗓️" if mensagens_eventos else "Próximos Eventos"
        events_clicked = st.button(event_button_text, use_container_width=True)

events_placeholder = st.empty()
if 'show_events' not in st.session_state:
    st.session_state.show_events = False
if events_clicked:
    st.session_state.show_events = not st.session_state.show_events
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
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if calculate_clicked:
    st.session_state.show_results = True
if st.session_state.show_results:
    if not entrada_str:
        st.warning("Por favor, preencha pelo menos o horário de entrada.")
        st.session_state.show_results = False
    else:
        try:
            hora_entrada = datetime.datetime.strptime(formatar_hora_input(entrada_str), "%H:%M")
            limite_saida = hora_entrada.replace(hour=20, minute=0, second=0, microsecond=0)
            duracao_almoço_previsao = 0
            if saida_almoco_str and retorno_almoco_str:
                saida_almoco_prev = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                retorno_almoco_prev = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                duracao_almoço_previsao = (retorno_almoco_prev - saida_almoco_prev).total_seconds() / 60
            minutos_intervalo_5h = max(15, duracao_almoço_previsao)
            hora_nucleo_inicio = hora_entrada.replace(hour=9, minute=0)
            hora_base_5h = max(hora_entrada, hora_nucleo_inicio)
            hora_saida_5h_calculada = hora_base_5h + datetime.timedelta(hours=5, minutes=minutos_intervalo_5h)
            hora_saida_5h = min(hora_saida_5h_calculada, limite_saida)
            minutos_intervalo_demais = max(30, duracao_almoço_previsao)
            hora_saida_8h_calculada = hora_entrada + datetime.timedelta(hours=8, minutes=minutos_intervalo_demais)
            hora_saida_8h = min(hora_saida_8h_calculada, limite_saida)
            hora_saida_10h_calculada = hora_entrada + datetime.timedelta(hours=10, minutes=minutos_intervalo_demais)
            hora_saida_10h = min(hora_saida_10h_calculada, limite_saida)
            duracao_5h_min = (hora_saida_5h - hora_entrada).total_seconds() / 60 - minutos_intervalo_5h
            duracao_8h_min = (hora_saida_8h - hora_entrada).total_seconds() / 60 - minutos_intervalo_demais
            duracao_10h_min = (hora_saida_10h - hora_entrada).total_seconds() / 60 - minutos_intervalo_demais
            texto_desc_5h = f"({formatar_duracao(duracao_5h_min)})" if hora_saida_5h_calculada > limite_saida else "(5h no núcleo)"
            texto_desc_8h = f"({formatar_duracao(duracao_8h_min)})" if hora_saida_8h_calculada > limite_saida else "(8h)"
            texto_desc_10h = f"({formatar_duracao(duracao_10h_min)})" if hora_saida_10h_calculada > limite_saida else "(10h)"
            predictions_html = f"""<div class='section-container'><h3>Previsões de Saída</h3><div class="predictions-grid-container"><div class="metric-custom metric-minimo"><div class="label">Mínimo {texto_desc_5h}</div><div class="value">{hora_saida_5h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_5h:.0f}min de intervalo</div></div><div class="metric-custom metric-padrao"><div class="label">Jornada Padrão {texto_desc_8h}</div><div class="value">{hora_saida_8h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_demais:.0f}min de almoço</div></div><div class="metric-custom metric-maximo"><div class="label">Máximo {texto_desc_10h}</div><div class="value">{hora_saida_10h.strftime('%H:%M')}</div><div class="details">{minutos_intervalo_demais:.0f}min de almoço</div></div></div></div>"""
            footnote = ""
            warnings_html = ""
            if saida_real_str:
                hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
                if hora_saida_real < hora_entrada:
                    raise ValueError("A Saída deve ser depois da Entrada.")
                limite_inicio_jornada = hora_entrada.replace(hour=7, minute=0, second=0, microsecond=0)
                limite_fim_jornada = hora_entrada.replace(hour=20, minute=0, second=0, microsecond=0)
                entrada_valida = max(hora_entrada, limite_inicio_jornada)
                saida_valida = min(hora_saida_real, limite_fim_jornada)
                duracao_almoco_minutos_real = 0
                saida_almoco, retorno_almoco = None, None
                if saida_almoco_str and retorno_almoco_str:
                    saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                    retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                    if retorno_almoco < saida_almoco:
                        raise ValueError("A volta do almoço deve ser depois da saída para o almoço.")
                    duracao_almoco_minutos_real = (retorno_almoco - saida_almoco).total_seconds() / 60
                almoco_efetivo_minutos = 0
                if saida_almoco and retorno_almoco:
                    inicio_almoco_valido = max(saida_almoco, entrada_valida)
                    fim_almoco_valido = min(retorno_almoco, saida_valida)
                    if fim_almoco_valido > inicio_almoco_valido:
                        almoco_efetivo_minutos = (fim_almoco_valido - inicio_almoco_valido).total_seconds() / 60
                trabalho_bruto_minutos = 0
                if saida_valida > entrada_valida:
                    trabalho_bruto_minutos = (saida_valida - entrada_valida).total_seconds() / 60
                tempo_trabalhado_efetivo = trabalho_bruto_minutos - almoco_efetivo_minutos
                if tempo_trabalhado_efetivo > 360: min_intervalo_real, termo_intervalo_real = 30, "almoço"
                elif tempo_trabalhado_efetivo > 240: min_intervalo_real, termo_intervalo_real = 15, "intervalo"
                else: min_intervalo_real, termo_intervalo_real = 0, "intervalo"
                valor_almoco_display = f"{duracao_almoco_minutos_real:.0f}min"
                if min_intervalo_real > 0 and duracao_almoco_minutos_real < min_intervalo_real:
                    valor_almoco_display = f"{min_intervalo_real:.0f}min*"
                    footnote = f"<p style='font-size: 0.75rem; color: gray; text-align: center; margin-top: 1rem;'>*O tempo de {termo_intervalo_real} foi de {duracao_almoco_minutos_real:.0f}min, mas para o cálculo da hora trabalhada foi considerado o valor mínimo para a jornada.</p>"
                duracao_almoço_para_calculo = max(min_intervalo_real, almoco_efetivo_minutos)
                trabalho_liquido_minutos = trabalho_bruto_minutos - duracao_almoço_para_calculo
                saldo_banco_horas_minutos = trabalho_liquido_minutos - 480
                tempo_nucleo_minutos = calcular_tempo_nucleo(entrada_valida, saida_valida, saida_almoco, retorno_almoco)
                if tempo_nucleo_minutos < 300:
                    warnings_html += '<div class="custom-warning">Atenção: Não cumpriu as 5h obrigatórias no período núcleo.</div>'
                lista_de_permanencia = []
                if hora_entrada.time() < datetime.time(7, 0):
                    lista_de_permanencia.append("A entrada foi registrada antes das 7h")
                if min_intervalo_real > 0 and duracao_almoco_minutos_real < min_intervalo_real:
                    lista_de_permanencia.append(f"O {termo_intervalo_real} foi inferior a {min_intervalo_real} minutos")
                if trabalho_liquido_minutos > 600:
                    lista_de_permanencia.append("A jornada de trabalho excedeu 10 horas")
                if hora_saida_real.time() > datetime.time(20, 0):
                    lista_de_permanencia.append("A saída foi registrada após as 20h")
                if lista_de_permanencia:
                    motivo_header = "Motivo" if len(lista_de_permanencia) == 1 else "Motivos"
                    motivos_texto = "<br>".join(lista_de_permanencia)
                    warnings_html += f"""<div class="custom-error"><b>‼️ PERMANÊNCIA NÃO AUTORIZADA ‼️</b><p><b>{motivo_header}:</b></p><p>{motivos_texto}</p></div>"""
                weather_warning = get_weather_forecast(saida_valida)
                if weather_warning:
                    warnings_html += f'<div class="custom-warning">{weather_warning}</div>'
            with results_placeholder.container():
                st.markdown(f'<div class="results-container">{predictions_html}</div>', unsafe_allow_html=True)
                if saida_real_str:
                    st.markdown("<hr>", unsafe_allow_html=True)
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

# ADIÇÃO DO TEXTO DE PREVISÃO NO FINAL DA PÁGINA
daily_forecast = get_daily_weather()
if daily_forecast:
    st.markdown("---")
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.85rem;'>{daily_forecast}</p>", unsafe_allow_html=True)
