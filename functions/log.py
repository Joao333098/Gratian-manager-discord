import discord
import time
from events.logs_system import stats
from functions.utils import BackButton
from events.system_manager import system_running

class ViewLogsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Logs", style=discord.ButtonStyle.secondary, emoji="📊")

    async def callback(self, interaction: discord.Interaction):
        try:
            with open('config/tokens.txt', 'r') as f:
                token_count = len([line for line in f.readlines() if line.strip()])
        except:
            token_count = 0

        guilds_count = len(interaction.client.guilds) if interaction.client and hasattr(interaction.client, 'guilds') else 0

        embed = discord.Embed(
            title="📊 Estatísticas do Sistema",
            description="**Status em Tempo Real**",
            color=discord.Color.green() if system_running else discord.Color.red()
        )

        embed.add_field(
            name="📈 Contadores Principais",
            value=f"```\n📤 DMs Enviadas: {stats.dms_deliver}\n👥 Usuários Capturados: {stats.dms_captured}\n🔑 Tokens Ativos: {token_count}\n🏠 Servidores Conectados: {guilds_count}\n```",
            inline=False
        )

        embed.add_field(
            name="🔥 Sistema",
            value=f"```\n{'🟢 Online' if system_running else '🔴 Offline'}\n⏰ {time.strftime('%H:%M:%S')}\n📋 Logs: {len(stats.log_messages)}\n```",
            inline=False
        )

        important_logs = [log for log in stats.log_messages[-10:] if any(word in log for word in ['iniciado', 'parado', 'erro', 'conectado'])]
        if important_logs:
            embed.add_field(
                name="📋 Últimas Atividades",
                value=f"```\n{chr(10).join(important_logs[-5:])}\n```",
                inline=False
            )

        view = discord.ui.View()
        view.add_item(RefreshLogsButton())
        view.add_item(BackButton())

        await interaction.response.edit_message(embed=embed, view=view)

class RefreshLogsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Atualizar", style=discord.ButtonStyle.primary, emoji="🔃")

    async def callback(self, interaction: discord.Interaction):
        logs_button = ViewLogsButton()
        await logs_button.callback(interaction)
