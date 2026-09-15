import datetime
import calendar
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestor de Escalas & Salários PRO", page_icon="🛡️", layout="centered"
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

# Inicializar Base de Dados de Perfis na Sessão (Memória Local)
if "perfis" not in st.session_state:
    st.session_state.perfis = {
        "João Amaral": {
            "pin": "1994",
            "valor_hora": 5.87,
            "subs_refeicao": 6.00,
            "desc_ss": 11.0,
            "desc_irs": 4.23,
            "turnos": [],
            "padrao_turnos": {
                0: {"ativo": True, "nome": "Noturno", "horas": 8.0, "valor_extra_hora": 0.0},
                1: {"ativo": True, "nome": "Noturno", "horas": 8.0, "valor_extra_hora": 0.0},
                2: {"ativo": False, "nome": "Folga", "horas": 0.0, "valor_extra_hora": 0.0},
                3: {"ativo": True, "nome": "Noturno", "horas": 8.0, "valor_extra_hora": 0.0},
                4: {"ativo": False, "nome": "Folga", "horas": 0.0, "valor_extra_hora": 0.0},
                5: {"ativo": True, "nome": "Fim de Semana", "horas": 12.0, "valor_extra_hora": 0.0},
                6: {"ativo": True, "nome": "Fim de Semana", "horas": 12.0, "valor_extra_hora": 0.0},
            },
        }
    }

if "utilizador_atual" not in st.session_state:
    st.session_state.utilizador_atual = None

# Cabeçalho Principal
st.title("🛡️ Gestor de Escala & Salário PRO")

# Sistema de Autenticação / Seleção de Perfil
if st.session_state.utilizador_atual is None:
    st.markdown("### 🔐 Acesso Seguro à Conta")
    st.markdown("Identifica-te com o teu PIN ou cria um novo perfil.")

    modo = st.radio("Escolhe uma opção:", ["Entrar na minha conta", "Criar novo perfil"])

    lista_nomes = list(st.session_state.perfis.keys())

    if modo == "Entrar na minha conta":
        if lista_nomes:
            nome_escolhido = st.selectbox("Seleciona o teu nome:", lista_nomes)
            pin_inserido = st.text_input("Insere o teu PIN de acesso:", type="password")

            if st.button("🔓 Entrar", type="primary"):
                if pin_inserido == st.session_state.perfis[nome_escolhido]["pin"]:
                    st.session_state.utilizador_atual = nome_escolhido
                    st.success(f"Bem-vindo de volta, {nome_escolhido}!")
                    st.rerun()
                else:
                    st.error("PIN incorreto. Tenta novamente.")
        else:
            st.info("Ainda não existem perfis criados. Cria um novo perfil.")

    else:
        novo_nome = st.text_input("O teu Nome:")
        novo_pin = st.text_input("Cria um PIN secreto (ex: 4 dígitos):", type="password")
        novo_pin_conf = st.text_input("Confirma o PIN secreto:", type="password")

        if st.button("✨ Criar Perfil Privado", type="primary"):
            if not novo_nome:
                st.error("Por favor, insere o teu nome.")
            elif not novo_pin or novo_pin != novo_pin_conf:
                st.error("Os PINs não coincidem ou estão vazios.")
            elif novo_nome in st.session_state.perfis:
                st.error("Este nome já existe. Escolhe outro ou entra na conta.")
            else:
                st.session_state.perfis[novo_nome] = {
                    "pin": novo_pin,
                    "valor_hora": 6.00,
                    "subs_refeicao": 6.00,
                    "desc_ss": 11.0,
                    "desc_irs": 0.0,
                    "turnos": [],
                    "padrao_turnos": {
                        d: {"ativo": False, "nome": "Turno Normal", "horas": 8.0, "valor_extra_hora": 0.0} for d in range(7)
                    },
                }
                st.session_state.utilizador_atual = novo_nome
                st.success(f"Perfil de {novo_nome} criado com sucesso!")
                st.rerun()

else:
    # Utilizador Autenticado - Área Principal
    perfil = st.session_state.perfis[st.session_state.utilizador_atual]

    if "subs_refeicao" not in perfil:
        perfil["subs_refeicao"] = 6.00

    if "padrao_turnos" not in perfil:
        perfil["padrao_turnos"] = {
            d: {"ativo": False, "nome": "Turno Normal", "horas": 8.0, "valor_extra_hora": 0.0} for d in range(7)
        }

    # Barra Lateral - Configurações Salariais e de Padrão
    st.sidebar.markdown(f"## 👤 Sessão: {st.session_state.utilizador_atual}")
    if st.sidebar.button("🚪 Terminar Sessão"):
        st.session_state.utilizador_atual = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚙️ Configurações Salariais")
    perfil["valor_hora"] = st.sidebar.number_input(
        "Valor base por hora (€):", min_value=0.0, value=float(perfil["valor_hora"]), step=0.01
    )
    perfil["subs_refeicao"] = st.sidebar.number_input(
        "Subsídio de Refeição / Dia (€):", min_value=0.0, value=float(perfil["subs_refeicao"]), step=0.25
    )
    perfil["desc_ss"] = (
        st.sidebar.slider(
            "Desconto Segurança Social (%):", min_value=0.0, max_value=20.0, value=float(perfil["desc_ss"])
        )
    )
    perfil["desc_irs"] = (
        st.sidebar.slider(
            "Desconto IRS (%):", min_value=0.0, max_value=30.0, value=float(perfil["desc_irs"])
        )
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🕒 Configurar Padrão Semanal & Extras")
    st.sidebar.markdown("Define dias, horas e adicionais por hora (ex: noites/fins de semana).")

    dias_semana_nrs = [
        ("Segunda-feira", 0), ("Terça-feira", 1), ("Quarta-feira", 2),
        ("Quinta-feira", 3), ("Sexta-feira", 4), ("Sábado", 5), ("Domingo", 6)
    ]

    for nome_dia, idx in dias_semana_nrs:
        with st.sidebar.expander(nome_dia):
            ativo = st.checkbox("Trabalha neste dia?", value=perfil["padrao_turnos"][idx]["ativo"], key=f"ativo_{idx}")
            perfil["padrao_turnos"][idx]["ativo"] = ativo
            if ativo:
                perfil["padrao_turnos"][idx]["nome"] = st.text_input(
                    "Nome do Turno:", value=perfil["padrao_turnos"][idx]["nome"], key=f"nome_turno_{idx}"
                )
                perfil["padrao_turnos"][idx]["horas"] = st.number_input(
                    "Nº de Horas:", min_value=0.5, max_value=24.0, value=float(perfil["padrao_turnos"][idx]["horas"]), step=0.5, key=f"horas_{idx}"
                )
                perfil["padrao_turnos"][idx]["valor_extra_hora"] = st.number_input(
                    "Adicional por hora (€/h extra):", min_value=0.0, value=float(perfil["padrao_turnos"][idx].get("valor_extra_hora", 0.0)), step=0.10, key=f"extra_{idx}", help="Valor a somar à hora base para este turno (ex: noturno ou fim de semana)"
                )

    st.markdown(f"Olá, **{st.session_state.utilizador_atual}**! Gere a tua escala mensal avançada e calcula os teus ganhos.")

    # Abas da Aplicação
    aba1, aba2 = st.tabs(["📅 Geração Automática de Escala", "📊 Resumo & Contabilidade"])

    with aba1:
        st.markdown("### 🗓️ Gerar Escala Mensal Automática")
        st.markdown("A aplicação vai aplicar o padrão semanal configurado na barra lateral para o mês selecionado.")

        col1, col2 = st.columns(2)
        with col1:
            ano_sel = st.selectbox("Ano:", [2026, 2027], index=0)
        with col2:
            mes_sel = st.selectbox("Mês:", list(range(1, 13)), index=8, format_func=lambda x: calendar.month_name[x])

        if st.button("🚀 Gerar Escala para este Mês", type="primary"):
            perfil["turnos"] = []
            num_dias = calendar.monthrange(ano_sel, mes_sel)[1]

            for dia in range(1, num_dias + 1):
                data_atual = datetime.date(ano_sel, mes_sel, dia)
                dia_semana = data_atual.weekday()

                config_dia = perfil["padrao_turnos"][dia_semana]
                if config_dia["ativo"]:
                    perfil["turnos"].append({
                        "data": data_atual.strftime("%Y-%m-%d"),
                        "tipo": config_dia["nome"],
                        "horas": config_dia["horas"],
                        "valor_hora_efetivo": perfil["valor_hora"] + config_dia.get("valor_extra_hora", 0.0),
                        "subs_refeicao": perfil["subs_refeicao"]
                    })

            st.success(f"Escala gerada com sucesso para {calendar.month_name[mes_sel]}!")
            st.rerun()

    with aba2:
        st.markdown("### 📋 Resumo dos Turnos e Salário")

        if perfil["turnos"]:
            total_horas = sum(t["horas"] for t in perfil["turnos"])
            
            # Cálculo de vencimento base/turnos com os extras aplicados por turno
            total_bruto_vencimento = sum(t["horas"] * t.get("valor_hora_efetivo", perfil["valor_hora"]) for t in perfil["turnos"])
            
            # Subsídio de refeição total
            total_dias_trabalho = len(perfil["turnos"])
            total_subs_refeicao = total_dias_trabalho * perfil["subs_refeicao"]
            
            total_bruto_global = total_bruto_vencimento + total_subs_refeicao

            taxa_ss = perfil["desc_ss"] / 100.0
            taxa_irs = perfil["desc_irs"] / 100.0

            valor_ss = total_bruto_vencimento * taxa_ss
            valor_irs = total_bruto_vencimento * taxa_irs
            total_liquido = total_bruto_vencimento - (valor_ss + valor_irs) + total_subs_refeicao

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total Horas", f"{total_horas:.1f} h")
            col_m2.metric("Bruto Global", f"{total_bruto_global:.2f} €")
            col_m3.metric("Líquido Estimado", f"{total_liquido:.2f} €")

            st.markdown("---")
            st.markdown(f"**Breakdown Financeiro:**")
            st.write(f"• Vencimento Base/Turnos: **{total_bruto_vencimento:.2f} €**")
            st.write(f"• Subsídio de Refeição ({total_dias_trabalho} dias): **+{total_subs_refeicao:.2f} €**")
            st.write(f"• Segurança Social ({(perfil['desc_ss']):.2f}%): -{valor_ss:.2f} €")
            st.write(f"• IRS ({(perfil['desc_irs']):.2f}%): -{valor_irs:.2f} €")

            st.markdown("---")
            st.markdown("#### Lista Detalhada de Turnos:")
            st.dataframe(perfil["turnos"], use_container_width=True)

            if st.button("🗑️ Limpar Todos os Registos"):
                perfil["turnos"] = []
                st.rerun()
        else:
            st.info("Ainda não tens turnos gerados. Configura o teu padrão na barra lateral, vai à aba 'Geração Automática de Escala' e clica no botão!")
