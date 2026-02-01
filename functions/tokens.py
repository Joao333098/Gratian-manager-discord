import discord
from functions.utils import BackButton
from events.token_system import get_id

class TokenButton(discord.ui.Button):
    def __init__(self, emoji="🗝️"):
        super().__init__(label="Tokens", style=discord.ButtonStyle.secondary, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        try:
            with open('config/tokens.txt', 'r') as f:
                tokens = f.read().splitlines()
        except FileNotFoundError:
            tokens = []

        embed = discord.Embed(
            title="🔑 Gerenciamento de Tokens",
            description="Gerencie seus tokens abaixo:"
        )

        for i, token in enumerate(tokens, 1):
            if not token.strip(): continue
            masked_token = f"{token[:20]}...{token[-20:]}" if len(token) > 40 else token
            embed.add_field(name=f"Token {i}", value=f"`{masked_token}`", inline=False)

        buttons = discord.ui.View()
        buttons.add_item(AddTokenButton())
        buttons.add_item(RemoveTokenButton())
        buttons.add_item(ClearTokensButton())
        buttons.add_item(BackButton())

        await interaction.response.edit_message(embed=embed, view=buttons)

class AddTokenButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Adicionar", style=discord.ButtonStyle.success, emoji="✅")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddTokenModal())

class RemoveTokenButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Remover", style=discord.ButtonStyle.danger, emoji="❌")

    async def callback(self, interaction: discord.Interaction):
        try:
            with open('config/tokens.txt', 'r') as f:
                tokens = [token.strip() for token in f.readlines() if token.strip()]
        except FileNotFoundError:
            tokens = []

        if not tokens:
            embed = discord.Embed(
                title="❌ Nenhum Token",
                description="Não há tokens para remover!"
            )
            buttons = discord.ui.View()
            buttons.add_item(BackButton())
            await interaction.response.edit_message(embed=embed, view=buttons)
            return

        embed = discord.Embed(
            title="🗑️ Remover Tokens",
            description="Selecione os tokens que deseja remover:"
        )

        view = TokenRemovalView(tokens)
        await interaction.response.edit_message(embed=embed, view=view)

class ClearTokensButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Limpar", style=discord.ButtonStyle.danger, emoji="🧹")

    async def callback(self, interaction: discord.Interaction):
        with open('config/tokens.txt', 'w') as f:
            f.write("")

        embed = discord.Embed(
            title="✅ Sucesso",
            description="Tokens limpos com sucesso!"
        )

        buttons = discord.ui.View()
        buttons.add_item(BackButton())

        await interaction.response.edit_message(embed=embed, view=buttons)

class AddTokenModal(discord.ui.Modal, title='Adicionar Token'):
    token = discord.ui.TextInput(label='Token', placeholder='Cole o token aqui')

    async def on_submit(self, interaction: discord.Interaction):
        token = self.token.value.strip()
        if token:
            with open('config/tokens.txt', 'a') as f:
                f.write(f"{token}\n")
            await interaction.response.send_message(f"Token adicionado com sucesso!", ephemeral=True)
        else:
             await interaction.response.send_message(f"Token vazio!", ephemeral=True)

class TokenRemovalView(discord.ui.View):
    def __init__(self, tokens):
        super().__init__()
        self.tokens = tokens

        options = []
        for i, token in enumerate(tokens):
            masked_token = f"{token[:15]}...{token[-15:]}" if len(token) > 30 else token
            try:
                user_id = get_id(token)
            except:
                user_id = "Desconhecido"
            options.append(discord.SelectOption(
                label=f"Token {i+1}",
                description=f"ID: {user_id} | {masked_token}",
                value=str(i)
            ))

        if len(options) <= 25:
            self.add_item(TokenSelectionDropdown(tokens, options))
        else:
            for page in range(0, len(options), 25):
                page_options = options[page:page+25]
                self.add_item(TokenSelectionDropdown(tokens, page_options, page // 25))

        self.add_item(RemoveAllTokensButton())
        self.add_item(BackToTokensButton())

class TokenSelectionDropdown(discord.ui.Select):
    def __init__(self, tokens, options, page=0):
        self.tokens = tokens
        self.page = page
        placeholder = f"Selecione tokens para remover (Página {page+1})" if page > 0 else "Selecione tokens para remover"
        super().__init__(placeholder=placeholder, options=options, max_values=min(len(options), 25))

    async def callback(self, interaction: discord.Interaction):
        selected_indices = [int(value) for value in self.values]
        tokens_to_remove = [self.tokens[i] for i in selected_indices if i < len(self.tokens)]

        embed = discord.Embed(
            title="⚠️ Confirmar Remoção",
            description=f"Você está prestes a remover **{len(tokens_to_remove)}** tokens:"
        )

        for i, token in enumerate(tokens_to_remove):
            try:
                user_id = get_id(token)
            except:
                user_id = "?"
            masked = f"{token[:15]}...{token[-15:]}" if len(token) > 30 else token
            embed.add_field(
                name=f"Token {i+1}",
                value=f"ID: `{user_id}`\nToken: `{masked}`",
                inline=True
            )

        view = ConfirmRemovalView(tokens_to_remove)
        await interaction.response.edit_message(embed=embed, view=view)

class ConfirmRemovalView(discord.ui.View):
    def __init__(self, tokens_to_remove):
        super().__init__()
        self.tokens_to_remove = tokens_to_remove

    @discord.ui.button(label="✅ Confirmar Remoção", style=discord.ButtonStyle.danger)
    async def confirm_removal(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            with open('config/tokens.txt', 'r') as f:
                all_tokens = [token.strip() for token in f.readlines() if token.strip()]

            remaining_tokens = [token for token in all_tokens if token not in self.tokens_to_remove]

            with open('config/tokens.txt', 'w') as f:
                for token in remaining_tokens:
                    f.write(f"{token}\n")

            embed = discord.Embed(
                title="✅ Tokens Removidos",
                description=f"**{len(self.tokens_to_remove)}** tokens foram removidos com sucesso!\n\n"
                           f"**Tokens restantes:** {len(remaining_tokens)}",
                color=discord.Color.green()
            )

            buttons = discord.ui.View()
            buttons.add_item(BackToTokensButton())

            await interaction.response.edit_message(embed=embed, view=buttons)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro",
                description=f"Erro ao remover tokens: {str(e)}"
            )
            buttons = discord.ui.View()
            buttons.add_item(BackToTokensButton())
            await interaction.response.edit_message(embed=embed, view=buttons)

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel_removal(self, interaction: discord.Interaction, button: discord.ui.Button):
        token_button = TokenButton()
        await token_button.callback(interaction)

class RemoveAllTokensButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🗑️ Remover Todos", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚠️ ATENÇÃO - Remover Todos os Tokens",
            description="**Você está prestes a remover TODOS os tokens!**\n\n"
                       "⚠️ Esta ação é **irreversível**\n"
                       "🚨 O sistema ficará sem tokens para funcionar\n\n"
                       "Tem certeza que deseja continuar?",
            color=discord.Color.red()
        )

        view = ConfirmRemoveAllView()
        await interaction.response.edit_message(embed=embed, view=view)

class ConfirmRemoveAllView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="🗑️ SIM, REMOVER TODOS", style=discord.ButtonStyle.danger)
    async def confirm_remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('config/tokens.txt', 'w') as f:
            f.write("")

        embed = discord.Embed(
            title="✅ Todos os Tokens Removidos",
            description="Todos os tokens foram removidos com sucesso!\n\n"
                       "⚠️ **Sistema sem tokens** - adicione novos tokens para usar o sistema",
            color=discord.Color.green()
        )

        buttons = discord.ui.View()
        buttons.add_item(AddTokenButton())
        buttons.add_item(BackToTokensButton())
        await interaction.response.edit_message(embed=embed, view=buttons)

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel_remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        token_button = TokenButton()
        await token_button.callback(interaction)

class BackToTokensButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="↩️ Voltar aos Tokens", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        token_button = TokenButton()
        await token_button.callback(interaction)
