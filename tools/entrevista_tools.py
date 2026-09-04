import pandas as pd
from crewai.tools import tool

@tool("Recalcular Score de Crédito")
def recalcular_score(cpf: str, renda_mensal: float, tipo_emprego: str, despesas: float, num_dependentes: int, tem_dividas: str) -> str:
    """Calcula o novo score do cliente com base na entrevista financeira e atualiza a base de dados."""
    try:
        # Dicionários de Pesos
        peso_renda = 30
        peso_emprego = {"formal": 300, "autônomo": 200, "desempregado": 0}
        peso_dependentes = {0: 100, 1: 80, 2: 60} # Valores >= 3 usarão 30
        peso_dividas = {"sim": -100, "não": 100, "nao": 100}

        # Tratamento de Inputs
        emprego_limpo = tipo_emprego.lower().strip()
        divida_limpa = tem_dividas.lower().strip()
        
        p_emp = peso_emprego.get(emprego_limpo, 0)
        p_dep = peso_dependentes.get(num_dependentes, 30) if num_dependentes < 3 else 30
        p_div = peso_dividas.get(divida_limpa, -100) # Penaliza por padrão em caso de dúvida

        # Cálculo com teto e piso (Clamping 0 - 1000)
        score_bruto = ((renda_mensal / (despesas + 1)) * peso_renda) + p_emp + p_dep + p_div
        score_final = int(max(0, min(score_bruto, 1000)))

        # Atualização no Banco de Dados
        df_clientes = pd.read_csv("data/clientes.csv", dtype=str)
        cliente_mask = df_clientes['cpf'] == str(cpf).strip()
        
        if not cliente_mask.any():
            return "Erro: CPF não localizado para atualizar o score."
            
        cliente_idx = df_clientes.index[cliente_mask][0]
        df_clientes.at[cliente_idx, 'score'] = str(score_final)
        df_clientes.to_csv("data/clientes.csv", index=False)

        return f"Cálculo concluído com sucesso. O novo score do cliente é {score_final}."
        
    except Exception as e:
        return f"Erro interno ao calcular o score: {str(e)}"