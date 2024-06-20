import requests
import json
from datetime import datetime, timezone, timedelta
import os
from getpass import getpass

log_file = "event_log.txt"

def send_request(event_id, token, past_date, tenant):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Enviando requisição para o evento {event_id}...\n")

    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Bearer {token}"
    }

    data = [
        {"op": "replace", "path": "/completionStatus", "value": "Success"},
        {"op": "replace", "path": "/completed", "value": past_date}
    ]

    response = requests.patch(f"https://{tenant}.api.identitynow.com/beta/task-status/{event_id}", headers=headers, json=data)

    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Requisição enviada para o evento {event_id}.\n")

def get_oauth_token(client_id, client_secret, tenant):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Obtendo token OAuth...\n")

    response = requests.post(f'https://{tenant}.api.identitynow.com/oauth/token',
                             params={'grant_type': 'client_credentials',
                                     'client_id': client_id,
                                     'client_secret': client_secret})

    token = response.json()["access_token"]

    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Token OAuth obtido.\n")

    return token

def process_pending_events(token, tenant):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Obtendo eventos pendentes...\n")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f'https://{tenant}.api.identitynow.com/beta/task-status/pending-tasks', headers=headers)

    events = response.json()

    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Eventos pendentes obtidos.\n")

    print("JSON dos eventos:")
    print(json.dumps(events, indent=4))

    if not events:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [ERROR] Nenhum evento pendente foi retornado.\n")
        return

    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Processando eventos pendentes...\n")

    for event in events:
        event_id = event["id"]
        unique_name = event.get("uniqueName", "")
        if not event_id:
            with open(log_file, "a") as f:
                f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [WARNING] Evento sem ID encontrado. Ignorando...\n")
            continue
        if unique_name == "Cloud Account Aggregation":
            past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            send_request(event_id, token, past_date, tenant)

    with open(log_file, "a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')} [INFO] Eventos pendentes processados.\n")

# Obter credenciais do usuário
tenant = input("Insira o Tenant: ")
client_id = input("Insira o client_id: ")
client_secret = getpass("Insira o secret_id: ")

# Obter token OAuth
token = get_oauth_token(client_id, client_secret, tenant)

# Processar eventos pendentes
process_pending_events(token, tenant)
