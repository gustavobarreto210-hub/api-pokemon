from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="POKEDEX-API")

POKEAPI_URL = "https://pokeapi.co/api/v2"


@app.get("/")
def home():
    return {"mensagem": "Bem-vindo à Minha API Pokémon! Use o endpoint /pokemon/{nome} para buscar informações sobre um Pokémon específico."}


@app.get("/pokemon/{nome}")
async def buscar_pokemon(nome: str):
    async with httpx.AsyncClient() as client:
        resposta = await client.get(f"{POKEAPI_URL}/pokemon/{nome.lower()}")

    if resposta.status_code == 404:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
   
    dados = resposta.json()

    return {
        "id": dados["id"],
        "nome": dados["name"],
        "altura": dados["height"],
        "peso": dados["weight"],
        "tipos": [tipo["type"]["name"] for tipo in dados["types"]],
        "habilidades": [
            habilidade["ability"]["name"]
            for habilidade in dados["abilities"]
        ],
        "imagem": dados["sprites"]["other"]["official-artwork"]["front_default"]
    }

