import sqlite3
from pathlib import Path

# Usando pathlib para garantir compatibilidade entre macOS e Windows
DB_PATH = Path(__file__).parent / "instagram_bot.db"

def init_db():
    """Cria o banco de dados e a tabela de controle se não existirem."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela para registrar os comentários que já foram processados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios_processados (
            comment_id TEXT PRIMARY KEY,
            username TEXT,
            post_id TEXT,
            texto TEXT,
            data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def ja_foi_processado(comment_id):
    """Verifica se o ID do comentário já existe no banco."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM comentarios_processados WHERE comment_id = ?', (str(comment_id),))
    resultado = cursor.fetchone()
    
    conn.close()
    return resultado is not None

def salvar_comentario_processado(comment_id, username, post_id, texto):
    """Salva o comentário no banco de dados para não processar de novo."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO comentarios_processados (comment_id, username, post_id, texto)
            VALUES (?, ?, ?, ?)
        ''', (str(comment_id), username, str(post_id), texto))
        conn.commit()
    except sqlite3.IntegrityError:
        # Caso o ID já exista por algum motivo, ignora o erro de duplicidade
        pass
    finally:
        conn.close()