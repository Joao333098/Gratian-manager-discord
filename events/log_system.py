import threading
import time
import os

class stats:
    dms_deliver = 0
    dms_captured = 0
    dms_sends = []
    log_messages = []
    _lock = threading.Lock()
    client = None
    system_running = False

    @classmethod
    def add_log(cls, message):
        with cls._lock:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            formatted_message = f"[{timestamp}] {message}"
            cls.log_messages.append(formatted_message)
            if len(cls.log_messages) > 100:
                cls.log_messages.pop(0)

            cls.update_title()

    @classmethod
    def set_client(cls, client):
        cls.client = client

    @classmethod
    def set_system_status(cls, is_running):
        cls.system_running = is_running

    @classmethod
    def update_title(cls):
        try:
            if os.path.exists('config/tokens.txt'):
                with open('config/tokens.txt', 'r') as f:
                    token_count = len([line for line in f.readlines() if line.strip()])
            else:
                token_count = 0
        except:
            token_count = 0

        guilds_count = len(cls.client.guilds) if cls.client and hasattr(cls.client, 'guilds') else 0

        # Using simple print as in original, assuming this runs in terminal
        # ANSI escape codes for clearing screen might not work everywhere but keeping original behavior
        print(f'\033[2J\033[H[📤 Enviados {cls.dms_deliver}, 👥 Capturados {cls.dms_captured}, 🔑 Tokens {token_count}, 🏠 Servidores {guilds_count}]')

        status_emoji = "🟢" if cls.system_running else "🔴"
        print(f'[{status_emoji} Sistema: {"Rodando" if cls.system_running else "Parado"} | 📊 Logs: {len(cls.log_messages)} | ⏰ {time.strftime("%H:%M:%S")}]')
        print('━' * 80)

    @classmethod
    def increment_deliver(cls):
        with cls._lock:
            cls.dms_deliver += 1

    @classmethod
    def increment_captured(cls):
        with cls._lock:
            cls.dms_captured += 1

    @classmethod
    def add_dm_send(cls, user_id):
        with cls._lock:
            if user_id not in cls.dms_sends:
                cls.dms_sends.append(user_id)
