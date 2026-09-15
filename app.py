import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gestão de Escalas e Salários", page_icon="⏰", layout="centered"
)

st.title("⏰ Gestão de Escalas e Salários")
st.write(
    "Regista a tua identificação, configura a tua escala e calcula os teus"
    " ganhos."
)

# --- Identificação Geral ---
st.subheader("1. Identificação")
nome = st.text_input("Nome do Trabalhador:", placeholder="Ex: João Amaral")

# Configurações na barra lateral
st.sidebar.header("⚙️ Configurações Salariais")
valor_hora_base = st.sidebar.number_input(
    "Valor base por hora (€):", min_value=0.0, value=7.50, step=0.50
)

# Criar Abas para diferentes formas de cálculo
tab1, tab2 = st.tabs(["📊 Estimativa Mensal", "📝 Registo Detalhado de Turnos"])

# --- ABA 1: Estimativa Rápida ---
with tab1:
  st.subheader("Cálculo Estimado por Mês")
  col1, col2 = st.columns(2)

  with col1:
    turnos_mes = st.number_input(
        "Total de turnos no mês:", min_value=1, max_value=31, value=16
    )
  with col2:
    horas_por_turno = st.number_input(
        "Horas por cada turno:", min_value=1.0, max_value=24.0, value=8.0, step=0.5
    )

  if st.button("Calcular Estimativa", type="primary"):
    if not nome:
      st.warning("Por favor, introduz o teu nome primeiro.")
    else:
      total_horas = turnos_mes * horas_por_turno
      total_receber = total_horas * valor_hora_base

      st.markdown("---")
      mcol1, mcol2, mcol3 = st.columns(3)
      mcol1.metric("Turnos", f"{turnos_mes}")
      mcol2.metric("Total Horas", f"{total_horas:,.1f} h")
      mcol3.metric("A Receber", f"{total_receber:,.2f} €")

      st.success(
          f"Olá **{nome}**! Com base na tua estimativa, vais acumular"
          f" **{total_horas:,.1f} horas** e deves receber cerca de"
          f" **{total_receber:,.2f} €**."
      )

# --- ABA 2: Registo de Turnos (Diário) ---
with tab2:
  st.subheader("Adicionar Turno à Escala")

  data_turno = st.date_input("Data do turno:", datetime.date.today())
  tipo_turno = st.selectbox(
      "Tipo de Turno:", ["Normal", "Noturno", "Fim de Semana"]
  )
  horas_turno_reg = st.number_input(
      "Duração do turno (horas):", min_value=1.0, max_value=24.0, value=8.0
  )

  # Inicializar histórico na sessão
  if "historico_turnos" not in st.session_state:
    st.session_state.historico_turnos = []

  if st.button("Adicionar este Turno"):
    st.session_state.historico_turnos.append({
        "Data": data_turno,
        "Tipo": tipo_turno,
        "Horas": horas_turno_reg,
        "Valor/Hora": valor_hora_base,
    })
    st.success("Turno adicionado com sucesso!")

  # Mostrar tabela se houver registos
  if st.session_state.historico_turnos:
    st.markdown("---")
    st.subheader(
        f"Resumo de Turnos Registados para: {nome if nome else 'Utilizador'}"
    )

    df = pd.DataFrame(st.session_state.historico_turnos)
    st.dataframe(df, use_container_width=True)

    total_horas_reg = df["Horas"].sum()
    total_valor_reg = (df["Horas"] * df["Valor/Hora"]).sum()

    rcol1, rcol2 = st.columns(2)
    rcol1.metric("Total de Horas Registadas", f"{total_horas_reg:.1f} h")
    rcol2.metric("Total a Receber", f"{total_valor_reg:.2f} €")

    if st.button("Limpar Histórico"):
      st.session_state.historico_turnos = []
      st.rerun()
