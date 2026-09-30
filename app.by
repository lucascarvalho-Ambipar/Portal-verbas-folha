import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração da página e Banco de Dados temporário (Memória da Sessão)
st.set_page_config(page_title="Portal de Verbas", layout="wide")

if 'dados_lancamentos' not in st.session_state:
    # Cria uma tabela vazia para armazenar os dados durante a demonstração
    st.session_state.dados_lancamentos = pd.DataFrame(
        columns=["Empresa", "Chapa", "Verba", "Horas", "Recorrência", "Data Limite", "Solicitante", "Data Solicitação"]
    )
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = ""

# 2. Tela de Autenticação Inicial
if st.session_state.email_logado == "":
    st.title("🔐 Portal de Lançamento de Verbas")
    st.write("Bem-vindo(a). Por favor, informe seu e-mail corporativo para iniciar.")
    
    email_input = st.text_input("E-mail Corporativo")
    if st.button("Acessar Sistema"):
        if "@" in email_input:
            st.session_state.email_logado = email_input
            st.rerun()
        else:
            st.error("Por favor, insira um e-mail válido.")

# 3. O Sistema (Após Login)
else:
    # Menu Lateral
    st.sidebar.title("Navegação")
    st.sidebar.write(f"👤 Usuário: {st.session_state.email_logado}")
    menu = st.sidebar.radio("Ir para:", ["📝 Fazer Lançamento", "📊 Painel da Folha (Restrito)"])
    
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        st.session_state.email_logado = ""
        st.rerun()

    # --- ABA 1: TELA DAS PONTAS (LANÇAMENTO) ---
    if menu == "📝 Fazer Lançamento":
        st.title("Novo Lançamento de Verba")
        st.info("Preencha os dados abaixo. Após a submissão, um e-mail de auditoria será gerado em seu nome.")

        mapa_verbas = {"Hora Extra 50% (HE.01)": "HE.01", "Hora Extra 100% (HE.02)": "HE.02"}
        empresas_teste = ["Solutions", "Response"] # Depois substituímos pelo seu banco de dados completo

        with st.form("form_lancamento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                empresa = st.selectbox("Empresa", empresas_teste)
                chapa = st.text_input("Chapa / Matrícula do Colaborador")
                tipo_verba = st.selectbox("Tipo de Verba", list(mapa_verbas.keys()))
                horas = st.number_input("Quantidade da Verba (em Horas)", min_value=0.0, step=0.5)
                
            with col2:
                recorrencia = st.selectbox("Recorrência", ["Apenas este mês", "Temporário (Informar data limite)", "Vitalício"])
                data_limite = None
                if recorrencia == "Temporário (Informar data limite)":
                    data_limite = st.date_input("Manter pagamento até:")
            
            submit = st.form_submit_button("Validar e Enviar para Folha", type="primary")

            if submit:
                if chapa.strip() == "" or horas <= 0:
                    st.error("⚠️ Atenção: A Chapa e as Horas devem ser preenchidas corretamente.")
                else:
                    # Salva os dados na nossa tabela virtual
                    novo_dado = pd.DataFrame([{
                        "Empresa": empresa,
                        "Chapa": chapa,
                        "Verba": mapa_verbas[tipo_verba],
                        "Horas": horas,
                        "Recorrência": recorrencia,
                        "Data Limite": data_limite.strftime("%d/%m/%Y") if data_limite else "-",
                        "Solicitante": st.session_state.email_logado,
                        "Data Solicitação": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    st.session_state.dados_lancamentos = pd.concat([st.session_state.dados_lancamentos, novo_dado], ignore_index=True)
                    
                    st.success(f"✅ Lançamento submetido com sucesso para a chapa {chapa}!")
                    # Simulação do e-mail
                    st.toast(f"📧 E-mail de confirmação enviado para {st.session_state.email_logado}", icon="📩")

    # --- ABA 2: TELA DA FOLHA (DIRETORIA/ADMIN) ---
    elif menu == "📊 Painel da Folha (Restrito)":
        st.title("Painel de Controle - Equipe de Folha")
        
        # Proteção por Palavra-Passe
        senha = st.text_input("Insira a palavra-passe para acessar as consolidações:", type="password")
        
        if senha == "diretoria2026":
            st.success("Acesso Liberado!")
            st.divider()
            
            df = st.session_state.dados_lancamentos
            
            if df.empty:
                st.warning("Nenhum lançamento foi realizado até o momento.")
            else:
                # Cria abas para organizar por empresa
                empresas_lancadas = df['Empresa'].unique()
                abas = st.tabs(list(empresas_lancadas) + ["Visão Geral (Todas)"])
                
                # Preenche as abas individuais
                for i, emp in enumerate(empresas_lancadas):
                    with abas[i]:
                        df_empresa = df[df['Empresa'] == emp]
                        st.write(f"### Lançamentos - {emp}")
                        st.dataframe(df_empresa, use_container_width=True, hide_index=True)
                        
                # Preenche a aba "Visão Geral"
                with abas[-1]:
                    st.write("### Base de Dados Completa")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Botão para exportar para Excel/CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Exportar Base Completa (CSV)", data=csv, file_name="lancamentos_folha.csv", mime="text/csv")
        elif senha != "":
            st.error("Palavra-passe incorreta.")
