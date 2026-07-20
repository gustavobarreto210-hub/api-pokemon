from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="POKEDEX-API")

POKEAPI_URL = "https://pokeapi.co/api/v2"


@app.exception_handler(Exception)
async def erro_global_exception_handler(request: Request, exc: Exception):
   
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "erro": "Erro Interno",
            "detalhes": f"Ocorreu um erro inesperado no servidor. Tente novamente mais tarde. Erro: {str(exc)}"
        }
    )


@app.get("/")
def home():
    return {"mensagem": "Bem-vindo à Minha API Pokémon! Use o endpoint /pokemon/{nome} para buscar informações sobre um Pokémon específico."}


@app.get("/pokemon/{nome}")
async def buscar_pokemon(nome: str):
    nome_limpo = nome.strip().lower()
    if not nome_limpo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="O nome do Pokémon não pode ser vazio."
        )

    try:
      
        async with httpx.AsyncClient(timeout=5.0) as client:
            resposta = await client.get(f"{POKEAPI_URL}/pokemon/{nome_limpo}")
            
           
            resposta.raise_for_status()

    
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Pokémon '{nome}' não encontrado."
            )
        
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A API externa de Pokémon apresentou instabilidade. Tente novamente mais tarde."
        )

   
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="O servidor externo demorou muito para responder. Limite de tempo esgotado."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível estabelecer conexão com o serviço externo de Pokémon."
        )

    try:
        dados = resposta.json()

        return {
            "id": dados["id"],
            "nome": dados["name"],
            "altura": dados["height"] / 10,
            "peso": dados["weight"] / 10,
            "tipos": [tipo["type"]["name"] for tipo in dados["types"]],
            "habilidades": [
                habilidade["ability"]["name"]
                for habilidade in dados["abilities"]
            ],
            "imagem": dados.get("sprites", {})
                           .get("other", {})
                           .get("official-artwork", {})
                           .get("front_default")
        }
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A estrutura de dados retornada pelo servidor externo é inválida ou incompatível."
        )
