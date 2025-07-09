
# 🎮 Gratian Manager

**Sistema Avançado de Gerenciamento de Múltiplos Bots Discord**

[![Discord](https://img.shields.io/badge/Discord-Bot%20Manager-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com)
[![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org)
[![AI](https://img.shields.io/badge/IA-GLM--4-9B59B6?style=for-the-badge&logo=openai&logoColor=white)](https://bigmodel.cn)

## 📋 Índice

- [🎯 Sobre](#-sobre)
- [✨ Funcionalidades](#-funcionalidades)
- [🚀 Instalação](#-instalação)
- [⚙️ Configuração](#️-configuração)
- [📖 Como Usar](#-como-usar)
- [🤖 Comandos e Funções](#-comandos-e-funções)
- [🧠 Assistente IA](#-assistente-ia)
- [📝 Editor de Arquivos](#-editor-de-arquivos)
- [📊 Monitoramento](#-monitoramento)
- [🔧 Solução de Problemas](#-solução-de-problemas)
- [🤝 Contribuição](#-contribuição)

## 🎯 Sobre

O **Gratian Manager Pro** é um sistema completo de gerenciamento de bots Discord que permite:

- 🎮 **Gerenciar múltiplos bots** em uma única interface
- 🤖 **Diagnóstico inteligente** com IA GLM-4
- 📝 **Editor de arquivos** integrado no Discord
- 📦 **Instalação automática** de dependências
- 📊 **Monitoramento em tempo real**
- 🔄 **Auto-update** do sistema

## ✨ Funcionalidades

### 🎮 Gerenciamento de Bots
- ▶️ Iniciar/Parar bots individualmente
- 🔄 Reiniciar bots com um clique
- 📜 Visualizar logs em tempo real
- 🗑️ Remover bots com confirmação

### 📦 Instalação Inteligente
- 📁 Upload via arquivo ZIP
- 🔍 Detecção automática de estrutura
- 📦 Instalação automática de dependências
- ⚠️ Diagnóstico de problemas na instalação

### 🤖 Assistente IA (GLM-4)
- 🔍 **Diagnóstico automático** de erros
- 🔧 **Configuração inteligente** de tokens
- 💡 **Sugestões de correção** específicas
- 📝 **Análise de código** completa

### 📝 Editor Integrado
- ✏️ Editar arquivos diretamente no Discord
- 💾 Backup automático antes de salvar
- 🔍 Visualização de estrutura de arquivos
- 📱 Interface responsiva via modais

### 📊 Monitoramento
- ⏱️ Uptime de cada bot
- 📈 Status em tempo real
- 📜 Logs categorizados
- 🔄 Atualização automática de status

## 🚀 Instalação

### Pré-requisitos
- Node.js 18+ instalado
- Conta Discord com bot criado
- API Key da GLM-4 (opcional, para IA)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seuusuario/gratian-manager.git
cd gratian-manager
```

2. **Instale as dependências:**
```bash
npm install
```

3. **Configure o sistema:**
```bash
node g-manager.js
```
*O sistema criará automaticamente o arquivo `config.json`*

4. **Configure suas credenciais:**
Edite o arquivo `config.json`:
```json
{
  "discord_token": "SEU_TOKEN_DO_BOT_MANAGER",
  "glm4_api_key": "SUA_API_KEY_GLM4",
  "glm4_endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
  "auto_update": true,
  "update_server": "https://seuservidor.com"
}
```

5. **Inicie o sistema:**
```bash
node g-manager.js
```

## ⚙️ Configuração

### Token do Discord
1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá em "Bot" e copie o token
4. Cole no `config.json` em `discord_token`

### API Key GLM-4 (Opcional)
1. Registre-se em [BigModel](https://bigmodel.cn)
2. Obtenha sua API Key
3. Cole no `config.json` em `glm4_api_key`

### Permissões do Bot
O bot manager precisa das seguintes permissões:
- ✅ Enviar mensagens
- ✅ Usar comandos slash
- ✅ Anexar arquivos
- ✅ Incorporar links
- ✅ Usar botões e menus

## 📖 Como Usar

### 1. Comando Principal
Use o comando `/painel` no Discord para abrir o painel principal.

### 2. Adicionando Bots
1. Clique em "📦 Adicionar Bot"
2. Envie um arquivo ZIP com seu bot
3. O sistema processará automaticamente
4. Configure o token se necessário

### 3. Gerenciando Bots
1. Clique em "🎮 Gerenciar Bots"
2. Selecione o bot desejado
3. Use os botões para controlar o bot

## 🤖 Comandos e Funções

### Comandos Slash
| Comando | Descrição |
|---------|-----------|
| `/painel` | Abre o painel principal do manager |

### Botões do Painel Principal
| Botão | Função |
|-------|--------|
| 🎮 Gerenciar Bots | Abre lista de bots instalados |
| 📦 Adicionar Bot | Instruções para adicionar novos bots |
| 📜 Ver Logs | Visualizar logs de todos os bots |
| 🤖 Assistente IA | Acesso ao diagnóstico inteligente |
| 📝 Editor de Arquivos | Editor integrado de código |
| ⚙️ Configurações | Configurações do sistema |

### Funções de Gerenciamento
| Função | Descrição |
|--------|-----------|
| `startBot(botName)` | Inicia um bot específico |
| `stopBot(botName)` | Para um bot em execução |
| `restartBot(botName)` | Reinicia um bot |
| `deleteBot(botName)` | Remove um bot completamente |
| `installDependencies(botName)` | Instala dependências npm |

## 🧠 Assistente IA

### Funcionalidades da IA
- **🔍 Diagnóstico Automático:** Analisa logs e código para identificar problemas
- **🔧 Configuração de Token:** Localiza e configura tokens automaticamente
- **💡 Sugestões de Correção:** Propõe soluções específicas para erros
- **📦 Detecção de Dependências:** Identifica módulos faltantes

### Como Usar a IA
1. Acesse "🤖 Assistente IA" no painel
2. Selecione o bot para análise
3. Escolha o tipo de diagnóstico:
   - 🔍 Diagnosticar Erros
   - 🔑 Configurar Token
   - 📦 Instalar Dependências

### Prompts Especializados
O sistema usa dois prompts diferentes:

**Diagnóstico de Erros:**
- Analisa código completo
- Examina logs de erro
- Verifica dependências
- Propõe soluções específicas

**Configuração de Token:**
- Localiza arquivos de configuração
- Identifica padrões de token
- Sugere métodos de configuração
- Gera código pronto para uso

## 📝 Editor de Arquivos

### Funcionalidades
- ✏️ **Edição Direta:** Modifique arquivos via Discord
- 💾 **Backup Automático:** Cria backup antes de salvar
- 🔍 **Navegação de Arquivos:** Explore a estrutura do bot
- 📱 **Interface Modal:** Editor responsivo e intuitivo

### Como Usar
1. Clique em "📝 Editor de Arquivos"
2. Selecione o bot desejado
3. Escolha o arquivo para editar
4. Modifique o conteúdo no modal
5. Clique em "Salvar" para aplicar mudanças

### Arquivos Suportados
- `.js` - JavaScript
- `.json` - Configurações
- `.env` - Variáveis de ambiente
- `.md` - Documentação
- `.txt` - Texto simples

## 📊 Monitoramento

### Métricas Disponíveis
- 📊 **Status em Tempo Real:** Online/Offline de cada bot
- ⏱️ **Uptime:** Tempo de atividade preciso
- 📈 **Estatísticas:** Total de bots, bots ativos
- 📜 **Logs Categorizados:** Erros, avisos, informações

### Sistema de Logs
```javascript
// Tipos de log monitorados:
- [INFO] Informações gerais
- [ERROR] Erros críticos
- [WARN] Avisos importantes
- [DEBUG] Informações de depuração
```

### Alertas Automáticos
- 🔴 Bot parou inesperadamente
- ⚠️ Erro detectado nos logs
- 📦 Dependência faltando
- 🔑 Token inválido

## 🔧 Solução de Problemas

### Problemas Comuns

#### Bot não inicia
```
❌ Erro: spawn is not defined
```
**Solução:** Verifique se o Node.js está instalado corretamente

#### Dependências não instalam
```
❌ Erro na instalação de dependências
```
**Solução:** 
1. Verifique se existe `package.json`
2. Use o botão "📦 Instalar Dependências"
3. Verifique logs de instalação

#### IA não funciona
```
❌ API Key da IA não configurada
```
**Solução:**
1. Obtenha API Key da GLM-4
2. Configure no `config.json`
3. Reinicie o manager

#### Token inválido
```
❌ Token do Discord inválido
```
**Solução:**
1. Verifique o token no Developer Portal
2. Regenere se necessário
3. Atualize `config.json`

### Debug Mode
Para ativar debug detalhado:
```javascript
// No código, adicione:
console.log('DEBUG:', variavel);
```

### Estrutura de Arquivos Recomendada
```
meubot.zip
├── index.js          # Arquivo principal
├── package.json      # Dependências
├── config.json       # Configurações
├── commands/         # Comandos (opcional)
└── events/           # Eventos (opcional)
```

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Diretrizes
- 📝 Documente novas funcionalidades
- 🧪 Teste antes de enviar
- 🎨 [Mantenha o padrão de código](https://github.com/Gratian-pro/gratian-manager/blob/main/README.md)
- 📋 Atualize o README se necessário

### Issues e Sugestões
- 🐛 [Reportar Bug](https://discord.gg/uDQfeDnhYF)
- 💡 [LINK DO SITE](https://github.com/seuusuario/gratian-manager/issues)
- ❓ [painel link](https://dashboard.gratian.pro/profile)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🎉 Agradecimentos

- [doc gratian](https://docs.gratian.pro/)
- [status gratian](https://status.gratian.pro/) 
- [gratian](https://gratian.pro/)
- [TERMOS](https://gratian.pro/terms)

---

**Desenvolvido vovo666 amor muito amor ❤️ para a comunidade Discord**

