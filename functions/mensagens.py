import discord
import threading
import time
import random
import asyncio
import requests
import discum
from functions.utils import BackButton
from events.token_system import get_id, get_token_guilds, get_all_tokens
from events.log_system import stats
from events.config_system import load_message, save_message

class MessageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Mensagem", style=discord.ButtonStyle.secondary, emoji="💬")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📝 Gerenciamento de Mensagem",
            description="Gerencie a mensagem do bot abaixo:"
        )
        await interaction.response.edit_message(embed=embed, view=MessagePanel())

class MessagePanel(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.load_current_message()

    def load_current_message(self):
        self.current_message = load_message() or "Nenhuma mensagem definida"

    @discord.ui.button(label="Ver Atual", style=discord.ButtonStyle.secondary, emoji="👀")
    async def view_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📝 Mensagem Atual",
            description=self.current_message
        )
        view = discord.ui.View()
        view.add_item(BackButton())
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Editar", style=discord.ButtonStyle.primary, emoji="📝")
    async def edit_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MessageModal(self.current_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Nova", style=discord.ButtonStyle.success, emoji="📄")
    async def new_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MessageModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="🗂️")
    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        save_message("")
        self.current_message = ""

        embed = discord.Embed(
            title="✅ Sucesso",
            description="Mensagem deletada com sucesso!"
        )

        buttons = discord.ui.View()
        buttons.add_item(BackButton())

        await interaction.response.edit_message(embed=embed, view=buttons)

    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.secondary, emoji="◀️", row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        back_btn = BackButton()
        await back_btn.callback(interaction)

class MessageModal(discord.ui.Modal, title="Gerenciar Mensagem"):
    def __init__(self, current_message=""):
        super().__init__()
        self.message = discord.ui.TextInput(
            label="Mensagem",
            style=discord.TextStyle.paragraph,
            placeholder="Digite a mensagem aqui...",
            default=current_message,
            required=True
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        save_message(self.message.value)
        await interaction.response.send_message("✅ Mensagem atualizada com sucesso!", ephemeral=True)

class ServerMessageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Mensagem Server", style=discord.ButtonStyle.secondary, emoji="📢")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 Mensagem para Servidores",
            description="**Envie uma mensagem para todos os servidores**\n\n"
                       "🎯 **Como funciona:**\n"
                       "• O bot enviará a mensagem em todos os canais onde tem permissão\n"
                       "• Funciona apenas em servidores onde o bot está presente\n"
                       "• Respeitará as permissões de cada canal\n\n"
                       "⚠️ **Atenção:** Use com responsabilidade!",
            color=discord.Color.orange()
        )

        buttons = discord.ui.View()
        buttons.add_item(SendServerMessageButton())
        buttons.add_item(BackButton())

        await interaction.response.edit_message(embed=embed, view=buttons)

class SendServerMessageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Enviar Mensagem", style=discord.ButtonStyle.primary, emoji="📤")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ServerMessageModal())

class ServerMessageModal(discord.ui.Modal, title='📢 Enviar Mensagem para Servidores'):
    def __init__(self):
        super().__init__()

        self.message_content = discord.ui.TextInput(
            label='Mensagem',
            style=discord.TextStyle.paragraph,
            placeholder='Digite a mensagem que será enviada para todos os servidores...',
            required=True,
            max_length=2000
        )
        self.add_item(self.message_content)

        self.bio_content = discord.ui.TextInput(
            label='Bio dos Self-bots (Opcional)',
            style=discord.TextStyle.paragraph,
            placeholder='Digite a bio que será definida nos self-bots (deixe vazio para não alterar)',
            required=False,
            max_length=190
        )
        self.add_item(self.bio_content)

        self.delay_seconds = discord.ui.TextInput(
            label='Delay entre envios (segundos)',
            placeholder='Tempo de espera entre cada canal (recomendado: 2-5)',
            default='3',
            required=True,
            max_length=3
        )
        self.add_item(self.delay_seconds)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            delay = int(self.delay_seconds.value)
            if delay < 1:
                delay = 1
            elif delay > 60:
                delay = 60
        except ValueError:
            delay = 3

        message = self.message_content.value
        bio = self.bio_content.value.strip() if self.bio_content.value else None

        embed = discord.Embed(
            title="⚠️ Confirmar Envio",
            description=f"**Você está prestes a enviar esta mensagem para TODOS os servidores:**\n\n"
                       f"```\n{message}\n```\n\n"
                       f"**Delay:** {delay} segundos entre envios\n"
                       f"**Bio:** {'`' + bio + '`' if bio else 'Não será alterada'}\n"
                       f"**Esta ação não pode ser desfeita!**",
            color=discord.Color.red()
        )

        view = ConfirmServerMessageView(message, delay, bio)
        await interaction.response.edit_message(embed=embed, view=view)

class ConfirmServerMessageView(discord.ui.View):
    def __init__(self, message, delay, bio=None):
        super().__init__()
        self.message = message
        self.delay = delay
        self.bio = bio

    @discord.ui.button(label="✅ CONFIRMAR ENVIO", style=discord.ButtonStyle.danger)
    async def confirm_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="📤 Enviando Mensagens...",
                description="Iniciando envio para todos os servidores. Aguarde...",
                color=discord.Color.yellow()
            ),
            view=discord.ui.View()
        )

        thread = threading.Thread(target=send_to_all_servers, args=(self.message, self.delay, interaction, self.bio))
        thread.start()

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        server_button = ServerMessageButton()
        await server_button.callback(interaction)

def send_to_all_servers(message, delay, interaction, bio=None):
    try:
        tokens = get_all_tokens()

        if not tokens:
            stats.add_log("❌ Nenhum self-bot (token) disponível para envio")
            return

        stats.add_log(f"📢 Iniciando envio via self-bots para servidores com {len(tokens)} tokens")

        total_sent = 0
        total_errors = 0
        servers_reached = set()

        for token in tokens:
            try:
                user_id = get_id(token)
                stats.add_log(f"🤖 Usando self-bot: {user_id}")

                bot = discum.Client(token=token, log=False)

                if bio:
                    try:
                        headers = {
                            'authorization': token,
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'content-type': 'application/json'
                        }

                        bio_url = 'https://discord.com/api/v10/users/@me'
                        bio_payload = {'bio': bio}

                        bio_response = requests.patch(bio_url, headers=headers, json=bio_payload)

                        if bio_response.status_code == 200:
                            stats.add_log(f"📝 Self-bot {user_id} - Bio atualizada: {bio[:30]}{'...' if len(bio) > 30 else ''}")
                        elif bio_response.status_code == 403:
                            stats.add_log(f"⚠️ Self-bot {user_id} - Sem permissão para alterar bio")
                        elif bio_response.status_code == 429:
                            stats.add_log(f"⚠️ Self-bot {user_id} - Rate limited ao alterar bio")
                        else:
                            stats.add_log(f"❌ Self-bot {user_id} - Erro {bio_response.status_code} ao alterar bio")

                        time.sleep(2)

                    except Exception as e:
                        stats.add_log(f"❌ Self-bot {user_id} - Erro ao alterar bio: {str(e)}")

                guilds = get_token_guilds(token)

                if not guilds:
                    stats.add_log(f"⚠️ Self-bot {user_id} não está em nenhum servidor")
                    continue

                stats.add_log(f"🔍 Self-bot {user_id} - {len(guilds)} servidores encontrados")

                for guild in guilds:
                    try:
                        guild_id = guild['id']
                        guild_name = guild.get('name', 'Servidor Desconhecido')

                        if guild_id in servers_reached:
                            continue
                        servers_reached.add(guild_id)

                        headers = {
                            'authorization': token,
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'content-type': 'application/json'
                        }

                        try:
                            channels_response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/channels', headers=headers)
                            if channels_response.status_code != 200:
                                stats.add_log(f"⚠️ Não foi possível obter canais de {guild_name}")
                                continue

                            channels = channels_response.json()
                        except Exception as e:
                            stats.add_log(f"❌ Erro ao obter canais de {guild_name}: {str(e)}")
                            continue

                        text_channels = []
                        for channel in channels:
                            if channel.get('type') == 0:
                                if not channel.get('nsfw', False):
                                    text_channels.append(channel)

                        if not text_channels:
                            stats.add_log(f"⚠️ Nenhum canal de texto encontrado em {guild_name}")
                            continue

                        channel_sent = False

                        priority_channels = [ch for ch in text_channels if any(word in ch.get('name', '').lower() for word in ['geral', 'general', 'chat', 'principal'])]
                        if priority_channels:
                            channels_to_try = priority_channels[:1]
                        else:
                            channels_to_try = text_channels[:1]

                        for channel in channels_to_try:
                            try:
                                channel_id = channel['id']
                                channel_name = channel.get('name', 'canal')

                                typing_url = f'https://discord.com/api/v10/channels/{channel_id}/typing'
                                requests.post(typing_url, headers=headers)

                                time.sleep(random.uniform(1, 3))

                                send_url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
                                payload = {'content': message}

                                response = requests.post(send_url, headers=headers, json=payload)

                                if response.status_code == 200:
                                    total_sent += 1
                                    channel_sent = True
                                    stats.add_log(f"✅ Self-bot {user_id} enviou em #{channel_name} ({guild_name})")
                                    break
                                elif response.status_code == 403:
                                    stats.add_log(f"⚠️ Self-bot {user_id} sem permissão em #{channel_name} ({guild_name})")
                                    continue
                                elif response.status_code == 429:
                                    stats.add_log(f"⚠️ Self-bot {user_id} rate limited em {guild_name}")
                                    time.sleep(5)
                                    continue
                                else:
                                    stats.add_log(f"❌ Erro {response.status_code} em #{channel_name} ({guild_name})")
                                    continue

                            except Exception as e:
                                stats.add_log(f"❌ Erro ao enviar em #{channel_name}: {str(e)}")
                                continue

                            time.sleep(delay)

                        if not channel_sent:
                            stats.add_log(f"⚠️ Self-bot {user_id} não conseguiu enviar em {guild_name}")
                            total_errors += 1

                    except Exception as e:
                        total_errors += 1
                        stats.add_log(f"❌ Erro no servidor {guild_name}: {str(e)}")
                        continue

                time.sleep(random.uniform(3, 7))

            except Exception as e:
                stats.add_log(f"❌ Erro crítico com self-bot {token[:20]}: {str(e)}")
                total_errors += 1
                continue

        stats.add_log(f"📊 Envio concluído:")
        stats.add_log(f"✅ Mensagens enviadas: {total_sent}")
        stats.add_log(f"🏠 Servidores alcançados: {len(servers_reached)}")
        stats.add_log(f"❌ Erros: {total_errors}")
        if bio:
            stats.add_log(f"📝 Bio definida em {len(tokens)} self-bots")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            embed = discord.Embed(
                title="✅ Envio Concluído!",
                description=f"**Resultado do envio:**\n\n"
                           f"📤 **Mensagens enviadas:** {total_sent}\n"
                           f"🏠 **Servidores alcançados:** {len(servers_reached)}\n"
                           f"❌ **Erros:** {total_errors}\n"
                           f"{'📝 **Bio atualizada:** ' + str(len(tokens)) + ' self-bots' if bio else ''}\n\n"
                           f"📋 **Verifique os logs para mais detalhes**",
                color=discord.Color.green()
            )

            view = discord.ui.View()
            view.add_item(BackButton())

            loop.run_until_complete(
                interaction.edit_original_response(embed=embed, view=view)
            )
            loop.close()

        except Exception as e:
            stats.add_log(f"❌ Erro ao atualizar mensagem de confirmação: {str(e)}")

    except Exception as e:
        stats.add_log(f"❌ Erro crítico no envio para servidores: {str(e)}")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            embed = discord.Embed(
                title="❌ Erro no Envio",
                description=f"Erro crítico durante o envio:\n```{str(e)}```",
                color=discord.Color.red()
            )

            view = discord.ui.View()
            view.add_item(BackButton())

            loop.run_until_complete(
                interaction.edit_original_response(embed=embed, view=view)
            )
            loop.close()

        except:
            pass
