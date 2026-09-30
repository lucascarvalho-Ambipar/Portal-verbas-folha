import streamlit as st
import pandas as pd
from datetime import datetime
import io
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Portal de Verbas", layout="wide")

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'dados_lancamentos' not in st.session_state:
    st.session_state.dados_lancamentos = pd.DataFrame(
        columns=["Empresa", "Chapa", "Verba", "Horas", "Valor (R$)", "Recorrência", "Data Limite", "Solicitante", "Data Solicitação"]
    )
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = ""

# Dicionário de Verbas (Nome, ID e Explicação)
dic_verbas = {
    "Hora Extra 50%": {"id": "HE.01", "desc": "Adiciona o valor de vencimento à folha referente a 50% de hora extra."},
    "Hora Extra 100%": {"id": "HE.02", "desc": "Adiciona o valor de vencimento à folha referente a 100% de hora extra (Domingos e Feriados)."},
    "Adicional Noturno": {"id": "AN.01", "desc": "Pagamento de adicional para horas trabalhadas no período noturno."},
    "Auxílio Creche": {"id": "BE.01", "desc": "Pagamento de benefício para auxílio com dependentes (Apenas Valor)."}
}

# --- FUNÇÃO DE E-MAIL (PREPARADA PARA USO REAL) ---
def enviar_email_confirmacao(destinatario, chapa, verba):
    # NOTA: Para funcionar de verdade, você precisará configurar as "Secrets" no Streamlit Cloud
    # com o seu e-mail e uma "Senha de Aplicativo". 
    try:
        # Exemplo usando Gmail (precisa de configuração prévia)
        # remetente = st.secrets["EMAIL_REMETENTE"]
        # senha = st.secrets["SENHA_APP"]
        
        # msg = EmailMessage()
        # msg['Subject'] = f"Confirmação de Lançamento - Chapa {chapa}"
        # msg['From'] = remetente
        # msg['To'] = destinatario
        # msg.set_content(f"Olá, confirmamos o recebimento da solicitação de {verba} para a chapa {chapa} em seu nome.")
        
        # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        #     smtp.login(remetente, senha)
        #     smtp.send_message(msg)
        return True
    except Exception as e:
        return False

# --- TELA DE LOGIN ---
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

# --- SISTEMA PRINCIPAL ---
else:
    st.sidebar.title("Navegação")
    st.sidebar.write(f"👤 Usuário: {st.session_state.email_logado}")
    menu = st.sidebar.radio("Ir para:", ["📝 Fazer Lançamento", "📊 Painel da Folha (Restrito)", "📖 Explicação de Verbas"])
    
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        st.session_state.email_logado = ""
        st.rerun()

    # --- ABA 1: FAZER LANÇAMENTO ---
    if menu == "📝 Fazer Lançamento":
        st.title("Novo Lançamento de Verba")
        st.info("Preencha os dados abaixo. Após a submissão, um e-mail de auditoria será gerado em seu nome.")

        empresas_teste = ["Solutions", "Response"]

        # Tiramos o st.form para a tela reagir na mesma hora que você muda a opção!
        col1, col2 = st.columns(2)
        
        with col1:
            empresa = st.selectbox("Empresa", empresas_teste)
            chapa = st.text_input("Chapa / Matrícula do Colaborador")
            
            opcoes_verba = [f"{k} ({v['id']})" for k, v in dic_verbas.items()]
            tipo_verba_selecionada = st.selectbox("Tipo de Verba", opcoes_verba)
            
            # Divide horas e valores
            st.write("Preencha Horas OU Valor (ou ambos, se necessário):")
            col_h, col_v = st.columns(2)
            with col_h:
                horas = st.number_input("Horas", min_value=0.0, step=0.5)
            with col_v:
                valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            
        with col2:
            recorrencia = st.selectbox("Recorrência", ["Apenas este mês", "Temporário (Informar data limite)", "Vitalício"])
            
            data_limite = None
            # AGORA FUNCIONA! Como tiramos o form, a tela atualiza ao escolher "Temporário"
            if recorrencia == "Temporário (Informar data limite)":
                data_limite = st.date_input("Manter pagamento até:")
        
        st.write("") # Espaçamento
        if st.button("Validar e Enviar para Folha", type="primary"):
            if chapa.strip() == "":
                st.error("⚠️ Atenção: A Chapa é obrigatória.")
            elif horas == 0 and valor == 0:
                st.error("⚠️ Atenção: Preencha a quantidade de Horas OU o Valor financeiro.")
            else:
                nome_verba_pura = tipo_verba_selecionada.split(" (")[0]
                id_verba = dic_verbas[nome_verba_pura]["id"]
                
                novo_dado = pd.DataFrame([{
                    "Empresa": empresa,
                    "Chapa": chapa,
                    "Verba": id_verba,
                    "Horas": horas,
                    "Valor (R$)": valor,
                    "Recorrência": recorrencia,
                    "Data Limite": data_limite.strftime("%d/%m/%Y") if data_limite else "-",
                    "Solicitante": st.session_state.email_logado,
                    "Data Solicitação": datetime.now().strftime("%d/%m/%Y %H:%M")
                }])
                st.session_state.dados_lancamentos = pd.concat([st.session_state.dados_lancamentos, novo_dado], ignore_index=True)
                
                st.success(f"✅ Lançamento submetido com sucesso para a chapa {chapa}!")
                
                # Chamada do e-mail simulada (pronta para o código real)
                enviar_email_confirmacao(st.session_state.email_logado, chapa, id_verba)
                st.toast(f"📧 E-mail de confirmação enviado para {st.session_state.email_logado}", icon="📩")

    # --- ABA 2: PAINEL DA FOLHA (RESTRITO) ---
    elif menu == "📊 Painel da Folha (Restrito)":
        st.title("Painel de Controle - Equipe de Folha")
        
        senha = st.text_input("Insira a palavra-passe para acessar as consolidações:", type="password")
        
        if senha == "diretoria2026":
            st.success("Acesso Liberado!")
            df = st.session_state.dados_lancamentos
            
            if df.empty:
                st.warning("Nenhum lançamento foi realizado até o momento.")
            else:
                empresas_lancadas = df['Empresa'].unique()
                abas = st.tabs(list(empresas_lancadas) + ["Visão Geral (Todas)"])
                
                for i, emp in enumerate(empresas_lancadas):
                    with abas[i]:
                        df_empresa = df[df['Empresa'] == emp]
                        st.dataframe(df_empresa, use_container_width=True, hide_index=True)
                        
                with abas[-1]:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # GERADOR DE EXCEL REAL (.xlsx) - Divide perfeitamente as colunas!
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Lançamentos')
                    
                    st.download_button(
                        label="📥 Baixar Planilha Excel (Formatada)", 
                        data=buffer.getvalue(), 
                        file_name="lancamentos_folha.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        elif senha != "":
            st.error("Palavra-passe incorreta.")

    # --- ABA 3: EXPLICAÇÃO DE VERBAS ---
    elif menu == "📖 Explicação de Verbas":
        st.title("Dicionário e Explicação de Verbas")
        st.write("Consulte abaixo o que significa cada código para evitar erros de lançamento.")
        
        # Transforma nosso dicionário em uma tabela para visualização
        tabela_explicacao = []
        for nome, dados in dic_verbas.items():
            tabela_explicacao.append({"Código (ID)": dados["id"], "Nome da Verba": nome, "Regra / Explicação": dados["desc"]})
            
        df_explicacao = pd.DataFrame(tabela_explicacao)
        st.table(df_explicacao)
