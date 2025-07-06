const { existsSync, mkdirSync } = require("fs");
const { resolve } = require("path");

// Garantir que a pasta bots existe
const botsDir = resolve(__dirname, "bots");
if (!existsSync(botsDir)) {
  console.log("Executando 'gratian-manager init'...");
  mkdirSync(botsDir, { recursive: true });
} else {
  console.log("Pasta 'bots/' já existe. Pulando 'init'...");
}

console.log("Iniciando 'gratian-manager'...");

// ===== GRATIAN MANAGER COMPLETO =====

const { Client, GatewayIntentBits, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, StringSelectMenuBuilder, AttachmentBuilder } = require('discord.js');
const fs = require('fs-extra');
const path = require('path');
const AdmZip = require('adm-zip');
const axios = require('axios');
const { spawn, exec } = require('child_process');

class GratianManager {
    constructor() {
        this.client = new Client({ 
            intents: [
                GatewayIntentBits.Guilds, 
                GatewayIntentBits.GuildMessages, 
                GatewayIntentBits.MessageContent
            ] 
        });
        this.runningBots = new Map();
        this.botLogs = new Map();
        this.botConfigs = new Map();
        this.botsDir = path.join(__dirname, 'bots');
        this.tempDir = path.join(__dirname, 'temp');
        this.configPath = path.join(__dirname, 'config.json');
        this.versionPath = path.join(__dirname, 'version.json');

        this.setupDirectories();
        this.setupEvents();
    }

    async setupDirectories() {
        await fs.ensureDir(this.botsDir);
        await fs.ensureDir(this.tempDir);

        if (!await fs.pathExists(this.versionPath)) {
            await fs.writeJSON(this.versionPath, { version: "1.0.0" });
        }
    }

    async init() {
        console.log("🚀 Inicializando Gratian Manager...");

        if (!await fs.pathExists(this.configPath)) {
            console.log("❌ Arquivo config.json não encontrado!");
            console.log("📝 Criando arquivo de configuração...");

            const defaultConfig = {
                discord_token: "SEU_TOKEN_AQUI",
                glm4_api_key: "SUA_API_KEY_AQUI",
                glm4_endpoint: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                auto_update: true,
                update_server: "https://seuservidor.com"
            };

            await fs.writeJSON(this.configPath, defaultConfig, { spaces: 2 });
            console.log("✅ Arquivo config.json criado! Configure-o antes de continuar.");
            return;
        }

        const config = await fs.readJSON(this.configPath);

        if (config.discord_token === "SEU_TOKEN_AQUI") {
            console.log("❌ Por favor, configure o discord_token no config.json");
            return;
        }

        if (config.auto_update && config.update_server) {
            await this.checkForUpdates(config.update_server);
        }

        await this.start(config);
    }

    async checkForUpdates(updateServer) {
        try {
            console.log("🔄 Verificando atualizações...");

            const response = await axios.get(`${updateServer}/version.json`);
            const remoteVersion = response.data.version;

            const localVersion = await fs.readJSON(this.versionPath);

            if (remoteVersion !== localVersion.version) {
                console.log(`🆕 Nova versão disponível: ${remoteVersion}`);
                console.log("📦 Baixando atualização...");

                const updateResponse = await axios.get(`${updateServer}/update.zip`, {
                    responseType: 'arraybuffer'
                });

                const updatePath = path.join(this.tempDir, 'update.zip');
                await fs.writeFile(updatePath, updateResponse.data);

                console.log("📂 Extraindo atualização...");
                const zip = new AdmZip(updatePath);
                zip.extractAllTo(__dirname, true);

                await fs.writeJSON(this.versionPath, { version: remoteVersion });

                console.log("✅ Atualização concluída! Reiniciando...");
                await fs.remove(updatePath);

                process.exit(0);
            } else {
                console.log("✅ Sistema já está atualizado!");
            }
        } catch (error) {
            console.log("⚠️ Erro ao verificar atualizações:", error.message);
        }
    }

    setupEvents() {
        this.client.once('ready', () => {
            console.log(`✅ Gratian Manager iniciado como ${this.client.user.tag}`);
            console.log(`🎮 Gerenciando bots na pasta: ${this.botsDir}`);
            this.registerSlashCommands();
        });

        this.client.on('interactionCreate', async (interaction) => {
            try {
                if (interaction.isChatInputCommand()) {
                    await this.handleSlashCommand(interaction);
                } else if (interaction.isButton()) {
                    await this.handleButtonInteraction(interaction);
                } else if (interaction.isStringSelectMenu()) {
                    await this.handleSelectMenu(interaction);
                } else if (interaction.isModalSubmit()) {
                    await this.handleModalSubmit(interaction);
                }
            } catch (error) {
                console.error('Erro na interação:', error);
                const reply = { content: '❌ Ocorreu um erro interno.', ephemeral: true };
                if (interaction.replied || interaction.deferred) {
                    await interaction.followUp(reply);
                } else {
                    await interaction.reply(reply);
                }
            }
        });

        this.client.on('messageCreate', async (message) => {
            if (message.author.bot) return;

            if (message.attachments.size > 0) {
                const attachment = message.attachments.first();
                if (attachment.name.endsWith('.zip')) {
                    await this.handleZipUpload(message, attachment);
                }
            }
        });
    }

    async registerSlashCommands() {
        const commands = [
            new SlashCommandBuilder()
                .setName('painel')
                .setDescription('🎮 Abrir painel principal do Gratian Manager')
        ];

        try {
            await this.client.application.commands.set(commands);
            console.log('✅ Comandos slash registrados');
        } catch (error) {
            console.error('❌ Erro ao registrar comandos:', error);
        }
    }

    async handleSlashCommand(interaction) {
        if (interaction.commandName === 'painel') {
            await this.showMainPanel(interaction);
        }
    }

    async showMainPanel(interaction) {
        const bots = await this.listBots();
        const version = await fs.readJSON(this.versionPath);
        const onlineBots = this.runningBots.size;

        const embed = new EmbedBuilder()
            .setTitle('🎮 Gratian Manager - Painel Principal')
            .setDescription('**Sistema Avançado de Gerenciamento de Múltiplos Bots**\n\n' +
                '📋 **Como usar:**\n' +
                '• **Adicionar Bot:** Envie um arquivo .zip com seu bot\n' +
                '• **Gerenciar:** Use os botões para controlar seus bots\n' +
                '• **IA Assistente:** Diagnóstico automático de erros\n' +
                '• **Editor:** Edite arquivos diretamente pelo Discord')
            .setColor(0x2F3136)
            .addFields(
                { name: '📊 Estatísticas', value: `🤖 **${bots.length}** bots instalados\n🟢 **${onlineBots}** bots online\n🔴 **${bots.length - onlineBots}** bots offline`, inline: true },
                { name: '🔧 Sistema', value: `📦 Versão: **v${version.version}**\n📁 Diretório: \`bots/\`\n🤖 IA: **GLM-4 Ativo**`, inline: true },
                { name: '⚡ Status', value: `🔄 Auto-update: **Ativo**\n🛡️ Monitoramento: **24/7**\n📝 Logs: **Tempo Real**`, inline: true }
            )
            .setFooter({ text: 'Gratian Manager Pro • Todos os direitos reservados' })
            .setTimestamp();

        const row1 = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId('manage_bots')
                .setLabel('🎮 Gerenciar Bots')
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId('add_bot_panel')
                .setLabel('📦 Adicionar Bot')
                .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
                .setCustomId('view_logs')
                .setLabel('📜 Ver Logs')
                .setStyle(ButtonStyle.Secondary)
        );

        const row2 = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId('ai_assistant')
                .setLabel('🤖 Assistente IA')
                .setStyle(ButtonStyle.Secondary),
            new ButtonBuilder()
                .setCustomId('file_editor')
                .setLabel('📝 Editor de Arquivos')
                .setStyle(ButtonStyle.Secondary),
            new ButtonBuilder()
                .setCustomId('system_config')
                .setLabel('⚙️ Configurações')
                .setStyle(ButtonStyle.Secondary)
        );

        await interaction.reply({ embeds: [embed], components: [row1, row2], flags: 64 });
    }

    async handleButtonInteraction(interaction) {
        switch (interaction.customId) {
            case 'manage_bots':
                await this.showBotsManagement(interaction);
                break;
            case 'add_bot_panel':
                await this.showAddBotPanel(interaction);
                break;
            case 'view_logs':
                await this.showLogsPanel(interaction);
                break;
            case 'ai_assistant':
                await this.showAIAssistant(interaction);
                break;
            case 'file_editor':
                await this.showFileEditor(interaction);
                break;
            case 'system_config':
                await this.showSystemConfig(interaction);
                break;
            default:
                if (interaction.customId.startsWith('start_bot_')) {
                    const botName = interaction.customId.replace('start_bot_', '');
                    await this.startBot(interaction, botName);
                } else if (interaction.customId.startsWith('stop_bot_')) {
                    const botName = interaction.customId.replace('stop_bot_', '');
                    await this.stopBot(interaction, botName);
                } else if (interaction.customId.startsWith('restart_bot_')) {
                    const botName = interaction.customId.replace('restart_bot_', '');
                    await this.restartBot(interaction, botName);
                } else if (interaction.customId.startsWith('delete_bot_')) {
                    const botName = interaction.customId.replace('delete_bot_', '');
                    await this.deleteBot(interaction, botName);
                } else if (interaction.customId.startsWith('edit_file_')) {
                    const data = interaction.customId.replace('edit_file_', '');
                    const [botName, fileName] = data.split('_FILE_');
                    await this.editFile(interaction, botName, fileName);
                } else if (interaction.customId.startsWith('ai_fix_')) {
                    const botName = interaction.customId.replace('ai_fix_', '');
                    await this.aiFix(interaction, botName);
                } else if (interaction.customId.startsWith('install_deps_')) {
                    const botName = interaction.customId.replace('install_deps_', '');
                    await this.installDependencies(interaction, botName);
                } else if (interaction.customId.startsWith('confirm_delete_')) {
                    const botName = interaction.customId.replace('confirm_delete_', '');
                    await this.confirmDeleteBot(interaction, botName);
                } else if (interaction.customId === 'cancel_delete') {
                    await interaction.update({ content: '❌ Operação cancelada.', embeds: [], components: [] });
                } else if (interaction.customId.startsWith('edit_files_')) {
                    const botName = interaction.customId.replace('edit_files_', '');
                    await this.showBotFilesMenu(interaction, botName);
                } else if (interaction.customId.startsWith('logs_')) {
                    const botName = interaction.customId.replace('logs_', '');
                    await this.showBotLogs(interaction, botName);
                } else if (interaction.customId.startsWith('ai_configure_token_')) {
                    const botName = interaction.customId.replace('ai_configure_token_', '');
                    await this.aiConfigureToken(interaction, botName);
                }
                break;
        }
    }

    async showBotsManagement(interaction) {
        const bots = await this.listBots();

        if (bots.length === 0) {
            const embed = new EmbedBuilder()
                .setTitle('📦 Nenhum Bot Instalado')
                .setDescription('Você ainda não possui bots instalados.\n\n**Para adicionar um bot:**\n1. Clique em "📦 Adicionar Bot"\n2. Ou envie um arquivo .zip neste canal')
                .setColor(0xFF6B6B);

            await interaction.reply({ embeds: [embed], flags: 64 });
            return;
        }

        const embed = new EmbedBuilder()
            .setTitle('🎮 Gerenciamento de Bots')
            .setDescription('Selecione um bot para gerenciar:')
            .setColor(0x3498DB);

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_bot_manage')
            .setPlaceholder('Escolha um bot para gerenciar...');

        for (const bot of bots) {
            const isRunning = this.runningBots.has(bot);
            const status = isRunning ? '🟢' : '🔴';
            const uptime = isRunning ? ` (${this.getBotUptime(bot)})` : '';

            selectMenu.addOptions({
                label: `${bot}`,
                description: `${status} ${isRunning ? 'Online' : 'Offline'}${uptime}`,
                value: bot
            });
        }

        const row = new ActionRowBuilder().addComponents(selectMenu);

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async handleSelectMenu(interaction) {
        if (interaction.customId === 'select_bot_manage') {
            const botName = interaction.values[0];
            await this.showBotDetails(interaction, botName);
        } else if (interaction.customId === 'select_bot_logs') {
            const botName = interaction.values[0];
            await this.showBotLogs(interaction, botName);
        } else if (interaction.customId === 'select_bot_edit') {
           // Menu de seleção para escolher o que editar
            const botName = interaction.values[0];
            const embed = new EmbedBuilder()
              .setTitle(`📝 Editor de Arquivos - ${botName}`)
              .setDescription('Escolha o arquivo que deseja editar:');

            const selectMenu = new StringSelectMenuBuilder()
              .setCustomId('select_file_to_edit_' + botName)
              .setPlaceholder('Selecione um arquivo...');

            const botFiles = await this.getBotFiles(botName);
            for (const file of botFiles) {
              selectMenu.addOptions({
                label: file,
                value: file,
              });
            }

            const row = new ActionRowBuilder().addComponents(selectMenu);
            await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
          } else if (interaction.customId.startsWith('select_file_to_edit_')) {
              const botName = interaction.customId.split('_')[4]; // Extrai o nome do bot
              const fileName = interaction.values[0];
              await this.editFile(interaction, botName, fileName);
          } else if (interaction.customId === 'select_bot_ai') {
            const botName = interaction.values[0];
            await this.showAIBotHelp(interaction, botName);
        }
    }

    async showBotDetails(interaction, botName) {
        const isRunning = this.runningBots.has(botName);
        const uptime = isRunning ? this.getBotUptime(botName) : '0s';
        const botPath = path.join(this.botsDir, botName);
        const mainFile = await this.detectMainFile(botPath);

        const files = await this.getBotFiles(botName);
        const logsCount = (this.botLogs.get(botName) || []).length;

        const embed = new EmbedBuilder()
            .setTitle(`🤖 ${botName}`)
            .setDescription(`**Detalhes e Controles do Bot**`)
            .setColor(isRunning ? 0x4ECDC4 : 0xFF6B6B)
            .addFields(
                { name: '📊 Status', value: `${isRunning ? '🟢 Online' : '🔴 Offline'}\n⏱️ Uptime: ${uptime}`, inline: true },
                { name: '📁 Arquivos', value: `📄 Total: ${files.length}\n🎯 Principal: \`${mainFile}\``, inline: true },
                { name: '📜 Logs', value: `📝 Registros: ${logsCount}\n🔄 Monitoramento: Ativo`, inline: true }
            )
            .setFooter({ text: `Bot: ${botName} • Gratian Manager` });

        const row1 = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`${isRunning ? 'stop' : 'start'}_bot_${botName}`)
                .setLabel(isRunning ? '⏹️ Parar' : '▶️ Iniciar')
                .setStyle(isRunning ? ButtonStyle.Danger : ButtonStyle.Success),
            new ButtonBuilder()
                .setCustomId(`restart_bot_${botName}`)
                .setLabel('🔄 Reiniciar')
                .setStyle(ButtonStyle.Primary)
                .setDisabled(!isRunning),
            new ButtonBuilder()
                .setCustomId(`logs_${botName}`)
                .setLabel('📜 Ver Logs')
                .setStyle(ButtonStyle.Secondary)
        );

        const row2 = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`edit_files_${botName}`)
                .setLabel('📝 Editar Arquivos')
                .setStyle(ButtonStyle.Secondary),
            new ButtonBuilder()
                .setCustomId(`install_deps_${botName}`)
                .setLabel('📦 Instalar Deps')
                .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
                .setCustomId(`ai_fix_${botName}`)
                .setLabel('🤖 IA Diagnosticar')
                .setStyle(ButtonStyle.Secondary)
        );

        const row3 = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`delete_bot_${botName}`)
                .setLabel('🗑️ Deletar')
                .setStyle(ButtonStyle.Danger)
        );

        await interaction.update({ embeds: [embed], components: [row1, row2, row3] });
    }

    async installDependencies(interaction, botName) {
        await interaction.deferReply({ ephemeral: true });

        try {
            const botPath = path.join(this.botsDir, botName);
            const packageJsonPath = path.join(botPath, 'package.json');

            if (!await fs.pathExists(packageJsonPath)) {
                await interaction.editReply('❌ package.json não encontrado neste bot!');
                return;
            }

            await interaction.editReply('📦 Instalando dependências... Isso pode levar alguns minutos.');

            const installProcess = spawn('npm', ['install'], {
                cwd: botPath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            let errorOutput = '';

            installProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            installProcess.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            installProcess.on('close', async (code) => {
                if (code === 0) {
                    const embed = new EmbedBuilder()
                        .setTitle('✅ Dependências Instaladas')
                        .setDescription(`Todas as dependências do bot **${botName}** foram instaladas com sucesso!`)
                        .setColor(0x4ECDC4)
                        .addFields({
                            name: '📋 Output',
                            value: output.length > 1000 ? output.substring(0, 1000) + '...' : output || 'Instalação concluída',
                            inline: false
                        });

                    await interaction.editReply({ embeds: [embed] });
                } else {
                    const embed = new EmbedBuilder()
                        .setTitle('❌ Erro na Instalação')
                        .setDescription(`Erro ao instalar dependências do bot **${botName}**`)
                        .setColor(0xFF6B6B)
                        .addFields({
                            name: '❗ Erro',
                            value: errorOutput.length > 1000 ? errorOutput.substring(0, 1000) + '...' : errorOutput || 'Erro desconhecido',
                            inline: false
                        });

                    await interaction.editReply({ embeds: [embed] });
                }
            });

        } catch (error) {
            await interaction.editReply(`❌ Erro ao instalar dependências: ${error.message}`);
        }
    }

    async startBot(interaction, botName) {
        if (this.runningBots.has(botName)) {
            await interaction.reply({ content: '❌ Bot já está rodando!', flags: 64 });
            return;
        }

        await interaction.deferReply({ ephemeral: true });

        try {
            const botPath = path.join(this.botsDir, botName);
            const mainFile = await this.detectMainFile(botPath);
            const mainFilePath = path.join(botPath, mainFile);

            if (!await fs.pathExists(mainFilePath)) {
                await interaction.editReply('❌ Arquivo principal não encontrado!');
                return;
            }

            const proc = spawn('node', [mainFilePath], {
                cwd: botPath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            proc.startTime = Date.now();
            this.runningBots.set(botName, proc);

            if (!this.botLogs.has(botName)) {
                this.botLogs.set(botName, []);
            }

            proc.stdout.on('data', (data) => {
                const logs = this.botLogs.get(botName);
                logs.push(`[${new Date().toLocaleTimeString()}] ${data.toString().trim()}`);
                if (logs.length > 100) logs.shift();
            });

            proc.stderr.on('data', (data) => {
                const logs = this.botLogs.get(botName);
                logs.push(`[${new Date().toLocaleTimeString()}] ERROR: ${data.toString().trim()}`);
                if (logs.length > 100) logs.shift();
            });

            proc.on('exit', (code) => {
                this.runningBots.delete(botName);
                const logs = this.botLogs.get(botName);
                logs.push(`[${new Date().toLocaleTimeString()}] Bot finalizado com código ${code}`);
            });

            await interaction.editReply(`✅ Bot **${botName}** iniciado com sucesso!`);

        } catch (error) {
            await interaction.editReply(`❌ Erro ao iniciar bot: ${error.message}`);
        }
    }

    async stopBot(interaction, botName) {
        const proc = this.runningBots.get(botName);

        if (!proc) {
            await interaction.reply({ content: '❌ Bot não está rodando!', flags: 64 });
            return;
        }

        proc.kill();
        this.runningBots.delete(botName);

        await interaction.reply({ content: `✅ Bot **${botName}** parado com sucesso!`, flags: 64 });
    }

    async restartBot(interaction, botName) {
        await interaction.deferReply({ ephemeral: true });

        const proc = this.runningBots.get(botName);
        if (proc) {
            proc.kill();
            this.runningBots.delete(botName);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        await this.startBot(interaction, botName);
    }

    async deleteBot(interaction, botName) {
        const embed = new EmbedBuilder()
            .setTitle('⚠️ Confirmar Exclusão')
            .setDescription(`Você tem certeza que deseja deletar o bot **${botName}**?\n\n❌ **Esta ação não pode ser desfeita!**`)
            .setColor(0xFF6B6B);

        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`confirm_delete_${botName}`)
                .setLabel('✅ Sim, Deletar')
                .setStyle(ButtonStyle.Danger),
            new ButtonBuilder()
                .setCustomId('cancel_delete')
                .setLabel('❌ Cancelar')
                .setStyle(ButtonStyle.Secondary)
        );

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async confirmDeleteBot(interaction, botName) {
        await interaction.deferReply({ ephemeral: true });

        try {
            // Parar o bot se estiver rodando
            const proc = this.runningBots.get(botName);
            if (proc) {
                proc.kill();
                this.runningBots.delete(botName);
            }

            // Remover logs
            this.botLogs.delete(botName);

            // Deletar pasta do bot
            const botPath = path.join(this.botsDir, botName);
            if (await fs.pathExists(botPath)) {
                await fs.remove(botPath);
            }

            const embed = new EmbedBuilder()
                .setTitle('✅ Bot Deletado')
                .setDescription(`Bot **${botName}** foi removido completamente do sistema!`)
                .setColor(0x4ECDC4);

            await interaction.editReply({ embeds: [embed] });

        } catch (error) {
            await interaction.editReply(`❌ Erro ao deletar bot: ${error.message}`);
        }
    }

    async showAddBotPanel(interaction) {
        const embed = new EmbedBuilder()
            .setTitle('📦 Adicionar Novo Bot')
            .setDescription('**📋 Como adicionar um bot:**\n\n' +
                '1️⃣ **Prepare seu bot:** Certifique-se que seu bot está em uma pasta\n' +
                '2️⃣ **Compacte:** Crie um arquivo .zip com todos os arquivos\n' +
                '3️⃣ **Envie:** Arraste o .zip para este canal\n' +
                '4️⃣ **Aguarde:** O sistema irá processar automaticamente\n\n' +
                '⚠️ **Importante:**\n' +
                '• O arquivo principal deve ser `index.js`, `main.js` ou `bot.js`\n' +
                '• Inclua todas as dependências no package.json\n' +
                '• Não inclua a pasta node_modules no zip')
            .setColor(0x4ECDC4)
            .addFields(
                { name: '📁 Estrutura Recomendada', value: '```\nmeubot.zip\n├── index.js\n├── package.json\n├── config.json\n└── outros arquivos...\n```', inline: false },
                { name: '🔧 Suporte', value: 'Formatos: `.zip`\nTamanho máximo: `8MB`\nIA irá diagnosticar erros', inline: true }
            );

        await interaction.reply({ embeds: [embed], flags: 64 });
    }

    async showLogsPanel(interaction) {
        const bots = await this.listBots();

        if (bots.length === 0) {
            const embed = new EmbedBuilder()
                .setTitle('📜 Logs - Nenhum Bot')
                .setDescription('Nenhum bot instalado para mostrar logs.')
                .setColor(0xFF6B6B);

            await interaction.reply({ embeds: [embed], flags: 64 });
            return;
        }

        const embed = new EmbedBuilder()
            .setTitle('📜 Visualizar Logs')
            .setDescription('Selecione um bot para ver os logs:')
            .setColor(0x3498DB);

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_bot_logs')
            .setPlaceholder('Escolha um bot para ver os logs...');

        for (const bot of bots) {
            const logsCount = (this.botLogs.get(bot) || []).length;
            const isRunning = this.runningBots.has(bot);

            selectMenu.addOptions({
                label: `${bot}`,
                description: `${isRunning ? '🟢' : '🔴'} ${logsCount} registros`,
                value: bot
            });
        }

        const row = new ActionRowBuilder().addComponents(selectMenu);

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async showBotLogs(interaction, botName) {
        const logs = this.botLogs.get(botName) || [];
        const recentLogs = logs.slice(-15);

        const embed = new EmbedBuilder()
            .setTitle(`📜 Logs: ${botName}`)
            .setColor(0x3498DB);

        if (recentLogs.length === 0) {
            embed.setDescription('```\nNenhum log disponível ainda.\n```');
        } else {
            const logText = recentLogs.join('\n');
            embed.setDescription(`\`\`\`\n${logText.slice(-1900)}\n\`\`\``);
        }

        const isRunning = this.runningBots.has(botName);
        embed.addFields({
            name: '📊 Status',
            value: `${isRunning ? '🟢 Online' : '🔴 Offline'} • ${logs.length} registros totais`,
            inline: true
        });

        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`refresh_logs_${botName}`)
                .setLabel('🔄 Atualizar')
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId(`clear_logs_${botName}`)
                .setLabel('🗑️ Limpar')
                .setStyle(ButtonStyle.Danger)
        );

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async showAIAssistant(interaction) {
        const embed = new EmbedBuilder()
            .setTitle('🤖 Assistente IA - GLM-4')
            .setDescription('**Diagnóstico Inteligente e Suporte Técnico**\n\n' +
                '🔍 **Funcionalidades:**\n' +
                '• **Diagnóstico Automático:** Identifica erros nos bots\n' +
                '• **Correção Sugerida:** Propõe soluções para problemas\n' +
                '• **Assistência de Código:** Ajuda a editar arquivos\n' +
                '• **Configuração Inteligente:** Setup automático de tokens\n\n' +
                '🎯 **Como usar:**\n' +
                '1. Selecione um bot abaixo\n' +
                '2. Escolha o tipo de ajuda\n' +
                '3. A IA irá analisar e ajudar')
            .setColor(0x9B59B6);

        const bots = await this.listBots();

        if (bots.length === 0) {
            embed.addFields({ name: '❌ Nenhum Bot', value: 'Adicione bots primeiro para usar a IA', inline: false });
            await interaction.reply({ embeds: [embed], flags: 64 });
            return;
        }

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_bot_ai')
            .setPlaceholder('Escolha um bot para análise da IA...');

        for (const bot of bots) {
            const isRunning = this.runningBots.has(bot);
            const hasErrors = this.botHasErrors(bot);

            selectMenu.addOptions({
                label: `${bot}`,
                description: `${isRunning ? '🟢' : '🔴'} ${hasErrors ? '⚠️ Com erros' : '✅ Funcionando'}`,
                value: bot
            });
        }

        const row = new ActionRowBuilder().addComponents(selectMenu);

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async showAIBotHelp(interaction, botName) {
        const hasErrors = this.botHasErrors(botName);
        const isRunning = this.runningBots.has(botName);

        const embed = new EmbedBuilder()
            .setTitle(`🤖 IA Assistente: ${botName}`)
            .setDescription(`**Análise Inteligente do Bot**`)
            .setColor(0x9B59B6)
            .addFields(
                { name: '📊 Status Atual', value: `${isRunning ? '🟢 Online' : '🔴 Offline'}\n${hasErrors ? '⚠️ Erros detectados' : '✅ Funcionando bem'}`, inline: true },
                { name: '🔍 Análise', value: 'IA analisando logs e arquivos...', inline: true }
            );

        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId(`ai_fix_${botName}`)
                .setLabel('🔍 Diagnosticar Erros')
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId(`ai_configure_token_${botName}`)
                .setLabel('🔑 Configurar Token')
                .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
                .setCustomId(`install_deps_${botName}`)
                .setLabel('📦 Instalar Dependências')
                .setStyle(ButtonStyle.Secondary)
        );

        await interaction.update({ embeds: [embed], components: [row] });
    }

    async showBotFilesMenu(interaction, botName) {
        const embed = new EmbedBuilder()
            .setTitle(`📝 Editor de Arquivos - ${botName}`)
            .setDescription('Escolha o arquivo que deseja editar:')
            .setColor(0xE67E22);

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_file_to_edit_' + botName)
            .setPlaceholder('Selecione um arquivo...');

        const botFiles = await this.getBotFiles(botName);
        
        if (botFiles.length === 0) {
            await interaction.reply({ content: '❌ Nenhum arquivo encontrado neste bot!', flags: 64 });
            return;
        }

        for (const file of botFiles.slice(0, 25)) { // Limite de 25 arquivos
            selectMenu.addOptions({
                label: file,
                value: file,
            });
        }

        const row = new ActionRowBuilder().addComponents(selectMenu);
        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async showFileEditor(interaction) {
        const bots = await this.listBots();

        if (bots.length === 0) {
            const embed = new EmbedBuilder()
                .setTitle('📝 Editor - Nenhum Bot')
                .setDescription('Nenhum bot instalado para editar.')
                .setColor(0xFF6B6B);

            await interaction.reply({ embeds: [embed], flags: 64 });
            return;
        }

        const embed = new EmbedBuilder()
            .setTitle('📝 Editor de Arquivos')
            .setDescription('**Edição Direta via Discord**\n\n' +
                '✏️ **Funcionalidades:**\n' +
                '• Editar qualquer arquivo do bot\n' +
                '• Preview em tempo real\n' +
                '• Backup automático\n' +
                '• Syntax highlighting\n\n' +
                '📋 **Selecione um bot para editar:**')
            .setColor(0xE67E22);

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_bot_edit')
            .setPlaceholder('Escolha um bot para editar arquivos...');

        for (const bot of bots) {
            const files = await this.getBotFiles(bot);

            selectMenu.addOptions({
                label: `${bot}`,
                description: `📁 ${files.length} arquivos editáveis`,
                value: bot
            });
        }

        const row = new ActionRowBuilder().addComponents(selectMenu);

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

   async showBotFiles(interaction, botName) {
    const files = await this.getBotFiles(botName);

    const embed = new EmbedBuilder()
      .setTitle(`📁 Arquivos: ${botName}`)
      .setDescription('Selecione um arquivo para editar:')
      .setColor(0xE67E22);

    let description = '```\n';
    for (const file of files.slice(0, 10)) {
      const size = await this.getFileSize(path.join(this.botsDir, botName, file));
      description += `📄 ${file} (${size})\n`;
    }
    description += '```';

    embed.addFields({ name: '📂 Estrutura', value: description, inline: false });

    // Removendo os botões, pois agora a seleção é feita por um menu
    // const row = new ActionRowBuilder().addComponents(
    //   new ButtonBuilder()
    //     .setCustomId(`edit_file_${botName}_FILE_index.js`)
    //     .setLabel('📝 index.js')
    //     .setStyle(ButtonStyle.Primary),
    //   new ButtonBuilder()
    //     .setCustomId(`edit_file_${botName}_FILE_package.json`)
    //     .setLabel('📦 package.json')
    //     .setStyle(ButtonStyle.Secondary),
    //   new ButtonBuilder()
    //     .setCustomId(`edit_file_${botName}_FILE_config.json`)
    //     .setLabel('⚙️ config.json')
    //     .setStyle(ButtonStyle.Success)
    // );

    await interaction.update({ embeds: [embed], components: [] }); // Remove components
  }

    async editFile(interaction, botName, fileName) {
        const filePath = path.join(this.botsDir, botName, fileName);

        if (!await fs.pathExists(filePath)) {
            await interaction.reply({ content: `❌ Arquivo ${fileName} não encontrado!`, flags: 64 });
            return;
        }

        try {
            const content = await fs.readFile(filePath, 'utf8');
            const truncatedContent = content.length > 3000 ? content.substring(0, 3000) + '\n...(arquivo truncado)' : content;

            const modal = new ModalBuilder()
                .setCustomId(`save_file_${botName}_FILE_${fileName}`)
                .setTitle(`Editar: ${fileName}`);

            const textInput = new TextInputBuilder()
                .setCustomId('file_content')
                .setLabel('Conteúdo do Arquivo')
                .setStyle(TextInputStyle.Paragraph)
                .setValue(truncatedContent)
                .setRequired(true);

            const row = new ActionRowBuilder().addComponents(textInput);
            modal.addComponents(row);

            await interaction.showModal(modal);

        } catch (error) {
            await interaction.reply({ content: `❌ Erro ao ler arquivo: ${error.message}`, flags: 64 });
        }
    }

    async handleModalSubmit(interaction) {
        if (interaction.customId.startsWith('save_file_')) {
            const data = interaction.customId.replace('save_file_', '');
            const [botName, fileName] = data.split('_FILE_');
            const content = interaction.fields.getTextInputValue('file_content');

            try {
                const filePath = path.join(this.botsDir, botName, fileName);

                // Backup do arquivo original
                const backupPath = `${filePath}.backup`;
                if (await fs.pathExists(filePath)) {
                    await fs.copy(filePath, backupPath);
                }

                await fs.writeFile(filePath, content, 'utf8');

                const embed = new EmbedBuilder()
                    .setTitle('✅ Arquivo Salvo')
                    .setDescription(`Arquivo **${fileName}** do bot **${botName}** foi atualizado com sucesso!`)
                    .setColor(0x4ECDC4)
                    .addFields({
                        name: '💾 Backup',
                        value: `Backup salvo em: \`${fileName}.backup\``,
                        inline: true
                    });

                await interaction.reply({ embeds: [embed], flags: 64 });

            } catch (error) {
                await interaction.reply({ 
                    content: `❌ Erro ao salvar arquivo: ${error.message}`, 
                    flags: 64
                });
            }
        } else if (interaction.customId === 'ai_question_modal') {
            const question = interaction.fields.getTextInputValue('question');
            await this.askAI(interaction, question);
        }
    }

    async askAI(interaction, question) {
        await interaction.deferReply({ ephemeral: true });

        try {
            const config = await fs.readJSON(this.configPath);

            if (!config.glm4_api_key || config.glm4_api_key === 'SUA_API_KEY_AQUI') {
                await interaction.editReply('❌ API Key da IA não configurada! Configure no arquivo config.json');
                return;
            }

            const response = await axios.post(config.glm4_endpoint, {
                model: "glm-4",
                messages: [
                    { 
                        role: "system", 
                        content: "Você é um assistente especializado em Discord.js e Node.js. Ajude com problemas de bots Discord, diagnóstico de erros e configurações. Seja claro e objetivo." 
                    },
                    { role: "user", content: question }
                ],
                temperature: 0.7,
                web_search: false
            }, {
                headers: {
                    'Authorization': `Bearer ${config.glm4_api_key}`,
                    'Content-Type': 'application/json'
                }
            });

            const aiResponse = response.data.choices[0].message.content;

            const embed = new EmbedBuilder()
                .setTitle('🤖 Resposta da IA')
                .setDescription(aiResponse.length > 4000 ? aiResponse.substring(0, 4000) + '...' : aiResponse)
                .setColor(0x9B59B6)
                .setFooter({ text: 'Powered by GLM-4' });

            await interaction.editReply({ embeds: [embed] });

        } catch (error) {
            await interaction.editReply(`❌ Erro ao consultar IA: ${error.message}`);
        }
    }

    async aiFix(interaction, botName) {
        await interaction.deferReply({ ephemeral: true });

        try {
            const config = await fs.readJSON(this.configPath);

            if (!config.glm4_api_key || config.glm4_api_key === 'SUA_API_KEY_AQUI') {
                await interaction.editReply('❌ API Key da IA não configurada! Configure no arquivo config.json');
                return;
            }

            // Verificar se o bot existe
            const botPath = path.join(this.botsDir, botName);
            if (!await fs.pathExists(botPath)) {
                await interaction.editReply(`❌ Bot **${botName}** não encontrado!`);
                return;
            }

            // Coletar informações completas sobre o bot
            const logs = this.botLogs.get(botName) || [];
            const isRunning = this.runningBots.has(botName);
            const mainFile = await this.detectMainFile(botPath);
            
            // Analisar package.json
            let packageAnalysis = '';
            const packageJsonPath = path.join(botPath, 'package.json');
            if (await fs.pathExists(packageJsonPath)) {
                try {
                    const packageJson = await fs.readJSON(packageJsonPath);
                    const deps = Object.keys(packageJson.dependencies || {});
                    const devDeps = Object.keys(packageJson.devDependencies || {});
                    packageAnalysis = `
📦 Package.json encontrado:
- Dependências: ${deps.length > 0 ? deps.join(', ') : 'Nenhuma'}
- Dependências de desenvolvimento: ${devDeps.length > 0 ? devDeps.join(', ') : 'Nenhuma'}
- Scripts: ${Object.keys(packageJson.scripts || {}).join(', ') || 'Nenhum'}`;
                } catch (error) {
                    packageAnalysis = '❌ Erro ao analisar package.json';
                }
            } else {
                packageAnalysis = '❌ package.json não encontrado';
            }

            // Análise de logs mais detalhada
            const allErrors = logs.filter(log => 
                log.toLowerCase().includes('error') || 
                log.toLowerCase().includes('failed') ||
                log.toLowerCase().includes('cannot find module') ||
                log.toLowerCase().includes('missing') ||
                log.toLowerCase().includes('undefined') ||
                log.toLowerCase().includes('null')
            ).slice(-10);

            // Análise de arquivos do bot
            const files = await this.getBotFiles(botName);
            let codeAnalysis = '';
            
            // Ler múltiplos arquivos para análise
            const importantFiles = files.filter(file => 
                file.endsWith('.js') || 
                file.endsWith('.json') || 
                file.endsWith('.env')
            ).slice(0, 5);

            for (const file of importantFiles) {
                try {
                    const filePath = path.join(botPath, file);
                    const content = await fs.readFile(filePath, 'utf8');
                    codeAnalysis += `\n📄 ${file} (${content.length} chars):\n${content.substring(0, 800)}\n---\n`;
                } catch (error) {
                    codeAnalysis += `\n❌ Erro ao ler ${file}: ${error.message}\n`;
                }
            }

            // Criar prompt especializado para diagnóstico
            const diagnosticPrompt = `SISTEMA DE DIAGNÓSTICO AVANÇADO - ANÁLISE COMPLETA

🤖 BOT: ${botName}
📊 STATUS: ${isRunning ? 'ONLINE' : 'OFFLINE'}
🎯 ARQUIVO PRINCIPAL: ${mainFile}

${packageAnalysis}

📜 LOGS DE ERRO (últimos 10):
${allErrors.length > 0 ? allErrors.join('\n') : '✅ Nenhum erro detectado nos logs'}

📁 ESTRUTURA DE ARQUIVOS:
${files.slice(0, 15).map(f => `• ${f}`).join('\n')}

💻 ANÁLISE DE CÓDIGO:
${codeAnalysis}

🎯 TAREFA: 
Como especialista em Discord.js e Node.js, faça uma análise completa e diagnóstico preciso:

1. IDENTIFIQUE todos os problemas encontrados
2. CLASSIFIQUE a gravidade (Crítico/Alto/Médio/Baixo)
3. FORNEÇA soluções específicas e comandos exatos
4. DETECTE dependências faltantes e forneça comandos npm install
5. IDENTIFIQUE problemas de configuração (tokens, permissões, etc.)
6. ANALISE a estrutura do código para bugs comuns

FORMATO DE RESPOSTA:
🔍 PROBLEMAS IDENTIFICADOS:
[liste todos os problemas]

🛠️ SOLUÇÕES:
[comandos e correções específicas]

📦 DEPENDÊNCIAS:
[comandos npm install se necessário]

⚙️ CONFIGURAÇÃO:
[problemas de config e como resolver]`;

            const response = await axios.post(config.glm4_endpoint, {
                model: "glm-4",
                messages: [
                    { 
                        role: "system", 
                        content: "Você é um ESPECIALISTA SÊNIOR em Discord.js, Node.js e diagnóstico de bots. Analise TUDO: código, logs, dependências, configurações. Seja EXTREMAMENTE detalhado e forneça soluções PRÁTICAS e EXECUTÁVEIS. Sempre inclua comandos exatos quando necessário." 
                    },
                    { role: "user", content: diagnosticPrompt }
                ],
                temperature: 0.1,
                web_search: false
            }, {
                headers: {
                    'Authorization': `Bearer ${config.glm4_api_key}`,
                    'Content-Type': 'application/json'
                }
            });

            const aiResponse = response.data.choices[0].message.content;

            const embed = new EmbedBuilder()
                .setTitle(`🔍 Diagnóstico Completo: ${botName}`)
                .setDescription(aiResponse.length > 4000 ? aiResponse.substring(0, 4000) + '...' : aiResponse)
                .setColor(0x9B59B6)
                .addFields(
                    { name: '📊 Status', value: `${isRunning ? '🟢 Online' : '🔴 Offline'}`, inline: true },
                    { name: '📁 Arquivos', value: `${files.length} arquivos`, inline: true },
                    { name: '⚠️ Logs Analisados', value: `${allErrors.length} erros`, inline: true }
                )
                .setFooter({ text: 'Diagnóstico Avançado by GLM-4' });

            // Botões inteligentes baseados na análise
            const components = [];
            const installRow = new ActionRowBuilder();
            
            if (aiResponse.toLowerCase().includes('npm install') || aiResponse.toLowerCase().includes('dependência')) {
                installRow.addComponents(
                    new ButtonBuilder()
                        .setCustomId(`install_deps_${botName}`)
                        .setLabel('📦 Instalar Dependências')
                        .setStyle(ButtonStyle.Success)
                );
            }

            if (aiResponse.toLowerCase().includes('token') || aiResponse.toLowerCase().includes('configuração')) {
                installRow.addComponents(
                    new ButtonBuilder()
                        .setCustomId(`ai_configure_token_${botName}`)
                        .setLabel('🔧 Configurar Token')
                        .setStyle(ButtonStyle.Primary)
                );
            }

            if (installRow.components.length > 0) {
                components.push(installRow);
            }

            await interaction.editReply({ embeds: [embed], components });

        } catch (error) {
            console.error('Erro na função aiFix:', error);
            await interaction.editReply(`❌ Erro ao executar diagnóstico IA: ${error.message}`);
        }
    }

    async aiConfigureToken(interaction, botName) {
        await interaction.deferReply({ ephemeral: true });

        try {
            const config = await fs.readJSON(this.configPath);

            if (!config.glm4_api_key || config.glm4_api_key === 'SUA_API_KEY_AQUI') {
                await interaction.editReply('❌ API Key da IA não configurada! Configure no arquivo config.json');
                return;
            }

            const botPath = path.join(this.botsDir, botName);
            const files = await this.getBotFiles(botName);
            
            // Análise completa de TODOS os arquivos para encontrar tokens
            let fullCodeAnalysis = '';
            let tokenLocations = [];
            let recommendedFile = '';
            let suggestedToken = '';

            // Verificar todos os arquivos relevantes
            const relevantFiles = files.filter(file => 
                file.endsWith('.js') || 
                file.endsWith('.json') || 
                file.endsWith('.env') ||
                file.includes('config') ||
                file.includes('index') ||
                file.includes('main') ||
                file.includes('bot')
            );

            for (const file of relevantFiles) {
                try {
                    const filePath = path.join(botPath, file);
                    const content = await fs.readFile(filePath, 'utf8');
                    
                    // Análise detalhada de cada arquivo
                    fullCodeAnalysis += `\n📄 ARQUIVO: ${file}\n`;
                    fullCodeAnalysis += `CONTEÚDO COMPLETO:\n${content}\n${'='.repeat(50)}\n`;
                    
                    // Procurar por padrões de token
                    const lines = content.split('\n');
                    lines.forEach((line, index) => {
                        const lowerLine = line.toLowerCase();
                        if (lowerLine.includes('token') || 
                            lowerLine.includes('bot_token') ||
                            lowerLine.includes('discord_token') ||
                            lowerLine.includes('client.login')) {
                            
                            tokenLocations.push({
                                file: file,
                                line: index + 1,
                                content: line.trim(),
                                isConfigFile: file.includes('config'),
                                isMainFile: file.includes('index') || file.includes('main') || file.includes('bot')
                            });
                        }
                    });
                } catch (error) {
                    fullCodeAnalysis += `❌ Erro ao ler ${file}: ${error.message}\n`;
                }
            }

            // Determinar o melhor local e método para configurar o token
            if (tokenLocations.length > 0) {
                // Priorizar config.json se existir
                const configLocation = tokenLocations.find(loc => loc.file.includes('config.json'));
                const mainLocation = tokenLocations.find(loc => loc.isMainFile);
                
                recommendedFile = configLocation ? configLocation.file : (mainLocation ? mainLocation.file : tokenLocations[0].file);
            }

            // Criar prompt inteligente para configuração automática
            const configPrompt = `SISTEMA INTELIGENTE DE CONFIGURAÇÃO DE TOKEN DISCORD

🤖 BOT: ${botName}
📊 ANÁLISE COMPLETA DOS ARQUIVOS:

${fullCodeAnalysis}

🎯 LOCAIS DE TOKEN IDENTIFICADOS:
${tokenLocations.length > 0 ? 
    tokenLocations.map(loc => `📍 ${loc.file} (linha ${loc.line}): ${loc.content}`).join('\n') :
    '❌ Nenhuma referência a token encontrada'}

🔧 TAREFA ESPECÍFICA:
Como especialista em Discord.js, você deve:

1. IDENTIFICAR automaticamente onde o token está definido
2. DETERMINAR o melhor método de configuração
3. FORNECER o código EXATO para inserir o token
4. GERAR um token de exemplo válido no formato correto
5. MOSTRAR exatamente qual linha modificar

INSTRUÇÕES ESPECÍFICAS:
- Se existe config.json, use: "token": "SEU_TOKEN_AQUI"
- Se é hardcoded no código, mostre a linha exata para modificar
- Se usa variáveis de ambiente, configure o .env
- SEMPRE gere um exemplo de token no formato: "MTxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx"

FORMATO DE RESPOSTA:
🎯 ARQUIVO PARA MODIFICAR: [nome do arquivo]
📝 LINHA EXATA: [número da linha]
💻 CÓDIGO ANTIGO: [código atual]
✅ CÓDIGO NOVO: [código com token configurado]
🔑 TOKEN DE EXEMPLO: [gere um token de exemplo]

SEJA EXTREMAMENTE ESPECÍFICO E FORNEÇA CÓDIGO PRONTO PARA COPIAR!`;

            const response = await axios.post(config.glm4_endpoint, {
                model: "glm-4",
                messages: [
                    { 
                        role: "system", 
                        content: "Você é um ESPECIALISTA em configuração de bots Discord. Analise TODO o código fornecido e identifique AUTOMATICAMENTE onde e como configurar o token. Forneça instruções EXTREMAMENTE específicas e código PRONTO para usar. Sempre gere tokens de exemplo realistas." 
                    },
                    { role: "user", content: configPrompt }
                ],
                temperature: 0.1,
                web_search: false
            }, {
                headers: {
                    'Authorization': `Bearer ${config.glm4_api_key}`,
                    'Content-Type': 'application/json'
                }
            });

            const aiResponse = response.data.choices[0].message.content;

            const embed = new EmbedBuilder()
                .setTitle(`🔧 Configuração Automática de Token: ${botName}`)
                .setDescription(aiResponse.length > 4000 ? aiResponse.substring(0, 4000) + '...' : aiResponse)
                .setColor(0x4ECDC4)
                .addFields(
                    { name: '📁 Arquivos Analisados', value: `${relevantFiles.length} arquivos`, inline: true },
                    { name: '🎯 Tokens Encontrados', value: `${tokenLocations.length} locais`, inline: true },
                    { name: '📝 Arquivo Recomendado', value: recommendedFile || 'A ser determinado', inline: true }
                )
                .setFooter({ text: 'Configuração Inteligente by GLM-4' });

            // Botões inteligentes
            const row = new ActionRowBuilder();
            
            if (recommendedFile) {
                row.addComponents(
                    new ButtonBuilder()
                        .setCustomId(`edit_file_${botName}_FILE_${recommendedFile}`)
                        .setLabel(`📝 Editar ${recommendedFile}`)
                        .setStyle(ButtonStyle.Primary)
                );
            }

            row.addComponents(
                new ButtonBuilder()
                    .setCustomId(`edit_files_${botName}`)
                    .setLabel('📂 Ver Todos Arquivos')
                    .setStyle(ButtonStyle.Secondary)
            );

            await interaction.editReply({ embeds: [embed], components: [row] });

        } catch (error) {
            console.error('Erro na configuração de token:', error);
            await interaction.editReply(`❌ Erro ao analisar configuração: ${error.message}`);
        }
    }

    async showSystemConfig(interaction) {
        const config = await fs.readJSON(this.configPath);
        const version = await fs.readJSON(this.versionPath);

        const embed = new EmbedBuilder()
            .setTitle('⚙️ Configurações do Sistema')
            .setDescription('**Configurações Atuais do Gratian Manager**')
            .setColor(0x95A5A6)
            .addFields(
                { name: '🤖 Discord', value: `Token: ${config.discord_token ? '✅ Configurado' : '❌ Não configurado'}`, inline: true },
                { name: '🧠 IA GLM-4', value: `API Key: ${config.glm4_api_key && config.glm4_api_key !== 'SUA_API_KEY_AQUI' ? '✅ Configurado' : '❌ Não configurado'}`, inline: true },
                { name: '🔄 Auto-Update', value: `${config.auto_update ? '✅ Ativo' : '❌ Inativo'}`, inline: true },
                { name: '📦 Versão', value: `v${version.version}`, inline: true },
                { name: '🌐 Endpoint IA', value: `\`${config.glm4_endpoint}\``, inline: false }
            );

        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId('config_discord')
                .setLabel('🤖 Config Discord')
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId('config_ai')
                .setLabel('🧠 Config IA')
                .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
                .setCustomId('reset_config')
                .setLabel('🔄 Reset Config')
                .setStyle(ButtonStyle.Danger)
        );

        await interaction.reply({ embeds: [embed], components: [row], flags: 64 });
    }

    async handleZipUpload(message, attachment) {
        const loadingEmbed = new EmbedBuilder()
            .setTitle('📦 Processando Bot...')
            .setDescription('⏳ Baixando e extraindo arquivo...')
            .setColor(0xFFB347);

        const loadingMsg = await message.reply({ embeds: [loadingEmbed] });

        try {
            // Download do arquivo
            const response = await axios.get(attachment.url, { responseType: 'arraybuffer' });
            const zipPath = path.join(this.tempDir, `${Date.now()}_${attachment.name}`);
            await fs.writeFile(zipPath, response.data);

            loadingEmbed.setDescription('📂 Extraindo arquivos...');
            await loadingMsg.edit({ embeds: [loadingEmbed] });

            // Extrair ZIP
            const zip = new AdmZip(zipPath);
            const botName = path.basename(attachment.name, '.zip').replace(/[^a-zA-Z0-9_-]/g, '');
            const extractPath = path.join(this.botsDir, botName);

            // Verificar se já existe
            if (await fs.pathExists(extractPath)) {
                await fs.remove(extractPath);
            }

            zip.extractAllTo(extractPath, true);

            // Detectar estrutura do bot
            const mainFile = await this.detectMainFile(extractPath);
            const hasPackageJson = await fs.pathExists(path.join(extractPath, 'package.json'));

            loadingEmbed.setDescription('🔍 Analisando estrutura...');
            await loadingMsg.edit({ embeds: [loadingEmbed] });

            // Instalar dependências se houver package.json
            if (hasPackageJson) {
                loadingEmbed.setDescription('📦 Instalando dependências...');
                await loadingMsg.edit({ embeds: [loadingEmbed] });

                try {
                    await new Promise((resolve, reject) => {
                        const installProcess = spawn('npm', ['install'], {
                            cwd: extractPath,
                            stdio: ['pipe', 'pipe', 'pipe']
                        });

                        let output = '';
                        let errorOutput = '';

                        installProcess.stdout.on('data', (data) => {
                            output += data.toString();
                        });

                        installProcess.stderr.on('data', (data) => {
                            errorOutput += data.toString();
                        });

                        installProcess.on('close', (code) => {
                            if (code === 0) {
                                console.log('✅ Dependências instaladas com sucesso');
                                resolve();
                            } else {
                                console.warn(`⚠️ Aviso na instalação: ${errorOutput}`);
                                resolve(); // Continua mesmo com warnings
                            }
                        });

                        installProcess.on('error', (error) => {
                            console.warn(`⚠️ Erro na instalação: ${error.message}`);
                            resolve(); // Continua mesmo com erro
                        });
                    });
                } catch (error) {
                    console.warn(`Aviso ao instalar dependências: ${error.message}`);
                }
            }

            // Verificar por erros comuns
            const diagnostics = await this.diagnoseBotIssues(extractPath, mainFile);

            // Cleanup
            await fs.remove(zipPath);
            await message.delete();

            // Embed de sucesso
            const successEmbed = new EmbedBuilder()
                .setTitle('✅ Bot Instalado com Sucesso!')
                .setDescription(`Bot **${botName}** foi instalado e está pronto para uso!`)
                .setColor(0x4ECDC4)
                .addFields(
                    { name: '📁 Localização', value: `\`bots/${botName}/\``, inline: true },
                    { name: '🎯 Arquivo Principal', value: `\`${mainFile}\``, inline: true },
                    { name: '📦 Dependências', value: hasPackageJson ? '✅ Instaladas' : '❌ Não encontradas', inline: true }
                );

            if (diagnostics.issues.length > 0) {
                successEmbed.addFields({
                    name: '⚠️ Problemas Detectados',
                    value: diagnostics.issues.slice(0, 3).map(issue => `• ${issue}`).join('\n'),
                    inline: false
                });
            }

            const actionRow = new ActionRowBuilder().addComponents(
                new ButtonBuilder()
                    .setCustomId(`start_bot_${botName}`)
                    .setLabel('▶️ Iniciar Bot')
                    .setStyle(ButtonStyle.Success),
                new ButtonBuilder()
                    .setCustomId(`manage_bot_${botName}`)
                    .setLabel('⚙️ Gerenciar')
                    .setStyle(ButtonStyle.Primary)
            );

            await loadingMsg.edit({ 
                embeds: [successEmbed], 
                components: diagnostics.issues.length === 0 ? [actionRow] : [] 
            });

        } catch (error) {
            console.error('Erro ao processar ZIP:', error);

            const errorEmbed = new EmbedBuilder()
                .setTitle('❌ Erro ao Instalar Bot')
                .setDescription(`**Erro encontrado:** ${error.message}\n\n**Possíveis causas:**\n• Arquivo ZIP corrompido\n• Estrutura de arquivos inválida\n• Arquivo muito grande`)
                .setColor(0xFF6B6B)
                .addFields({
                    name: '💡 Solução',
                    value: '• Verifique se o ZIP contém um arquivo principal (index.js)\n• Certifique-se que o arquivo não está corrompido\n• Tente novamente com um arquivo menor',
                    inline: false
                });

            await loadingMsg.edit({ embeds: [errorEmbed] });
        }
    }

    async diagnoseBotIssues(botPath, mainFile) {
        const issues = [];
        const suggestions = [];

        try {
            // Verificar arquivo principal
            const mainFilePath = path.join(botPath, mainFile);
            if (!await fs.pathExists(mainFilePath)) {
                issues.push('Arquivo principal não encontrado');
                suggestions.push('Criar arquivo index.js');
            }

            // Verificar se há token hardcoded
            if (await fs.pathExists(mainFilePath)) {
                const content = await fs.readFile(mainFilePath, 'utf8');
                if (content.includes('YOUR_TOKEN_HERE') || content.includes('SEU_TOKEN_AQUI')) {
                    issues.push('Token não configurado no código');
                    suggestions.push('Configurar token no código ou config.json');
                }
            }

            // Verificar package.json
            const packagePath = path.join(botPath, 'package.json');
            if (!await fs.pathExists(packagePath)) {
                issues.push('package.json não encontrado');
                suggestions.push('Criar package.json com dependências');
            }

            // Verificar config.json
            const configPath = path.join(botPath, 'config.json');
            if (await fs.pathExists(configPath)) {
                const config = await fs.readJSON(configPath);
                if (config.token === 'SEU_TOKEN_AQUI' || !config.token) {
                    issues.push('Token não configurado em config.json');
                    suggestions.push('Configurar token válido');
                }
            }

        } catch (error) {
            issues.push(`Erro na análise: ${error.message}`);
        }

        return { issues, suggestions };
    }

    async detectMainFile(botPath) {
        const possibleNames = ['index.js', 'main.js', 'bot.js', 'app.js', 'start.js'];

        // Verificar diretórios aninhados primeiro
        const items = await fs.readdir(botPath);
        for (const item of items) {
            const itemPath = path.join(botPath, item);
            const stat = await fs.stat(itemPath);

            if (stat.isDirectory()) {
                // Verificar se há arquivos principais no subdiretório
                for (const name of possibleNames) {
                    const nestedFile = path.join(itemPath, name);
                    if (await fs.pathExists(nestedFile)) {
                        // Mover arquivos do subdiretório para o diretório principal
                        const files = await fs.readdir(itemPath);
                        for (const file of files) {
                            const srcPath = path.join(itemPath, file);
                            const destPath = path.join(botPath, file);
                            await fs.move(srcPath, destPath, { overwrite: true });
                        }
                        await fs.remove(itemPath);
                        return name;
                    }
                }
            }
        }

        // Verificar no diretório principal
        for (const name of possibleNames) {
            const filePath = path.join(botPath, name);
            if (await fs.pathExists(filePath)) {
                return name;
            }
        }

        return 'index.js';
    }

    async listBots() {
        try {
            const items = await fs.readdir(this.botsDir);
            const bots = [];

            for (const item of items) {
                const itemPath = path.join(this.botsDir, item);
                const stat = await fs.stat(itemPath);
                if (stat.isDirectory()) {
                    bots.push(item);
                }
            }

            return bots;
        } catch {
            return [];
        }
    }

    async getBotFiles(botName) {
        try {
            const botPath = path.join(this.botsDir, botName);
            const files = [];

            const scanDir = async (dir, relativePath = '') => {
                const items = await fs.readdir(dir);

                for (const item of items) {
                    if (item === 'node_modules' || item.startsWith('.')) continue;

                    const itemPath = path.join(dir, item);
                    const stat = await fs.stat(itemPath);
                    const relativeItemPath = path.join(relativePath, item);

                    if (stat.isFile()) {
                        files.push(relativeItemPath);
                    } else if (stat.isDirectory()) {
                        await scanDir(itemPath, relativeItemPath);
                    }
                }
            };

            await scanDir(botPath);
            return files;
        } catch {
            return [];
        }
    }

    async getFileSize(filePath) {
        try {
            const stats = await fs.stat(filePath);
            const size = stats.size;

            if (size < 1024) return `${size}B`;
            if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)}KB`;
            return `${(size / (1024 * 1024)).toFixed(1)}MB`;
        } catch {
            return '0B';
        }
    }

    getBotUptime(botName) {
        const proc = this.runningBots.get(botName);
        if (!proc || !proc.startTime) return '0s';

        const uptime = Date.now() - proc.startTime;
        const seconds = Math.floor(uptime / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    botHasErrors(botName) {
        const logs = this.botLogs.get(botName) || [];
        return logs.some(log => log.includes('ERROR') || log.includes('error'));
    }

    async start(config) {
        this.config = config;

        if (!config.discord_token || config.discord_token === "SEU_TOKEN_AQUI") {
            console.log("❌ Token do Discord inválido no config.json");
            return;
        }

        console.log("🔑 Conectando ao Discord...");
        this.client.login(config.discord_token);
    }
}

// ===== INICIALIZAÇÃO DO MANAGER =====

// Inicializar o GratianManager diretamente
async function startManager() {
    const manager = new GratianManager();
    await manager.init();
}

// Executar se for chamado diretamente
if (require.main === module) {
    startManager().catch(console.error);
}

// Inicializar automaticamente
startManager().catch(console.error);

module.exports = GratianManager;