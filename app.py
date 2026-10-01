import streamlit as st
import pandas as pd
from datetime import datetime
import io
import google.generativeai as genai

# Configuração da Página
st.set_page_config(page_title="Portal de Verbas", page_icon="🟢", layout="wide")

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'dados_lancamentos' not in st.session_state:
    st.session_state.dados_lancamentos = pd.DataFrame(
        columns=["Empresa", "Chapa", "Verba", "Horas", "Valor (R$)", "Recorrência", "Data Limite", "Solicitante", "Data Solicitação"]
    )
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = ""

dic_verbas = {
    "Hora Extra 50%": {
        "id": "HE.01", 
        "desc": "Adiciona o valor de vencimento à folha referente a 50% de hora extra.",
        "tags": ["extra", "50%", "semana", "dia útil", "ficou até mais tarde", "atraso"]
    },
    "Hora Extra 100%": {
        "id": "HE.02", 
        "desc": "Adiciona o valor de vencimento à folha referente a 100% de hora extra (Domingos e Feriados).",
        "tags": ["extra", "100%", "domingo", "feriado", "dobrado", "final de semana", "plantão"]
    },
    "Adicional Noturno": {
        "id": "AN.01", 
        "desc": "Pagamento de adicional para horas trabalhadas no período noturno (das 22h às 05h).",
        "tags": ["noturno", "noite", "madrugada", "22h", "turno", "dormiu"]
    },
    "Auxílio Creche": {
        "id": "BE.01", 
        "desc": "Pagamento de benefício para auxílio com dependentes (Apenas Valor).",
        "tags": ["creche", "filho", "dependente", "escola", "babá", "criança", "reembolso"]
    }
}

# --- TELA DE LOGIN ---
if st.session_state.email_logado == "":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.image("Branco+verde.png", use_container_width=True) 
        st.markdown("<h2 style='text-align: center;'>Portal de Lançamento de Verbas</h2>", unsafe_allow_html=True)
        st.write("---")
        
        email_input = st.text_input("E-mail Corporativo", placeholder="seu.nome@empresa.com")
        if st.button("Acessar Sistema", use_container_width=True, type="primary"):
            if "@" in email_input:
                st.session_state.email_logado = email_input
                st.rerun()
            else:
                st.error("Por favor, insira um e-mail válido.")

# --- SISTEMA PRINCIPAL ---
else:
    with st.sidebar:
        st.image("Branco+verde.png", use_container_width=True)
        st.write("---")
        st.markdown(f"**👤 Usuário:**<br>{st.session_state.email_logado}", unsafe_allow_html=True)
        st.write("---")
        menu = st.radio("Navegação:", ["📝 Fazer Lançamento", "📊 Painel da Folha", "📖 Consulta de Verbas"])
        
        st.write("---")
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state.email_logado = ""
            st.rerun()

    # --- ABA 1: FAZER LANÇAMENTO ---
    if menu == "📝 Fazer Lançamento":
        st.header("Novo Lançamento de Verba")
        st.caption("Preencha os dados da rubrica. Um relatório de auditoria será enviado ao seu e-mail após a validação.")
        
        with st.container(border=True): 
            empresas_teste = ["Solutions", "Response"]
            
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.selectbox("Empresa", empresas_teste)
                chapa = st.text_input("Chapa / Matrícula")
                
                opcoes_verba = [f"{k} ({v['id']})" for k, v in dic_verbas.items()]
                tipo_verba_selecionada = st.selectbox("Tipo de Verba", opcoes_verba)
                
            with col2:
                recorrencia = st.selectbox("Recorrência", ["Apenas este mês", "Temporário (Informar data limite)", "Vitalício"])
                data_limite = None
                if recorrencia == "Temporário (Informar data limite)":
                    data_limite = st.date_input("Manter pagamento até:")
                    
                st.write("Volume / Quantidade:")
                col_h, col_v = st.columns(2)
                with col_h:
                    horas = st.number_input("Horas (Opcional)", min_value=0.0, step=0.5)
                with col_v:
                    valor = st.number_input("Valor R$ (Opcional)", min_value=0.0, step=10.0)

            st.write("---")
            if st.button("Submeter para Validação", type="primary"):
                if chapa.strip() == "":
                    st.error("⚠️ A Chapa é obrigatória.")
                elif horas == 0 and valor == 0:
                    st.error("⚠️ Preencha a quantidade de Horas OU o Valor financeiro.")
                else:
                    nome_verba_pura = tipo_verba_selecionada.split(" (")[0]
                    id_verba = dic_verbas[nome_verba_pura]["id"]
                    
                    novo_dado = pd.DataFrame([{
                        "Empresa": empresa, "Chapa": chapa, "Verba": id_verba, 
                        "Horas": horas, "Valor (R$)": valor, "Recorrência": recorrencia,
                        "Data Limite": data_limite.strftime("%d/%m/%Y") if data_limite else "-",
                        "Solicitante": st.session_state.email_logado,
                        "Data Solicitação": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    st.session_state.dados_lancamentos = pd.concat([st.session_state.dados_lancamentos, novo_dado], ignore_index=True)
                    
                    st.success(f"✅ Lançamento da rubrica {id_verba} submetido para a chapa {chapa}!")

    # --- ABA 2: PAINEL DA FOLHA ---
    elif menu == "📊 Painel da Folha":
        st.header("Painel de Controle - Folha de Pagamento")
        
        with st.container(border=True):
            senha = st.text_input("Palavra-passe de segurança:", type="password", help="Acesso restrito.")
            
            if senha == "diretoria2026":
                st.success("Acesso Autenticado")
                df = st.session_state.dados_lancamentos
                
                if df.empty:
                    st.info("Nenhum lançamento aguardando processamento.")
                else:
                    st.write("---")
                    empresas_lancadas = list(df['Empresa'].unique())
                    abas = st.tabs(empresas_lancadas + ["Consolidado Total"])
                    
                    for i, emp in enumerate(empresas_lancadas):
                        with abas[i]:
                            st.dataframe(df[df['Empresa'] == emp], use_container_width=True, hide_index=True)
                            
                    with abas[-1]:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Base')
                        
                        st.download_button(
                            label="📥 Exportar Matriz (Excel)", data=buffer.getvalue(), 
                            file_name="matriz_lancamentos.xlsx", type="primary"
                        )
            elif senha != "":
                st.error("Credenciais incorretas.")

    # --- ABA 3: CONSULTA E ASSISTENTE IA ---
    elif menu == "📖 Consulta de Verbas":
        st.header("Biblioteca & Assistente de Rubricas")
        st.caption("Consulte o código exato ou descreva a situação para a IA sugerir a verba correta.")
        
        aba_pesquisa, aba_assistente = st.tabs(["🔍 Pesquisa por Nome/Código", "✨ Assistente IA (Descrever Situação)"])
        
        with aba_pesquisa:
            st.write("Busque diretamente pelo nome ou ID da verba:")
            termo_busca = st.text_input("Buscar:", placeholder="Ex: HE.01 ou Adicional Noturno", label_visibility="collapsed")
            
            for nome, dados in dic_verbas.items():
                if termo_busca.lower() in nome.lower() or termo_busca.lower() in dados["id"].lower():
                    with st.expander(f"**{dados['id']}** - {nome}", expanded=(termo_busca != "")):
                        st.write(f"**Descrição da regra:** {dados['desc']}")

        with aba_assistente:
            st.write("Não sabe qual verba usar? Descreva a situação com as suas palavras e a Inteligência Artificial fará a análise.")
            duvida = st.text_area("O que você precisa lançar?", placeholder="Ex: O funcionário cobriu um plantão no domingo e ficou até de madrugada.")
            
            if st.button("Analisar com IA", type="primary"):
                if duvida:
                    with st.spinner("Analisando cenário com a IA..."):
                        try:
                            # Conecta na API usando a chave secreta guardada no Streamlit
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            
                            # Usamos o modelo 'flash' pois é extremamente rápido para textos
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            prompt = f"""
                            Você é um assistente especialista em folha de pagamento da empresa. 
                            Aqui estão as únicas verbas disponíveis e suas regras: {dic_verbas}.
                            
                            Um analista/gestor relatou a seguinte situação: "{duvida}"
                            
                            Responda de forma curta, direta e amigável sugerindo a verba correta (Informe o ID e o Nome). 
                            Justifique rapidamente sua escolha baseada na regra da verba. Se a dúvida não tiver relação com as verbas informadas, peça para o usuário ser mais específico.
                            """
                            
                            resposta = model.generate_content(prompt)
                            
                            st.success("Análise concluída:")
                            st.write(resposta.text)
                            
                        except Exception as e:
                            st.error(f"Erro de comunicação com a IA. Verifique se a API Key foi configurada corretamente nos Secrets do Streamlit.")
