import streamlit as st
import base64

def carregar_imagem_base64(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def renderizar_hero():
    """Renderiza a seção Hero e os estilos globais da aplicação."""
    logo_b64 = carregar_imagem_base64("assets/bankLogo.png")
    background_b64 = carregar_imagem_base64("assets/background.jpg")
    
    st.set_page_config(
        page_title="Banco Ágil | Simples para você, Ágil para seu negócio",
        page_icon="assets/favicon.png",
        layout="wide"
    )
    st.html(f"""
    <style>
        /* Reset Global e Cores de Fundo */
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            height: 100%;
        }}

        header[data-testid="stHeader"] {{
            background-color: #ff6600 !important;
        }}

        [data-testid="stAppViewContainer"] {{
            position: relative;
            z-index: 1;
            background: transparent !important;
        }}

        .stApp {{
            position: relative;
            background: none !important;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background-image: url("data:image/jpeg;base64,{background_b64}");
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
            opacity: 0.2;
            z-index: 0;
            pointer-events: none;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            color: rgba(255, 255, 255, 0.5) !important;
        }}

        /* Hero Container */
        .hero-wrapper {{
            position: relative;
            width: 100%;
            overflow: visible;
        }}

        .hero {{
            position: relative;
            overflow: visible;
            padding: 60px 40px;
            text-align: center;
            box-sizing: border-box;
            z-index: 1;
        }}

        .hero img {{
            position: relative;
            z-index: 2;
            margin-top: -50px;
            width: 500px;
            max-width: 100%;
            height: auto;
            margin-bottom: 15px;
        }}

        .hero h1 {{
            position: relative;
            z-index: 2;
            color: white;
            font-size: 30px;
            margin: 10px 0 5px 0;
        }}

        .hero p {{
            position: relative;
            z-index: 2;
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            margin: 0;
            margin-top: -45px;
        }}

        /* Responsividade */
        @media (max-width: 600px) {{
            .hero {{
                padding: 40px 20px;
            }}
            .hero img {{
                width: 280px;
            }}
            .hero p {{
                font-size: 14px;
                margin-top: -10px;
            }}
        }}
    </style>

    <div class="hero-wrapper">
        <div class="hero">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo do Banco" />
            <p>Simples para você. Ágil para o seu futuro.</p>
        </div>
    </div>
    """)