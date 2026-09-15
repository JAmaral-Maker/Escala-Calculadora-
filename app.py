import streamlit as span
import streamlit as st
import datetime
import calendar
import pandas as pd
from supabase import create_client, Client

# Configuração da página
st.set_page_config(
    page_title="Gestor de Escala & Salário PRO",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LIGAÇÃO AO SUPABASE ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "O_TEU_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "O_TEU_SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

# Dicionário de tradução dos meses
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

# --- GESTÃO DE ESTADO ---
if "perfil_criado" not in st.session_state:
    st.session_state.perfil_criado = False

if "nome_utilizador" not in st.session_state:
    st.session_state.nome_utilizador = "João Amaral"

if "escala_dados" not in st.session_state:
    st.session_state.escala_dados = {}


# --- FUNÇÕES DE SUPABASE ---
def carregar_dados_supabase(utilizador, ano):
    if not supabase or SUPABASE_URL == "O_TEU_SUPABASE_URL":
        return
    try:
        response = supabase.table("escalas").select("*").eq("utilizador", utilizador).eq("ano", ano).execute()
        dados = {}
        for row in response.data:
            chave = f"{row['ano']}-{row['mes']}"
            dados[chave] = pd.DataFrame(row['dias_json'])
        st.session_state.escala_dados = dados
    except Exception as e:
        st.error(f"Erro ao carregar do Supabase: {e}")

def guardar_mes_supabase(utilizador, ano, mes, df):
    if not supabase or SUPABASE_URL == "O_TEU_SUPABASE_URL":
        return
    try:
        dias_json = df.to_dict(orient="records")
        supabase.table("escalas").upsert({
            "utilizador": utilizador,
            "ano": ano,
            "mes": mes,
            "dias_json": dias_json
        }, on_conflict="utilizador,ano,mes").execute()
    except Exception as e:
        st.error(f"Erro ao guardar no Supabase: {e}")


# --- 1. ECRÃ INICIAL DE CRIAÇÃO DE PERFIL ---
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
            
            carregar_dados_supabase(nome_input, 2026)
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
    
    col_ano, col_mes = st.columns(2)
    with col_ano:
        ano_ativo = st.selectbox("Ano:", options=[2026, 2027, 2028], index=0)
    with col_mes:
        mes_ativo_en = st.selectbox(
            "Mês Ativo:", 
            options=meses_ingles, 
            index=8, # Setembro
            format_func=lambda x: meses_pt.get(x, x)
        )

    mes_ativo_pt = meses_pt.get(mes_ativo_en)
    num_mes = meses_num[mes_ativo_en]

    st.markdown("---")

    # --- NAVEGAÇÃO POR ABAS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Escala", "✏️ Ajustes & Períodos", "📊 Resumo Mês", "📈 Resumo Anual"])

    chave_mes = f"{ano_ativo}-{num_mes}"

    with tab1:
        st.markdown(f"### 🗓️ Escala de {mes_ativo_pt} {ano_ativo}")
        
        if st.button("🚀 Gerar Escala Automática (Seg/Ter Noite, FDS 12h)", type="primary", use_container_width=True):
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
                
            df_novo = pd.DataFrame(lista_dias)
            st.session_state.escala_dados[chave_mes] = df_novo
            guardar_mes_supabase(st.session_state.nome_utilizador, ano_ativo, num_mes, df_novo)
            
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
            guardar_mes_supabase(st.session_state.nome_utilizador, ano_ativo, num_mes, df_editado)
        else:
            st.info("Clica em 'Gerar Escala Automática' para preencher o mês.")

    with tab2:
        st.markdown("### ✏️ Ajustes Pontuais & Períodos Automáticos")
        st.write("Aplica alterações rápidas a um dia isolado ou a um intervalo de dias (ex: férias, folgas extra).")
        
        tipo_ajuste = st.selectbox(
            "Tipo de Estado a Aplicar", 
            ["Folga", "Férias", "Falta Justificada", "Trabalho (Noite) [8h]", "Trabalho (FDS) [12h]"]
        )
        
        col_d1, col_d2 = st.columns(2)
        _, ultimo_dia_mes = calendar.monthrange(ano_ativo, num_mes)
        
        with col_d1:
            dia_inicio = st.number_input("Dia de Início", min_value=1, max_value=ultimo_dia_mes, value=1)
        with col_d2:
            dia_fim = st.number_input("Dia de Fim (ou igual ao de início)", min_value=1, max_value=ultimo_dia_mes, value=1)
            
        if st.button("⚡ Aplicar ao Período Selecionado", use_container_width=True):
            if chave_mes not in st.session_state.escala_dados:
                st.warning("Primeiro deves gerar a escala do mês na aba 'Escala'.")
            else:
                df_temp = st.session_state.escala_dados[chave_mes]
                
                # Definir horas padrão conforme o tipo escolhido
                if "Noite" in tipo_ajuste:
                    h_val = 8.0
                elif "FDS" in tipo_ajuste:
                    h_val = 12.0
                else:
                    h_val = 0.0 # Folga, Férias, Falta
                
                # Aplicar aos dias selecionados (convertendo índice do dia para o índice do DataFrame)
                for index, row in df_temp.iterrows():
                    d_num = int(row["Dia"].split("/")[0])
                    if dia_inicio <= d_num <= dia_fim:
                        df_temp.at[index, "Estado"] = tipo_ajuste
                        df_temp.at[index, "Horas"] = h_val
                
                st.session_state.escala_dados[chave_mes] = df_temp
                guardar_mes_supabase(st.session_state.nome_utilizador, ano_ativo, num_mes, df_temp)
                st.success(f"Período de {dia_inicio} a {dia_fim} atualizado para '{tipo_ajuste}' com sucesso!")
                st.rerun()

    with tab3:
        st.markdown(f"### 📊 Resumo do Mês ({mes_ativo_pt} {ano_ativo})")
        
        if chave_mes in st.session_state.escala_dados:
            df_res = st.session_state.escala_dados[chave_mes]
            # Considera dias de trabalho tudo o que contenha "Trabalho"
            mask_trab = df_res["Estado"].str.contains("Trabalho", na=False)
            horas_mes = df_res[mask_trab]["Horas"].sum()
            dias_trabalho = len(df_res[mask_trab])
        else:
            horas_mes = 0.0
            dias_trabalho = 0
            
        salario_base = horas_mes * valor_hora
        sub_ref_total = dias_trabalho * subs_refeicao
        total_bruto = salario_base + sub_ref_total
        
        desconto_irs_val = total_bruto * (t_irs / 100)
        desconto_ss_val = total_bruto * (t_ss / 100)
        total_liquido = total_bruto - desconto_irs_val - desconto_ss_val
        
        st.metric("Total Líquido Estimado", f"{total_liquido:.2f} €")
        st.metric("Total Bruto", f"{total_bruto:.2f} €")
        st.metric("Total Horas Trabalhadas", f"{horas_mes}h")
        st.metric("Subsídio de Refeição", f"{sub_ref_total:.2f} €")
        
        st.markdown("---")
        if st.button("📤 Copiar para WhatsApp", use_container_width=True):
            resumo_zap = f"Resumo {mes_ativo_pt} {ano_ativo} ({st.session_state.nome_utilizador}):\nTotal Horas: {horas_mes}h\nLíquido: {total_liquido:.2f}€"
            st.code(resumo_zap, language="text")
            st.success("Copiado!")

    with tab4:
        st.markdown(f"### 📈 Resumo Anual Global ({ano_ativo})")
        st.write("Acumulado de todos os meses gerados/guardados para o ano selecionado.")
        
        registos_ano = []
        total_horas_ano = 0.0
        total_liquido_ano = 0.0
        
        for k, df_m in st.session_state.escala_dados.items():
            partes = k.split("-")
            if len(partes) == 2 and int(partes[0]) == ano_ativo:
                m_num = int(partes[1])
                m_nome_pt = [k_pt for k_en, m_n in meses_num.items() if m_n == m_num and (k_pt := meses_pt.get(k_en))]
                m_nome_pt = m_nome_pt[0] if m_nome_pt else str(m_num)
                
                mask_t = df_m["Estado"].str.contains("Trabalho", na=False)
                h_m = df_m[mask_t]["Horas"].sum()
                d_m = len(df_m[mask_t])
                
                b_m = (h_m * valor_hora) + (d_m * subs_refeicao)
                l_m = b_m - (b_m * (t_irs / 100)) - (b_m * (t_ss / 100))
                
                total_horas_ano += h_m
                total_liquido_ano += l_m
                
                registos_ano.append({
                    "Mês_Num": m_num,
                    "Mês": m_nome_pt,
                    "Horas": h_m,
                    "Dias Trab.": d_m,
                    "Bruto (€)": round(b_m, 2),
                    "Líquido (€)": round(l_m, 2)
                })
                
        if registos_ano:
            # Ordenar por número do mês
            registos_ano = sorted(registos_ano, key=lambda x: x["Mês_Num"])
            
            st.metric("Total Líquido Acumulado no Ano", f"{total_liquido_ano:.2f} €")
            st.metric("Total Horas no Ano", f"{total_horas_ano}h")
            
            st.markdown("---")
            st.markdown("#### 📊 Evolução do Valor Líquido por Mês")
            
            # Preparar dados para o gráfico de barras
            df_anual = pd.DataFrame(registos_ano)
            df_grafico = df_anual.set_index("Mês")["Líquido (€)"]
            st.bar_chart(df_grafico)
            
            st.markdown("#### Detalhe por Mês")
            # Remover a coluna auxiliar Mês_Num antes de mostrar a tabela
            df_tabela = df_anual.drop(columns=["Mês_Num"])
            st.dataframe(df_tabela, use_container_width=True, hide_index=True)
        else:
            st.info(f"Ainda não tens meses guardados para o ano {ano_ativo}.")

    with st.sidebar:
        st.markdown("---")
        st.caption("Gestor de Escala PRO v2.9")
