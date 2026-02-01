import json
import os
from bot_controller import client

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Iniciando ...")

    try:
        with open('token.json', 'r') as f:
            token_config = json.load(f)

        token = token_config.get('token')
        if not token or token == "SEU_TOKEN_AQUI":
            print("❌ Token não configurado! Edite o arquivo token.json e adicione seu token do bot.")
            return

        client.run(token)
    except FileNotFoundError:
        print("❌ Arquivo token.json não encontrado! Crie o arquivo e adicione seu token.")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    main()
