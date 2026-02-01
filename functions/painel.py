import discord
import time
import asyncio
from events.logs_system import stats
from events.system_manager import start_dm_system, system_running, dm_tasks
from events.token_system import validate_token_api, get_id
from functions.tokens import TokenButton
from functions.mensagem import MessageButton, ServerMessageButton
from functions.settings import SettingsButton
from functions.log import ViewLogsButton
from functions.permissions import PermissionButton, check_permission, is_owner
from functions.utils import BackButton

class StartButton(discord.ui.Button):
    def __init__(self, emoji="🚀"):
        super().__init__(label="Iniciar Sistema", style=discord.ButtonStyle.success, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        global system_running, dm_tasks
        from events.system_manager import system_running as is_running # Import updated status

        try:
            if is_running:
                embed = discord.Embed(
                    title="⚠️ Sistema já está rodando",
                    description="O sistema já está em execução!"
                )
                buttons = discord.ui.View()
                buttons.add_item(StopButton())
                buttons.add_item(ViewLogsButton())
                buttons.add_item(BackButton())
                await interaction.response.edit_message(embed=embed, view=buttons)
                return

            with open('config/tokens.txt', 'r') as f:
                tokens = [token.strip() for token in f.readlines() if token.strip()]

            if not tokens:
                embed = discord.Embed(
                    title="❌ Nenhum Token Encontrado",
                    description="🔑 **Nenhum token configurado!**"
                )
                buttons = discord.ui.View()
                buttons.add_item(TokenButton())
                buttons.add_item(BackButton())
                await interaction.response.edit_message(embed=embed, view=buttons)
                return

            valid_tokens = []
            invalid_tokens = []

            embed_loading = discord.Embed(
                title="🔍 Verificando Tokens...",
                description="Validando tokens antes de iniciar o sistema...",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed_loading, ephemeral=True)

            for i, token in enumerate(tokens):
                try:
                    user_id = get_id(token)
                    embed_loading.description = f"Verificando token {i+1}/{len(tokens)}: {user_id}"
                    await interaction.edit_original_response(embed=embed_loading)

                    if validate_token_api(token):
                        valid_tokens.append(token)
                        stats.add_log(f"✅ Token válido: {user_id}")
                    else:
                        invalid_tokens.append(token[:20])
                        stats.add_log(f"❌ Token inválido: {user_id}")
                except Exception as e:
                    invalid_tokens.append(token[:20])
                    stats.add_log(f"❌ Token com erro: {token[:20]} - {str(e)}")

                await asyncio.sleep(0.5)

            if not valid_tokens:
                embed = discord.Embed(
                    title="❌ Tokens Inválidos",
                    description="🚫 **Todos os tokens são inválidos!**"
                )
                buttons = discord.ui.View()
                buttons.add_item(TokenButton())
                buttons.add_item(BackButton())
                await interaction.edit_original_response(embed=embed, view=buttons)
                return

            # Need to update system_running in events module
            from events import system_manager
            system_manager.system_running = True
            stats.add_log(f"🚀 Iniciando sistema com {len(valid_tokens)} tokens válidos")
            stats.set_system_status(True)

            embed = discord.Embed(
                title="🚀 Iniciando Sistema...",
                description=f"🔄 **Conectando self-bots...**\n\n✅ **Tokens válidos:** {len(valid_tokens)}\n❌ **Tokens inválidos:** {len(invalid_tokens)}\n\n⏳ **Aguarde a conexão...**"
            )

            await interaction.edit_original_response(embed=embed, view=discord.ui.View())

            for token in valid_tokens:
                task = asyncio.create_task(start_dm_system(token))
                dm_tasks.append(task)
                await asyncio.sleep(1)

            await asyncio.sleep(5)

            embed = discord.Embed(
                title="✅ Sistema Iniciado com Sucesso!",
                description=f"🎯 **Self-bots conectados e funcionando**\n\n🔑 **Tokens ativos:** {len(valid_tokens)}\n📊 **Status:** Sistema em execução",
                color=0x00ff00
            )

            buttons = discord.ui.View()
            buttons.add_item(StopButton())
            buttons.add_item(ViewLogsButton())
            buttons.add_item(BackButton())

            await interaction.edit_original_response(embed=embed, view=buttons)

        except Exception as e:
            stats.add_log(f"❌ Erro crítico ao iniciar sistema: {str(e)}")
            embed = discord.Embed(
                title="❌ Erro Crítico",
                description=f"🚫 **Falha ao iniciar o sistema**\n\n**Erro:** `{str(e)}`"
            )
            buttons = discord.ui.View()
            buttons.add_item(BackButton())
            if not interaction.response.is_done():
                await interaction.response.edit_message(embed=embed, view=buttons)
            else:
                await interaction.edit_original_response(embed=embed, view=buttons)

class StopButton(discord.ui.Button):
    def __init__(self, emoji="🛑"):
        super().__init__(label="Parar", style=discord.ButtonStyle.danger, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        from events import system_manager

        try:
            if not system_manager.system_running:
                embed = discord.Embed(
                    title="⚠️ Sistema já está parado",
                    description="O sistema não está em execução!"
                )
                buttons = discord.ui.View()
                buttons.add_item(StartButton())
                buttons.add_item(BackButton())
                await interaction.response.edit_message(embed=embed, view=buttons)
                return

            system_manager.system_running = False
            stats.set_system_status(False)

            for task in dm_tasks:
                if not task.done():
                    task.cancel()
            dm_tasks.clear()

            stats.add_log("🛑 Sistema parado pelo usuário")

            embed = discord.Embed(
                title="⏹️ Sistema Parado",
                description="O sistema foi parado com sucesso!"
            )

            buttons = discord.ui.View()
            buttons.add_item(StartButton())
            buttons.add_item(BackButton())

            await interaction.response.edit_message(embed=embed, view=buttons)

        except Exception as e:
            stats.add_log(f"Erro ao parar sistema: {str(e)}")
            embed = discord.Embed(
                title="❌ Erro ao Parar",
                description=f"Erro: {str(e)}"
            )
            buttons = discord.ui.View()
            buttons.add_item(BackButton())
            if not interaction.response.is_done():
                await interaction.response.edit_message(embed=embed, view=buttons)
            else:
                await interaction.edit_original_response(embed=embed, view=buttons)

class ModernStartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Iniciar Sistema", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        start_button = StartButton()
        await start_button.callback(interaction)

class ModernPainelView(discord.ui.View):
    def __init__(self, is_owner_user=False):
        super().__init__(timeout=None)
        self.is_owner_user = is_owner_user
        self.add_item(ModernStartButton())

        options = [
            discord.SelectOption(label="Gerenciar Tokens", description="Adicionar, remover ou visualizar tokens", value="tokens"),
            discord.SelectOption(label="Gerenciar Mensagem", description="Editar a mensagem do bot", value="message"),
            discord.SelectOption(label="Mensagem Server", description="Enviar mensagem em todos os servidores", value="server_message"),
            discord.SelectOption(label="Configurações", description="Alterar configurações do sistema", value="settings"),
            discord.SelectOption(label="Ver Logs", description="Visualizar logs do sistema", value="logs"),
        ]

        if self.is_owner_user:
            options.append(discord.SelectOption(label="Gerenciar Permissões", description="Gerenciar usuários permitidos", value="permissions"))

        self.add_item(ModernPainelDropdown(options))

class ModernPainelDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Selecione uma ação...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "tokens":
            await TokenButton().callback(interaction)
        elif self.values[0] == "message":
            await MessageButton().callback(interaction)
        elif self.values[0] == "server_message":
            await ServerMessageButton().callback(interaction)
        elif self.values[0] == "settings":
            await SettingsButton().callback(interaction)
        elif self.values[0] == "logs":
            await ViewLogsButton().callback(interaction)
        elif self.values[0] == "permissions":
            await PermissionButton().callback(interaction)

class PainelDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="📋 Selecione uma opção...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "tokens":
            await TokenButton().callback(interaction)
        elif self.values[0] == "message":
            await MessageButton().callback(interaction)
        elif self.values[0] == "server_message":
            await ServerMessageButton().callback(interaction)
        elif self.values[0] == "settings":
            await SettingsButton().callback(interaction)
        elif self.values[0] == "logs":
            await ViewLogsButton().callback(interaction)
        elif self.values[0] == "permissions":
            await PermissionButton().callback(interaction)

class PainelView(discord.ui.View):
    def __init__(self, is_owner_user=False):
        super().__init__(timeout=None)
        self.is_owner_user = is_owner_user
        self.add_item(TokenButton())
        self.add_item(MessageButton())
        self.add_item(SettingsButton())
        self.add_item(ViewLogsButton())
        self.add_item(StartButton())
        self.add_item(StopButton())
        if self.is_owner_user:
            self.add_item(PermissionButton())

async def painel_command(interaction: discord.Interaction, client):
    if not check_permission(interaction.user.id):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return

    try:
        with open('config/tokens.txt', 'r') as f:
            token_count = len(f.readlines())
    except:
        token_count = 0

    ping = round(client.latency * 1000)
    status_color = "Online" if ping < 200 else "Instável" if ping < 500 else "Alto Delay"

    # Import system_running from events.system_manager
    from events.system_manager import system_running

    embed = discord.Embed(
        title="Painel de Controle do Bot",
        description=f"Gerencie o sistema de controle {interaction.user.mention}",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Status do Sistema",
        value=f"**Status**: {status_color}\n**Ping**: {ping}ms\n**Tokens**: {token_count}",
        inline=True
    )

    embed.add_field(
        name="Estatísticas",
        value=f"**DMs Enviadas**: {stats.dms_deliver}\n**Usuários**: {stats.dms_captured}\n**Logs**: {len(stats.log_messages)}",
        inline=True
    )

    embed.add_field(
        name="Sistema Ativo",
        value=f"**Status**: {'Rodando' if system_running else 'Parado'}\n**Uptime**: Ativo\n**Memoria**: Normal",
        inline=True
    )

    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)

    embed.set_footer(text="Sistema de Controle - Desenvolvido pela Equipe")

    view = ModernPainelView(is_owner(interaction.user.id))
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )
