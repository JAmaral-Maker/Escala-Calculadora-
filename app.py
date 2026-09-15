import datetime
import calendar
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestor de Escalas SPDE", page_icon="🛡️", layout="centered"
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

# Inicializar Base de Dados de Perfis na Sessão
if "perfis" not in st.session_state:
    st.session_state.perfis = {
        "João Amaral": {
            "pin": "1994",
            "valor_hora": 5.87,
            "desc_ss": 11.0,
            "desc_irs": 4.23,
            "turnos": [],
        }
    }

if "utilizador_atual" not in st.session_state:
    st.session_state.utilizador_atual = None

# Cabeçalho Principal
st.title("🛡️ Gestor de Escala & Salário - SPDE")

# Sistema de Autenticação / Seleção de Perfil
if st.session_state.utilizador_atual is None:
    st.markdown("### 🔐 Acesso Seguro à Conta")
    st.markdown(
        "Para proteger os teus dados e manter a privacidade, identifica-te ou cria uma nova conta."
    )

    modo = st.radio(
        "Escolhe uma opção:", ["Entrar na minha conta", "Criar novo perfil"]
    )

    lista_nomes = list(st.session_state.perfis.keys())

    if modo == "Entrar na minha conta":
        if lista_nomes:
            nome_escolhido = st.selectbox("Seleciona o teu nome:", lista_nomes)
            pin_inserido = st.text_input(
                "Insere o teu PIN de acesso:", type="password"
            )

            if st.button("🔓 Entrar", type="primary"):
                if (
                    pin_inserido
                    == st.session_state.perfis[nome_escolhido]["pin"]
                ):
                    st.session_state.utilizador_atual = nome_escolhido
                    st.success(f"Bem-vindo de volta, {nome_escolhido}!")
                    st.rerun()
                else:
                    st.error("PIN incorreto. Tenta novamente.")
        else:
            st.info("Ainda não existem perfis criados. Cria um novo perfil.")

    else:
        novo_nome = st.text_input("O teu Nome:")
        novo_pin = st.text_input(
            "Cria um PIN secreto (ex: 4 dígitos):", type="password"
        )
        novo_pin_conf = st.text_input(
            "Confirma o PIN secreto:", type="password"
        )

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
                    "valor_hora": 5.87,
                    "desc_ss": 11.0,
                    "desc_irs": 4.23,
                    "turnos": [],
                }
                st.session_state.utilizador_atual = novo_nome
                st.success(
                    f"Perfil de {novo_nome} criado e protegido com sucesso!"
                )
                st.rerun()

else:
    # Utilizador Autenticado - Área Principal
    perfil = st.session_state.perfis[st.session_state.utilizador_atual]

    # Barra Lateral - Configurações Salariais do Utilizador Atual
    st.sidebar.markdown(f"## 👤 Sessão: {st.session_state.utilizador_atual}")
    if st.sidebar.button("🚪 Terminar Sessão"):
        st.session_state.utilizador_atual = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚙️ Configurações Salariais")
    perfil["valor_hora"] = st.sidebar.number_input(
        "Valor base por hora (€):",
        min_value=0.0,
        value=perfil["valor_hora"],
        step=0.01,
    )
    perfil["desc_ss"] = (
        st.sidebar.slider(
            "Desconto Segurança Social (%):",
            min_value=0.0,
            max_value=20.0,
            value=perfil["desc_ss"],
        )
        / 100
    )
    perfil["desc_irs"] = (
        st.sidebar.slider(
            "Desconto IRS (%):",
            min_value=0.0,
            max_value=30.0,
            value=perfil["desc_irs"],
        )
        / 100
    )

    st.markdown(
        f"Olá, **{st.session_state.utilizador_atual}**! Gere a tua escala mensal e calcula os teus ganhos com total privacidade."
    )

    # Abas da Aplicação
    aba1, aba2 = st.tabs(
        ["📅 Geração Automática de Escala", "📊 Resumo & Contabilidade"]
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
                "Mês:",
                list(range(1, 13)),
                index=8,
                format_func=lambda x: calendar.month_name[x],
            )

        if st.button("🚀 Gerar Escala para este Mês", type="primary"):
            perfil["turnos"] = []
            num_dias = calendar.monthrange(ano_sel, mes_sel)[1]

            for dia in range(1, num_dias + 1):
                data_atual = datetime.date(ano_sel, mes_sel, dia)
                dia_semana = data_atual.weekday()  # 0=Seg, 1=Ter, ..., 6=Dom

                # Segunda (0), Terça (1), Quinta (3) -> Noturno (8h)
                if dia_semana in [0, 1, 3]:
                    perfil["turnos"].append(
                        {
                            "data": data_atual.strftime("%Y-%m-%d"),
                            "tipo": "Noturno (8h)",
                            "horas": 8.0,
                            "valor_hora": perfil["valor_hora"],
                        }
                    )
                # Sábado (5), Domingo (6) -> Fim de Semana (12h)
                elif dia_semana in [5, 6]:
                    perfil["turnos"].append(
                        {
                            "data": data_atual.strftime("%Y-%m-%d"),
                            "tipo": "Fim de Semana (12h)",
                            "horas": 12.0,
                            "valor_hora": perfil["valor_hora"],
                        }
                    )

            st.success(
                f"Escala gerada com sucesso para {calendar.month_name[mes_sel]}!"
            )
            st.rerun()

    with aba2:
        st.markdown("### 📋 Resumo dos Turnos e Salário")

        if perfil["turnos"]:
            # Calcular totais
            total_horas = sum(t["horas"] for t in perfil["turnos"])
            total_bruto = sum(
                t["horas"] * perfil["valor_hora"] for t in perfil["turnos"]
            )

            valor_ss = total_bruto * perfil["desc_ss"]
            valor_irs = total_bruto * perfil["desc_irs"]
            total_liquido = total_bruto - (valor_ss + valor_irs)

            # Métricas visuais
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total de Horas", f"{total_horas:.1f} h")
            col_m2.metric("Total Bruto", f"{total_bruto:.2f} €")
            col_m3.metric("Total Líquido", f"{total_liquido:.2f} €")

            st.markdown("---")
            st.markdown(f"**Detalhes dos Descontos:**")
            st.write(
                f"• Segurança Social ({(perfil['desc_ss']*100):.1f}%): -{valor_ss:.2f} €"
            )
            st.write(
                f"• IRS ({(perfil['desc_irs']*100):.1f}%): -{valor_irs:.2f} €"
            )

            st.markdown("---")
            st.markdown("#### Lista de Turnos do Mês:")
            st.dataframe(perfil["turnos"], use_container_width=True)

            if st.button("🗑️ Limpar Todos os Registos"):
                perfil["turnos"] = []
                st.rerun()
        else:
            st.info(
                "Ainda não tens turnos gerados. Vai à aba 'Geração Automática de Escala' e clica no botão para criar o mês!"
            )
