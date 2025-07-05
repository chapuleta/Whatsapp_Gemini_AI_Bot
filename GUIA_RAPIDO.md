# 🤖 GUIA RÁPIDO - ASSISTENTE FINANCEIRO

## ✅ PROBLEMAS CORRIGIDOS:
1. **Sistema de usuários múltiplos removido** - Agora é otimizado para um usuário único
2. **Persistência de dados funcionando** - Usando backup em arquivo temporário
3. **Comandos debug e alertas adicionados**
4. **Registro de gastos funcionando** - Testa com "teste gasto" 

## 🚀 COMO USAR:

### 1. Deploy no Vercel:
```bash
vercel --prod
```

### 2. Comandos do Bot:
- **"gastei R$ 8 com pastel"** - Registra gasto (bot vai pedir detalhes)
- **"resumo"** - Mostra gastos da semana/mês
- **"alerta"** - Verifica alertas de gastos excessivos
- **"teste gasto"** - Adiciona gastos de teste para testar o sistema
- **"debug"** - Mostra informações do sistema

### 3. Fluxo de Registro:
1. Você: "gastei R$ 8 com pastel"
2. Bot: Pede onde foi, com quem, como pagou
3. Você: "na cantina, sozinho, dinheiro"
4. Bot: Confirma o registro e mostra alertas se houver

### 4. Teste Local:
```bash
python test_local.py
```

## 🔧 FUNCIONALIDADES:
- ✅ Registro de gastos com detalhes completos
- ✅ Categorização automática (lanche, bebida, alimentação)
- ✅ Alertas de gastos excessivos
- ✅ Resumos semanais e mensais
- ✅ Backup automático dos dados
- ✅ Sistema de usuário único
- ✅ Suporte a áudio e imagem

## 📊 DADOS SALVOS:
- Data/hora do gasto
- Valor
- Item comprado
- Local
- Acompanhantes
- Forma de pagamento
- Categoria (automática)

## ⚠️ IMPORTANTE:
- No Vercel serverless, os dados persistem durante a "sessão" da função
- Para persistência total, considere integrar um banco de dados
- O backup funciona durante o tempo de vida da instância serverless

## 🎯 PRÓXIMOS PASSOS (OPCIONAL):
1. Integrar MongoDB Atlas ou Supabase para persistência total
2. Adicionar mais categorias de gastos
3. Relatórios mais detalhados
4. Metas de gastos mensais
