## Rodando a Aplicação

### 1. Com Docker 

1.  **Construa as Imagens Docker:**
    ```bash
    docker-compose build
    ```

2.  **Inicie os Serviços:**
    ```bash
    docker-compose up -d
    ```

3.  **Verifique o Status dos Serviços:**
    ```bash
    docker-compose ps
    ```

4.  **Acesse a API:**
    * A API estará disponível em `http://localhost:8000`.
    * **Documentação Interativa (Swagger UI):** `http://localhost:8000/docs`
    * **Redoc UI:** `http://localhost:8000/redoc`

5.  **Populando o Banco de Dados (Opcional):**
    ```bash
    docker-compose exec backend python populate_db.py
    ```

6.  **Parar os Serviços:**
    ```bash
    docker-compose down
    ```
    ```bash
    docker-compose down -v
    ```

### 2. Sem Docker

1.  **Instale as Dependências Python:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute o Backend:**
    ```bash
    cd app
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **Acesse a API:**
    * A API estará disponível em `http://localhost:8000`.
    * **Documentação Interativa (Swagger UI):** `http://localhost:8000/docs`
    * **Redoc UI:** `http://localhost:8000/redoc`

4.  **Desativar o Ambiente Virtual:**
    ```bash
    deactivate
    ```

## Endpoints Principais (Exemplos)

* `GET /`: Mensagem de boas-vindas.
* `GET /status`: Verifica o status da conexão com o banco de dados.
* `POST /api/v1/auth/login`: Autentica o usuário. 
* `GET /api/v1/member/profile`: Obtém dados do perfil do sócio. (Requer autenticação) 
* `GET /api/v1/member/cards`: Lista os cartões de crédito salvos. (Requer autenticação) 
* `POST /api/v1/member/cards`: Adiciona um novo cartão. (Requer autenticação) 
* `DELETE /api/v1/member/cards/{cardId}`: Remove um cartão. (Requer autenticação) 
* `GET /api/v1/dashboard`: Carrega dados da tela principal (próximo jogo, notícias, etc.). 
* `GET /api/v1/news/{newsId}`: Obtém detalhes de uma notícia específica. 
* `POST /api/v1/news/{newsId}/like`: Curte ou descurte uma notícia. (Requer autenticação) 
* `GET /api/v1/matches`: Lista os próximos jogos para venda ou check-in. 
* `POST /api/v1/tickets/orders`: Finaliza a compra de ingressos. (Requer autenticação) 
* `POST /api/v1/matches/{matchId}/checkin`: Realiza o check-in em um jogo. (Requer autenticação) 
* `GET /api/v1/benefits`: Lista os parceiros e seus benefícios. 
* `GET /api/v1/benefits/{benefitId}`: Obtém detalhes de um benefício específico. 

Para uma lista completa e detalhada de todos os endpoints, parâmetros de requisição e formatos de resposta, consulte a documentação interativa em `/docs`.
