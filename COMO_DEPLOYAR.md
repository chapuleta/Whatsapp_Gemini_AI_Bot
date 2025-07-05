# 🚀 DEPLOY NO VERCEL - ASSISTENTE FINANCEIRO

## ⚠️ IMPORTANTE: 
Este bot **NÃO funciona localmente**. Foi projetado para funcionar APENAS no Vercel com webhooks do WhatsApp.

## 📋 PRÉ-REQUISITOS:
1. ✅ Conta no Vercel (vercel.com)
2. ✅ Conta Meta Developer (developers.facebook.com)
3. ✅ Número de telefone para WhatsApp Business
4. ✅ Conta no Google AI Studio (makersuite.google.com)

## 🎯 PASSO A PASSO COMPLETO:

### 🔑 PASSO 1: OBTER API KEYS

#### Google AI Studio:
1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave gerada (ex: AIza...)

#### Meta Developer (WhatsApp):
1. Acesse: https://developers.facebook.com/
2. Crie um novo app
3. Adicione produto "WhatsApp"
4. Configure API e obtenha:
   - `WA_TOKEN` (Token de acesso)
   - `PHONE_ID` (ID do número)
   - `PHONE_NUMBER` (Seu número)

### 🚀 PASSO 2: DEPLOY

```bash
# 1. Login no Vercel
vercel login

# 2. Deploy inicial
vercel

# 3. Deploy de produção
vercel --prod
```

### ⚙️ PASSO 3: CONFIGURAR VARIÁVEIS

No dashboard do Vercel (https://vercel.com/dashboard):
1. Vá no seu projeto
2. Settings > Environment Variables
3. Adicione:
   - `WA_TOKEN` = Seu token do WhatsApp
   - `GEN_API` = Sua API key do Google AI
   - `PHONE_ID` = ID do telefone
   - `PHONE_NUMBER` = Seu número

### 🔗 PASSO 4: CONFIGURAR WEBHOOK

No Meta Developer Console:
1. Webhook URL: `https://seu-projeto.vercel.app/webhook`
2. Verify Token: `BOT`
3. Webhook Fields: marque `messages`

## 📱 COMO TESTAR:

### 1. Teste básico:
Acesse: `https://seu-projeto.vercel.app/`
Deve retornar: "Bot"

### 2. Teste de gasto:
```
Você: gastei R$ 8 com pastel
Bot: Anotei o gasto de R$ 8,00 com pastel! Para completar...
Você: na cantina, sozinho, dinheiro
Bot: ✅ Gasto registrado com sucesso!
```

### 3. Comandos disponíveis:
- `resumo` - Ver gastos
- `alerta` - Ver alertas  
- `teste gasto` - Adicionar dados de exemplo
- `debug` - Informações do sistema

## ❌ SOLUÇÃO DE PROBLEMAS:

### "Bot não responde":
- ✅ Verifique se o deploy foi bem-sucedido
- ✅ Confirme URL do webhook no Meta Developer
- ✅ Verifique logs no Vercel dashboard

### "Não registra gastos":
- ✅ Teste comando `debug` primeiro
- ✅ Verifique variáveis de ambiente
- ✅ Confirme webhook conectado

### "Erro de API":
- ✅ Confirme API Key do Google AI Studio
- ✅ Verifique tokens do WhatsApp

## 💾 PERSISTÊNCIA DE DADOS:
- ✅ Dados ficam salvos durante a sessão
- ✅ Backup automático em arquivo temporário
- ⚠️ Para persistência total, integre banco de dados

## 🎉 AGORA É SÓ USAR!
Após seguir todos os passos, seu assistente financeiro estará funcionando no WhatsApp! 🚀
