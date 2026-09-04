import random
import textwrap
import re
import streamlit as st

from crewai import Task, Crew

from agents.triagem import agente_triagem
from agents.cambio import agente_cambio
from agents.entrevista import agente_entrevista
from agents.credito import agente_credito

from static.MsgProntas import saudacoes_iniciais, mensagens_erro_api
from config.ui_setup import renderizar_hero
from dotenv import load_dotenv


load_dotenv()
renderizar_hero()


# ============================================================
# ESTADO DA SESSÃO
# ============================================================

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": random.choice(saudacoes_iniciais)
        }
    ]

if "tentativas_autenticacao" not in st.session_state:
    st.session_state.tentativas_autenticacao = 0

if "agente_ativo" not in st.session_state:
    st.session_state.agente_ativo = agente_triagem

if "cliente_autenticado" not in st.session_state:
    st.session_state.cliente_autenticado = False

if "erro_api" not in st.session_state:
    st.session_state.erro_api = False

if "msg_erro_temporaria" not in st.session_state:
    st.session_state.msg_erro_temporaria = ""

if "ultimo_prompt" not in st.session_state:
    st.session_state.ultimo_prompt = ""

if "resposta_pendente" not in st.session_state:
    st.session_state.resposta_pendente = None

if "sessao_encerrada" not in st.session_state:
    st.session_state.sessao_encerrada = False

# ============================================================
# FUNÇÃO PRINCIPAL DO AGENTE
# ============================================================

def processar_mensagem(prompt_atual):

    agente = st.session_state.agente_ativo
    historico_texto = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in st.session_state.mensagens
    )
    instrucao_extra = ""
    saida_esperada = (
        "Uma resposta natural ajudando o cliente "
        "e executando as ferramentas necessárias."
    )

    # --------------------------------------------------------
    # TRIAGEM
    # --------------------------------------------------------

    if agente == agente_triagem:
        if st.session_state.cliente_autenticado:
            instrucao_extra = textwrap.dedent("""
                AVISO DO SISTEMA:
                O cliente JÁ FOI AUTENTICADO.
                NÃO solicite CPF.
                NÃO solicite data de nascimento.
                Leia a intenção no histórico e faça o roteamento imediatamente.
                """)

            saida_esperada = textwrap.dedent("""
                Retorne UNICAMENTE uma das tags:
                [ROTA_CREDITO]
                [ROTA_CAMBIO]
                [ROTA_ENTREVISTA]
                Não adicione nenhuma outra palavra.
                """)
        else:
            instrucao_extra = textwrap.dedent(f"""
                AVISO DO SISTEMA:
                O cliente AINDA NÃO FOI AUTENTICADO.

                Se ainda não forneceu CPF e data de nascimento:
                solicite os dois dados.

                Se acabou de fornecer os dados:
                valide utilizando a ferramenta apropriada.

                Se a autenticação for bem-sucedida:
                informe brevemente o sucesso e inclua a tag de roteamento
                correspondente à intenção original.
                """)

            saida_esperada = textwrap.dedent("""
                Uma resposta solicitando os dados OU, se a autenticação
                for bem-sucedida, uma mensagem de sucesso seguida
                obrigatoriamente pela tag de roteamento.
                """)

    # --------------------------------------------------------
    # PRIMEIRA EXECUÇÃO
    # --------------------------------------------------------
    tarefa = Task(
        description=textwrap.dedent(f"""
            Histórico da conversa: {historico_texto}; 
            Mensagem atual: {prompt_atual}
            {instrucao_extra}
            """),
        expected_output=saida_esperada,
        agent=agente
    )
    crew = Crew(
        agents=[agente],
        tasks=[tarefa],
        verbose=True
    )
    resposta = str(crew.kickoff())

    if "[FALHA_AUTENTICACAO]" in resposta:
        st.session_state.tentativas_autenticacao += 1
        resposta = resposta.replace("[FALHA_AUTENTICACAO]", "").strip()

    # --------------------------------------------------------
    # PROCESSAMENTO DAS ROTAS
    # --------------------------------------------------------

    max_saltos = 3
    saltos = 0

    while saltos < max_saltos:
        nova_rota = False

        if "[ROTA_CREDITO]" in resposta:
            st.session_state.agente_ativo = agente_credito
            st.session_state.cliente_autenticado = True
            resposta = resposta.replace(
                "[ROTA_CREDITO]", ""
            ).strip()
            nova_rota = True

        elif "[ROTA_CAMBIO]" in resposta:
            st.session_state.agente_ativo = agente_cambio
            st.session_state.cliente_autenticado = True
            resposta = resposta.replace(
                "[ROTA_CAMBIO]", ""
            ).strip()
            nova_rota = True

        elif "[ROTA_ENTREVISTA]" in resposta:
            st.session_state.agente_ativo = agente_entrevista
            st.session_state.cliente_autenticado = True
            resposta = resposta.replace(
                "[ROTA_ENTREVISTA]", ""
            ).strip()
            nova_rota = True

        elif "[ROTA_TRIAGEM]" in resposta:
            st.session_state.agente_ativo = agente_triagem
            resposta = resposta.replace(
                "[ROTA_TRIAGEM]", ""
            ).strip()
            nova_rota = True

        elif "[ENCERRAR_SESSAO]" in resposta:
            resposta = resposta.replace(
                "[ENCERRAR_SESSAO]", ""
            ).strip()
            return {
                "resposta": resposta,
                "encerrar": True
            }

        # ----------------------------------------------------
        # NÃO HOUVE ROTA
        # ----------------------------------------------------
        if not nova_rota:
            break

        saltos += 1
        if resposta:
            st.session_state.mensagens.append(
                {
                    "role": "assistant",
                    "content": resposta
                }
            )

        # ----------------------------------------------------
        # EXECUTA ESPECIALISTA
        # ----------------------------------------------------
        historico_atualizado = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in st.session_state.mensagens
        )
        tarefa_especialista = Task(
            description=textwrap.dedent(f"""
                Histórico da conversa:
                {historico_atualizado}
                O cliente já foi autenticado.
                Você é o especialista definitivo para este assunto.
                Não diga que irá transferir o cliente.
                Não explique o roteamento.
                Assuma o atendimento diretamente.
                Execute as ferramentas necessárias.
                """),
            expected_output=(
                "Uma resposta direta executando a ação solicitada."
            ),
            agent=st.session_state.agente_ativo
        )
        crew_especialista = Crew(
            agents=[st.session_state.agente_ativo],
            tasks=[tarefa_especialista],
            verbose=True
        )
        resposta = str(
            crew_especialista.kickoff()
        )

    # ----------------------------------------------------
    # PROTEÇÃO CONTRA VAZAMENTO DE TAGS DE ROTEAMENTO
    # ----------------------------------------------------
    resposta = re.sub(r'\[ROTA_[A-Z_]+\]', '', resposta).strip()

    return {
        "resposta": resposta,
        "encerrar": False
    }


# ============================================================
# HISTÓRICO
# ============================================================
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"].replace("$", r"\$"))

# ============================================================
# FUNÇÃO DE EXECUÇÃO COM TRATAMENTO DE ERRO
# ============================================================
def executar_com_retry(prompt):
    st.session_state.ultimo_prompt = prompt
    st.session_state.erro_api = False

    try:
        resultado = processar_mensagem(prompt)
        resposta = resultado["resposta"]
        if resposta:
            st.session_state.mensagens.append(
                {
                    "role": "assistant",
                    "content": resposta
                }
            )

        st.session_state.resposta_pendente = None
        return resultado

    except Exception as e:
        print("\n========== ERRO ==========")
        print(repr(e))
        print("==========================\n")

        st.session_state.erro_api = True
        st.session_state.msg_erro_temporaria = random.choice(mensagens_erro_api)

        return {
            "resposta": None,
            "encerrar": False
        }

# ============================================================
# INPUT
# ============================================================
bloqueio_seguranca = st.session_state.get("tentativas_autenticacao", 0) >= 3
trava_geral = bloqueio_seguranca or st.session_state.get("sessao_encerrada", False)

prompt = st.chat_input("Digite sua mensagem:", disabled=trava_geral)
if bloqueio_seguranca:
    st.error("Limite de tentativas de autenticação excedido. Seu acesso foi temporariamente bloqueado.")
elif st.session_state.get("sessao_encerrada", False):
    st.info("Atendimento encerrado. Conte sempre conosco! (Atualize a página (F5) para iniciar uma nova sessão)")

if prompt:
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Define que há uma requisição nova pronta para rodar
    st.session_state.resposta_pendente = prompt

# ============================================================
# MOTOR UNIFICADO DE EXECUÇÃO (Nova Mensagem e Retry)
# ============================================================
if st.session_state.resposta_pendente:

    prompt_processar = st.session_state.resposta_pendente
    st.session_state.resposta_pendente = None # Consome o gatilho
    
    # Contêiner vazio EXCLUSIVO para o loading.
    loading_container = st.empty()
    
    with loading_container.container():
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                resultado = executar_com_retry(prompt_processar)

    loading_container.empty()

    # Se a ferramenta rodou com sucesso, desenhamos a bolha definitiva
    if not st.session_state.erro_api and resultado and resultado.get("resposta"):
        if resultado.get("encerrar"):
            st.session_state.sessao_encerrada = True
        st.rerun()

# ============================================================
# RETRY E TRATAMENTO DE ERRO (Sempre a última coisa a rodar)
# ============================================================
if st.session_state.erro_api and not st.session_state.resposta_pendente:

    with st.chat_message("assistant"):
        st.markdown(st.session_state.msg_erro_temporaria)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 Tentar novamente", key="retry_btn", use_container_width=True):

                # Prepara os estados para a nova tentativa
                st.session_state.erro_api = False
                st.session_state.msg_erro_temporaria = ""
                st.session_state.resposta_pendente = st.session_state.ultimo_prompt
                
                # Recarrega a página para iniciar o fluxo limpo
                st.rerun()