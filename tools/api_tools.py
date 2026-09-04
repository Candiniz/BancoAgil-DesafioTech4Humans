import requests
from crewai.tools import tool

@tool("Consultar Cotação de Moedas")
def consultar_cotacao(moeda_origem: str, moeda_destino: str = "BRL") -> str:
    """
    Busca a cotação atual de uma moeda em relação a outra.
    Aceita códigos de três letras (ex: USD, EUR, BTC, JPY, CLP).
    Se o usuário perguntar a cotação de uma moeda sem especificar contra qual, 
    assuma que a moeda_destino é BRL. 
    Exemplo: "Cotação do Dólar" -> moeda_origem="USD", moeda_destino="BRL".
    Exemplo: "Euro para Dólar" -> moeda_origem="EUR", moeda_destino="USD".
    """
    try:
        origem = moeda_origem.upper().strip()
        destino = moeda_destino.upper().strip()
        
        url = f"https://economia.awesomeapi.com.br/last/{origem}-{destino}"
        response = requests.get(url)
        
        if response.status_code == 200:
            dados = response.json()
            chave = f"{origem}{destino}"
            cotacao = float(dados[chave]['bid'])
            
            # Formatação com 4 casas decimais para moedas fracas
            return f"A cotação de 1 {origem} em {destino} é {cotacao:.4f}."
            
        return f"Não foi possível encontrar a cotação de {origem} para {destino}. Verifique se os pares estão corretos."
    except Exception as e:
        return f"Erro ao acessar a API de câmbio: {str(e)}"