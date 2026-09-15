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

# --- GESTÃO DE ESTADO GLOBAL ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "utilizador_atual" not in st.session_state:
    st.session_state.utilizador_atual = None

if "perfis_guardados" not in st.session_state:
    st.session_state.perfis_guardados = {}


# --- 1. ECRÃ DE LOGIN / REGISTO POR PIN ---
if not st.session_state.autenticado:
    st.markdown("## 🛡️ Gestor de Escala PRO")
    st.write("Acede à tua conta ou cria um novo perfil.")
    
    nomes_existentes = list(st.session_state.perfis_guardados.keys())
    
    if not nomes_existentes:
        st.info("👋 Bem-vindo! Começa por criar o teu perfil.")
        aba_registo, aba_login = st.tabs(["➕ Criar Novo Perfil", "🔑 Entrar"])
    else:
        aba_login, aba_registo = st.tabs(["🔑 Entrar", "➕ Criar Novo Perfil"])
    
    with aba_login:
        if nomes_existentes:
            with st.form("form_login"):
                nome_escolhido = st.selectbox("Seleciona o teu Nome", options=nomes_existentes)
                pin_input = st.text_input("PIN de Acesso (4 dígitos)", type="password", max_chars=4)
                
                btn_login = st.form_submit_button("🔓 Entrar", type="primary", use_container_width=True)
                
                if btn_login:
                    if nome_escolhido in st.session_state.perfis_guardados:
                        perfil = st.session_state.perfis_guardados[nome_escolhido]
                        if perfil["pin"] == pin_input:
                            st.session_state.autenticado = True
                            st.session_state.utilizador_atual = nome_escolhido
                            st.success("Login efetuado com sucesso!")
                            st.rerun()
                        else:
                            st.error("PIN incorreto.")
                    else:
                        st.error("Utilizador não encontrado.")
        else:
            st.warning("Ainda não existem utilizadores registados.")

    with aba_registo:
        with st.form("form_registo"):
            st.markdown("### Criar Nova Conta")
            novo_nome = st.text_input("Nome do Utilizador")
            novo_pin = st.text_input("Define um PIN (4 dígitos)", type="password", max_chars=4)
            
            c1, c2 = st.columns(2)
            with c1:
                reg_v_hora = st.number_input("Valor Hora Base (€)", value=0.0, step=0.25, format="%.2f")
                reg_irs = st.number_input("IRS (%)", value=0.0, step=0.5, format="%.1f")
            with c2:
                reg_sub = st.number_input("Subs. Refeição (€)", value=0.0, step=0.50, format="%.2f")
                reg_ss = st.number_input("Seg. Social (%)", value=0.0, step=0.0, format="%.1f")
                
            btn_criar = st.form_submit_button("✨ Registar e Entrar", use_container_width=True)
            
            if btn_criar:
                if not novo_nome.strip():
                    st.warning("Por favor, introduz um nome válido.")
                elif len(novo_pin) != 4 or not novo_pin.isdigit():
                    st.warning("O PIN deve conter exatamente 4 dígitos numéricos.")
                elif novo_nome in st.session_state.perfis_guardados:
                    st.warning("Esse nome já existe. Escolhe outro.")
                else:
                    st.session_state.perfis_guardados[novo_nome] = {
                        "pin": novo_pin,
                        "valor_hora": reg_v_hora,
                        "subs_refeicao": reg_sub,
                        "taxa_irs": reg_irs,
                        "taxa_ss": reg_ss,
                        "escala_dados": {}
                    }
                    st.session_state.autenticado = True
                    st.session_state.utilizador_atual = novo_nome
                    st.success("Perfil criado com sucesso!")
                    st.rerun()

    if nomes_existentes:
        st.markdown("---")
        if st.button("🗑️ Limpar Todos os Dados da Aplicação", use_container_width=True):
            st.session_state.clear()
            st.rerun()

else:
    # --- 2. APLICAÇÃO PRINCIPAL ---
    nome_u = st.session_state.utilizador_atual
    
    if nome_u not in st.session_state.perfis_guardados:
        st.session_state.autenticado = False
        st.session_state.utilizador_atual = None
        st.rerun()

    dados_perfil = st.session_state.perfis_guardados[nome_u]

    v_hora = dados_perfil["valor_hora"]
    s_refeicao = dados_perfil["subs_refeicao"]
    t_irs = dados_perfil["taxa_irs"]
    t_ss = dados_perfil["taxa_ss"]
    
    if "escala_dados" not in dados_perfil:
        dados_perfil["escala_dados"] = {}
    escala_dados = dados_perfil["escala_dados"]

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f"### 👤 Utilizador: {nome_u}")
        st.markdown("### ⚙️ Definições Gerais")
        
        novo_v_hora = st.number_input("Valor Hora Base de Referência (€)", value=v_hora, step=0.25, format="%.2f")
        novo_s_refeicao = st.number_input("Subs. Refeição (€)", value=s_refeicao, step=0.50, format="%.2f")
        
        novo_t_irs = st.number_input("IRS (%)", value=t_irs, step=0.5, format="%.1f")
        novo_t_ss = st.number_input("Segurança Social (%)", value=t_ss, step=0.0, format="%.1f")
        
        dados_perfil["valor_hora"] = novo_v_hora
        dados_perfil["subs_refeicao"] = novo_s_refeicao
        dados_perfil["taxa_irs"] = novo_t_irs
        dados_perfil["taxa_ss"] = novo_t_ss
        
        st.markdown("---")
        if st.button("🔒 Sair da Conta", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.utilizador_atual = None
            st.rerun()
            
        st.markdown("---")
        if st.button("🗑️ Apagar Conta", use_container_width=True):
            if nome_u in st.session_state.perfis_guardados:
                del st.session_state.perfis_guardados[nome_u]
            st.session_state.autenticado = False
            st.session_state.utilizador_atual = None
            st.rerun()

    # --- CABEÇALHO PRINCIPAL ---
    st.markdown(f"## 🛡️ Olá, {nome_u}!")
    
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
        
        # PAINEL DE CONFIGURAÇÃO COM VALOR HORA POR TURNO
        with st.expander("⚙️ Configurar Dias, Horários e Valor Hora por Turno", expanded=False):
            st.write("Seleciona os dias, dá nome ao turno, define as horas e o respetivo valor por hora (ex: valor noturno diferenciado):")
            
            dias_semana_lista = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            
            config_dias = {}
            for d in dias_semana_lista:
                st.markdown(f"**{d}**")
                c_trab = st.checkbox(f"Trabalha à {d}?", value=False, key=f"chk_{d}")
                if c_trab:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        t_nome = st.text_input(f"Nome do Turno ({d})", value="Trabalho", key=f"nome_{d}")
                    with c2:
                        t_horas = st.number_input(f"Horas ({d})", value=8.0, step=0.5, key=f"h_{d}")
                    with c3:
                        t_vhora = st.number_input(f"Valor/Hora (€) ({d})", value=novo_v_hora, step=0.25, format="%.2f", key=f"vh_{d}")
                    
                    config_dias[d] = {"trabalha": True, "estado": t_nome, "horas": t_horas, "valor_hora": t_vhora}
                else:
                    config_dias[d] = {"trabalha": False, "estado": "Folga", "horas": 0.0, "valor_hora": 0.0}
                st.markdown("---")

        if st.button("🚀 Gerar Escala com a Minha Configuração", type="primary", use_container_width=True):
            _, ultimo_dia = calendar.monthrange(ano_ativo, num_mes)
            lista_dias = []
            
            for dia in range(1, ultimo_dia + 1):
                data_atual = datetime.date(ano_ativo, num_mes, dia)
                dia_sem_idx = data_atual.weekday()
                nome_dia_sem = dias_semana_lista[dia_sem_idx]
                
                info_dia = config_dias.get(nome_dia_sem, {"trabalha": False, "estado": "Folga", "horas": 0.0, "valor_hora": 0.0})
                
                if info_dia["trabalha"]:
                    estado = info_dia["estado"]
                    h = info_dia["horas"]
                    vh = info_dia["valor_hora"]
                else:
                    estado = "Folga"
                    h = 0.0
                    vh = 0.0
                
                data_formatada = f"{dia:02d}/{num_mes:02d}/{ano_ativo}"
                
                lista_dias.append({
                    "Dia": data_formatada,
                    "Dia da Semana": nome_dia_sem,
                    "Estado": estado,
                    "Horas": h,
                    "Valor/Hora (€)": vh
                })
                
            df_novo = pd.DataFrame(lista_dias)
            escala_dados[chave_mes] = df_novo
            st.success("Escala gerada com valores por hora personalizados por turno!")
            st.rerun()

        st.markdown("#### Histórico do Mês (Podes editar diretamente na tabela abaixo, incluindo o valor/hora)")
        if chave_mes in escala_dados and not escala_dados[chave_mes].empty:
            df_atual = escala_dados[chave_mes]
            df_editado = st.data_editor(
                df_atual,
                num_rows="fixed",
                use_container_width=True,
                key=f"editor_{nome_u}_{chave_mes}"
            )
            escala_dados[chave_mes] = df_editado
        else:
            st.info("Ainda não tens escala gerada para este mês. Configura os teus dias acima e clica em gerar.")

    with tab2:
        st.markdown("### ✏️ Ajustes Pontuais & Períodos")
        st.write("Aplica alterações rápidas a dias isolados ou intervalos (ex: férias, folgas extra).")
        
        tipo_ajuste = st.selectbox(
            "Novo Estado a Aplicar", 
            ["Folga", "Férias", "Falta Justificada", "Trabalho (Noite)", "Trabalho (Normal)", "Trabalho (Extra)"]
        )
        
        col_d1, col_d2 = st.columns(2)
        _, ultimo_dia_mes = calendar.monthrange(ano_ativo, num_mes)
        
        with col_d1:
            dia_inicio = st.number_input("Dia de Início", min_value=1, max_value=ultimo_dia_mes, value=1)
        with col_d2:
            dia_fim = st.number_input("Dia de Fim", min_value=1, max_value=ultimo_dia_mes, value=1)
            
        col_aj1, col_aj2 = st.columns(2)
        with col_aj1:
            h_ajuste = st.number_input("Horas para este período", value=8.0, step=0.5)
        with col_aj2:
            vh_ajuste = st.number_input("Valor/Hora (€) para este período", value=novo_v_hora, step=0.25, format="%.2f")
            
        if st.button("⚡ Aplicar ao Período", use_container_width=True):
            if chave_mes not in escala_dados or escala_dados[chave_mes].empty:
                st.warning("Primeiro deves gerar a escala do mês.")
            else:
                df_temp = escala_dados[chave_mes]
                for index, row in df_temp.iterrows():
                    d_num = int(row["Dia"].split("/")[0])
                    if dia_inicio <= d_num <= dia_fim:
                        df_temp.at[index, "Estado"] = tipo_ajuste
                        is_trabalho = not any(w in tipo_ajuste.lower() for w in ["folga", "férias", "falta"])
                        df_temp.at[index, "Horas"] = h_ajuste if is_trabalho else 0.0
                        df_temp.at[index, "Valor/Hora (€)"] = vh_ajuste if is_trabalho else 0.0
                
                escala_dados[chave_mes] = df_temp
                st.success(f"Período atualizado com sucesso!")
                st.rerun()

    with tab3:
        st.markdown(f"### 📊 Resumo do Mês ({mes_ativo_pt} {ano_ativo})")
        
        if chave_mes in escala_dados and not escala_dados[chave_mes].empty:
            df_res = escala_dados[chave_mes]
            mask_trab = ~df_res["Estado"].str.contains("Folga|Férias|Falta", case=False, na=False)
            df_trab = df_res[mask_trab]
            
            horas_mes = df_trab["Horas"].sum()
            dias_trabalho = len(df_trab)
            
            # Cálculo exato multiplicando cada hora pelo respetivo valor/hora da linha
            if "Valor/Hora (€)" in df_trab.columns:
                salario_base = (df_trab["Horas"] * df_trab["Valor/Hora (€)"]).sum()
            else:
                salario_base = horas_mes * novo_v_hora
        else:
            horas_mes = 0.0
            dias_trabalho = 0
            salario_base = 0.0
            
        sub_ref_total = dias_trabalho * novo_s_refeicao
        total_bruto = salario_base + sub_ref_total
        
        desconto_irs_val = total_bruto * (novo_t_irs / 100)
        desconto_ss_val = total_bruto * (novo_t_ss / 100)
        total_liquido = total_bruto - desconto_irs_val - desconto_ss_val
        
        st.metric("Total Líquido Estimado", f"{total_liquido:.2f} €")
        st.metric("Total Bruto", f"{total_bruto:.2f} €")
        st.metric("Total Horas Trabalhadas", f"{horas_mes}h")
        st.metric("Subsídio de Refeição", f"{sub_ref_total:.2f} €")
        
        st.markdown("---")
        if st.button("📤 Copiar para WhatsApp", use_container_width=True):
            resumo_zap = f"Resumo {mes_ativo_pt} {ano_ativo} ({nome_u}):\nTotal Horas: {horas_mes}h\nLíquido: {total_liquido:.2f}€"
            st.code(resumo_zap, language="text")
            st.success("Copiado!")

    with tab4:
        st.markdown(f"### 📈 Resumo Anual Global ({ano_ativo})")
        registos_ano = []
        total_horas_ano = 0.0
        total_liquido_ano = 0.0
        
        for k, df_m in escala_dados.items():
            if df_m.empty:
                continue
            partes = k.split("-")
            if len(partes) == 2 and int(partes[0]) == ano_ativo:
                m_num = int(partes[1])
                m_nome_pt = [k_pt for k_en, m_n in meses_num.items() if m_n == m_num and (k_pt := meses_pt.get(k_en))]
                m_nome_pt = m_nome_pt[0] if m_nome_pt else str(m_num)
                
                mask_t = ~df_m["Estado"].str.contains("Folga|Férias|Falta", case=False, na=False)
                df_tm = df_m[mask_t]
                
                h_m = df_tm["Horas"].sum()
                d_m = len(df_tm)
                
                if "Valor/Hora (€)" in df_tm.columns:
                    s_base_m = (df_tm["Horas"] * df_tm["Valor/Hora (€)"]).sum()
                else:
                    s_base_m = h_m * novo_v_hora
                
                b_m = s_base_m + (d_m * novo_s_refeicao)
                l_m = b_m - (b_m * (novo_t_irs / 100)) - (b_m * (novo_t_ss / 100))
                
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
            registos_ano = sorted(registos_ano, key=lambda x: x["Mês_Num"])
            st.metric("Total Líquido Acumulado no Ano", f"{total_liquido_ano:.2f} €")
            st.metric("Total Horas no Ano", f"{total_horas_ano}h")
            
            st.markdown("---")
            df_anual = pd.DataFrame(registos_ano)
            st.bar_chart(df_anual.set_index("Mês")["Líquido (€)"])
            st.dataframe(df_anual.drop(columns=["Mês_Num"]), use_container_width=True, hide_index=True)
        else:
            st.info(f"Ainda não tens meses gerados para o ano {ano_ativo}.")

    with st.sidebar:
        st.markdown("---")
        st.caption("Gestor de Escala PRO v4.1 (Valor Hora Dinâmico por Turno)")
