import discord
import requests
import yaml
from events.log_system import stats
from events.token_system import get_all_tokens

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Voltar", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        from functions.painel import ModernPainelView
        from events.permission_system import is_owner
        from events.runner_system import system_running

        client = interaction.client

        token_count = len(get_all_tokens())

        ping = round(client.latency * 1000)
        status_color = "Online" if ping < 200 else "Instável" if ping < 500 else "Alto Delay"

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
        await interaction.response.edit_message(embed=embed, view=view)

class EmojiManager:
    def __init__(self, guild):
        self.guild = guild
        self.emoji_urls = {
            "tokens": "https://cdn.discordapp.com/emojis/1184123456789012345.png",
            "message": "https://cdn.discordapp.com/emojis/1184123456789012346.png",
            "settings": "https://cdn.discordapp.com/emojis/1184123456789012347.png",
            "logs": "https://cdn.discordapp.com/emojis/1184123456789012348.png",
            "permissions": "https://cdn.discordapp.com/emojis/1184123456789012349.png",
            "start": "https://cdn.discordapp.com/emojis/1184123456789012350.png",
            "stop": "https://cdn.discordapp.com/emojis/1184123456789012351.png",
            "back": "https://cdn.discordapp.com/emojis/1184123456789012352.png",
        }
        self.backup_urls = {
            "tokens": "https://i.imgur.com/vKjPy7q.png",
            "message": "https://i.imgur.com/8mGhT3w.png",
            "settings": "https://i.imgur.com/nF4mX8s.png",
            "logs": "https://i.imgur.com/kL3nM7t.png",
            "permissions": "https://i.imgur.com/xR9sK4p.png",
            "start": "https://i.imgur.com/yH6vN2w.png",
            "stop": "https://i.imgur.com/zQ8tP5x.png",
            "back": "https://i.imgur.com/mK7nL9q.png",
        }
        self.created_emojis = {}

    async def download_image(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except:
            return None

    async def create_emoji(self, name, url):
        try:
            image_data = await self.download_image(url)
            if not image_data and name in self.backup_urls:
                image_data = await self.download_image(self.backup_urls[name])

            if not image_data:
                return None

            emoji = await self.guild.create_custom_emoji(
                name=f"panel_{name}",
                image=image_data,
                reason="Emoji para painel de controle"
            )

            self.created_emojis[name] = str(emoji)
            return str(emoji)

        except discord.HTTPException as e:
            stats.add_log(f"Erro ao criar emoji {name}: {str(e)}")
            return None
        except Exception as e:
            stats.add_log(f"Erro geral ao criar emoji {name}: {str(e)}")
            return None

    async def get_emoji(self, name):
        if name in self.created_emojis:
            return self.created_emojis[name]

        for emoji in self.guild.emojis:
            if emoji.name == f"panel_{name}":
                self.created_emojis[name] = str(emoji)
                return str(emoji)

        emoji_str = await self.create_emoji(name, self.emoji_urls.get(name, ""))
        if emoji_str:
            return emoji_str

        fallback_emojis = {
            "tokens": "🗝️",
            "message": "💬",
            "settings": "⚙️",
            "logs": "📊",
            "permissions": "🔒",
            "start": "🚀",
            "stop": "🛑",
            "back": "🔙"
        }
        return fallback_emojis.get(name, "⚙️")

    async def setup_all_emojis(self):
        stats.add_log("Configurando emojis customizados...")
        for name in self.emoji_urls.keys():
            emoji = await self.get_emoji(name)
            stats.add_log(f"Emoji {name}: {emoji}")
        stats.add_log("Configuração de emojis concluída!")

emoji_manager = None
