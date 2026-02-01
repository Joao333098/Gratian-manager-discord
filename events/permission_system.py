import json
import os

def check_permission(user_id):
    try:
        if not os.path.exists('data/config.json'):
            return False

        with open('data/config.json', 'r') as f:
            config = json.load(f)

        # Load permissions if file exists
        owners = []
        permitted = []
        if os.path.exists('data/perm.json'):
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)
            owners = perm.get('owners', [])
            permitted = perm.get('permitted', [])

        return user_id == config.get('ownerID') or str(user_id) in owners or str(user_id) in permitted
    except Exception as e:
        print(f"Erro ao verificar permissões: {e}")
        return False

def is_owner(user_id):
    try:
        if not os.path.exists('data/config.json'):
            return False

        with open('data/config.json', 'r') as f:
            config = json.load(f)

        owners = []
        if os.path.exists('data/perm.json'):
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)
            owners = perm.get('owners', [])

        return user_id == config.get('ownerID') or str(user_id) in owners
    except Exception as e:
        print(f"Erro ao verificar se é dono: {e}")
        return False

def get_owners():
    try:
        if os.path.exists('data/perm.json'):
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)
            return perm.get('owners', [])
        return []
    except:
        return []

def get_permitted():
    try:
        if os.path.exists('data/perm.json'):
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)
            return perm.get('permitted', [])
        return []
    except:
        return []

def add_permission(user_id, perm_type):
    try:
        os.makedirs('data', exist_ok=True)
        if not os.path.exists('data/perm.json'):
            perm = {"owners": [], "permitted": []}
        else:
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)

        user_id = str(user_id)

        if perm_type == "owner":
            if user_id not in perm.get('owners', []):
                perm.setdefault('owners', []).append(user_id)
        else:
            if user_id not in perm.get('permitted', []):
                perm.setdefault('permitted', []).append(user_id)

        with open('data/perm.json', 'w') as f:
            json.dump(perm, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao adicionar permissão: {e}")
        return False

def remove_permission(user_id):
    try:
        if not os.path.exists('data/perm.json'):
            return False

        with open('data/perm.json', 'r') as f:
            perm = json.load(f)

        user_id = str(user_id)
        removed = False

        if user_id in perm.get('owners', []):
            perm['owners'].remove(user_id)
            removed = True
        elif user_id in perm.get('permitted', []):
            perm['permitted'].remove(user_id)
            removed = True

        if removed:
            with open('data/perm.json', 'w') as f:
                json.dump(perm, f, indent=4)

        return removed
    except Exception as e:
        print(f"Erro ao remover permissão: {e}")
        return False
