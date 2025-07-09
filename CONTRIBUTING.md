
# 🤝 Guia de Contribuição - Gratian Manager Pro

Obrigado por considerar contribuir para o Gratian Manager Pro! 

## 🎯 Como Contribuir

### 1. 🍴 Fork do Projeto
```bash
# Clone seu fork
git clone https://github.com/seuusuario/gratian-manager-pro.git
cd gratian-manager-pro

# Adicione o repositório original como upstream
git remote add upstream https://github.com/usuario-original/gratian-manager-pro.git
```

### 2. 🌿 Crie uma Branch
```bash
# Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade

# Ou para correção de bug
git checkout -b fix/correcao-bug
```

### 3. 🔧 Desenvolvimento

#### Configuração do Ambiente
```bash
# Instale dependências
npm install

# Configure seu config.json
cp config.example.json config.json
# Edite config.json com suas credenciais
```

#### Padrões de Código
- Use **camelCase** para variáveis e funções
- Use **PascalCase** para classes
- Comentários em português para documentação
- ESLint será configurado em breve

#### Estrutura de Commits
```bash
# Formato: tipo(escopo): descrição

feat(ai): adiciona diagnóstico avançado
fix(bot): corrige erro de inicialização
docs(readme): atualiza documentação
style(ui): melhora interface de botões
```

### 4. 🧪 Testes
```bash
# Execute testes locais
npm test

# Teste manualmente no Discord
node g-manager.js
```

### 5. 📝 Documentação
- Atualize README.md se necessário
- Documente novas funcionalidades
- Mantenha TECHNICAL_DOCS.md atualizado

### 6. 🚀 Pull Request
```bash
# Commit suas mudanças
git commit -m "feat(ai): adiciona nova funcionalidade"

# Push para sua branch
git push origin feature/nova-funcionalidade
```

Depois crie um Pull Request no GitHub com:
- Título descritivo
- Descrição detalhada das mudanças
- Screenshots se applicable
- Lista de testes realizados

## 🐛 Reportando Bugs

### Template de Bug Report
```markdown
**Descrição do Bug**
Descrição clara do que está acontecendo.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente**
- OS: [ex. Windows 10]
- Node.js: [ex. 18.17.0]
- Discord.js: [ex. 14.16.3]
```

## 💡 Sugerindo Features

### Template de Feature Request
```markdown
**Problema Relacionado**
Descreva o problema que esta feature resolveria.

**Solução Proposta**
Descrição clara da solução que você gostaria.

**Alternativas Consideradas**
Outras soluções que você considerou.

**Informações Adicionais**
Qualquer contexto adicional sobre a feature.
```

## 📋 Checklist para Contributors

### Antes de Enviar PR
- [ ] Código está funcionando localmente
- [ ] Comentários adicionados onde necessário
- [ ] Documentação atualizada
- [ ] Testes realizados
- [ ] Commit messages seguem padrão
- [ ] Branch está atualizada com main

### Code Review
- [ ] Código segue padrões do projeto
- [ ] Funcionalidade está bem testada
- [ ] Não quebra funcionalidades existentes
- [ ] Performance não foi impactada negativamente

## 🏷️ Labels do GitHub

| Label | Uso |
|-------|-----|
| `bug` | Relatórios de bugs |
| `enhancement` | Novas funcionalidades |
| `documentation` | Melhorias na documentação |
| `good first issue` | Bom para iniciantes |
| `help wanted` | Precisa de ajuda |
| `priority-high` | Alta prioridade |
| `priority-low` | Baixa prioridade |

## 🎨 Diretrizes de UI

### Padrões de Embeds
```javascript
// Cores padrão
const cores = {
  sucesso: 0x4ECDC4,
  erro: 0xFF6B6B,
  aviso: 0xFFB347,
  info: 0x3498DB,
  ia: 0x9B59B6
};

// Emojis padrão
const emojis = {
  sucesso: '✅',
  erro: '❌',
  aviso: '⚠️',
  info: 'ℹ️',
  bot: '🤖'
};
```

### Padrões de Botões
- **Primary**: Ações principais (iniciar, salvar)
- **Success**: Ações positivas (adicionar, confirmar)
- **Danger**: Ações destrutivas (deletar, parar)
- **Secondary**: Ações secundárias (visualizar, configurar)

## 🤖 Contribuindo com IA

### Melhorias no Sistema de IA
- Novos prompts especializados
- Melhorias na análise de código
- Suporte a mais linguagens
- Otimizações de performance

### Prompts de Qualidade
```javascript
// Exemplo de prompt bem estruturado
const prompt = `
CONTEXTO: [contexto específico]
DADOS: [dados relevantes]
TAREFA: [tarefa específica]
FORMATO: [formato de resposta]
`;
```

## 🏆 Reconhecimento

Contributors são listados no README.md e recebem:
- 🎖️ Badge de contributor
- 📝 Menção nos releases
- 🤝 Convite para equipe de maintainers (contributors ativos)

## 📞 Contato

- **Discord**: [Server de Desenvolvimento]([https://discord.gg/seuservidor](https://discord.gg/uDQfeDnhYF))
- **GitHub Issues**: Para bugs e features
- **GitHub Discussions**: Para perguntas gerais

---

**Obrigado por contribuir com o Gratian Manager Pro!** 🚀
