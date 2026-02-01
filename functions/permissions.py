import discord
import json
from functions.utils import BackButton

def is_owner(user_id):
    try:
        with open('data/config.json', 'r') as f:
            config = json.load(f)

        with open('data/perm.json', 'r') as f:
            perm = json.load(f)

        return user_id == config.get('ownerID') or str(user_id) in perm.get('owners', [])
    except Exception as e:
        print(f"Erro ao verificar se é dono: {e}")
        return False

def check_permission(user_id):
    try:
        with open('data/config.json', 'r') as f:
            config = json.load(f)

        with open('data/perm.json', 'r') as f:
            perm = json.load(f)

        return user_id == config.get('ownerID') or str(user_id) in perm.get('owners', []) or str(user_id) in perm.get('permitted', [])
    except Exception as e:
        print(f"Erro ao verificar permissões: {e}")
        return False

class PermissionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Permissões", style=discord.ButtonStyle.secondary, emoji="🔐")

    async def callback(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Você não tem permissão para gerenciar permissões."
            )
            buttons = discord.ui.View()
            buttons.add_item(BackButton())
            await interaction.response.edit_message(embed=embed, view=buttons)
            return

        embed = discord.Embed(
            title="🔒 Gerenciamento de Permissões",
            description="Gerencie quem pode acessar o painel de controle."
        )

        try:
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)

            owners = perm.get('owners', [])
            permitted = perm.get('permitted', [])

            if owners:
                embed.add_field(name="👑 Donos adicionais", value="\n".join([f"<@{owner}> ({owner})" for owner in owners]), inline=False)
            else:
                embed.add_field(name="👑 Donos adicionais", value="Nenhum", inline=False)

            if permitted:
                embed.add_field(name="🔑 Usuários permitidos", value="\n".join([f"<@{user}> ({user})" for user in permitted]), inline=False)
            else:
                embed.add_field(name="🔑 Usuários permitidos", value="Nenhum", inline=False)
        except:
            embed.add_field(name="Erro", value="Não foi possível carregar as permissões.", inline=False)

        buttons = PermissionPanel()
        await interaction.response.edit_message(embed=embed, view=buttons)

class PermissionPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Adicionar", style=discord.ButtonStyle.success, emoji="➕")
    async def add_permission(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddPermissionModal())

    @discord.ui.button(label="Remover", style=discord.ButtonStyle.danger, emoji="➖")
    async def remove_permission(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('data/perm.json', 'r') as f:
            perm = json.load(f)

        owners = perm.get('owners', [])
        permitted = perm.get('permitted', [])

        if not owners and not permitted:
            embed = discord.Embed(
                title="❌ Erro",
                description="Não há usuários com permissão para remover."
            )
            buttons = discord.ui.View()
            buttons.add_item(BackButton())
            await interaction.response.edit_message(embed=embed, view=buttons)
            return

        await interaction.response.send_modal(RemovePermissionModal())

    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        back_btn = BackButton()
        await back_btn.callback(interaction)

class AddPermissionModal(discord.ui.Modal, title='Adicionar Permissão'):
    user_id = discord.ui.TextInput(label='ID do Usuário', placeholder='Digite o ID do usuário')
    permission_type = discord.ui.TextInput(
        label='Tipo de Permissão',
        placeholder='Digite "owner" para dono ou "user" para usuário comum',
        default="user"
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id.value.strip()
        perm_type = self.permission_type.value.strip().lower()

        if not user_id.isdigit():
            await interaction.response.send_message("ID inválido. O ID deve conter apenas números.", ephemeral=True)
            return

        if perm_type not in ["owner", "user"]:
            await interaction.response.send_message('Tipo de permissão inválido. Use "owner" ou "user".', ephemeral=True)
            return

        try:
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)

            if perm_type == "owner":
                if user_id not in perm.get('owners', []):
                    perm.setdefault('owners', []).append(user_id)
            else:
                if user_id not in perm.get('permitted', []):
                    perm.setdefault('permitted', []).append(user_id)

            with open('data/perm.json', 'w') as f:
                json.dump(perm, f, indent=2)

            await interaction.response.send_message(f"Permissão adicionada com sucesso para o ID {user_id}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao adicionar permissão: {str(e)}", ephemeral=True)

class RemovePermissionModal(discord.ui.Modal, title='Remover Permissão'):
    user_id = discord.ui.TextInput(label='ID do Usuário', placeholder='Digite o ID do usuário a ser removido')

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id.value.strip()

        if not user_id.isdigit():
            await interaction.response.send_message("ID inválido. O ID deve conter apenas números.", ephemeral=True)
            return

        try:
            with open('data/perm.json', 'r') as f:
                perm = json.load(f)

            if user_id in perm.get('owners', []):
                perm['owners'].remove(user_id)
                removed = True
            elif user_id in perm.get('permitted', []):
                perm['permitted'].remove(user_id)
                removed = True
            else:
                removed = False

            if removed:
                with open('data/perm.json', 'w') as f:
                    json.dump(perm, f, indent=2)
                await interaction.response.send_message(f"Permissão removida com sucesso para o ID {user_id}!", ephemeral=True)
            else:
                await interaction.response.send_message(f"O ID {user_id} não possui permissões para serem removidas.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao remover permissão: {str(e)}", ephemeral=True)
