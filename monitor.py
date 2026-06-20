import time
import httpx
from database import ja_foi_processado, salvar_comentario_processado
from dotenv import dotenv_values

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

# Configurações da sua IA Local
IA_BASE_API = config.get("IA_BASE_API")
MODELO_ATUAL = None  

def obter_resposta_da_ia(texto_comentario):
    """Obtém o modelo disponível e consome o stream de texto da API."""
    global MODELO_ATUAL
    
    # 1. Pega o modelo se ainda não estiver definido na memória
    if not MODELO_ATUAL:
        try:
            response_models = httpx.post(f"{IA_BASE_API}/models", timeout=10.0)
            if response_models.status_code == 200:
                modelos_disponiveis = response_models.json()
                if modelos_disponiveis and len(modelos_disponiveis) > 0:
                    MODELO_ATUAL = modelos_disponiveis[0]
                    print(f"🧠 Modelo de IA selecionado: {MODELO_ATUAL}")
                else:
                    print("❌ A API não retornou nenhum modelo na lista.")
                    return None
            else:
                print(f"❌ Erro ao buscar modelos. Status: {response_models.status_code}")
                return None
        except Exception as e:
            print(f"❌ Falha de conexão ao buscar modelos (Verifique o Firewall): {e}")
            return None

    # 2. Prepara os dados para gerar a resposta
    payload = {
        "prompt": texto_comentario,
        "model": MODELO_ATUAL
    }
    
    texto_completo = ""
    
    try:
        # 3. Conecta no stream de resposta
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", f"{IA_BASE_API}/stream", json=payload) as response:
                if response.status_code != 200:
                    print(f"❌ Erro na geração de texto: Status {response.status_code}")
                    return None
                
                print(f"🤖 IA pensando ({MODELO_ATUAL}): ", end="", flush=True)
                
                # Consome o stream aos poucos
                for chunk in response.iter_text():
                    texto_completo += chunk
                    print(chunk, end="", flush=True)
                    
                print("\n") # Quebra de linha ao fim do stream
                
    except Exception as e:
        print(f"\n❌ Falha ao conectar no stream da IA: {e}")
        return None
        
    return texto_completo.strip()


def monitor_latest_comments(cl, check_interval_seconds=300):
    """Loop principal que vasculha o Instagram e interage com a IA."""
    print("✅ Módulo de monitoramento iniciado com sucesso!")
    
    # ID numérico da sua própria conta logada
    my_user_id = cl.user_id 

    while True:
        try:
            print(f"\n🕒 [{time.strftime('%X')}] Buscando novos comentários...")
            
            # Pega as 3 últimas postagens (ajuste se quiser analisar mais)
            ultimos_posts = cl.user_medias(my_user_id, amount=3)
            
            for post in ultimos_posts:
                # Pega os últimos 10 comentários do post
                comentarios = cl.media_comments(post.id, amount=10)
                
                for comentario in comentarios:
                    comment_id = comentario.pk 
                    
                    # Ignora se o comentário for seu mesmo
                    if comentario.user.pk == my_user_id:
                        continue
                        
                    # Consulta o SQLite: Se já lemos, pula
                    if ja_foi_processado(comment_id):
                        continue
                        
                    # Achou um comentário novo e não respondido
                    autor = comentario.user.username
                    texto = comentario.text
                    
                    print(f"🔔 NOVO COMENTÁRIO!")
                    print(f"Post ID: {post.id} | Autor: @{autor}")
                    print(f"Texto: {texto}")
                    print("-" * 40)
                    
                    # Envia o texto do comentário para a IA responder
                    resposta_ia = obter_resposta_da_ia(texto)
                    
                    # Se a IA retornou um texto com sucesso
                    if resposta_ia:
                        try:
                            print(f"🚀 Enviando resposta para o Instagram...")
                            # cl.media_comment_reply(post.id, comment_id, resposta_ia)
                            cl.media_comment(post.id, resposta_ia, replied_to_comment_id=comment_id)
                            print("✅ Resposta publicada com sucesso!")
                            
                            # Só salva no banco de dados se a resposta foi postada sem erros
                            salvar_comentario_processado(
                                comment_id=comment_id,
                                username=autor,
                                post_id=post.id,
                                texto=texto
                            )
                            print(f"💾 Comentário {comment_id} arquivado no SQLite.")
                            
                        except Exception as e:
                            print(f"❌ Erro ao tentar postar a resposta no Instagram: {e}")
                    else:
                        print("⚠️ IA falhou em retornar um texto. Tentaremos de novo na próxima rodada.")
            
            # Rate limit para proteger a conta
            print(f"⏳ Aguardando {check_interval_seconds} segundos para o próximo ciclo...")
            time.sleep(check_interval_seconds)

        except Exception as e:
            print(f"❌ Erro geral durante o loop de monitoramento: {e}")
            # Pausa de segurança em caso de erro da API do Instagram
            time.sleep(60)