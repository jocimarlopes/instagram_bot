from auth import setup_instagram_client
from monitor import monitor_latest_comments
from database import init_db
from random import randint

MIN_CHECK_INTERVAL_SECONDS = 600  # 10 minutos
MAX_CHECK_INTERVAL_SECONDS = 1800  # 30 minutos

def main():
    print("🚀 Iniciando o Bot do Instagram com Integração de IA...")

    # 1. Inicializa o banco de dados SQLite (garante que a tabela existe)
    print("Verificando banco de dados...")
    init_db()

    # 2. Faz o login no Instagram ou carrega a sessão salva (auth.py)
    print("Autenticando no Instagram...")
    cliente_insta = setup_instagram_client()

    # 3. Inicia o loop infinito de monitoramento (monitor.py)
    # Definido para rodar a cada 300 segundos (5 minutos) para evitar bloqueios
    INTERVAL_SECONDS = randint(MIN_CHECK_INTERVAL_SECONDS, MAX_CHECK_INTERVAL_SECONDS)
    monitor_latest_comments(cliente_insta, check_interval_seconds=INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Sistema encerrado pelo usuário (Ctrl+C).")
    except Exception as e:
        print(f"\n❌ Ocorreu um erro fatal: {e}")