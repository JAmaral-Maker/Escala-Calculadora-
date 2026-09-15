import datetime
import calendar
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Calculadora de Escalas SPDE", page_icon="🛡️", layout="centered"
)

# Estilo visual limpo
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""",
        unsafe_allow_html=True,
)

# Barra Lateral - Configurações Salariais
st.sidebar.markdown("## ⚙️ Configurações Salariais")
valor_hora = st.sidebar.number_input(
    "Valor base por hora (€):", min_value=0.0, value=5.87, step=0.01
)
desc_ss = (
    st.sidebar.slider(
        "Desconto Segurança Social (%):", min_value=0.0, max_value=20.0, value=11.0
    )
    / 100
)
desc_irs = (
    st.sidebar.slider(
        "Desconto IRS (%):", min_value=0.0, max_value=30.0, value=4.23
    )
    / 100
)

# Cabeçalho Principal
st.title("🛡️ Gestor de Escala & Salário")
st.markdown(
    "Gera a tua escala mensal automaticamente e calcula os teus ganhos brutos e líquidos."
)

# Identificação
nome = st.text_input("Nome do Trabalhador:", value="João Amaral")

# Gestão de Turnos na Sessão
if "turnos_guardados" not in st.session_state:
    st.session_state.turnos_guardados = []

# Abas da Aplicação
aba1, aba2 = st.tabs(
    ["📅 Geração Automática de Escala", "📊 Resistor & Contabilidade"]
)

with aba1:
    st.markdown("### 🗓️ Gerar Escala Mensal Automática")
    st.markdown(
        "Aplica o teu padrão fixo: **Segundas, Terças e Quintas (23h-07h = 8h)** e **Sábados e Domingos (07h-19h = 12h)**."
    )

    col1, col2 = st.columns(2)
    with col1:
        ano_sel = st.selectbox("Ano:", [2026, 2027], index=0)
    with col2:
        mes_sel = st.selectbox(
            "Mês:", list(range(1, 13)), index=8, format_func=lambda x: calendar.month_name[x]
        )

    if st.button("🚀 Gerar Escala para este Mês", type="primary"):
        st.session_state.turnos_guardados = []
        num_dias = calendar.monthrange(ano_sel, mes_sel)[1]

        for dia in range(1, num_dias + 1):
            data_atual = datetime.date(ano_sel, mes_sel, dia)
            dia_semana = data_atual.weekday()  # 0=Seg, 1=Ter, ..., 6=Dom

            # Segunda (0), Terça (1), Quinta (3) -> Noturno (8h)
            if dia_semana in [0, 1, 3]:
                st.session_state.turnos_guardados.append(
                    {
                        "data": data_atual.strftime("%Y-%m-%d"),
                        "tipo": "Noturno (8h)",
                        "horas": 8.0,
                        "valor_hora": valor_hora,
                    }
                )
            # Sábado (5), Domingo (6) -> Fim de Semana (12h)
            elif dia_semana in [5, 6]:
                st.session_state.turnos_guardados.append(
                    {
                        "data": data_atual.strftime("%Y-%m-%d"),
                        "tipo": "Fim de Semana (12h)",
                        "horas": 12.0,
                        "valor_hora": valor_hora,
                    }
                )

        st.success(
            f"Escala gerada com sucesso para {calendar.month_name[mes_sel]}!"
        )
        st.rerun()

with aba2:
    st.markdown("### 📋 Resumo dos Turnos e Salário")

    if st.session_state.turnos_guardados:
        # Calcular totais
        total_horas = sum(t["horas"] for t in st.session_state.turnos_guardados)
        total_bruto = sum(
            t["horas"] * t["valor_hora"]
            for t in st.session_state.turnos_guardados
        )

        valor_ss = total_bruto * desc_ss
        valor_irs = total_bruto * desc_irs
        total_liquido = total_bruto - (valor_ss + valor_irs)

        # Métricas visuais
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de Horas", f"{total_horas:.1f} h")
        col_m2.metric("Total Bruto", f"{total_bruto:.2f} €")
        col_m3.metric("Total Líquido", f"{total_liquido:.2f} €")

        st.markdown("---")
        st.markdown(f"**Detalhes dos Descontos:**")
        st.write(
            f"• Segurança Social ({(desc_ss*100):.1f}%): -{valor_ss:.2f} €"
        )
        st.write(f"• IRS ({(desc_irs*100):.1f}%): -{valor_irs:.2f} €")

        st.markdown("---")
        st.markdown("#### Lista de Turnos do Mês:")
        st.dataframe(st.session_state.turnos_guardados, use_container_width=True)

        if st.button("🗑️ Limpar Todos os Registos"):
            st.session_state.turnos_guardados = []
            st.rerun()
    else:
        st.info(
            "Ainda não tens turnos gerados. Vai à aba 'Geração Automática de Escala' e clica no botão para criar o mês!"
        )

