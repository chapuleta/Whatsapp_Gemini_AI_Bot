# 🧪 Guia de Testes - Assistente Financeiro

## 🔧 Problema Corrigido
✅ **Persistência de dados**: Implementado sistema de arquivos temporários no Vercel

## 📋 Testes para Fazer

### 1. **Teste Básico de Funcionamento**
```
Você: "Oi"
Bot: Deve responder como assistente financeiro
```

### 2. **Teste de Debug (IMPORTANTE)**
```
Você: "debug"
Bot: Deve mostrar:
- 📊 Gastos armazenados: 0
- 🎯 Intenções armazenadas: 0
- 💾 Estado da sessão: X usuários ativos
```

### 3. **Teste de Registro de Gasto**
```
Você: "gastei R$ 15 com hamburguer"
Bot: Deve pedir detalhes (onde, com quem, pagamento)

Você: "no shopping, sozinho, cartão"
Bot: Deve confirmar salvamento e mostrar "Total de gastos: 1"
```

### 4. **Teste de Verificação**
```
Você: "debug"
Bot: Deve mostrar "Gastos armazenados: 1" e os detalhes
```

### 5. **Teste de Relatório**
```
Você: "resumo"
Bot: Deve mostrar o gasto registrado
```

### 6. **Teste com Múltiplos Gastos**
```
Repita o processo com:
- "gastei R$ 8 com pastel"
- "comprei um refrigerante por R$ 5"
- etc.
```

## 🚨 **Se Os Testes Falharem**

### Problema 1: Debug mostra "0 gastos"
**Causa**: Sistema de arquivos não funciona no Vercel
**Solução**: Implementar banco de dados

### Problema 2: Erro ao salvar
**Causa**: Permissões no /tmp
**Solução**: Tentar path alternativo

### Problema 3: Dados perdidos entre mensagens
**Causa**: Função serverless reinicia
**Solução**: Normal no ambiente serverless

## 💡 **Comandos de Teste**

| Comando | Função |
|---------|--------|
| `debug` | Ver estado do sistema |
| `resumo` | Ver gastos salvos |
| `alerta` | Ver alertas financeiros |
| `gastei R$ X com Y` | Registrar gasto |

## 🔄 **Fluxo de Teste Completo**

1. **Deploy** no Vercel
2. **Teste**: `debug` (deve mostrar 0 gastos)
3. **Registre**: `gastei R$ 10 com pastel`
4. **Complete**: detalhes solicitados
5. **Verifique**: `debug` (deve mostrar 1 gasto)
6. **Relatório**: `resumo` (deve mostrar o gasto)
7. **Repita**: com mais gastos

## 📊 **Resultados Esperados**

✅ **Funcionando**: Dados persistem durante a conversa
⚠️ **Limitado**: Dados podem ser perdidos entre deployments
❌ **Falhando**: Precisa implementar banco de dados

## 🛠️ **Próximos Passos**

Se os testes falharem, podemos implementar:
1. **MongoDB Atlas** (gratuito, 512MB)
2. **Supabase** (gratuito, PostgreSQL)
3. **Vercel KV** (Redis, pago)

Teste e me avise os resultados! 🚀
