import sys
import json
import csv

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

def json_to_csv(json_file, csv_file):
    # Abrir o arquivo JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Verificar se os dados são uma lista de dicionários
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        # Achar todas as chaves, incluindo as de dicionários aninhados
        flat_data = [flatten_dict(item) for item in data]
        headers = set()
        for item in flat_data:
            headers.update(item.keys())
        headers = list(headers)

        # Abrir o arquivo CSV para escrita
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in flat_data:
                writer.writerow(item)
        print(f"Arquivo CSV '{csv_file}' criado com sucesso.")
    else:
        print("O arquivo JSON não é uma lista de dicionários.")

if __name__ == "__main__":
    # Verificar se o arquivo JSON foi passado como argumento
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    csv_file = json_file.replace('.json', '.csv')
    
    json_to_csv(json_file, csv_file)
