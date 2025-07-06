
# 📚 Documentação Técnica - Gratian Manager

## 🔧 Arquitetura do Sistema

### Classe Principal: GratianManager

```javascript
class GratianManager {
    constructor() {
        // Inicialização do cliente Discord e configurações
    }
}
```

## 🎯 Métodos Principais

### 🚀 Inicialização

#### `constructor()`
- **Função:** Inicializa o manager e configurações
- **Parâmetros:** Nenhum
- **Retorno:** Instância do GratianManager
- **Funcionalidades:**
  - Configura cliente Discord
  - Inicializa Maps para bots ativos e logs
  - Define diretórios de trabalho

#### `init()`
- **Função:** Inicialização completa do sistema
- **Processo:**
  1. Verifica arquivo config.json
  2. Cria configuração padrão se não existir
  3. Valida token Discord
  4. Verifica atualizações (se ativado)
  5. Inicia o bot manager

#### `setupDirectories()`
- **Função:** Cria estrutura de pastas necessárias
- **Diretórios criados:**
  - `/bots` - Armazena bots instalados
  - `/temp` - Arquivos temporários
  - `version.json` - Controle de versão

### 🎮 Gerenciamento de Bots

#### `startBot(interaction, botName)`
- **Função:** Inicia um bot específico
- **Parâmetros:**
  - `interaction` - Interação Discord
  - `botName` - Nome do bot a iniciar
- **Processo:**
  1. Verifica se bot já está rodando
  2. Localiza arquivo principal
  3. Executa processo filho com spawn
  4. Configura monitoramento de logs
  5. Registra processo ativo

#### `stopBot(interaction, botName)`
- **Função:** Para um bot em execução
- **Processo:**
  1. Localiza processo ativo
  2. Envia sinal de terminação
  3. Remove do registro de bots ativos
  4. Confirma parada

#### `restartBot(interaction, botName)`
- **Função:** Reinicia um bot
- **Processo:**
  1. Para o bot se estiver rodando
  2. Aguarda 1 segundo
  3. Inicia novamente

#### `deleteBot(interaction, botName)`
- **Função:** Remove completamente um bot
- **Processo:**
  1. Para o bot se ativo
  2. Remove logs da memória
  3. Deleta pasta do bot
  4. Confirma remoção

### 📦 Instalação e Upload

#### `handleZipUpload(message, attachment)`
- **Função:** Processa upload de bot via ZIP
- **Processo:**
  1. Download do arquivo ZIP
  2. Extração para pasta temporária
  3. Detecção de estrutura do bot
  4. Reorganização de arquivos se necessário
  5. Instalação de dependências
  6. Diagnóstico inicial
  7. Confirmação de instalação

#### `detectMainFile(botPath)`
- **Função:** Identifica arquivo principal do bot
- **Arquivos verificados:** `index.js`, `main.js`, `bot.js`, `app.js`, `start.js`
- **Processo:**
  1. Verifica subdiretórios primeiro
  2. Move arquivos para raiz se necessário
  3. Procura no diretório principal
  4. Retorna primeiro arquivo encontrado

#### `installDependencies(interaction, botName)`
- **Função:** Instala dependências npm do bot
- **Processo:**
  1. Verifica existência de package.json
  2. Executa `npm install` no diretório do bot
  3. Monitora output e erros
  4. Reporta resultado da instalação

### 🤖 Sistema de IA

#### `aiFix(interaction, botName)`
- **Função:** Diagnóstico inteligente com IA
- **Análise realizada:**
  - Logs de erro dos últimos registros
  - Conteúdo dos arquivos principais
  - Estrutura do package.json
  - Dependências instaladas
  - Status atual do bot

**Prompt utilizado:**
```javascript
const diagnosticPrompt = `
SISTEMA DE DIAGNÓSTICO AVANÇADO

🤖 BOT: ${botName}
📊 STATUS: ${isRunning ? 'ONLINE' : 'OFFLINE'}
📜 LOGS DE ERRO: ${errorLogs}
💻 ANÁLISE DE CÓDIGO: ${codeAnalysis}

TAREFA: Diagnóstico completo e soluções específicas
`;
```

#### `aiConfigureToken(interaction, botName)`
- **Função:** Configuração inteligente de tokens
- **Processo:**
  1. Analisa TODOS os arquivos do bot
  2. Identifica padrões de token
  3. Localiza melhores pontos de configuração
  4. Gera código pronto para uso
  5. Sugere método de configuração

**Arquivos analisados:**
- `.js` - Arquivos JavaScript
- `.json` - Arquivos de configuração
- `.env` - Variáveis de ambiente

### 📝 Editor de Arquivos

#### `editFile(interaction, botName, fileName)`
- **Função:** Abre editor para arquivo específico
- **Processo:**
  1. Lê conteúdo do arquivo
  2. Trunca se muito grande (>3000 chars)
  3. Cria modal de edição
  4. Popula com conteúdo atual

#### `handleModalSubmit(interaction)`
- **Função:** Processa salvamento de arquivo editado
- **Processo:**
  1. Extrai conteúdo do modal
  2. Cria backup do arquivo original
  3. Salva novo conteúdo
  4. Confirma operação

### 📊 Monitoramento e Logs

#### `getBotUptime(botName)`
- **Função:** Calcula tempo de atividade do bot
- **Retorno:** String formatada (ex: "2h 30m", "45s")
- **Cálculo:**
  ```javascript
  const uptime = Date.now() - proc.startTime;
  // Conversão para horas, minutos, segundos
  ```

#### Sistema de Logs
- **Armazenamento:** Map na memória (`this.botLogs`)
- **Limite:** 100 registros por bot
- **Tipos capturados:**
  - stdout - Saída padrão
  - stderr - Erros
  - Eventos de sistema

#### `botHasErrors(botName)`
- **Função:** Verifica se bot tem erros nos logs
- **Critério:** Presença de "ERROR" ou "error" nos logs

### 🔍 Utilitários

#### `listBots()`
- **Função:** Lista todos os bots instalados
- **Retorno:** Array com nomes dos bots
- **Filtros:** Apenas diretórios válidos

#### `getBotFiles(botName)`
- **Função:** Lista arquivos de um bot específico
- **Exclusões:** 
  - `node_modules`
  - Arquivos ocultos (começam com .)
- **Recursivo:** Varre subdiretórios

#### `getFileSize(filePath)`
- **Função:** Calcula tamanho formatado de arquivo
- **Formatos:** B, KB, MB
- **Retorno:** String formatada (ex: "2.5KB")

### 📋 Interfaces e Menus

#### `showMainPanel(interaction)`
- **Função:** Exibe painel principal
- **Componentes:**
  - Embed com estatísticas
  - Botões de navegação
  - Status do sistema

#### `showBotsManagement(interaction)`
- **Função:** Menu de gerenciamento de bots
- **Funcionalidades:**
  - Lista bots com status
  - Menu de seleção
  - Indicadores visuais

#### `showBotDetails(interaction, botName)`
- **Função:** Detalhes completos de um bot
- **Informações:**
  - Status e uptime
  - Arquivos e logs
  - Botões de controle

### 🔄 Atualizações

#### `checkForUpdates(updateServer)`
- **Função:** Verifica e aplica atualizações
- **Processo:**
  1. Consulta servidor de atualizações
  2. Compara versões
  3. Download se nova versão disponível
  4. Extração e aplicação
  5. Reinicialização automática

## 🔧 Configurações

### Arquivo config.json
```json
{
  "discord_token": "Token do bot manager",
  "glm4_api_key": "API key da IA",
  "glm4_endpoint": "Endpoint da API GLM-4",
  "auto_update": true,
  "update_server": "URL do servidor de updates"
}
```

### Variáveis de Ambiente
- `NODE_ENV` - Ambiente de execução
- `DEBUG` - Modo debug (opcional)

## 🚨 Tratamento de Erros

### Try-Catch Blocks
Todos os métodos principais implementam tratamento de erro:
```javascript
try {
    // Operação principal
} catch (error) {
    console.error('Erro específico:', error);
    await interaction.reply('Mensagem de erro amigável');
}
```

### Logs de Sistema
- Erros são logados no console
- Mensagens amigáveis para usuários
- Fallbacks para operações críticas

## 📈 Performance

### Otimizações Implementadas
- **Maps** para acesso rápido a dados
- **Limite de logs** para controle de memória
- **Truncamento de arquivos** grandes
- **Limpeza automática** de arquivos temporários

### Monitoramento de Recursos
- Processos filhos são rastreados
- Limpeza automática em falhas
- Controle de memória nos logs

## 🔐 Segurança

### Validações
- Nomes de bots são sanitizados
- Caminhos de arquivo são validados
- Tokens são mascarados nos logs

### Isolamento
- Cada bot roda em processo separado
- Diretórios isolados por bot
- Permissões limitadas

---

**Esta documentação técnica cobre todos os aspectos internos do Gratian Manager Pro** 🚀
