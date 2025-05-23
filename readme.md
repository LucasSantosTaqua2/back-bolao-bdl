# Bolão Balde de Lixo - API Backend (FastAPI + MySQL)

Bem-vindo ao backend da API do Bolão Balde de Lixo! Este projeto é a espinha dorsal para o sistema de bolão de futebol, construído com FastAPI, SQLAlchemy e MySQL.

---

## Descrição do Projeto

Este backend fornece as funcionalidades essenciais para o seu bolão do Brasileirão, incluindo:

* **Gerenciamento de Usuários:** Cadastro, login com autenticação via JWT (JSON Web Tokens) e perfis de usuário.
* **Gerenciamento de Jogos:** Criação de jogos (incluindo upload via planilha Excel), listagem por rodada e atualização de resultados (funcionalidade de admin).
* **Gerenciamento de Apostas:** Submissão de apostas pelos usuários e visualização das apostas feitas.
* **Ranking de Usuários:** Cálculo e exibição da pontuação dos usuários.
* **Armazenamento de Dados:** Utiliza MySQL como banco de dados.
* **API RESTful:** Endpoints bem definidos para comunicação com o frontend.

---

## Tecnologias Utilizadas

* Python 3.12+
* **FastAPI:** Framework web de alta performance para construir APIs.
* **SQLAlchemy:** ORM para interagir com o banco de dados MySQL.
* **PyMySQL:** Driver Python para MySQL.
* **Pydantic:** Para validação de dados e schemas.
* **Pydantic-Settings:** Para gerenciamento de configurações e variáveis de ambiente.
* **Uvicorn:** Servidor ASGI para rodar a aplicação FastAPI em desenvolvimento.
* **Gunicorn:** Servidor WSGI (usado com Uvicorn workers) para produção.
* **Passlib com Bcrypt:** Para hashing seguro de senhas.
* **Python-JOSE:** Para criação e validação de tokens JWT.
* **Openpyxl:** Para manipulação de ficheiros Excel (upload de jogos/resultados).
* **MySQL:** Banco de dados relacional.

---

## Arquitetura de Deploy

* **Backend (Esta API):** Hospedado no Railway.
* **Banco de dados MySQL:** Hospedado no Railway.

* **Frontend (Angular):** Hospedado no Vercel.

