import datetime

# ==========================================
# EVENTOS COMBINADOS (2025 + 2026)
# O sistema filtrará automaticamente com base na data de hoje
# ==========================================

FERIADOS = {
    # --- 2025 ---
    datetime.date(2025, 1, 1): "dia da Confraternização Universal",
    datetime.date(2025, 1, 20): "dia de São Sebastião (RJ)",
    datetime.date(2025, 3, 3): "Ponto Facultativo de Carnaval",
    datetime.date(2025, 3, 4): "Carnaval",
    datetime.date(2025, 3, 5): "Ponto Facultativo de Carnaval",
    datetime.date(2025, 4, 18): "dia da Paixão de Cristo",
    datetime.date(2025, 4, 21): "dia de Tiradentes",
    datetime.date(2025, 4, 23): "Dia de São Jorge (RJ)",
    datetime.date(2025, 5, 1): "dia do Trabalho",
    datetime.date(2025, 5, 2): "Compensação (Dia Ponte)",
    datetime.date(2025, 6, 19): "dia de Corpus Christi",
    datetime.date(2025, 6, 20): "Compensação (Dia Ponte)",
    datetime.date(2025, 9, 7): "dia da Independência do Brasil",
    datetime.date(2025, 10, 12): "dia da Nossa Senhora Aparecida",
    datetime.date(2025, 11, 2): "dia de Finados",
    datetime.date(2025, 11, 15): "dia da Proclamação da República",
    datetime.date(2025, 11, 20): "dia da Consciência Negra",
    datetime.date(2025, 11, 21): "dia Ponte",
    datetime.date(2025, 12, 24): "ponto Facultativo de Natal",
    datetime.date(2025, 12, 25): "Natal",
    datetime.date(2025, 12, 26): "Compensação (Dia Ponte)",
    datetime.date(2025, 12, 31): "ponto Facultativo de Ano Novo",
    # [cite_start]--- 2026 [cite: 6] ---
    datetime.date(2026, 1, 1): "dia da Confraternização Universal",
    datetime.date(2026, 1, 2): "Compensação (Dia Ponte)",
    datetime.date(2026, 1, 20): "dia de São Sebastião (RJ)",
    datetime.date(2026, 2, 16): "Ponto Facultativo de Carnaval",
    datetime.date(2026, 2, 17): "Carnaval",
    datetime.date(2026, 2, 18): "Ponto Facultativo (Quarta de Cinzas)",
    datetime.date(2026, 4, 3): "dia da Paixão de Cristo",
    datetime.date(2026, 4, 20): "Compensação (Dia Ponte)",
    datetime.date(2026, 4, 21): "dia de Tiradentes",
    datetime.date(2026, 4, 23): "Dia de São Jorge (RJ)",
    datetime.date(2026, 5, 1): "dia do Trabalho",
    datetime.date(2026, 6, 4): "dia de Corpus Christi",
    datetime.date(2026, 6, 5): "Compensação (Dia Ponte)",
    datetime.date(2026, 9, 7): "dia da Independência do Brasil",
    datetime.date(2026, 10, 12): "dia da Nossa Senhora Aparecida",
    datetime.date(2026, 11, 2): "dia de Finados",
    datetime.date(2026, 11, 15): "dia da Proclamação da República",
    datetime.date(2026, 11, 20): "dia da Consciência Negra",
    datetime.date(2026, 12, 24): "ponto Facultativo de Natal",
    datetime.date(2026, 12, 25): "Natal",
    datetime.date(2026, 12, 31): "ponto Facultativo de Ano Novo",
}

DATAS_PAGAMENTO_VA_VR = {
    # --- 2025 ---
    datetime.date(2025, 1, 30): "Crédito do VA/VR (Ref. Fevereiro)",
    datetime.date(2025, 2, 28): "Crédito do VA/VR (Ref. Março)",
    datetime.date(2025, 3, 28): "Crédito do VA/VR (Ref. Abril)",
    datetime.date(2025, 4, 30): "Crédito do VA/VR (Ref. Maio)",
    datetime.date(2025, 5, 30): "Crédito do VA/VR (Ref. Junho)",
    datetime.date(2025, 6, 30): "Crédito do VA/VR (Ref. Julho)",
    datetime.date(2025, 7, 30): "Crédito do VA/VR (Ref. Agosto)",
    datetime.date(2025, 8, 29): "Crédito do VA/VR (Ref. Setembro)",
    datetime.date(2025, 9, 30): "Crédito do VA/VR (Ref. Outubro)",
    datetime.date(2025, 10, 30): "Crédito do VA/VR (Ref. Novembro)",
    datetime.date(2025, 11, 28): "Crédito do VA/VR (Ref. Dezembro)",
    datetime.date(2025, 12, 30): "Crédito do VA/VR (Ref. Janeiro/26)",
    # [cite_start]--- 2026 [cite: 63] ---
    datetime.date(2026, 1, 30): "Crédito do VA/VR (Ref. Fevereiro)",
    datetime.date(2026, 2, 27): "Crédito do VA/VR (Ref. Março)",
    datetime.date(2026, 3, 30): "Crédito do VA/VR (Ref. Abril)",
    datetime.date(2026, 4, 30): "Crédito do VA/VR (Ref. Maio)",
    datetime.date(2026, 5, 29): "Crédito do VA/VR (Ref. Junho)",
    datetime.date(2026, 6, 30): "Crédito do VA/VR (Ref. Julho)",
    datetime.date(2026, 7, 30): "Crédito do VA/VR (Ref. Agosto)",
    datetime.date(2026, 8, 28): "Crédito do VA/VR (Ref. Setembro)",
    datetime.date(2026, 9, 30): "Crédito do VA/VR (Ref. Outubro)",
    datetime.date(2026, 10, 30): "Crédito do VA/VR (Ref. Novembro)",
    datetime.date(2026, 11, 30): "Crédito do VA/VR (Ref. Dezembro)",
    datetime.date(2026, 12, 30): "Crédito do VA/VR (Ref. Janeiro/27)",
}

DATAS_LIMITE_BENEFICIOS = {
    # --- 2025 ---
    datetime.date(2025, 1, 10): "data limite de solicitações e alterações de benefícios (Janeiro)",
    datetime.date(2025, 2, 10): "data limite de solicitações e alterações de benefícios (Fevereiro)",
    datetime.date(2025, 3, 11): "data limite de solicitações e alterações de benefícios (Março)",
    datetime.date(2025, 4, 10): "data limite de solicitações e alterações de benefícios (Abril)",
    datetime.date(2025, 5, 12): "data limite de solicitações e alterações de benefícios (Maio)",
    datetime.date(2025, 6, 10): "data limite de solicitações e alterações de benefícios (Junho)",
    datetime.date(2025, 7, 10): "data limite de solicitações e alterações de benefícios (Julho)",
    datetime.date(2025, 8, 11): "data limite de solicitações e alterações de benefícios (Agosto)",
    datetime.date(2025, 9, 10): "data limite de solicitações e alterações de benefícios (Setembro)",
    datetime.date(2025, 10, 10): "data limite de solicitações e alterações de benefícios (Outubro)",
    datetime.date(2025, 11, 10): "data limite de solicitações e alterações de benefícios (Novembro)",
    datetime.date(2025, 12, 10): "data limite de solicitações e alterações de benefícios (Dezembro)",
    # [cite_start]--- 2026 [cite: 54] ---
    datetime.date(2026, 1, 12): "data limite de solicitações e alterações de benefícios (Janeiro)",
    datetime.date(2026, 2, 10): "data limite de solicitações e alterações de benefícios (Fevereiro)",
    datetime.date(2026, 3, 10): "data limite de solicitações e alterações de benefícios (Março)",
    datetime.date(2026, 4, 10): "data limite de solicitações e alterações de benefícios (Abril)",
    datetime.date(2026, 5, 11): "data limite de solicitações e alterações de benefícios (Maio)",
    datetime.date(2026, 6, 10): "data limite de solicitações e alterações de benefícios (Junho)",
    datetime.date(2026, 7, 10): "data limite de solicitações e alterações de benefícios (Julho)",
    datetime.date(2026, 8, 10): "data limite de solicitações e alterações de benefícios (Agosto)",
    datetime.date(2026, 9, 10): "data limite de solicitações e alterações de benefícios (Setembro)",
    datetime.date(2026, 10, 13): "data limite de solicitações e alterações de benefícios (Outubro)",
    datetime.date(2026, 11, 10): "data limite de solicitações e alterações de benefícios (Novembro)",
    datetime.date(2026, 12, 10): "data limite de solicitações e alterações de benefícios (Dezembro)",
}

DATAS_PAGAMENTO_SALARIO = {
    # --- 2025 ---
    datetime.date(2025, 1, 30): "Pagamento do Salário (Janeiro)",
    datetime.date(2025, 2, 28): "Pagamento do Salário (Fevereiro)",
    datetime.date(2025, 3, 28): "Pagamento do Salário (Março)",
    datetime.date(2025, 4, 30): "Pagamento do Salário (Abril)",
    datetime.date(2025, 5, 30): "Pagamento do Salário (Maio)",
    datetime.date(2025, 6, 30): "Pagamento do Salário (Junho)",
    datetime.date(2025, 7, 30): "Pagamento do Salário (Julho)",
    datetime.date(2025, 8, 29): "Pagamento do Salário (Agosto)",
    datetime.date(2025, 9, 30): "Pagamento do Salário (Setembro)",
    datetime.date(2025, 10, 30): "Pagamento do Salário (Outubro)",
    datetime.date(2025, 11, 28): "Pagamento do Salário (Novembro)",
    datetime.date(2025, 12, 30): "Pagamento do Salário (Dezembro)",
    # [cite_start]--- 2026 [cite: 14] ---
    datetime.date(2026, 1, 30): "Pagamento do Salário (Janeiro)",
    datetime.date(2026, 2, 27): "Pagamento do Salário (Fevereiro)",
    datetime.date(2026, 3, 30): "Pagamento do Salário (Março)",
    datetime.date(2026, 4, 30): "Pagamento do Salário (Abril)",
    datetime.date(2026, 5, 29): "Pagamento do Salário (Maio)",
    datetime.date(2026, 6, 30): "Pagamento do Salário (Junho)",
    datetime.date(2026, 7, 30): "Pagamento do Salário (Julho)",
    datetime.date(2026, 8, 28): "Pagamento do Salário (Agosto)",
    datetime.date(2026, 9, 30): "Pagamento do Salário (Setembro)",
    datetime.date(2026, 10, 30): "Pagamento do Salário (Outubro)",
    datetime.date(2026, 11, 30): "Pagamento do Salário (Novembro)",
    datetime.date(2026, 12, 30): "Pagamento do Salário (Dezembro)",
}

DATAS_PAGAMENTO_13 = {
    # --- 2025 ---
    datetime.date(2025, 1, 10): "Adiantamento 1ª parcela do 13º Salário",
    datetime.date(2025, 11, 28): "13º Salário (para quem não pediu adiantamento)",
    datetime.date(2025, 12, 19): "2ª parcela do 13º Salário",
    # [cite_start]--- 2026 [cite: 42] ---
    datetime.date(2026, 1, 9): "Adiantamento 1ª parcela do 13º Salário",
    datetime.date(2026, 11, 30): "1ª parcela do 13º Salário (para quem não adiantou)",
    datetime.date(2026, 12, 18): "2ª parcela do 13º Salário",
}

DATAS_ADIANTAMENTO_SALARIO = {
    # --- 2025 ---
    datetime.date(2025, 1, 15): "Adiantamento Salarial (Janeiro)",
    datetime.date(2025, 2, 14): "Adiantamento Salarial (Fevereiro)",
    datetime.date(2025, 3, 14): "Adiantamento Salarial (Março)",
    datetime.date(2025, 4, 15): "Adiantamento Salarial (Abril)",
    datetime.date(2025, 5, 15): "Adiantamento Salarial (Maio)",
    datetime.date(2025, 6, 13): "Adiantamento Salarial (Junho)",
    datetime.date(2025, 7, 15): "Adiantamento Salarial (Julho)",
    datetime.date(2025, 8, 15): "Adiantamento Salarial (Agosto)",
    datetime.date(2025, 9, 15): "Adiantamento Salarial (Setembro)",
    datetime.date(2025, 10, 15): "Adiantamento Salarial (Outubro)",
    datetime.date(2025, 11, 14): "Adiantamento Salarial (Novembro)",
    datetime.date(2025, 12, 12): "Adiantamento Salarial (Dezembro)",
    # [cite_start]--- 2026 [cite: 16-41] ---
    datetime.date(2026, 1, 15): "Adiantamento Salarial (Janeiro)",
    datetime.date(2026, 2, 13): "Adiantamento Salarial (Fevereiro)",
    datetime.date(2026, 3, 13): "Adiantamento Salarial (Março)",
    datetime.date(2026, 4, 15): "Adiantamento Salarial (Abril)",
    datetime.date(2026, 5, 15): "Adiantamento Salarial (Maio)",
    datetime.date(2026, 6, 15): "Adiantamento Salarial (Junho)",
    datetime.date(2026, 7, 15): "Adiantamento Salarial (Julho)",
    datetime.date(2026, 8, 14): "Adiantamento Salarial (Agosto)",
    datetime.date(2026, 9, 15): "Adiantamento Salarial (Setembro)",
    datetime.date(2026, 10, 15): "Adiantamento Salarial (Outubro)",
    datetime.date(2026, 11, 13): "Adiantamento Salarial (Novembro)",
    datetime.date(2026, 12, 11): "Adiantamento Salarial (Dezembro)",
}

CESTA_NATALINA = {
    # --- 2025 ---
    datetime.date(2025, 12, 19): "Cesta Natalina",
    # [cite_start]--- 2026 [cite: 63] ---
    datetime.date(2026, 12, 18): "Cesta Natalina",
}
