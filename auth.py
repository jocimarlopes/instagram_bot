import os
from instagrapi import Client
from dotenv import dotenv_values

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

# Credenciais (Idealmente, use variáveis de ambiente (.env))
USERNAME = config.get("USERNAME")
PASSWORD = config.get("PASSWORD")
SESSION_FILE = 'session.json'
    
def setup_instagram_client():
    cl = Client()
    
    # Simular um dispositivo específico ajuda a evitar bloqueios
    cl.delay_range = [1, 3] # Pausas aleatórias entre 1 e 3 segundos

    try:
        # Tenta carregar a sessão salva
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            
            # Verifica se a sessão carregada ainda é válida
            cl.get_timeline_feed()
            print("Sessão carregada com sucesso!")
        else:
            raise Exception("Arquivo de sessão não encontrado.")
            
    except Exception as e:
        print(f"Não foi possível usar a sessão salva: {e}")
        print("Fazendo um novo login...")
        
        # Faz o login do zero
        cl.login(USERNAME, PASSWORD)
        
        # Salva a sessão para a próxima execução
        cl.dump_settings(SESSION_FILE)
        print("Novo login efetuado e sessão salva!")

    return cl

# Inicializando
# if __name__ == "__main__":
#     cl = setup_instagram_client()
    
#     # Exemplo: Pegar as informações do seu próprio perfil
#     user_info = cl.user_info_by_username(USERNAME)
#     print(f"Conectado como: {user_info.full_name} - Seguidores: {user_info.follower_count}")