# 💰 Assistente Financeiro WhatsApp

Um bot inteligente para WhatsApp que ajuda você a controlar seus gastos, registrar compras e ter mais consciência financeira.

## 🚀 Funcionalidades

### 📝 Registro de Gastos
- **Automático**: Diga "gastei R$ 8 com um pastel" e o bot registra automaticamente
- **Detalhado**: Pergunta onde você estava, com quem, forma de pagamento
- **Categorização**: Classifica automaticamente em categorias (lanche, alimentação, transporte, etc.)

### 📊 Relatórios e Análises
- **Resumo semanal/mensal**: Compare seus gastos com períodos anteriores
- **Gastos por categoria**: Veja onde você mais gasta dinheiro
- **Análise de junk food**: Alertas específicos para gastos com lanches e fast food

### ⚠️ Alertas Inteligentes
- **Gastos excessivos**: Avisa quando você gasta mais que o normal
- **Padrões ruins**: Identifica quando você está gastando muito com junk food
- **Comparações**: "Você gastou 30% a mais esta semana!"

### 🎯 Intenções de Compra
- **Registro de objetivos**: Anote o que você quer comprar
- **Comparações inteligentes**: "O dinheiro dos 2 pastéis daria para comprar a espuma do fone!"
- **Controle de prioridades**: Ajuda a focar no que realmente importa

## 🛠️ Como Usar

### Comandos Básicos

1. **Registrar um gasto**:
   ```
   "Gastei R$ 15 com hamburguer"
   "Comprei um refrigerante por R$ 5"
   ```

2. **Ver relatório**:
   ```
   "resumo"
   "relatório"
   ```

3. **Verificar alertas**:
   ```
   "alerta"
   ```

4. **Gerenciar objetivos**:
   ```
   "meta"
   "objetivo"
   ```

### Exemplos de Uso

**Registrando um gasto:**
```
Você: "Gastei R$ 8 com um pastel"
Bot: "💰 Anotei o gasto de R$ 8,00 com pastel!
Para completar o registro, me conta:
- 📍 Onde você estava?
- 👥 Com quem você estava?
- 💳 Como você pagou?"

Você: "Na faculdade, com o João, paguei em dinheiro"
Bot: "✅ Gasto registrado com sucesso!"
```

**Recebendo alertas:**
```
Bot: "⚠️ Você gastou R$ 45,00 esta semana, 25% a mais que a semana passada!"
Bot: "🍔 Você gastou R$ 32,00 com junk food esta semana!"
```

## 📁 Estrutura dos Dados

Os dados são salvos em arquivos CSV:

### expenses.csv
- **data**: Data e hora do gasto
- **valor**: Valor em reais
- **nome**: Nome do item/produto
- **local**: Onde foi feita a compra
- **acompanhantes**: Com quem você estava
- **forma_pagamento**: Como pagou (dinheiro, cartão, pix, etc.)
- **categoria**: Categoria automática (lanche, alimentação, etc.)

### intentions.csv
- **item**: O que você quer comprar
- **valor**: Valor estimado
- **data_criacao**: Quando registrou a intenção
- **ativo**: Se ainda está ativo

## 🔧 Configuração

### Variáveis de Ambiente
```bash
WA_TOKEN=seu_token_whatsapp
GEN_API=sua_chave_gemini
PHONE_ID=id_do_telefone
PHONE_NUMBER=seu_numero
```

### Dependências
```bash
pip install -r requirements.txt
```

### Execução
```bash
python main.py
```

## 💡 Dicas de Uso

1. **Seja específico**: Quanto mais detalhes você der, melhor será o controle
2. **Use regularmente**: Registre todos os gastos para ter dados precisos
3. **Defina objetivos**: Registre suas intenções de compra para melhor controle
4. **Verifique alertas**: Preste atenção nos avisos do bot

## 🤖 Inteligência Artificial

O bot usa o **Gemini AI** para:
- Entender mensagens de áudio automaticamente
- Processar linguagem natural
- Categorizar gastos automaticamente
- Gerar insights personalizados

## 📱 Compatibilidade

- ✅ Mensagens de texto
- ✅ Mensagens de áudio (transcrição automática)
- ✅ Imagens (análise de conteúdo)
- ✅ Documentos PDF

## 🔒 Privacidade

- Todos os dados ficam no seu servidor
- Não há compartilhamento de informações pessoais
- Controle total sobre seus dados financeiros

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as variáveis de ambiente estão configuradas
2. Confirme se o webhook está funcionando
3. Teste com mensagens simples primeiro

---

*Desenvolvido para ajudar você a ter mais consciência e controle financeiro! 💰*
