# Configuração para deploy no Vercel
import os

# Configurações do ambiente
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

# Configurações de timeout para serverless
TIMEOUT = 30  # segundos

# Configurações de memória
MEMORY_SIZE = 512  # MB

# Configurações do bot
BOT_CONFIG = {
    'max_audio_size': 10 * 1024 * 1024,  # 10MB
    'max_image_size': 5 * 1024 * 1024,   # 5MB
    'max_response_length': 2000,          # caracteres
    'timeout': 25                         # segundos
}

# Categorias de gastos
EXPENSE_CATEGORIES = {
    'lanche': ['pastel', 'coxinha', 'hamburguer', 'salgado', 'lanche'],
    'bebida': ['refrigerante', 'suco', 'água', 'café', 'beer', 'cerveja'],
    'alimentação': ['comida', 'almoço', 'jantar', 'refeição'],
    'transporte': ['uber', 'taxi', 'ônibus', 'metrô', 'gasolina'],
    'lazer': ['cinema', 'bar', 'balada', 'diversão'],
    'compras': ['roupa', 'sapato', 'presente', 'compra'],
    'saúde': ['remédio', 'médico', 'farmácia'],
    'outros': []
}

# Palavras-chave para detectar gastos
MONEY_KEYWORDS = [
    'gastei', 'comprei', 'paguei', 'custou', 'valor', 'preço',
    'r$', 'reais', 'real', 'dinheiro', 'gasto'
]

# Alertas
ALERT_LIMITS = {
    'weekly_increase': 0.2,  # 20% de aumento semanal
    'junk_food_limit': 50,   # R$ 50 em junk food por semana
    'daily_limit': 100       # R$ 100 por dia
}

# Mensagens padrão
DEFAULT_MESSAGES = {
    'welcome': "👋 Olá! Sou seu assistente financeiro. Conte-me sobre seus gastos!",
    'expense_recorded': "✅ Gasto registrado com sucesso!",
    'need_details': "Para completar o registro, preciso de mais detalhes:",
    'error': "❌ Ops! Algo deu errado. Tente novamente.",
    'not_supported': "❌ Formato não suportado. Use texto, áudio ou imagem."
}
