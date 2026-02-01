import discord
import yaml
from functions.utils import BackButton
from events.config_system import load_settings, save_settings

class SettingsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Configurações", style=discord.ButtonStyle.secondary, emoji="🔧")

    async def callback(self, interaction: discord.Interaction):
        settings = load_settings()

        embed = discord.Embed(
            title="⚙️ Configurações Avançadas do Sistema",
            description="**Gerencie todas as configurações do bot de forma intuitiva**",
            color=discord.Color.orange()
        )

        config_status = f"""
**🔧 Status Atual das Configurações:**
```yaml
Auto Reply: {'✅ Ativado' if settings.get('dm_reply', False) else '❌ Desativado'}
Digitando: {'✅ Ativado' if settings.get('dm_typing', False) else '❌ Desativado'}
Reações: {'✅ Ativado' if settings.get('dm_reaction', False) else '❌ Desativado'}
Fixar Msg: {'✅ Ativado' if settings.get('dm_pin', False) else '❌ Desativado'}
Cooldown: {settings.get('dm_cooldown', 3)} segundos
```"""

        embed.add_field(name="📊 Resumo das Configurações", value=config_status, inline=False)
        embed.set_footer(text="💡 Dica: Use os menus para navegar entre as diferentes categorias de configurações")

        await interaction.response.edit_message(embed=embed, view=AdvancedSettingsPanel())

class AdvancedSettingsPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

        options = [
            discord.SelectOption(label="🤖 Comportamento DM", value="dm_behavior", emoji="🤖"),
            discord.SelectOption(label="⚡ Performance", value="performance", emoji="⚡"),
            discord.SelectOption(label="🎯 Eventos", value="events", emoji="🎯"),
            discord.SelectOption(label="🛡️ Segurança", value="security", emoji="🛡️"),
            discord.SelectOption(label="📈 Ver Todas", value="view_all", emoji="📈")
        ]
        self.add_item(SettingsDropdown(options))

    @discord.ui.button(label="🔄 Atualizar", style=discord.ButtonStyle.primary, emoji="🔄")
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        back_btn = BackButton()
        await back_btn.callback(interaction)

class SettingsDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="📋 Selecione uma categoria de configurações...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        if category == "dm_behavior": await self.show_dm_behavior(interaction)
        elif category == "performance": await self.show_performance(interaction)
        elif category == "events": await self.show_events(interaction)
        elif category == "security": await self.show_security(interaction)
        elif category == "view_all": await self.show_all_settings(interaction)

    async def show_dm_behavior(self, interaction):
        settings = load_settings()
        embed = discord.Embed(title="🤖 Configurações de Comportamento DM", description="Configure como o bot se comporta ao enviar DMs", color=discord.Color.green())
        view = DMBehaviorPanel(settings)
        await interaction.response.edit_message(embed=embed, view=view)

    async def show_performance(self, interaction):
        settings = load_settings()
        embed = discord.Embed(title="⚡ Configurações de Performance", description="Otimize a performance e velocidade do bot", color=discord.Color.yellow())
        embed.add_field(name="⏱️ Configuração Atual", value=f"**Cooldown**: `{settings.get('dm_cooldown', 3)} segundos`", inline=False)
        view = PerformancePanel()
        await interaction.response.edit_message(embed=embed, view=view)

    async def show_events(self, interaction):
        settings = load_settings()
        embed = discord.Embed(title="🎯 Configurações de Eventos", description="Configure quais eventos o bot deve monitorar", color=discord.Color.purple())
        view = EventsPanel(settings)
        await interaction.response.edit_message(embed=embed, view=view)

    async def show_security(self, interaction):
        embed = discord.Embed(title="🛡️ Configurações de Segurança", description="Configurações avançadas de segurança", color=discord.Color.red())
        view = SecurityPanel()
        await interaction.response.edit_message(embed=embed, view=view)

    async def show_all_settings(self, interaction):
        settings = load_settings()
        embed = discord.Embed(title="📋 Todas as Configurações", description="Visualização completa de todas as configurações", color=discord.Color.blue())
        config_text = "```yaml\n" + "\n".join([f"{k}: {v}" for k, v in settings.items() if k != 'message']) + "```"
        embed.add_field(name="🔧 Configurações Atuais", value=config_text, inline=False)
        view = AllSettingsPanel()
        await interaction.response.edit_message(embed=embed, view=view)

class ToggleButton(discord.ui.Button):
    def __init__(self, feature_name, setting_key, is_active):
        self.feature_name = feature_name
        self.setting_key = setting_key
        self.is_active = is_active
        super().__init__(label=f"{feature_name}: {'Ativado' if is_active else 'Desativado'}", style=discord.ButtonStyle.green if is_active else discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        self.is_active = not self.is_active
        self.label = f"{self.feature_name}: {'Ativado' if self.is_active else 'Desativado'}"
        self.style = discord.ButtonStyle.green if self.is_active else discord.ButtonStyle.danger

        settings = load_settings()
        settings[self.setting_key] = self.is_active
        save_settings(settings)

        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"Configuração '{self.feature_name}' foi {'ativada' if self.is_active else 'desativada'}.", ephemeral=True)

class DMBehaviorPanel(discord.ui.View):
    def __init__(self, settings):
        super().__init__()
        self.add_item(ToggleButton("Auto Reply", "dm_reply", settings.get('dm_reply', False)))
        self.add_item(ToggleButton("Digitando", "dm_typing", settings.get('dm_typing', False)))
        self.add_item(ToggleButton("Reações", "dm_reaction", settings.get('dm_reaction', False)))
        self.add_item(ToggleButton("Fixar Mensagem", "dm_pin", settings.get('dm_pin', False)))

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️", row=2)
    async def back_to_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

class PerformancePanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="⏱️ Ajustar Cooldown", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def adjust_cooldown(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CooldownModal())

    @discord.ui.button(label="🚀 Modo Rápido", style=discord.ButtonStyle.success, emoji="🚀")
    async def fast_mode(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_cooldown(interaction, 1, "Modo Rápido")

    @discord.ui.button(label="⚖️ Modo Balanceado", style=discord.ButtonStyle.primary, emoji="⚖️")
    async def balanced_mode(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_cooldown(interaction, 3, "Modo Balanceado")

    @discord.ui.button(label="🛡️ Modo Seguro", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def safe_mode(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_cooldown(interaction, 5, "Modo Seguro")

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️", row=2)
    async def back_to_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

    async def set_cooldown(self, interaction, cooldown_value, mode_name):
        try:
            settings = load_settings()
            settings['dm_cooldown'] = cooldown_value
            save_settings(settings)
            await interaction.response.send_message(f"✅ {mode_name} ativado! Cooldown definido para {cooldown_value} segundos.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao alterar configuração: {str(e)}", ephemeral=True)

class EventsPanel(discord.ui.View):
    def __init__(self, settings):
        super().__init__()
        self.add_item(ToggleButton("Evento de Mensagem", "event_message", settings.get('event_message', True)))
        self.add_item(ToggleButton("Evento de Voz", "event_voice", settings.get('event_voice', True)))

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️", row=1)
    async def back_to_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

class SecurityPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="🔒 Configurações em breve", style=discord.ButtonStyle.secondary, emoji="🔒", disabled=True)
    async def security_placeholder(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

class AllSettingsPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="✏️ Editar YAML", style=discord.ButtonStyle.primary, emoji="✏️")
    async def edit_yaml(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdvancedSettingsModal())

    @discord.ui.button(label="🔄 Recarregar", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def reload_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        dropdown = SettingsDropdown([])
        await dropdown.show_all_settings(interaction)

    @discord.ui.button(label="◀️ Voltar", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings_button = SettingsButton()
        await settings_button.callback(interaction)

class CooldownModal(discord.ui.Modal, title='⏱️ Ajustar Cooldown'):
    def __init__(self):
        super().__init__()
        settings = load_settings()
        self.cooldown = discord.ui.TextInput(label='Cooldown (segundos)', placeholder='Tempo entre DMs', default=str(settings.get('dm_cooldown', 3)), required=True)
        self.add_item(self.cooldown)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cooldown_value = int(self.cooldown.value)
            if cooldown_value < 1:
                await interaction.response.send_message("❌ Cooldown deve ser maior que 0 segundos!", ephemeral=True)
                return
            settings = load_settings()
            settings['dm_cooldown'] = cooldown_value
            save_settings(settings)
            status = "🟢 Seguro" if cooldown_value >= 5 else "🟡 Balanceado" if cooldown_value >= 3 else "🔴 Rápido"
            await interaction.response.send_message(f"✅ Cooldown atualizado para {cooldown_value} segundos! Status: {status}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Por favor, insira um número válido!", ephemeral=True)

class AdvancedSettingsModal(discord.ui.Modal, title='✏️ Editor Avançado de Configurações'):
    def __init__(self):
        super().__init__()
        with open('config/settings.yaml', 'r') as f: current_content = f.read()
        self.settings_content = discord.ui.TextInput(label='Configurações YAML', style=discord.TextStyle.paragraph, placeholder='Edite as configurações...', default=current_content, required=True)
        self.add_item(self.settings_content)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            yaml.safe_load(self.settings_content.value)
            with open('config/settings.yaml', 'w') as f: f.write(self.settings_content.value)
            await interaction.response.send_message("✅ Configurações atualizadas com sucesso!", ephemeral=True)
        except yaml.YAMLError as e:
            await interaction.response.send_message(f"❌ Erro no formato YAML: {str(e)}", ephemeral=True)
