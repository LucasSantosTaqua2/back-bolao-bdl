# Bolão Balde de Lixo - API Backend

Bem-vindo ao backend da API do Bolão Balde de Lixo! Este projeto é a espinha dorsal para o seu sistema de bolão de futebol, construído com **FastAPI** e **SQLite**.

---

## Descrição do Projeto

Este backend fornece as funcionalidades essenciais para o seu bolão do Brasileirão, incluindo:

* **Gerenciamento de Usuários:** Cadastro e autenticação via JWT (JSON Web Tokens).
* **Armazenamento de Dados:** Utiliza SQLite para o banco de dados, ideal para desenvolvimento.
* **API RESTful:** Endpoints bem definidos para comunicação com o frontend Angular.

---

## Tecnologias Utilizadas

* Python 3.12+
* **FastAPI**: Framework web de alta performance para construir APIs.
* **SQLModel**: Uma biblioteca para interagir com bancos de dados, combinando a elegância do Pydantic com o poder do SQLAlchemy.
* **SQLite**: Banco de dados leve baseado em arquivo, perfeito para desenvolvimento.
* **Uvicorn**: Servidor ASGI para rodar a aplicação FastAPI.
* `passlib` e `python-jose`: Para hashing de senhas e JWT.

---

## Como Configurar e Rodar o Projeto

Siga estes passos para colocar o backend da API em funcionamento na sua máquina local:

### 1. Clonar o Repositório

Primeiro, clone o repositório para a sua máquina (se você ainda não o fez):

\`\`\`bash
git clone [https://github.com/seu_usuario/bolao-api.git](https://github.com/LucasSantosTaqua2/bolao_bdl)
cd bolao-api
\`\`\`

### 2. Configurar o Ambiente Virtual

É **altamente recomendado** usar um ambiente virtual para isolar as dependências do seu projeto.

\`\`\`bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual

### No Windows:
.\\venv\\Scripts\\activate

### No macOS/Linux:
source venv/bin/activate
\`\`\`

### 3. Instalar as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias listadas no `requirements.txt`:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configurar Variáveis de Ambiente

Crie um arquivo chamado **`.env`** na **raiz do projeto** (`bolao-api/`) com as seguintes informações.

\`\`\`
DATABASE_URL="sqlite:///./sql_app.db"
SECRET_KEY="SUA_SUPER_CHAVE_SECRETA_E_UNICA_AQUI"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
\`\`\`

**Importante:** A `SECRET_KEY` deve ser uma string longa e aleatória, crucial para a segurança dos seus JWTs. Você pode gerar uma com `openssl rand -hex 32` no terminal.

### 5. (Opcional) Limpar Banco de Dados Existente

Se você já rodou o projeto antes e modificou os modelos de dados, para garantir que o banco de dados SQLite (`sql_app.db`) seja recriado com a estrutura mais recente, você pode excluí-lo:

\`\`\`bash
# No Windows:
del sql_app.db

# No macOS/Linux:
rm sql_app.db
\`\`\`

*(Este passo é opcional e só é necessário se você precisar de um banco de dados "limpo" com as tabelas atualizadas.)*

### 6. Rodar a Aplicação FastAPI

Com todas as dependências instaladas e o ambiente configurado, você pode iniciar o servidor da API:

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

\*O `--reload` faz com que o servidor reinicie automaticamente quando você faz alterações no código.\*

### 7. Acessar a API

A API estará disponível em `http://127.0.0.1:8000`.

Você pode acessar a **documentação interativa do Swagger UI** em:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Ou a documentação do ReDoc em:
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Use a documentação para testar os endpoints de registro, login e perfil de usuário.

---

## Próximos Passos (Desenvolvimento)

* Definir e implementar os modelos, CRUD e endpoints para **Jogos** e **Apostas**.
* Integrar o frontend Angular com os endpoints da API.
* Implementar autenticação JWT no frontend para proteger as rotas.

---
