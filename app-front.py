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
VIDEO_PATH = BASE_DIR / "assets" / "pokemon.mp4"


def adicionar_background():
    if not VIDEO_PATH.exists():
        st.error(f"Vídeo não encontrado em: {VIDEO_PATH}")
        st.stop()

    with open(VIDEO_PATH, "rb") as video:
        video_base64 = base64.b64encode(video.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: transparent;
        }}

        #video-background {{
            position: fixed;

            top: 50%;
            left: 50%;

            min-width: 100%;
            min-height: 100%;

            width: auto;
            height: auto;

            transform: translate(-48%, -50%) scale(1.15);

            object-fit: cover;
            object-position: center center;

            z-index: -2;
        }}

        #overlay {{
            position: fixed;
            top: 0;
            left: 0;

            width: 100vw;
            height: 100vh;

            background: rgba(0,0,0,0.55);
            z-index: -1;
        }}

        h1, h2, h3, h4, h5, h6,
        p, span, label {{
            color: white !important;
        }}

        .stTextInput input {{
            background: rgba(255,255,255,0.9);
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
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            background: #2A75BB;
            color: white;
            transform: scale(1.02);
        }}

        .pokemon-card {{
            background: rgba(0,0,0,0.70);
            backdrop-filter: blur(15px);

            border: 3px solid #FFCB05;
            border-radius: 20px;

            padding: 30px;

            max-width: 420px;
            margin: 30px auto;

            text-align: center;
            box-shadow: 0 0 25px rgba(255,203,5,.4);
        }}

        .pokemon-card img {{
            image-rendering: pixelated;
        }}
        </style>

        <video autoplay muted loop playsinline id="video-background">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>

        <div id="overlay"></div>
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

                tipos = ", ".join(pokemon["tipos"])
                habilidades = ", ".join(pokemon["habilidades"])

                st.markdown(
                    f"""
                    <div class="pokemon-card">
                        <h2>{pokemon['nome'].capitalize()}</h2>

                        <img src="{pokemon['imagem']}" width="220">

                        <br><br>

                        <b>ID:</b> {pokemon['id']}<br>
                        <b>Altura:</b> {pokemon['altura']}<br>
                        <b>Peso:</b> {pokemon['peso']}<br>
                        <b>Tipos:</b> {tipos}<br>
                        <b>Habilidades:</b> {habilidades}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Não foi possível conectar à API FastAPI. "
                "Verifique se ela está rodando."
            )

        except requests.exceptions.Timeout:
            st.error("A consulta demorou muito. Tente novamente.")