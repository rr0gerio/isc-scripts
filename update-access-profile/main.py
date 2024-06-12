import requests
import certifi
import csv

# Função para obter o token de acesso
def obter_token(tenant, client_id, client_secret):
    url = f'https://{tenant}.api.identitynow.com/oauth/token?grant_type=client_credentials'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Levanta um erro se a requisição falhar
    return response.json()['access_token']

# Função para atualizar perfis de acesso
def atualizar_perfil(tenant, access_token, profile_id):
    url = f'https://{tenant}.api.identitynow.com/v3/access-profiles/{profile_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json-patch+json',
        'Accept': 'application/json'
    }
    payload = [
        {
            "op": "replace",
            "path": "/enabled",
            "value": True,
            
        }
    ]
    response = requests.patch(url, headers=headers, json=payload, verify=certifi.where())
    if response.status_code == 200:
        print(f"Perfil {profile_id} atualizado com sucesso.")
    else:
        print(f"Falha ao atualizar o perfil {profile_id}. Status: {response.status_code}, Response: {response.text}")

# Configurações
tenant = input("insira o tenant (ex: acme-sb): ")
client_id = input("insira o client_id: ")
client_secret = input("insira o client_secret: ")
csv_file_path = 'ap.csv'


# Obtém o token de acesso
token = obter_token(tenant, client_id, client_secret)

# Lê o arquivo CSV e atualiza os perfis
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        profile_id = row['Access Profile ID']
        atualizar_perfil(token, profile_id)
