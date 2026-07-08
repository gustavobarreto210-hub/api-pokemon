from pathlib import Path
import base64
import requests
import streamlit as st

st.set_page_config(
    page_title="Pokédex",
    page_icon="⚡",
    layout="centered"
)

API_URL = "http://127.0.0.1:8000"

BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "assets" / "pokemon.jpg"


def adicionar_background():

    if not IMAGE_PATH.exists():
        st.error(f"Imagem não encontrada em: {IMAGE_PATH}")
        st.stop()

    with open(IMAGE_PATH, "rb") as img:
        img_base64 = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background:
                linear-gradient(
                    rgba(0,0,0,0.55),
                    rgba(0,0,0,0.55)
                ),
                url("data:image/jpeg;base64,{img_base64}");

            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        h1, h2, h3, h4, h5, h6,
        p, span, label {{
            color: white !important;
        }}

        .stTextInput input {{
            background: rgba(255,255,255,0.90);
            color: black;
            border-radius: 12px;
        }}

        .stButton > button {{
            width: 100%;
            height: 45px;
            background: #FFCB05;
            color: black;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            transition: .3s;
        }}

        .stButton > button:hover {{
            background: #2A75BB;
            color: white;
        }}

        .pokemon-card {{
            background: rgba(0,0,0,.70);
            backdrop-filter: blur(15px);
            border: 3px solid #FFCB05;
            border-radius: 20px;
            padding: 30px;
            max-width: 420px;
            margin: 30px auto;
            text-align: center;
            box-shadow: 0 0 25px rgba(255,203,5,.4);
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

adicionar_background()

st.title("⚡ Pokédex")

st.write("Digite o nome de um Pokémon para consultar sua API FastAPI.")

nome = st.text_input(
    "Nome do Pokémon",
    placeholder="Ex: Pikachu"
)

if st.button("Buscar Pokémon"):

    if not nome.strip():
        st.warning("Digite o nome de um Pokémon.")

    else:
        try:
            resposta = requests.get(
                f"{API_URL}/pokemon/{nome.lower().strip()}",
                timeout=10
            )

            if resposta.status_code == 404:
                st.error("Pokémon não encontrado.")

            elif resposta.status_code != 200:
                st.error("Erro ao consultar a API.")

            else:
                pokemon = resposta.json()

                # Card de resultado
                st.markdown("<div class='pokemon-card'>", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <h1 style="text-align:center; color:white;">
                        {pokemon['nome'].capitalize()}
                    </h1>
                    """,
                    unsafe_allow_html=True
                )

                # Imagem centralizada
                col1, col2, col3 = st.columns([1, 2, 1])

                with col2:
                    st.image(
                        pokemon["imagem"],
                        width=220
                    )

                st.divider()

                # Informações
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label="🆔 ID",
                        value=pokemon["id"]
                    )

                    st.metric(
                        label="📏 Altura",
                        value=pokemon["altura"]
                    )

                with col2:
                    st.metric(
                        label="⚖️ Peso",
                        value=pokemon["peso"]
                    )

                    st.metric(
                        label="🏷️ Tipos",
                        value=", ".join(
                            tipo.capitalize()
                            for tipo in pokemon["tipos"]
                        )
                    )

                st.markdown("### ✨ Habilidades")

                for habilidade in pokemon["habilidades"]:
                    st.write(f"• {habilidade.capitalize()}")

                st.markdown("</div>", unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error(
                "Não foi possível conectar à API FastAPI.\n\n"
                "Verifique se ela está rodando."
            )

        except requests.exceptions.Timeout:
            st.error("A consulta demorou muito. Tente novamente.")