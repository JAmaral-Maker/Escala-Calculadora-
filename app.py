import streamlit as st
import datetime
import calendar

# Configuração da página
st.set_page_config(
    page_title="Gestor de Escala & Salário PRO",
    page_icon="🛡️",
    layout="centered"
)

# Dicionário de tradução dos meses para português
meses_pt = {
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro"
}

# Meses em inglês para compatibilidade com o seletor
meses_ingles = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]

# --- BARRA LATERAL: Configurações e Perfil ---
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")
    
    # Perfil / Nome
    nome_utilizador = st.text_input("Nome do Utilizador", value="João Amaral")
    
    st.markdown("### Parâmetros Salariais")
    valor_hora = st.number_input("Valor da Hora Base (€)", value=7.50, step=0.25)
    subs_refeicao = st.number_input("Subsídio de Refeição / Dia (€)", value=6.00, step=0.50)
    
    st.markdown("### Descontos (%)")
    taxa_irs = st.number_input("IRS (%)", value=13.0, step=0.5)
    taxa_ss = st.number_input("Segurança Social (%)", value=11.0, step=0.0)
    
    st.markdown("### Padrão Semanal")
    st.info("Configura aqui os teus turnos habituais.")
    turno_padrao = st.text_input("Descrição do Turno Padrão", value="23h - 07h (Noite)")
    horas_padrao = st.number_input("Horas por Turno", value=8.0, step=0.5)

# --- CABEÇALHO PRINCIPAL ---
st.markdown("## 🛡️ Gestor de Escala & Salário PRO")
st.write(f"Olá, **{nome_utilizador}**! Gere e consulta o teu histórico e escalas mensais.")

# Seleção de Ano e Mês Ativo
col_ano, col_mes = st.columns(2)
with col_ano:
    ano_ativo = st.selectbox("Ano:", options=[2026, 2027, 2028], index=0)

with col_mes:
    # Mês ativo traduzido visualmente com o format_func
    mes_ativo_en = st.selectbox(
        "Mês Ativo:", 
        options=meses_ingles, 
        index=8, # Setembro por defeito (exemplo)
        format_func=lambda x: meses_pt.get(x, x)
    )

mes_ativo_pt = meses_pt.get(mes_ativo_en)

st.markdown("---")

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3 = st.tabs(["📅 Gerar / Editar Mês", "✏️ Ajustes Pontuais", "📊 Resumo, Banco & Envio"])

with tab1:
    st.markdown(f"### 🗓️ Geração de Escala para {mes_ativo_pt} {ano_ativo}")
    st.write("Clica no botão abaixo para preencher automaticamente os dias do mês com base no teu padrão semanal configurado na barra lateral.")
    
    if st.button("🚀 Gerar Escala para este Mês", type="primary"):
        st.success(f"Escala gerada com sucesso para {mes_ativo_pt} {ano_ativo}!")
        
    # Exemplo visual de tabela de escala
    st.markdown("#### Histórico de Turnos do Mês")
    st.info("Abaixo aparecerão os dias gerados onde poderás marcar presença, folgas ou turnos extra.")

with tab2:
    st.markdown("### ✏️ Ajustes Pontuais")
    st.write("Adiciona faltas, férias, dias de baja ou ajustes de última hora no mês selecionado.")
    
    dia_ajuste = st.number_input("Dia do Mês", min_value=1, max_value=31, value=1)
    tipo_ajuste = st.selectbox("Tipo de Registo", ["Folga Extra", "Falta Justificada", "Horas Extra (Extra)", "Férias"])
    horas_extra = st.number_input("Horas Ajustadas", value=0.0, step=0.5)
    
    if st.button("Guardar Ajuste"):
        st.success(f"Ajuste para o dia {dia_ajuste} guardado com sucesso!")

with tab3:
    st.markdown("### 📊 Resumo Financeiro & Banco de Horas")
    
    # Cálculos simulados para demonstração
    horas_mes = 160
    salario_base = horas_mes * valor_hora
    sub_ref_total = 22 * subs_refeicao
    total_bruto = salario_base + sub_ref_total
    
    desconto_irs_val = total_bruto * (taxa_irs / 100)
    desconto_ss_val = total_bruto * (taxa_ss / 100)
    total_liquido = total_bruto - desconto_irs_val - desconto_ss_val
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Bruto Estimado", f"{total_bruto:.2f} €")
        st.metric("Descontos (IRS + SS)", f"{(desconto_irs_val + desconto_ss_val):.2f} €")
    with col2:
        st.metric("Total Líquido Final", f"{total_liquido:.2f} €", delta="Estimativa")
        st.metric("Subsídio de Refeição", f"{sub_ref_total:.2f} €")
        
    st.markdown("---")
    if st.button("📤 Copiar Resumo para WhatsApp"):
        resumo_whatsapp = f"Resumo {mes_ativo_pt} {ano_ativo}:\nLíquido Estimado: {total_liquido:.2f}€\nHoras: {horas_mes}h"
        st.code(resumo_whatsapp, language="text")
        st.success("Resumo pronto a copiar!")

# Rodapé discreto na barra lateral para controlo
with st.sidebar:
    st.markdown("---")
    st.caption("Gestor de Escala & Salário PRO v2.1")
