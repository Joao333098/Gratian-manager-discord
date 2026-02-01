import discord
from discord import app_commands
import threading
import time
import os
import functions.utils
from events.logs_system import stats
from functions.painel import painel_command
from functions.permissions import check_permission, is_owner

class BotController(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = BotController()
stats.set_client(client)

@client.event
async def on_ready():
    # Setup global emoji manager
    if client.guilds:
        functions.utils.emoji_manager = functions.utils.EmojiManager(client.guilds[0])
        await functions.utils.emoji_manager.setup_all_emojis()
        stats.add_log(f'🎨 Emojis customizados configurados para {client.guilds[0].name}')
    else:
        stats.add_log("⚠️ Bot não está em nenhum servidor para criar emojis customizados")

    stats.add_log(f'🤖 Bot Controller está online como {client.user.name}')

    # Check dependencies
    try:
        import discum
        stats.add_log(f'✅ Dependência discum encontrada')
    except ImportError:
        stats.add_log(f'❌ ERRO: Dependência discum não encontrada!')

    # Check config files
    config_files = ['config/tokens.txt', 'config/settings.yaml', 'config/message.txt']
    for file_path in config_files:
        if os.path.exists(file_path):
            stats.add_log(f'✅ Arquivo encontrado: {file_path}')
        else:
            stats.add_log(f'⚠️ Arquivo ausente: {file_path}')

    update_thread = threading.Thread(target=auto_update_display, daemon=True)
    update_thread.start()

    stats.add_log(f'🚀 Sistema pronto para uso! Use /painel para começar')

def auto_update_display():
    while True:
        time.sleep(5)
        stats.update_title()

@client.tree.command(name="setup_emojis", description="Configurar emojis customizados para o painel")
async def setup_emojis(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("Apenas donos podem configurar emojis customizados.", ephemeral=True)
        return

    if not functions.utils.emoji_manager:
        functions.utils.emoji_manager = functions.utils.EmojiManager(interaction.guild)

    await interaction.response.send_message("Configurando emojis customizados...", ephemeral=True)
    await functions.utils.emoji_manager.setup_all_emojis()

    embed = discord.Embed(
        title="✅ Emojis Configurados",
        description="Todos os emojis customizados foram configurados com sucesso!",
        color=discord.Color.green()
    )
    await interaction.edit_original_response(content="", embed=embed)

@client.tree.command(name="painel", description="Painel de controle do bot")
async def painel(interaction: discord.Interaction):
    await painel_command(interaction, client)
