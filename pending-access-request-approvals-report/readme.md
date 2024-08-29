## Requisitos

Certifique-se de que você tenha o Python 3.x instalado. As dependências do projeto estão listadas no arquivo `requirements.txt`.

Para instalar as dependências, execute:

```sh
pip install -r requirements.txt
```

## Configuração

Antes de executar o script, você deve configurar as variáveis `tenant`, `client_id`, e `client_secret` que são usadas para autenticação com a API.

## Executando o Script

1. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

2. Execute o script:

    ```sh
    python main.py
    ```

    O script solicitará que você insira o `tenant`, `client_id` e `client_secret`. Após fornecer essas informações, o script irá gerar um arquivo CSV com o relatório das aprovações de acesso pendentes.

## Estrutura do Projeto

- `main.py`: Script principal que realiza a coleta dos dados, a autenticação, e a geração do relatório.
- `app-YYYY-MM-DD.log`: Arquivo de log gerado com o registro das operações do script.
- `report-YYYY-MM-DD.csv`: Arquivo CSV gerado contendo os dados das aprovações de acesso pendentes.
- `requirements.txt`: Arquivo que lista as dependências do projeto.

## Exemplo de Uso

Ao executar o script, você será solicitado a inserir as seguintes informações:

```plaintext
Insira o tenant (ex: acme, acme-sb): 
Insira o client id: 
Insira o client secret: 
```

O script gerará um arquivo CSV com o nome `report-YYYY-MM-DD.csv`, onde `YYYY-MM-DD` é a data atual, contendo os dados das aprovações de acesso pendentes.

## Contribuindo

Se você deseja contribuir para este projeto, sinta-se à vontade para enviar pull requests ou abrir issues.

