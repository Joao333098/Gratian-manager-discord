import discum
import threading
import asyncio
import time
import random
import yaml
import requests
from database.manager import Manager
from .logs_system import stats
from .token_system import tokens_index, get_id, validate_token_api, get_token_guilds

system_running = False
dm_tasks = []
db_manager = Manager()

def load_settings():
    try:
        with open('config/settings.yaml', encoding='utf-8') as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)

        # Load message
        with open('config/message.txt', encoding='utf-8') as f:
            settings['message'] = f.read()

        # Mask link logic
        if settings.get('mask_link'):
            for line in settings['message'].split():
                if "https://discord.gg/aresrp" in line:
                    new_link = settings.get('mask', '')
                    new_message = settings['message'].replace(line, f"<{new_link}> ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||")
                    settings['message'] = new_message

        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}

def get_emoji(settings):
    return random.choice(settings.get('reactions', ['👍', '❤️', '😂', '😮', '😢', '😡']))

class BotInstance:
    def __init__(self, db, settings) -> None:
        self.db = db
        self.token = settings['token']
        self.settings = settings
        self.message = settings['message']

    def check_user(self, userid):
        bot_id = get_id(self.token)
        return self.db.check_user(bot_id, str(userid))

    def add_user(self, userid):
        bot_id = get_id(self.token)
        return self.db.add_user(bot_id, str(userid))

async def start_dm_system(token):
    global system_running, tokens_index
    settings = load_settings()

    try:
        user_id = get_id(token)
        stats.add_log(f"🚀 Iniciando self-bot para: {user_id}")

        if token not in tokens_index:
            tokens_index[token] = {'is_sleeping': False, 'is_rate_limit': False, 'reply_users_sience': {}}
            stats.add_log(f"📝 Token {user_id} adicionado ao índice")

        if not validate_token_api(token):
            stats.add_log(f"❌ Token inválido ou expirado: {user_id}")
            return

        stats.add_log(f"✅ Token válido confirmado: {user_id}")

        nav_settings = settings.copy()
        nav_settings["token"] = token
        nav = BotInstance(db_manager, nav_settings)

        def run_self_bot():
            try:
                bot = discum.Client(token=token, log=False)

                def AfterReadySupp(resp, bot):
                    if resp.event.ready_supplemental:
                        try:
                            guilds = []
                            r = get_token_guilds(token)
                            for g in r:
                                guilds.append(g['id'])
                            bot.gateway.subscribeToGuildEvents(wait=1, guildIDs=guilds, token=token)
                        except:
                            stats.add_log(f"⚠️ Erro ao configurar eventos para {user_id}")

                        stats.add_log(f"✅ Self-bot conectado: {user_id}")

                        try:
                            bot.gateway.setStatus("idle")
                            bot.gateway.setCustomStatus("Sistema Ativo")
                        except:
                            pass

                bot.gateway.command({"function": AfterReadySupp, "params":{"bot":bot}})

                @bot.gateway.command
                def handle_event(resp):
                    if not system_running:
                        return

                    if resp.event.message:
                        if settings.get('event_message', True):
                            m = resp.parsed.auto()
                            user = m['author']
                            if "guild_id" in m:
                                user['guild_id'] = m['guild_id']
                            if "channel_id" in m:
                                user['channel_id'] = m['channel_id']
                            if "id" in m:
                                user['message_id'] = m['id']
                            if "content" in m:
                                user['content'] = m['content']
                            if "bot" in m:
                                user['bot'] = m['bot']

                            sience_to_dm(bot, nav, user, settings)

                    elif resp.event.voice_state_updated:
                        if settings.get('event_voice', True):
                            m = resp.parsed.auto()
                            if 'member' in m:
                                user = m['member']['user']
                                if "guild_id" in m:
                                    user['guild_id'] = m['guild_id']
                                if "channel_id" in m:
                                    user['channel_id'] = m['channel_id']
                                if "id" in m:
                                    user['message_id'] = m['id']
                                if "content" in m:
                                    user['content'] = m['content']
                                if "bot" in m:
                                    user['bot'] = m['bot']

                                sience_to_dm(bot, nav, user, settings)

                bot.gateway.run(auto_reconnect=True)

            except Exception as e:
                stats.add_log(f"❌ Erro no self-bot {user_id}: {str(e)}")

        discord_thread = threading.Thread(target=run_self_bot, daemon=True)
        discord_thread.start()

        await asyncio.sleep(3)
        stats.add_log(f"🎯 Self-bot {user_id} iniciado com sucesso")

    except Exception as e:
        stats.add_log(f"❌ Erro crítico no token {token[:20]}: {str(e)}")

def sience_to_dm(bot, nav, user, settings):
    global tokens_index

    user_token = bot._Client__user_token
    bot_user_id = get_id(user_token)

    if user['id'] == bot_user_id:
        return

    if "bot" in user and user['bot']:
        return

    if user_token not in tokens_index:
        tokens_index[user_token] = {'is_sleeping': False, 'is_rate_limit': False, 'reply_users_sience': {}}

    if not tokens_index[user_token]['is_sleeping']:
        if "guild_id" in user:
            if not nav.check_user(user['id']):
                if nav.add_user(user['id']):
                    tokens_index[user_token]['is_sleeping'] = True

                    try:
                        newDM = bot.createDM([user['id']]).json()["id"]
                    except:
                        stats.add_log(f"❌ {bot_user_id} - Caiu para verificação")
                        tokens_index[user_token]['is_sleeping'] = False
                        return bot.gateway.close()

                    r = bot.gateway.request.call(newDM, video=True)
                    bot.typingAction(newDM)
                    stats.increment_captured()

                    try:
                        guild = bot.gateway.session.guild(user["guild_id"]).name
                    except:
                        guild = None

                    stats.add_log(f"✅ {bot_user_id} - Capturado: {user['username']} | Servidor: {guild} | Cooldown: {settings.get('dm_cooldown', 3)}s")

                    _thread = threading.Thread(target=between_callback, args=(user_token, settings))
                    _thread.start()
    else:
        # stats.add_log(f"⏱️ {bot_user_id} - Em cooldown, aguardando...")
        pass

    if not "guild_id" in user:
        newDM = user['channel_id']

        if not user['id'] in stats.dms_sends:
            stats.add_dm_send(user['id'])
            if settings.get('dm_typing'):
                bot.typingAction(newDM)
            if settings.get('dm_reaction'):
                bot.addReaction(newDM, user['message_id'], get_emoji(settings))
            if settings.get('dm_reply'):
                bot.reply(newDM, user['message_id'], settings['message'])
            else:
                bot.sendMessage(newDM, settings['message'])
            if settings.get('dm_pin'):
                bot.pinMessage(newDM, user['message_id'])

            stats.increment_deliver()
            stats.add_log(f"✅ {bot_user_id} - DM enviada para: {user['username']}")
            tokens_index[user_token]['reply_users_sience'][user['id']] = []

        elif user['id'] in stats.dms_sends:
            bot.addReaction(newDM, user['message_id'], get_emoji(settings))
            for msg in settings.get('reply_messages', []):
                if not user['id'] in tokens_index[user_token]['reply_users_sience']:
                    tokens_index[user_token]['reply_users_sience'][user['id']] = []
                if not msg in tokens_index[user_token]['reply_users_sience'][user['id']]:
                    bot.typingAction(newDM)
                    time.sleep(random.randint(1, 2))
                    bot.reply(newDM, user['message_id'], msg)
                    tokens_index[user_token]['reply_users_sience'][user['id']].append(msg)
                    break

def between_callback(token, settings):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(reset_sleep_token(token, settings))
    loop.close()

async def reset_sleep_token(token, settings):
    cooldown_time = settings.get("dm_cooldown", 3)
    if cooldown_time > 0:
        bot_user_id = get_id(token)
        await asyncio.sleep(cooldown_time)

        if token in tokens_index:
            tokens_index[token]['is_sleeping'] = False
        else:
            stats.add_log(f"⚠️ {bot_user_id} - Token não encontrado no índice ao finalizar cooldown")
