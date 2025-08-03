import os
import requests
from supabase import create_client, Client

# --- CONFIGURAÇÃO ---
# Estas variáveis serão configuradas como "Secrets" no GitHub, não diretamente no código.
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # Esta é a chave 'service_role'

# Conecta ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lista de categorias que queremos pesquisar no Mercado Livre (MLB)
CATEGORIAS = {
    "Celulares": "MLB1055",
    "Informática": "MLB1648",
    "Eletrônicos": "MLB1000",
    "Games": "MLB1144"
}

def coletar_e_salvar_tendencias():
    print("Iniciando a coleta de dados do Mercado Livre...")

    # Primeiro, limpa a tabela para não acumular dados velhos
    print("Limpando dados antigos da tabela 'produtos'...")
    supabase.table('produtos').delete().gt('id', 0).execute() # Deleta tudo

    produtos_para_inserir = []

    for nome_cat, id_cat in CATEGORIAS.items():
        api_url = f"https://api.mercadolibre.com/trends/MLB/{id_cat}"
        print(f"Buscando categoria: {nome_cat} ({id_cat})")
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            trends = response.json()

            for i, trend in enumerate(trends):
                produto = {
                    'nome': trend['keyword'],
                    'ranking': i + 1,
                    'link_busca': trend['url'],
                    'plataforma': 'Mercado Livre',
                    'categoria_id': id_cat
                }
                produtos_para_inserir.append(produto)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a categoria {nome_cat}: {e}")
            continue # Pula para a próxima categoria se der erro

    if produtos_para_inserir:
        print(f"Inserindo {len(produtos_para_inserir)} novos produtos no Supabase...")
        data, count = supabase.table('produtos').insert(produtos_para_inserir).execute()
        print("Dados inseridos com sucesso!")
    else:
        print("Nenhum produto encontrado para inserir.")

if __name__ == "__main__":
    coletar_e_salvar_tendencias()
