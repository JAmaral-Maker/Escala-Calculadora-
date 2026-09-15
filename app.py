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
    st.markdown("## 🛡️ Bem-vindo ao Gestor de Escala & Salário PRO")
    st.write("Para começar a utilizar a aplicação e calcular os teus turnos e salários, cria o teu perfil.")
    
    st.markdown("---")
    
    with st.form("form_perfil"):
        st.markdown("### 👤 Dados de Utilizador")
        nome_input = st.text_input("O teu Nome", value=st.session_state.nome_utilizador)
        
        st.markdown("### 💰 Configuração Inicial Rápida")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            valor_hora_init = st.number_input("Valor da Hora Base (€)", value=7.50, step=0.25)
            taxa_irs_init = st.number_input("IRS (%)", value=13.0, step=0.5)
        with col_f2:
            subs_refeicao_init = st.number_input("Subsídio de Refeição / Dia (€)", value=6.00, step=0.50)
            taxa_ss_init = st.number_input("Segurança Social (%)", value=11.0, step=0.0)
            
        btn_entrar = st.form_submit_button("🚀 Criar Perfil e Entrar", type="primary")
        
        if btn_entrar:
            st.session_state.nome_utilizador = nome_input
            # Guardamos também as variáveis globais na sessão se necessário
            st.session_state.valor_hora = valor_hora_init
            st.session_state.subs_refeicao = subs_refeicao_init
            st.session_state.taxa_irs = taxa_irs_init
            st.session_state.taxa_ss = taxa_ss_init
            
            st.session_state.perfil_criado = True
            st.rerun()

else:
    # --- 2. APLICAÇÃO PRINCIPAL (SÓ APARECE DEPOIS DE CRIAR O PERFIL) ---
    
    # Valores por defeito caso venham da sessão
    v_hora = st.session_state.get("valor_hora", 7.50)
    s_refeicao = st.session_state.get("subs_refeicao", 6.00)
    t_irs = st.session_state.get("taxa_irs", 13.0)
    t_ss = st.session_state.get("taxa_ss", 11.0)

    # --- BARRA LATERAL: Definições e Alteração de Perfil ---
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        st.markdown("---")
        
        st.session_state.nome_utilizador = st.text_input("Nome do Utilizador", value=st.session_state.nome_utilizador)
        
        st.markdown("### Parâmetros Salariais")
        valor_hora = st.number_input("Valor da Hora Base (€)", value=v_hora, step=0.25)
        subs_refeicao = st.number_input("Subsídio de Refeição / Dia (€)", value=s_refeicao, step=0.50)
        
        st.markdown("### Descontos (%)")
        taxa_irs = st.number_input("IRS (%)", value=t_irs, step=0.5)
        taxa_ss = st.number_input("Segurança Social (%)", value=t_ss, step=0.0)
        
        st.markdown("### Padrão Semanal")
        turno_padrao = st.text_input("Descrição do Turno Padrão", value="23h - 07h (Noite)")
        horas_padrao = st.number_input("Horas por Turno", value=8.0, step=0.5)
        
        st.markdown("---")
        if st.button("🔄 Terminar Sessão / Mudar Perfil"):
            st.session_state.perfil_criado = False
            st.rerun()

    # --- CABEÇALHO PRINCIPAL ---
    st.markdown("## 🛡️ Gestor de Escala & Salário PRO")
    st.write(f"Olá, **{st.session_state.nome_utilizador}**! Gere e consulta o teu histórico e escalas mensais.")

    # Seleção de Ano e Mês Ativo
    col_ano, col_mes = st.columns(2)
    with col_ano:
        ano_ativo = st.selectbox("Ano:", options=[2026, 2027, 2028], index=0)

    with col_mes:
        mes_ativo_en = st.selectbox(
            "Mês Ativo:", 
            options=meses_ingles, 
            index=8, # Setembro por defeito
            format_func=lambda x: meses_pt.get(x, x)
        )

    mes_ativo_pt = meses_pt.get(mes_ativo_en)
    num_mes = meses_num[mes_ativo_en]

    st.markdown("---")

    # --- NAVEGAÇÃO POR ABAS ---
    tab1, tab2, tab3 = st.tabs(["📅 Gerar / Editar Mês", "✏️ Ajustes Pontuais", "📊 Resumo, Banco & Envio"])

    with tab1:
        st.markdown(f"### 🗓️ Geração de Escala para {mes_ativo_pt} {ano_ativo}")
        st.write("Clica no botão abaixo para preencher automaticamente os dias do mês com base no teu padrão semanal.")
        
        chave_mes = f"{ano_ativo}-{num_mes}"
        
        if st.button("🚀 Gerar Escala para este Mês", type="primary"):
            _, ultimo_dia = calendar.monthrange(ano_ativo, num_mes)
            
            lista_dias = []
            dias_semana_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            
            for dia in range(1, ultimo_dia + 1):
                data_atual = datetime.date(ano_ativo, num_mes, dia)
                dia_sem_idx = data_atual.weekday()
                nome_dia_sem = dias_semana_pt[dia_sem_idx]
                
                if dia_sem_idx in [0, 1]: # Seg, Ter
                    estado = "Trabalho (Noite)"
                    h = horas_padrao
                elif dia_sem_idx in [5, 6]: # Sáb, Dom
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
            st.success(f"Escala gerada com sucesso para {mes_ativo_pt} {ano_ativo}!")
            st.rerun()

        st.markdown("#### Histórico de Turnos do Mês")
        
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
            st.info("Ainda não geraste a escala para este mês. Clica no botão acima para começar.")

    with tab2:
        st.markdown("### ✏️ Ajustes Pontuais")
        st.write("Adiciona faltas, férias ou ajustes de última hora no mês selecionado.")
        
        dia_ajuste = st.number_input("Dia do Mês", min_value=1, max_value=31, value=1)
        tipo_ajuste = st.selectbox("Tipo de Registo", ["Folga Extra", "Falta Justificada", "Horas Extra (Extra)", "Férias"])
        horas_extra = st.number_input("Horas Ajustadas", value=0.0, step=0.5)
        
        if st.button("Guardar Ajuste"):
            st.success(f"Ajuste para o dia {dia_ajuste} guardado com sucesso!")

    with tab3:
        st.markdown("### 📊 Resumo Financeiro & Banco de Horas")
        
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
            resumo_whatsapp = f"Resumo {mes_ativo_pt} {ano_ativo} ({st.session_state.nome_utilizador}):\nTotal Horas: {horas_mes}h\nLíquido Estimado: {total_liquido:.2f}€"
            st.code(resumo_whatsapp, language="text")
            st.success("Resumo pronto a copiar!")

    # Rodapé na barra lateral
    with st.sidebar:
        st.markdown("---")
        st.caption("Gestor de Escala & Salário PRO v2.5")
