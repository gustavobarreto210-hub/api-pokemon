from pathlib import Path
import base64
from fastapi import background
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
            background: rgba(255,255,255,.92);
            border-radius:14px;
            height:55px;
            font-size:20px;
            text-align:center;
            font-weight:bold;
        }}

        .stButton > button {{
            width:100%;
            height:55px;
            font-size:18px;
            border-radius:14px;
            background:#ffcb05;
            color:#222;
            font-weight:bold;
            transition:.25s;
        }}

        .stButton > button:hover {{
            background:#2a75bb;
            color:white;
            transform:scale(1.02);
        }}

        .pokemon-card {{
            background:rgba(15,15,15,.72);

            backdrop-filter:blur(18px);

            border:3px solid #ffcb05;

            border-radius:25px;

            padding:35px;

            margin-top:35px;

             box-shadow:0 0 40px rgba(255,203,5,.45);
        }}
        .badge{{

            display:inline-block;

            background:#ffcb05;

            color:black;

            font-weight:bold;

            padding:6px 14px;

            margin:4px;

            border-radius:999px;
                
        }}
        .info-box{{
            background:rgba(255,255,255,.08);
            border-radius:15px;
            padding:15px;
            text-align:center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

adicionar_background()

st.markdown(
    """
    <h1 style='text-align:center;font-size:55px;'>
        ⚡ Pokédex
    </h1>

    <h4 style='text-align:center;color:white;'>
        Pesquise qualquer Pokémon
    </h4>
    """,
    unsafe_allow_html=True
)

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
        except requests.RequestException:
            st.error("Erro ao consultar a API.")
        else:
            if resposta.status_code == 404:
                st.error("Pokémon não encontrado.")

            elif resposta.status_code != 200:
                st.error("Erro ao consultar a API.")

            else:
                pokemon = resposta.json()

                st.markdown("<div class='pokemon-card'>", unsafe_allow_html=True)

            st.markdown(
            f"""
                <h1 style="text-align:center;">
                     {pokemon['nome'].capitalize()}
                </h1>
                 """,
                unsafe_allow_html=True
            )

c1, c2, c3 = st.columns([1,2,1])

with c2:
    st.image(
        pokemon["imagem"],
        width=260
    )

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"""
        <div class='info-box'>
        <h4>ID</h4>
        <h2>{pokemon['id']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='info-box'>
        <h4>Altura</h4>
        <h2>{pokemon['altura']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class='info-box'>
        <h4>Peso</h4>
        <h2>{pokemon['peso']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='info-box'>
        <h4>Tipo</h4>
        <h2>{', '.join(pokemon['tipos']).title()}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("## ✨ Habilidades")

habilidades = ""

for habilidade in pokemon["habilidades"]:
    habilidades += f"<span class='badge'>{habilidade.title()}</span>"

st.markdown(habilidades, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)