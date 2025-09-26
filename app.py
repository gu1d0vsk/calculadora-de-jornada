import streamlit as st
import datetime
import time

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

def formatar_duracao(minutos):
    """Formata uma duração em minutos para o formato Xh Ymin."""
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
    /* Limita a largura do container principal */
    .main .block-container {
        max-width: 800px;
    }
    /* Estiliza o título principal customizado */
    .main-title {
        font-size: 2.2rem !important;
        font-weight: bold;
        text-align: center;
    }
    
    /* Estiliza o subtítulo customizado */
    .sub-title {
        color: gray;
        text-align: center;
        font-size: 1.5rem !important;
    }
    /* Estiliza o botão de cálculo */
    div[data-testid="stButton"] > button {
        background-color: rgb(92, 228, 136);
        color: #FFFFFF;
    }
    /* Arredonda as caixas de input de texto */
    div[data-testid="stTextInput"] input {
        border-radius: 1.5rem !important;
        text-align: center;
    }
    div[data-testid="stTextInput"] label {
        text-align: center;
        width: 100%;
    }

    /* Animação de fade-in */
    .results-container {
        animation: fadeIn 0.5s ease-out forwards;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Estilos para alertas customizados */
    .custom-warning, .custom-error {
        border-radius: 1.5rem;
        padding: 1rem;
        margin-top: 1rem;
        text-align: center;
        color: #31333f;
    }
    .custom-warning {
        background-color: rgba(255, 170, 0, 0.15);
        border: 1px solid #ffaa00;
    }
    .custom-error {
        background-color: rgba(255, 108, 108, 0.15);
        border: 1px solid rgb(255, 108, 108);
    }
    .custom-error p {
        margin: 0.5rem 0 0 0;
    }

    /* Estilos gerais */
    .st-emotion-cache-1anq8dj {border-radius: 1.25rem; }
    .st-emotion-cache-zh2fnc {align-self: center;}
    .st-emotion-cache-1weic72 {justify-content: center;}
    .st-emotion-cache-467cry h3 { text-align: center; } /* Centraliza os headers */
    .st-emotion-cache-467cry p { text-align: center; }
    .st-emotion-cache-ubko3j svg, .st-emotion-cache-gquqoo { display: none !important; }
    .st-bv {    font-weight: 600;}
    .st-ay {    font-size: 1.3rem;}
    .st-aw {    border-bottom-right-radius: 1.5rem;}
    .st-av {    border-top-right-radius: 1.5rem;}
    .st-au {    border-bottom-left-radius: 1.5rem;}
    .st-at {    border-top-left-radius: 1.5rem;}

</style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-title">Calculadora de Jornada de Trabalho</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Informe seus horários para calcular a jornada diária</p>', unsafe_allow_html=True)

# Layout dos campos de entrada
with st.container():
    entrada_str = st.text_input("Entrada", key="entrada")
    col1, col2 = st.columns(2)
    with col1:
        saida_almoco_str = st.text_input("Saída Almoço", key="saida_almoco")
    with col2:
        retorno_almoco_str = st.text_input("Volta Almoço", key="retorno_almoco")
    saida_real_str = st.text_input("Saída", key="saida_real")

# Botão centralizado
_, center_col, _ = st.columns([2, 3, 2])
with center_col:
    calculate_clicked = st.button("Calcular")

# Placeholder para os resultados
results_placeholder = st.empty()

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if calculate_clicked:
    st.session_state.show_results = True

if st.session_state.show_results:
    if not entrada_str:
        st.warning("Por favor, preencha pelo menos o horário de entrada.")
        st.session_state.show_results = False # Reseta para não mostrar na próxima recarga
    else:
        try:
            hora_entrada = datetime.datetime.strptime(formatar_hora_input(entrada_str), "%H:%M")

            # --- Construção do HTML dos resultados ---
            results_html = "<div>" # Container para os resultados
            
            # --- Parte 1: Cálculo das previsões ---
            results_html += "<h3>Previsões de Saída</h3>"
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

            results_html += f"""
            <p>
            <b>Mínimo {texto_desc_5h}:</b> {hora_saida_5h.strftime('%H:%M')} ({minutos_intervalo_5h:.0f}min de intervalo)<br>
            <b>Jornada Padrão {texto_desc_8h}:</b> {hora_saida_8h.strftime('%H:%M')} ({minutos_intervalo_demais:.0f}min de almoço)<br>
            <b>Máximo {texto_desc_10h}:</b> {hora_saida_10h.strftime('%H:%M')} ({minutos_intervalo_demais:.0f}min de almoço)
            </p>
            """
            
            # --- Parte 2: Resumo do dia ---
            if saida_real_str:
                results_html += "<hr>" # Separador visual
                results_html += "<h3>Resumo do Dia</h3>"
                
                hora_saida_real = datetime.datetime.strptime(formatar_hora_input(saida_real_str), "%H:%M")
                
                if hora_saida_real < hora_entrada:
                    raise ValueError("A Saída deve ser depois da Entrada.")

                saida_almoco, retorno_almoco, duracao_almoco_minutos_real = None, None, 0
                if saida_almoco_str and retorno_almoco_str:
                    saida_almoco = datetime.datetime.strptime(formatar_hora_input(saida_almoco_str), "%H:%M")
                    retorno_almoco = datetime.datetime.strptime(formatar_hora_input(retorno_almoco_str), "%H:%M")
                    if retorno_almoco < saida_almoco:
                        raise ValueError("A volta do almoço deve ser depois da saída para o almoço.")
                    duracao_almoco_minutos_real = (retorno_almoco - saida_almoco).total_seconds() / 60

                trabalho_bruto_minutos = (hora_saida_real - hora_entrada).total_seconds() / 60
                tempo_trabalhado_efetivo = trabalho_bruto_minutos - duracao_almoco_minutos_real

                if tempo_trabalhado_efetivo > 360: min_intervalo_real, termo_intervalo_real = 30, "almoço"
                elif tempo_trabalhado_efetivo > 240: min_intervalo_real, termo_intervalo_real = 15, "intervalo"
                else: min_intervalo_real, termo_intervalo_real = 0, "intervalo"

                duracao_almoço_para_calculo = max(min_intervalo_real, duracao_almoco_minutos_real)
                trabalho_liquido_minutos = trabalho_bruto_minutos - duracao_almoço_para_calculo
                
                saldo_banco_horas_minutos = trabalho_liquido_minutos - 480
                saldo_texto = formatar_duracao(abs(saldo_banco_horas_minutos))
                saldo_string = f'<span style="color:rgb(92, 228, 136)">+ {saldo_texto}</span>' if saldo_banco_horas_minutos >= 0 else f'<span style="color:rgb(255, 108, 108)">- {saldo_texto}</span>'
                
                tempo_nucleo_minutos = calcular_tempo_nucleo(hora_entrada, hora_saida_real, saida_almoco, retorno_almoco)
                
                results_html += f"<p><b>Total trabalhado:</b> {formatar_duracao(trabalho_liquido_minutos)}"
                if duracao_almoco_minutos_real > 0:
                    results_html += f"<br><b>Tempo de {termo_intervalo_real}:</b> {duracao_almoco_minutos_real:.0f}min"
                results_html += f"<br><b>Tempo no núcleo (9h-18h):</b> {formatar_duracao(tempo_nucleo_minutos)}"
                results_html += f"<br><b>Saldo do dia:</b> {saldo_string}</p>"
                
                if tempo_nucleo_minutos < 300:
                    results_html += '<div class="custom-warning">Atenção: Não cumpriu as 5h obrigatórias no período núcleo.</div>'

                lista_de_avisos = []
                if min_intervalo_real > 0 and duracao_almoco_minutos_real < min_intervalo_real:
                    lista_de_avisos.append(f"{termo_intervalo_real.capitalize()} foi inferior a {min_intervalo_real} minutos")
                if trabalho_liquido_minutos > 600:
                    lista_de_avisos.append("Jornada de trabalho excedeu 10 horas")
                if hora_saida_real.time() > datetime.time(20, 0):
                    lista_de_avisos.append("Saída registrada após as 20h")

                if lista_de_avisos:
                    motivo_header = "Motivo" if len(lista_de_avisos) == 1 else "Motivos"
                    motivos_texto = "<br>".join(lista_de_avisos)
                    results_html += f"""
                    <div class="custom-error">
                        <b>‼️ POSSÍVEL PERMANÊNCIA NÃO AUTORIZADA ‼️</b>
                        <p><b>{motivo_header}:</b></p>
                        <p>{motivos_texto}</p>
                    </div>
                    """

            results_html += "</div>"
            
            # Script para rolagem suave
            scroll_script = """
                <script>
                    // Espera um pouco para o elemento ser renderizado
                    setTimeout(function() {
                        const resultsEl = window.parent.document.querySelector('.results-container');
                        if (resultsEl) {
                            resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 100);
                </script>
            """
            
            # Exibe o HTML final no placeholder
            with results_placeholder.container():
                st.markdown(f'<div class="results-container">{results_html}</div>', unsafe_allow_html=True)
                st.components.v1.html(scroll_script, height=0)


        except ValueError as e:
            st.error(f"Erro: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
        finally:
            st.session_state.show_results = False # Reseta para a próxima interação

