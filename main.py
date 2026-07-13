from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="POKEDEX-API")

POKEAPI_URL = "https://pokeapi.co/api/v2"


# --- 1. Manipulador Global de Erros Inesperados (Erro 500) ---
@app.exception_handler(Exception)
async def erro_global_exception_handler(request: Request, exc: Exception):
    # Dica: Em produção, faça log do erro real aqui (ex: logger.error(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "erro": "Erro Interno",
            "detalhes": "Ocorreu um erro inesperado no servidor. Tente novamente mais tarde."
        }
    )


@app.get("/")
def home():
    return {"mensagem": "Bem-vindo à Minha API Pokémon! Use o endpoint /pokemon/{nome} para buscar informações sobre um Pokémon específico."}


@app.get("/pokemon/{nome}")
async def buscar_pokemon(nome: str):
    # Garantir que o nome não vá vazio ou cheio de espaços
    nome_limpo = nome.strip().lower()
    if not nome_limpo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="O nome do Pokémon não pode ser vazio."
        )

    try:
        # Definimos um timeout de 5 segundos para a API não ficar travada esperando a PokeAPI externa
        async with httpx.AsyncClient(timeout=5.0) as client:
            resposta = await client.get(f"{POKEAPI_URL}/pokemon/{nome_limpo}")
            
            # Lança uma exceção httpx.HTTPStatusError se o status_code for 4xx ou 5xx
            resposta.raise_for_status()

    # --- 2. Tratamento para erros de Status HTTP da PokeAPI (4xx e 5xx) ---
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Pokémon '{nome}' não encontrado."
            )
        
        # Caso a PokeAPI externa esteja fora do ar ou instável (Ex: Erro 500 ou 503)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A API externa de Pokémon apresentou instabilidade. Tente novamente mais tarde."
        )

    # --- 3. Tratamento para problemas de Rede e Conexão (DNS, Timeout, etc.) ---
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

    # --- 4. Processamento dos Dados com segurança ---
    try:
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
            # Usando .get() e caminhos seguros para evitar KeyError se a PokeAPI mudar a estrutura da imagem
            "imagem": dados.get("sprites", {})
                           .get("other", {})
                           .get("official-artwork", {})
                           .get("front_default")
        }
    except (ValueError, KeyError):
        # Trata casos onde o JSON retornado veio corrompido ou modificaram as chaves esperadas
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A estrutura de dados retornada pelo servidor externo é inválida ou incompatível."
        )