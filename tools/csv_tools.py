import pandas as pd
from datetime import datetime
from crewai.tools import tool
import os
import re

@tool("Encerrar Atendimento")
def encerrar_atendimento() -> str:
    """Use esta ferramenta APENAS quando o usuário pedir expressamente para encerrar, dar tchau ou finalizar a conversa."""
    return "SISTEMA: Loop de atendimento finalizado com sucesso."

@tool("Autenticar Cliente")
def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
    """Usa o CPF e a data de nascimento para verificar se o cliente existe na base."""
    try:
        # ---------------------------------------------------------------------
        # LIMPANDO E TRATANDO CPF:
        # ---------------------------------------------------------------------
        cpf_num = re.sub(r'\D', '', str(cpf))
        cpf_limpo = f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}" if len(cpf_num) == 11 else str(cpf)
        # ---------------------------------------------------------------------
        # LIMPANDO E TRATANDO DATA:
        # ---------------------------------------------------------------------
        data_str = str(data_nascimento).strip()
        if "-" in data_str and len(data_str) == 10:
            data_limpa = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        else:
            d_num = re.sub(r'\D', '', data_str)
            if len(d_num) == 6:
                # Assume anos 1900 para 90+ ou 2000 para < 90, ou force 4 dígitos
                d_num = d_num[:4] + ("19" + d_num[4:] if int(d_num[4:]) > 30 else "20" + d_num[4:])
            data_limpa = f"{d_num[:2]}/{d_num[2:4]}/{d_num[4:]}" if len(d_num) == 8 else data_str

        df = pd.read_csv("data/clientes.csv", dtype=str)
        cliente = df[(df['cpf'] == cpf_limpo) & (df['data_nascimento'] == data_limpa)]
        
        if not cliente.empty:
            return f"Autenticado com sucesso. Nome do cliente: {cliente.iloc[0]['nome']}"
        return "Dados não conferem ou houve erro de sincronização. Peça de forma muito gentil e natural para o cliente verificar os dados e tentar novamente."
    except Exception as e:
        return f"Erro interno ao acessar a base: {str(e)}"

@tool("Consultar Limite de Crédito")
def consultar_limite_conta(cpf: str) -> str:
    """Consulta o limite de crédito atual do cliente diretamente no banco de dados."""
    try:
        cpf_num = re.sub(r'\D', '', str(cpf))
        cpf_limpo = f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}" if len(cpf_num) == 11 else str(cpf)

        df_clientes = pd.read_csv("data/clientes.csv", dtype=str)
        cliente_mask = df_clientes['cpf'] == cpf_limpo

        if not cliente_mask.any():
            return "Erro: CPF não localizado."

        cliente_idx = df_clientes.index[cliente_mask][0]
        limite_atual = float(df_clientes.at[cliente_idx, 'limite_atual'])
        return f"O limite atual do cliente é R$ {limite_atual}."
    except Exception as e:
        return f"Erro interno da ferramenta: {str(e)}"    

@tool("Processar Solicitação de Crédito")
def processar_solicitacao_credito(cpf: str, limite_solicitado: float) -> str:
    """Processa pedidos de ajuste de limite (APENAS AUMENTO) checando as faixas permitidas."""
    try:       
        if limite_solicitado <= 0:
            return "Abortado: o valor solicitado deve ser maior que zero."

        cpf_num = re.sub(r'\D', '', str(cpf))
        cpf_limpo = f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}" if len(cpf_num) == 11 else str(cpf)

        df_clientes = pd.read_csv("data/clientes.csv", dtype=str)
        df_score = pd.read_csv("data/score_limite.csv")
        
        # Isola o cliente pelo CPF
        cliente_mask = df_clientes['cpf'] == cpf_limpo.strip()
        if not cliente_mask.any():
            return "Erro: CPF não localizado na base de clientes."
            
        cliente_idx = df_clientes.index[cliente_mask][0]
        # Converte dados do CSV para cálculo
        score_atual = int(df_clientes.at[cliente_idx, 'score'])
        limite_atual = float(df_clientes.at[cliente_idx, 'limite_atual'])

        if limite_solicitado <= limite_atual:
            return "Abortado: somente solicitações de aumento de limite são permitidas."
        
        faixa = df_score[(df_score['score_min'] <= score_atual) & (df_score['score_max'] >= score_atual)]
        if faixa.empty:
            return "Erro técnico: Score fora dos limites tabelados."
        limite_maximo = float(faixa.iloc[0]['limite_maximo'])
        status = 'aprovado' if limite_solicitado <= limite_maximo else 'rejeitado'
        
        # Gera o log exigido pelo desafio
        arquivo_log = "data/solicitacoes_aumento_limite.csv"
        novo_pedido = pd.DataFrame([{
            'cpf_cliente': cpf.strip(),
            'data_hora_solicitacao': datetime.now().isoformat(),
            'limite_atual': limite_atual,
            'novo_limite_solicitado': limite_solicitado,
            'status_pedido': status
        }])
        
        novo_pedido.to_csv(arquivo_log, mode='a', header=not os.path.exists(arquivo_log), index=False)
        
        if status == 'aprovado':
            # Atualiza o arquivo principal do cliente
            df_clientes.at[cliente_idx, 'limite_atual'] = str(limite_solicitado)
            df_clientes.to_csv("data/clientes.csv", index=False)
            return f"SUCESSO. O pedido foi aprovado. Limite atualizado para {limite_solicitado}."
        
        return f"REJEITADO. O valor ultrapassa o teto permitido para o score de {score_atual} pontos."

    except Exception as e:
        return f"Erro interno da ferramenta: {str(e)}"