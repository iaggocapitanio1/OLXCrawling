

# OLXCrawling
**Objetivo:** Extração otimizada de dados imobiliários da OLX em Santa Catarina com Scrapy. 

Este projeto é focado em obter dados de propriedades da OLX, navegando por seu conteúdo dinâmico. Ferramentas como Splash e Playwright são usadas para garantir a precisão da extração. A solução é desenvolvida respeitando padrões éticos, com ênfase no rate-limiting e no arquivo robots.txt.

## Requesitos:
- Python 3.9>+;

## Branches do Projeto:
### 1. Master (Playwright):
- **Características:** 
   - Processamento assíncrono.
   - Extração de dados fluida com o web driver Playwright.
   - Recomendado para varredura rápida.
   
- **Como acessar:** 
   ```shell
   git clone git@github.com:iaggocapitanio1/OLXCrawling.git
   cd OLXCrawling
   ```

### 2. Selenium:
- **Características:** 
   - Utiliza Selenium, ferramenta renomada para web scraping.
   - Apresenta de forma síncrona o fluxo dos processos, ideal para análise detalhada.

- **Como acessar:** 
   ```shell
   git clone git@github.com:iaggocapitanio1/OLXCrawling.git
   cd OLXCrawling
   git checkout selenium
   ```

## Integração com Docker e MongoDB:
O projeto é integrado ao Docker, facilitando o armazenamento dos dados no MongoDB - escolhido por sua estrutura NoSQL e alta velocidade de leitura.

**Passos para acessar os dados via Docker:**
1. Certifique-se de ter o Docker instalado.
2. No diretório do projeto, execute:
   ```shell
   docker-compose up --build -d
   ```
3. Acesse os dados via interface web do Mongo Express: [http://localhost:8081](http://localhost:8081)
   - Usuário: `root`
   - Senha: `ScrapyUtxMongo2023!`


## Primeiros Passos:

Após o clone do projeto, instale as dependências:
```shell
pip install -r requirements.txt
```
Certifique-se de ter o Docker instalado e execute o comando abaixo para iniciar o container do MongoDB:
```shell
docker-compose up --build -d
```
---
Certifique que o playwrigth está atualizado e instalado:
```shell
playwright install
```

Rode o projeto:
```shell
scrapy crawl olx
```

### Configurações:
Caso deseje mudar as configurações do projeto, basta acessar o arquivo `settings.py` e alterar os valores das variáveis.

Algumas delas são:

```python
PAGE_LIMIT = 100 # Número de páginas a serem varridas
DATABASE = {
    'host': 'localhost', # Host do MongoDB
    'port': '27017', # Porta do MongoDB
    'db': 'olx', # Nome do banco de dados
    'collection': 'items', # Nome da Collection
    'user': 'root', # Usuário do MongoDB
    'password': 'ScrapyUtxMongo2023!' # Senha do MongoDB
}
```


### Contato:
- Author: Iaggo Capitanio
- email: iaggo.capitanio@gmail.com