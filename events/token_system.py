import base64
import requests
import sys
from .logs_system import stats

tokens_index = {}

def get_id(token):
    """Extract the user ID from a Discord token"""
    try:
        if not token or '.' not in token:
            raise ValueError("Token inválido")

        token_part = token.split('.')[0]
        missing_padding = len(token_part) % 4
        if missing_padding:
            token_part += '=' * (4 - missing_padding)

        decoded = base64.b64decode(token_part).decode('utf-8')
        if not decoded.isdigit():
            raise ValueError("ID decodificado não é numérico")

        return decoded
    except Exception as e:
        raise ValueError(f"Erro ao extrair ID do token: {str(e)}")

def validate_token_api(token):
    """Validar token via API do Discord"""
    if not token or len(token) < 20:
        return False

    headers = {
        'authorization': token,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-discord-locale': 'en-US',
        'x-debug-options': 'bugReporterEnabled'
    }

    try:
        try:
            user_id = get_id(token)
            if not user_id.isdigit():
                return False
        except:
            return False

        response = requests.get('https://discord.com/api/v10/users/@me', headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if 'id' in data and 'username' in data:
                return True
        elif response.status_code == 401:
            return False
        elif response.status_code == 403:
            return True
        elif response.status_code == 429:
            stats.add_log(f"⚠️ Rate limit na validação do token {user_id}")
            return True
        else:
            stats.add_log(f"⚠️ Status desconhecido {response.status_code} para token {user_id}")
            return False

    except requests.exceptions.Timeout:
        stats.add_log(f"⚠️ Timeout na validação do token - assumindo válido")
        return True
    except requests.exceptions.ConnectionError:
        stats.add_log(f"⚠️ Erro de conexão na validação - assumindo válido")
        return True
    except Exception as e:
        stats.add_log(f"❌ Erro na validação do token: {str(e)}")
        return False

def get_token_guilds(token):
    headers = {
        'authorization': token,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers)
        return response.json()
    except:
        return []
