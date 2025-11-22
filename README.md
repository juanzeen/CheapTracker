# CheapTracker

O CheapTracker é um sistema de logística e otimização de rotas. O projeto foi desenvolvido como parte de um trabalho acadêmico e tem como objetivo principal calcular as rotas mais eficientes (menor distância e custo) para entregas, considerando diferentes variáveis como veículos, depósitos e pedidos.

## Funcionalidades

-   Gerenciamento de Pedidos (CRUD)
-   Gerenciamento de Frotas (Caminhões)
-   Gerenciamento de Entregas e Viagens
-   Cálculo e otimização de rotas
-   Autenticação e gerenciamento de usuários

## Dependências

O projeto é construído em Python com o framework Django. As principais dependências são:

-   Python 3.10+
-   Django
-   PostgreSQL (executado via Docker)
-   `psycopg2-binary`
-   `geopy`
-   `osmnx`
-   E outras listadas em `requirements.txt`

## Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar o ambiente de desenvolvimento.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd CheapTracker
```

### 2. Configurar Variáveis de Ambiente

Crie uma cópia do arquivo de exemplo `.envexample` e renomeie para `.env`. Em seguida, preencha as variáveis com as credenciais do seu banco de dados.

```bash
cp .envexample .env
```

Edite o arquivo `.env`:

```
POSTGRES_DB=cheaper_db
POSTGRES_USER=cheaper_user
POSTGRES_PASSWORD=cheaper_pass
PORT=5433
```

### 3. Iniciar o Banco de Dados com Docker

Certifique-se de ter o Docker e o Docker Compose instalados. Em seguida, inicie o container do PostgreSQL.

```bash
docker-compose up -d
```

### 4. Configurar o Ambiente Python

É recomendado usar um ambiente virtual (`venv`) para isolar as dependências do projeto.

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows:
venv\Scripts\activate
```

### 5. Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas Python listadas no `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 6. Executar as Migrações do Banco

Aplique as migrações do Django para criar as tabelas no banco de dados.

```bash
python project/manage.py migrate
```

### 7. Iniciar o Servidor de Desenvolvimento

Finalmente, inicie o servidor local do Django.

```bash
python project/manage.py runserver
```

O servidor estará disponível em `http://127.0.0.1:8000`.