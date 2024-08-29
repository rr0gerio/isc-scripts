import csv
from faker import Faker
import random

# Mapeamento de cargos por departamento
cargos_por_departamento = {
    'RH': ['Gerente de RH', 'Analista de RH', 'Coordenador de RH'],
    'Engenharia': ['Engenheiro de Software', 'Engenheiro de Sistemas', 'Arquiteto de Software'],
    'Marketing': ['Gerente de Marketing', 'Analista de Marketing', 'Coordenador de Marketing'],
    'Vendas': ['Gerente de Vendas', 'Representante de Vendas', 'Coordenador de Vendas'],
    'Finanças': ['CFO', 'Analista Financeiro', 'Contador'],
    'TI': ['Gerente de TI', 'Analista de TI', 'Suporte Técnico'],
    'Operações': ['Gerente de Operações', 'Coordenador de Operações', 'Supervisor de Operações']
}

def gerar_dados_rh(num_registros):
    if num_registros < 11:
        raise ValueError("O número de registros deve ser pelo menos 11 para garantir que cada time tenha pelo menos 10 membros.")
    
    fake = Faker('pt_BR')
    dados = []

    # Gerar todos os funcionários
    funcionarios = []
    for _ in range(num_registros):
        registro = {
            'ID do Funcionário': fake.unique.random_int(min=1000, max=9999),
            'Nome': fake.first_name(),
            'Sobrenome': fake.last_name(),
            'Email': fake.email(),
            'Telefone': fake.phone_number(),
            'Cargo': None,  # Cargo será atribuído depois
            'Departamento': None,  # Departamento será atribuído depois
            'Data de Admissão': fake.date_between(start_date='-10y', end_date='today'),
            'Salário': round(fake.random_number(digits=5, fix_len=True) * 1.1, 2),  # Salário fictício
            'Endereço': fake.street_address(),
            'Cidade': fake.city(),
            'Estado': fake.state(),
            'CEP': fake.postcode(),
            'País': fake.country(),
            'Data de Nascimento': fake.date_of_birth(minimum_age=18, maximum_age=65),
            'CPF': fake.cpf(),
            'ID do Gerente': None  # Inicialmente nenhum gerente
        }
        funcionarios.append(registro)

    # Escolher um presidente
    id_presidente = fake.unique.random_int(min=1000, max=9999)
    while any(f['ID do Funcionário'] == id_presidente for f in funcionarios):
        id_presidente = fake.unique.random_int(min=1000, max=9999)
    
    # Atualizar o cargo do presidente
    for f in funcionarios:
        if f['ID do Funcionário'] == id_presidente:
            f['Cargo'] = 'Presidente'
            break

    # Garantir que o número de gerentes é suficiente para formar equipes de pelo menos 10 membros
    num_gerentes = max(1, (num_registros // 10))  # Garantir pelo menos um gerente por time
    ids_gerentes = random.sample([f['ID do Funcionário'] for f in funcionarios if f['ID do Funcionário'] != id_presidente], k=num_gerentes)
    
    # Garantir que cada time tenha pelo menos 10 membros e todos no mesmo departamento
    for gerente_id in ids_gerentes:
        gerente = next(f for f in funcionarios if f['ID do Funcionário'] == gerente_id)
        departamento = fake.random_element(elements=('RH', 'Engenharia', 'Marketing', 'Vendas', 'Finanças', 'TI', 'Operações'))
        
        # Atualizar o departamento e cargo do gerente
        gerente['Departamento'] = departamento
        gerente['Cargo'] = fake.random_element(elements=cargos_por_departamento[departamento])
        
        equipe = [f for f in funcionarios if f['ID do Gerente'] == gerente_id]
        
        # Garantir que a equipe tenha pelo menos 10 membros
        while len(equipe) < 10:
            # Encontrar funcionários que ainda não têm gerente
            sem_gerente = [f for f in funcionarios if f['ID do Gerente'] is None]
            if sem_gerente:
                subordinado = random.choice(sem_gerente)
                subordinado['ID do Gerente'] = gerente_id
                subordinado['Departamento'] = departamento
                subordinado['Cargo'] = fake.random_element(elements=cargos_por_departamento[departamento])
                equipe.append(subordinado)
            else:
                break  # Se não há mais funcionários sem gerente, parar a alocação

    # Atribuir um gerente a cada funcionário
    for funcionario in funcionarios:
        if funcionario['ID do Funcionário'] == id_presidente:
            continue
        
        if funcionario['ID do Gerente'] is None:
            # Selecionar um gerente aleatório que não seja o próprio funcionário e do mesmo departamento
            possiveis_gerentes = [f['ID do Funcionário'] for f in funcionarios if f['ID do Funcionário'] != funcionario['ID do Funcionário'] and f['ID do Funcionário'] in ids_gerentes and f['Departamento'] == funcionario['Departamento']]
            if possiveis_gerentes:
                gerente_id = random.choice(possiveis_gerentes)
                funcionario['ID do Gerente'] = gerente_id
                funcionario['Cargo'] = fake.random_element(elements=cargos_por_departamento[funcionario['Departamento']])

    # Atualizar o departamento e cargos dos funcionários conforme seus gerentes
    for funcionario in funcionarios:
        if funcionario['ID do Gerente']:
            gerente = next(f for f in funcionarios if f['ID do Funcionário'] == funcionario['ID do Gerente'])
            funcionario['Departamento'] = gerente['Departamento']
            funcionario['Cargo'] = fake.random_element(elements=cargos_por_departamento[funcionario['Departamento']])
    
    dados.extend(funcionarios)

    # Escrever os dados gerados em um novo arquivo CSV
    arquivo_saida = 'dados_rh_com_gerentes.csv'
    with open(arquivo_saida, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)
    
    print(f"Dados gerados e salvos em {arquivo_saida}")

if __name__ == "__main__":
    num_registros = int(input("Digite o número de registros a serem gerados: "))
    gerar_dados_rh(num_registros)
