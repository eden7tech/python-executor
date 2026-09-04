import sys
import io
import traceback
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
import uvicorn

# Configuração de Segurança por Token (MCP_SECRET_TOKEN)
API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="Python Executor Service",
    description="Ambiente seguro para execução de rotinas Python no n8n",
    version="1.0.0"
)

def verify_token(api_key_header: str = Security(api_key_header)):
    """ Valida o token de segurança enviado no Header Authorization """
    import os
    expected_token = os.getenv("MCP_SECRET_TOKEN")
    
    if not expected_token:
        # Se não houver token configurado no ambiente, permite a execução (modo dev)
        return True
        
    if api_key_header:
        token = api_key_header.replace("Bearer ", "").strip()
        if token == expected_token:
            return True
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autorização inválido ou ausente."
    )

class ExecuteRequest(BaseModel):
    codigo: str = Field(..., description="Código Python a ser executado")
    variaveis: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Variáveis de entrada")
    timeout: Optional[int] = Field(default=300, description="Timeout em segundos (reservado)")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """ Rota do Liveness / Readiness Probe do Kubernetes """
    return {"status": "ok"}

# ⚠️ CORREÇÕES:
# 1. Mantida a rota '/executar' original que o n8n chama.
# 2. Alterado de 'async def' para 'def' normal (evita travar o /health durante o Pandas).
@app.post("/executar")
def executar(request: ExecuteRequest, authenticated: bool = Security(verify_token)):
    """ Executa código Python dinamicamente isolando o escopo """
    
    # Prepara o ambiente de execução global com bibliotecas comuns pré-carregadas
    exec_globals = {
        "__builtins__": __builtins__,
    }
    
    # Injeta as variáveis passadas pelo payload (ex: 'dados')
    if request.variaveis:
        exec_globals.update(request.variaveis)

    try:
        # Executa o código Python
        exec(request.codigo, exec_globals)
        
        # Recupera a variável 'resultado' ou 'resultado_json' definida no código do usuário
        resultado = exec_globals.get("resultado") or exec_globals.get("resultado_json")
        
        if resultado is None:
            # Se não definiu 'resultado', retorna as variáveis globais criadas (exceto builtins)
            resultado = {
                k: v for k, v in exec_globals.items() 
                if not k.startswith("__") and k not in ("pd", "np", "request")
            }

        return {"sucesso": True, "resultado": resultado}

    except Exception as e:
        error_msg = traceback.format_exc()
        return {
            "sucesso": False,
            "erro": str(e),
            "traceback": error_msg
        }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=2)
