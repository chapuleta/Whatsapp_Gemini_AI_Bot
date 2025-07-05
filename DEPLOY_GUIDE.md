# Deploy Otimizado para Vercel

## Problema Resolvido
✅ **Conflicting functions and builds configuration** - Removido o conflito entre `functions` e `builds` no vercel.json

## Otimizações Aplicadas

### 1. Redução de Tamanho
- ❌ Removido `pandas` (30MB+)
- ❌ Removido `pymupdf` (50MB+)
- ❌ Removido `csv` imports desnecessários
- ✅ Mantido apenas essenciais: `flask`, `google-generativeai`, `requests`

### 2. Configuração Serverless
- ✅ Dados em memória (temporário)
- ✅ Processamento otimizado de mídia
- ✅ Limpeza automática de arquivos
- ✅ Configuração simplificada

### 3. Arquivos Otimizados
- `main.py` - Código principal otimizado
- `requirements.txt` - Apenas dependências essenciais
- `vercel.json` - Configuração corrigida
- `.vercelignore` - Exclui arquivos desnecessários

## Como Deployar

### 1. Configurar Variáveis de Ambiente no Vercel
```bash
WA_TOKEN=seu_token_whatsapp
GEN_API=sua_chave_gemini
PHONE_ID=seu_phone_id
PHONE_NUMBER=seu_numero
```

### 2. Deploy
```bash
# Instalar Vercel CLI se não tiver
npm i -g vercel

# Fazer deploy
vercel --prod
```

### 3. Verificar
- URL do webhook: `https://seu-projeto.vercel.app/webhook`
- Teste básico: `https://seu-projeto.vercel.app/` (deve retornar "Bot")

## Limitações Temporárias

⚠️ **Dados em Memória**: Gastos são perdidos quando o servidor reinicia
⚠️ **Sem Persistência**: Para produção, adicionar banco de dados

## Próximos Passos (Opcional)

### Para Produção Completa:
1. **Banco de Dados**: MongoDB Atlas (gratuito)
2. **Armazenamento**: Cloudinary para imagens
3. **Cache**: Redis para performance

### Exemplo de Conexão com MongoDB:
```python
# Adicionar ao requirements.txt
# pymongo==4.6.0

# No código
from pymongo import MongoClient
client = MongoClient(os.environ.get('MONGODB_URI'))
db = client.financial_assistant
```

## Tamanho Final
- **Antes**: ~250MB+ (excedia limite)
- **Depois**: ~15MB (bem dentro do limite)

## Funcionalidades Mantidas
✅ Registro de gastos via texto/áudio
✅ Categorização automática  
✅ Alertas de gastos excessivos
✅ Comparações semanais
✅ Processamento de mídia
✅ Comandos especiais (resumo, alerta, meta)

Deploy pronto! 🚀
