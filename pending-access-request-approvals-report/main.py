import csv
import json
import logging
import certifi
from datetime import datetime
import requests

# Configurar o logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Alterado para INFO para capturar mais mensagens

# Criar handlers
console_handler = logging.StreamHandler()
date_str = datetime.now().strftime('%Y-%m-%d')
file_handler = logging.FileHandler(f'app-{date_str}.log')

# Configurar nível de log para os handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)

# Criar formatação e adicionar aos handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adicionar handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class ApiCalls:
    def __init__(self, jwt_token):
        self.token = jwt_token

    def _request(self, method, endpoint, headers=None, data=None, params=None):
        try:
            url = f"https://{tenant}.api.identitynow.com{endpoint}"
            logger.info(f"Enviando requisição {method} para {url}.")
            logger.debug(data)
            response = requests.request(method, url, headers=headers, data=data, params=params, verify=certifi.where())
            if response.status_code in [200, 201, 207]:
                logger.info(f"Requisição para {url} bem-sucedida com status {response.status_code}.")
                logger.debug(response.content)
                return response
            else:
                logger.error(f"Erro {response.status_code} para {url}: {response.json()}")
        except Exception as error:
            logger.error(f"Erro na requisição para {url}: {error}")
        return None

    def get_pending_access_request_approvals(self):
        all_data = []
        offset = 0
        limit = 250
        
        while True:
            url = '/beta/access-request-approvals/pending'
            params = {
                "count": True,
                "offset": offset,
                "limit": limit
            }
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = self._request("GET", endpoint=url, headers=headers, params=params)
            
            if response:
                data = response.json()
                all_data.extend(data)
                total_count = int(response.headers.get('X-Total-Count', 0))
                
                if len(data) < limit or len(all_data) >= total_count:
                    break
                
                offset += limit
            else:
                break
        
        return all_data


def get_token():
    url = f"https://{tenant}.api.identitynow.com/oauth/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        logger.info(f"Autenticando no tenant {tenant}")
        response = requests.post(url, data=payload, verify=certifi.where())
        if response.status_code == 200:
            logger.info("Autenticado com sucesso")
            return response.json()['access_token']
        else:
            logger.error(f"Erro ao obter token de acesso: {response.status_code} - {response.json()}")
    except Exception as error:
        logger.error(f"Erro ao tentar autenticar no tenant {tenant}: {error}")
    return None


def flatten_dict(d, parent_key='', sep='.'):
    """
    Função para "achatar" dicionários aninhados, utilizando dot notation para chaves.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def clean_newlines(value):
    """
    Remove todos os caracteres de nova linha de um valor.
    """
    if isinstance(value, str):
        return value.replace('\n', ' ').replace('\r', ' ')
    return value


def json_to_csv(json_data, csv_file):
    # Verificar se os dados são uma lista de dicionários
    if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
        # Achar todas as chaves, incluindo as de dicionários aninhados
        flat_data = [flatten_dict(item) for item in json_data]
        headers = set()
        for item in flat_data:
            headers.update(item.keys())
        headers = list(headers)

        # Abrir o arquivo CSV para escrita
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in flat_data:
                # Limpar caracteres de nova linha dos valores
                cleaned_item = {k: clean_newlines(v) for k, v in item.items()}
                writer.writerow(cleaned_item)
        logger.info(f"Arquivo CSV '{csv_file}' criado com sucesso.")
    else:
        logger.error("Os dados recebidos não são uma lista de dicionários.")


def generate_report(api):
    data = api.get_pending_access_request_approvals()
    if data:
        # Gerar o nome do arquivo CSV com a data atual
        csv_file = f'report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        # Converter JSON para CSV diretamente
        json_to_csv(data, csv_file)


def main():
    logger.info("Collecting report data - pending access approvals")
    token = get_token()
    if token:
        api = ApiCalls(token)
        generate_report(api)


if __name__ == "__main__":
    tenant = input("Insira o tenant (ex: acme, acme-sb): ")
    client_id = input("Insira o client id: ")
    client_secret = input("Insira o client secret: ")

    main()
