# Python Executor

Serviço baseado em **FastAPI** para execução controlada de rotinas Python através de uma API HTTP.

O `python-executor` foi desenvolvido para ser utilizado principalmente como um serviço auxiliar em automações, permitindo que aplicações como o **n8n** deleguem tarefas Python para um ambiente dedicado.

## Principais recursos

- Execução de código Python através de API REST
- Autenticação por token
- Endpoint de health check
- Suporte a diferentes conjuntos de dependências
- Processamento de imagens
- Criptografia e descriptografia de configurações
- Upload de arquivos via SFTP
- Execução em Docker
- Compatível com ambientes Kubernetes / OpenShift

## Imagem Docker

A imagem está disponível no Docker Hub:

`eden7tech/python-executor`

Existem diferentes versões de acordo com o conjunto de bibliotecas instalado:

```text
eden7tech/python-executor:basic
eden7tech/python-executor:pandas
eden7tech/python-executor:advanced
```

## Requisitos

- Docker
- Docker Compose (opcional)
- Porta `8000` disponível

## Configuração

O serviço utiliza variáveis de ambiente para configurações sensíveis.

### CONFIG_ENCRYPTION_KEY

Chave utilizada pela biblioteca de criptografia para proteger configurações.

### MCP_SECRET_TOKEN

Token utilizado para autenticar chamadas à API de execução.

Exemplo de arquivo `.env`:

```env
CONFIG_ENCRYPTION_KEY=sua_chave_de_criptografia
MCP_SECRET_TOKEN=seu_token_de_acesso
```

**Nunca publique o arquivo `.env` ou qualquer chave real no repositório.**

## Executando com Docker Compose

O projeto possui um `docker-compose.yaml` para execução do serviço.

```bash
docker compose up -d
```

Verificar o container:

```bash
docker compose ps
```

Visualizar os logs:

```bash
docker compose logs -f
```

Parar o serviço:

```bash
docker compose down
```

O serviço ficará disponível na porta:

```text
http://localhost:8000
```

## Health Check

O serviço disponibiliza:

```text
GET /health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

## API

### Executar código Python

Endpoint:

```text
POST /executar
```

A requisição deve utilizar o header:

```text
Authorization: Bearer SEU_TOKEN
```

O corpo da requisição possui a seguinte estrutura:

```json
{
  "codigo": "resultado = 10 + 20",
  "variaveis": {},
  "timeout": 300
}
```

O código executado pode utilizar as variáveis enviadas através do campo `variaveis`.

### Resposta

Em caso de sucesso:

```json
{
  "sucesso": true,
  "resultado": 30
}
```

Em caso de erro:

```json
{
  "sucesso": false,
  "erro": "mensagem do erro",
  "traceback": "..."
}
```

## Bibliotecas de apoio

O serviço possui bibliotecas internas para tarefas recorrentes.

### `lib.crypto`

Responsável por criptografar e descriptografar objetos utilizando a `CONFIG_ENCRYPTION_KEY`.

```python
from lib.crypto import Crypto

token = Crypto.encrypt(config)

config = Crypto.decrypt(token)
```

### `lib.imagem`

Funções para processamento de imagens, incluindo:

- Conversão de Base64
- Redimensionamento
- Miniaturas
- Crop
- Rotação
- Conversão para JPEG
- Conversão para PNG
- Conversão para WebP
- Consulta de dimensões

### `lib.upload`

Biblioteca para upload de arquivos via SFTP.

Suporta autenticação por:

- Senha
- Chave privada SSH

Também possui suporte a servidores que utilizam `ssh-rsa` para compatibilidade com ambientes antigos.

## Perfis de dependências

O projeto possui três conjuntos de dependências:

```text
requirements.basic
requirements.pandas
requirements.advanced
```

O perfil utilizado pode ser escolhido durante a construção da imagem Docker.

Exemplo:

```bash
docker build \
  --build-arg REQUIREMENTS=basic \
  -t eden7tech/python-executor:basic .
```

Para Pandas:

```bash
docker build \
  --build-arg REQUIREMENTS=pandas \
  -t eden7tech/python-executor:pandas .
```

Para o perfil avançado:

```bash
docker build \
  --build-arg REQUIREMENTS=advanced \
  -t eden7tech/python-executor:advanced .
```

## Código-fonte

O código-fonte, Dockerfile, Docker Compose e arquivos de configuração do projeto estão disponíveis neste repositório.

**GitHub:**  
`https://github.com/eden7tech/python-executor`

## Segurança

O endpoint `/executar` permite execução dinâmica de código Python. Portanto, o serviço deve ser executado em ambiente controlado e protegido por autenticação e regras de rede adequadas.

Não exponha o serviço diretamente à Internet sem implementar uma camada de segurança apropriada.

Nunca publique:

- Tokens
- Senhas
- Chaves privadas
- Arquivos `.env`
- Configurações reais
- Credenciais de servidores
- Chaves de API

## Licença

A licença do projeto será definida posteriormente.