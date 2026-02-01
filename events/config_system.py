import yaml
import os

def load_settings():
    try:
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f) or {}

        try:
            with open('config/message.txt', 'r', encoding='utf-8') as f:
                settings['message'] = f.read()
        except FileNotFoundError:
            settings['message'] = ""

        # Mask link logic (preserved from original)
        if settings.get('mask_link'):
            for line in settings['message'].split():
                if "https://discord.gg/aresrp" in line:
                    new_link = settings.get('mask', '')
                    new_message = settings['message'].replace(line, f"<{new_link}> ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||")
                    settings['message'] = new_message

        return settings
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return {}

def save_settings(settings):
    try:
        # Don't save 'message' key to yaml, it goes to txt
        yaml_settings = {k: v for k, v in settings.items() if k != 'message'}
        with open('config/settings.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(yaml_settings, f)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

def save_message(message_content):
    try:
        with open('config/message.txt', 'w', encoding='utf-8') as f:
            f.write(message_content)
        return True
    except Exception as e:
        print(f"Erro ao salvar mensagem: {e}")
        return False

def load_message():
    try:
        with open('config/message.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""
