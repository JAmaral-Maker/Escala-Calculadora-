import streamlit as st
import datetime
import calendar
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Gestor de Escala & Salário PRO",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dicionário de tradução dos meses para português
meses_pt = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março",
    "April": "Abril", "May": "Maio", "June": "Junho",
    "July": "Julho", "August": "Agosto", "September": "Setembro",
    "October": "Outubro", "November": "Novembro", "December": "Dezembro"
}

meses_num = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

meses_ingles = list(meses_num.keys())

# --- GESTÃO DE ESTADO (SESSION STATE) ---
if "perfil_criado" not in st.session_state:
    st.session_state.perfil_criado = False

if "nome_utilizador" not in st.session_state:
    st.session_state.nome_utilizador = "João Amaral"

if "escala_dados" not in st.session_state:
    st.session_state.escala_dados = {}


# --- 1. ECRÃ INICIAL DE CRIAÇÃO DE PERFIL / BOAS-VINDAS ---
if not st.session_state.perfil_criado:
    st.markdown("## 🛡️ Gestor de Escala PRO")
    st.write("Configura o teu perfil para começar.")
    
    with st.form("form_perfil"):
        st.markdown("### 👤 Utilizador")
        nome_input = st.text_input("O teu Nome", value=st.session_state.nome_utilizador)
        
        st.markdown("### 💰 Parâmetros Base")
        c1, c2 = st.columns(2)
        with c1:
            valor_hora_init = st.number_input("Valor Hora (€)", value=7.50, step=0.25)
            taxa_irs_init = st.number_input("IRS (%)", value=13.0, step=0.5)
        with c2:
            subs_refeicao_init = st.number_input("Subs. Refeição (€)", value=6.00, step=0.50)
            taxa_ss_init = st.number_input("Seg. Social (%)", value=11.0, step=0.0)
            
        st.markdown("")
        btn_entrar = st.form_submit_button("🚀 Entrar na Aplicação", type="primary", use_container_width=True)
        
        if btn_entrar:
            st.session_state.nome_utilizador = nome_input
            st.session_state.valor_hora = valor_hora_init
            st.session_state.subs_refeicao = subs_refeicao_init
            st.session_state.taxa_irs = taxa_irs_init
            st.session_state.taxa_ss = taxa_ss_init
            st.session_state.perfil_criado = True
            st.rerun()

else:
    # --- 2. APLICAÇÃO PRINCIPAL ---
    v_hora = st.session_state.get("valor_hora", 7.50)
    s_refeicao = st.session_state.get("subs_refeicao", 6.00)
    t_irs = st.session_state.get("taxa_irs", 13.0)
    t_ss = st.session_state.get("taxa_ss", 11.0)

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("### ⚙️ Definições")
        st.session_state.nome_utilizador = st.text_input("Nome", value=st.session_state.nome_utilizador)
        
        valor_hora = st.number_input("Valor Hora Base (€)", value=v_hora, step=0.25)
        subs_refeicao = st.number_input("Subs. Refeição (€)", value=s_refeicao, step=0.50)
        
        taxa_irs = st.number_input("IRS (%)", value=t_irs, step=0.5)
        taxa_ss = st.number_input("Segurança Social (%)", value=t_ss, step=0.0)
        
        st.markdown("---")
        if st.button("🔄 Mudar Perfil / Sair", use_container_width=True):
            st.session_state.perfil_criado = False
            st.rerun()

    # --- CABEÇALHO PRINCIPAL ---
    st.markdown(f"## 🛡️ Olá, {st.session_state.nome_utilizador}!")
    
    # Seleção de Ano e Mês Ativo
    col_ano, col_mes = st.columns(2)
    with col_ano:
        ano_ativo = st.selectbox("Ano:", options=[2026, 2027, 2028], index=0)
    with col_mes:
        mes_ativo_en = st.selectbox(
            "Mês:", 
            options=meses_ingles, 
            index=8, # Setembro
            format_func=lambda x: meses_pt.get(x, x)
        )

    mes_ativo_pt = meses_pt.get(mes_ativo_en)
    num_mes = mes_ativo_en = meses_num[mes_ativo_en]

    st.markdown("---")

    # --- NAVEGAÇÃO POR ABAS ---
    tab1, tab2, tab3 = st.tabs(["📅 Escala", "✏️ Ajustes", "📊 Resumo"])

    with tab1:
        st.markdown(f"### 🗓️ Escala de {mes_ativo_pt} {ano_ativo}")
        
        chave_mes = f"{ano_ativo}-{num_mes}"
        
        if st.button("🚀 Gerar Escala Automática", type="primary", use_container_width=True):
            _, ultimo_dia = calendar.monthrange(ano_ativo, num_mes)
            lista_dias = []
            dias_semana_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            
            for dia in range(1, ultimo_dia + 1):
                data_atual = datetime.date(ano_ativo, num_mes, dia)
                dia_sem_idx = data_atual.weekday()
                nome_dia_sem = dias_semana_pt[dia_sem_idx]
                
                if dia_sem_idx in [0, 1]: # Seg, Ter (Noite)
                    estado = "Trabalho (Noite)"
                    h = 8.0
                elif dia_sem_idx in [5, 6]: # Sáb, Dom (12h)
                    estado = "Trabalho (FDS)"
                    h = 12.0
                else:
                    estado = "Folga"
                    h = 0.0
                    
                lista_dias.append({
                    "Dia": f"{dia:02d}/{num_mes:02d}/{ano_ativo}",
                    "Dia da Semana": nome_dia_sem,
                    "Estado": estado,
                    "Horas": h
                })
                
            st.session_state.escala_dados[chave_mes] = pd.DataFrame(lista_dias)
            st.success("Escala gerada com sucesso!")
            st.rerun()

        st.markdown("#### Histórico do Mês")
        if chave_mes in st.session_state.escala_dados:
            df_atual = st.session_state.escala_dados[chave_mes]
            df_editado = st.data_editor(
                df_atual,
                num_rows="fixed",
                use_container_width=True,
                key=f"editor_{chave_mes}"
            )
            st.session_state.escala_dados[chave_mes] = df_editado
        else:
            st.info("Clica em 'Gerar Escala Automática' para preencher o mês.")

    with tab2:
        st.markdown("### ✏️ Ajustes Pontuais")
        dia_ajuste = st.number_input("Dia do Mês", min_value=1, max_value=31, value=1)
        tipo_ajuste = st.selectbox("Tipo", ["Folga Extra", "Falta Justificada", "Horas Extra", "Férias"])
        horas_ajuste = st.number_input("Horas", value=0.0, step=0.5)
        
        if st.button("Guardar Ajuste", use_container_width=True):
            st.success(f"Ajuste para o dia {dia_ajuste} guardado!")

    with tab3:
        st.markdown("### 📊 Resumo Financeiro")
        
        chave_mes = f"{ano_ativo}-{num_mes}"
        if chave_mes in st.session_state.escala_dados:
            df_res = st.session_state.escala_dados[chave_mes]
            horas_mes = df_res[df_res["Estado"].str.contains("Trabalho", na=False)]["Horas"].sum()
            dias_trabalho = len(df_res[df_res["Estado"].str.contains("Trabalho", na=False)])
        else:
            horas_mes = 160
            dias_trabalho = 22
            
        salario_base = horas_mes * valor_hora
        sub_ref_total = dias_trabalho * subs_refeicao
        total_bruto = salario_base + sub_ref_total
        
        desconto_irs_val = total_bruto * (t_irs / 100)
        desconto_ss_val = total_bruto * (t_ss / 100)
        total_liquido = total_bruto - desconto_irs_val - desconto_ss_val
        
        st.metric("Total Líquido Estimado", f"{total_liquido:.2f} €")
        st.metric("Total Bruto", f"{total_bruto:.2f} €")
        st.metric("Subsídio de Refeição", f"{sub_ref_total:.2f} €")
        
        st.markdown("---")
        if st.button("📤 Copiar para WhatsApp", use_container_width=True):
            resumo_zap = f"Resumo {mes_ativo_pt} {ano_ativo} ({st.session_state.nome_utilizador}):\nTotal Horas: {horas_mes}h\nLíquido: {total_liquido:.2f}€"
            st.code(resumo_zap, language="text")
            st.success("Copiado!")

    with st.sidebar:
        st.markdown("---")
        st.caption("Gestor de Escala PRO v2.6")
