import csv
import requests
import yaml
import json
import logging
import certifi
from datetime import datetime

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
                return response.json()
            else:
                logger.error(f"Erro {response.status_code} para {url}: {response.json()}")
        except Exception as error:
            logger.error(f"Erro na requisição para {url}: {error}")
        return None

    def get_source_id(self, source_name):
        url = '/v3/sources'
        params = {
            "filters": f'name eq "{source_name}"'
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        return self._request("GET", endpoint=url, headers=headers, data=None, params=params)[0].get("id")

    def get_entitlement_id(self, source_id, entitlement_name):
        name_convert = entitlement_name.replace("&", "%26") if "&" in entitlement_name else entitlement_name
        url = '/beta/entitlements'
        params = {
            "filters": f'source.id eq "{source_id}" and name eq "{name_convert}"'
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        response = self._request("GET", endpoint=url, headers=headers, data=None, params=params)
        if response:
            return response[0].get("id")
        else:
            return None

    def get_identity_id(self, mail):
        url = '/v3/search'
        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.token}"}
        payload = {
            "queryType": "SAILPOINT",
            "indices": ["identities"],
            "query": {"query": f"attributes.email:{mail}"},
            "queryResultFilter": {"includes": ["id", "name", "displayName"]}
        }
        logger.info(f"Obtendo ID da identidade para o email '{mail}'.")
        response = self._request("POST", url, headers, json.dumps(payload))
        if response:
            return response[0]
        else:
            logger.error(f"Erro ao obter ID da identidade para o email '{mail}'.")
            return None

    def create_access_profile(self, payload):
        url = "/v3/access-profiles"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        logger.info(f"Criando perfil de acesso '{payload['name']}'.")
        response = self._request("POST", url, headers, json.dumps(payload))
        if response:
            return response.get('id')
        else:
            logger.error(f"Erro ao criar perfil de acesso '{payload['name']}'.")
            return None

    def create_governance_group(self, group_name, description, owner_id, owner_name):
        url = '/beta/workgroups'
        payload = {
            "owner": {
                "type": "IDENTITY",
                "id": owner_id,
                "name": owner_name
            },
            "name": group_name,
            "description": description
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        logger.info(f"Criando grupo de governança '{group_name}'.")
        response = self._request("POST", url, headers=headers, data=json.dumps(payload))
        if response:
            logger.info(f"Grupo de governança '{group_name}' criado com sucesso.")
            return response.get('id')
        else:
            logger.error(f"Erro ao criar grupo de governança '{group_name}'.")
            return None

    def add_members_to_group(self, workgroup_id, members):
        url = f'/beta/workgroups/{workgroup_id}/members/bulk-add'
        payload = [{"type": "IDENTITY", "id": member['id'], "name": member['name']} for member in members]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        logger.info(f"Adicionando membros ao grupo de governança '{workgroup_id}'.")
        response = self._request("POST", url, headers=headers, data=json.dumps(payload))
        if response:
            logger.info(f"Membros adicionados ao grupo de governança '{workgroup_id}' com sucesso.")
        else:
            logger.error(f"Erro ao adicionar membros ao grupo de governança '{workgroup_id}'.")


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


def read_csv(file_path, key_column):
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                key = row[key_column]
                if key not in data:
                    data[key] = []
                data[key].append(row)
        logger.info(f"Arquivo CSV '{file_path}' lido e processado com sucesso.")
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise e
    except KeyError as e:
        logger.error(f"Coluna chave '{key_column}' não encontrada no arquivo CSV.")
        raise e
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo CSV: {e}")
        raise e
    return data


def create_approval_schemes(api, access_profiles, access_profile_name):
    # Obter todos os owners distintos dos perfis de acesso
    owners = set(access_profile['AccessProfileOwner'] for access_profile in access_profiles)
    logger.info(f"Encontrados {len(owners)} owners distintos para o perfil de acesso '{access_profile_name}'.")

    if len(owners) > 1:
        group_name = f"{access_profile_name} - Owners Aprovadores"
        description = f"Governance group for {access_profile_name}"

        # Obter informações do primeiro owner para criar o grupo
        logger.info(f"Criando grupo de governança '{group_name}' para múltiplos owners.")
        owner_info = api.get_identity_id(next(iter(owners)))
        owner_id = owner_info.get("id")
        owner_name = owner_info.get("name")
        workgroup_id = api.create_governance_group(group_name, description, owner_id, owner_name)

        # Adicionar todos os owners ao grupo de governança
        members = []
        for owner in owners:
            member_info = api.get_identity_id(owner)
            members.append({"id": member_info['id'], "name": member_info['name']})
            logger.info(f"Adicionando owner '{member_info['name']}' ao grupo de governança '{group_name}'.")

        api.add_members_to_group(workgroup_id, members)
        logger.info(f"Grupo de governança '{group_name}' criado e membros adicionados com sucesso.")

        return [{"approverType": "MANAGER","approverId": None},{"approverType": "GOVERNANCE_GROUP", "approverId": workgroup_id}]
    else:
        logger.info(f"Apenas um owner encontrado para o perfil de acesso '{access_profile_name}'. Usando o tipo de aprovador 'OWNER'.")
        return [{"approverType": "MANAGER","approverId": None},{"approverType": "OWNER"}]



def treat_access_profile(api, access_profile_name, access_profiles):
    entitlements = []
    source_id = api.get_source_id(access_profiles[0]['SourceName'])
    for access_profile in access_profiles:
        entitlement_id = api.get_entitlement_id(source_id, access_profile['Entitlement'])
        if entitlement_id:
            if entitlement_id not in entitlements:
                entitlements.append(entitlement_id)
        else:
            logger.error(f"Entitlement {access_profile['Entitlement']} não foi encontrado. Pulando criacao do access profile {access_profile_name}")
            return

    owner_info = api.get_identity_id(access_profiles[0]['AccessProfileOwner'])
    owner_id = owner_info.get("id")
    owner_name = owner_info.get("name")

    

    approval_schemes = create_approval_schemes(api, access_profiles, access_profile_name)

    payload = {
        "name": access_profile_name,
        "description": f"Grupo de acesso Suzano para o {access_profile_name}",
        "enabled": True,
        "owner": {
            "type": "IDENTITY",
            "id": owner_id,
            "name": owner_name
        },
        "source": {
            "id": source_id,
            "type": "SOURCE",
            "name": access_profiles[0]['SourceName']
        },
        "entitlements": [{'id': entitlement, 'type': 'ENTITLEMENT'} for entitlement in entitlements],
        "requestable": True,
        "accessRequestConfig": {
            "commentsRequired": True,
            "denialCommentsRequired": True,
            "approvalSchemes": approval_schemes
        },
        "revocationRequestConfig": {
            "approvalSchemes": []
        },
        "segments": [],
        "provisioningCriteria": None
    }

    access_profile_id = api.create_access_profile(payload)
    if access_profile_id:
        logger.info(f"Access Profile '{access_profile_name}' created successfully with ID: {access_profile_id}.")
    else:
        logger.error(f"Failed to create Access Profile '{access_profile_name}'.")


def main():
    logger.info("Starting Bulk Operation - Access Profile")
    token = get_token()
    api = ApiCalls(token)

    access_profiles_data = read_csv("access_profiles.csv", "AccessProfileName")

    for access_profile_name, access_profiles in access_profiles_data.items():
        treat_access_profile(api, access_profile_name, access_profiles)

    logger.info("Bulk Operation Completed.")


if __name__ == "__main__":
    #tenant = input("insira o tenant (ex: acme,acme-sb): ")
    #client_id = input("insira o client id: ")
    #client_secret = input("insira o client secret: ")

    tenant = "suzano"
    client_id = "499aa9fd87a040e08c078792f2b74047"
    client_secret = "feb6c07b06ebf6bbcb32c1e26f08665525626822704690af422225fe5e9e6cf2"
    main()
