# Configurações do Assistente Financeiro

# Categorias de junk food (para alertas especiais)
JUNK_FOOD_CATEGORIES = [
    'lanche', 'pastel', 'hamburguer', 'refrigerante', 
    'coxinha', 'salgado', 'doce', 'sorvete', 'batata frita'
]

# Categorias automáticas baseadas em palavras-chave
CATEGORY_KEYWORDS = {
    'alimentação': ['comida', 'almoço', 'jantar', 'refeição', 'restaurante'],
    'lanche': ['lanche', 'pastel', 'coxinha', 'salgado', 'hamburguer'],
    'bebida': ['refrigerante', 'suco', 'água', 'café', 'cerveja'],
    'transporte': ['uber', 'ônibus', 'metrô', 'gasolina', 'combustível'],
    'lazer': ['cinema', 'bar', 'balada', 'jogo', 'diversão'],
    'educação': ['livro', 'curso', 'faculdade', 'material'],
    'saúde': ['remédio', 'médico', 'farmácia', 'hospital'],
    'casa': ['mercado', 'supermercado', 'limpeza', 'conta'],
    'roupas': ['roupa', 'sapato', 'calça', 'camisa', 'tênis'],
    'tecnologia': ['fone', 'celular', 'carregador', 'cabo', 'eletrônicos']
}

# Limites para alertas
ALERT_THRESHOLDS = {
    'weekly_increase_percent': 20,  # % de aumento semanal para alertar
    'junk_food_weekly_limit': 50,   # Valor limite semanal para junk food
    'frequency_multiplier': 1.5     # Multiplicador para alertar sobre frequência
}

# Mensagens personalizadas
MESSAGES = {
    'expense_registered': "✅ *Gasto registrado com sucesso!*",
    'ask_details': "Para completar o registro, me conta:",
    'location_prompt': "📍 Onde você estava?",
    'companions_prompt': "👥 Com quem você estava?",
    'payment_prompt': "💳 Como você pagou? (dinheiro, cartão, pix, etc.)",
    'no_expenses': "📊 Ainda não há gastos registrados!",
    'no_alerts': "✅ Tudo sob controle! Nenhum alerta no momento.",
    'weekly_increase_alert': "⚠️ Você gastou *R$ {this_week:.2f}* esta semana, {increase:.1f}% a mais que a semana passada!",
    'junk_food_alert': "🍔 Você gastou *R$ {amount:.2f}* com junk food esta semana!",
    'frequency_alert': "📊 Você fez {this_week} compras esta semana, muito mais que as {last_week} da semana passada!"
}

# Configurações de arquivos
FILES = {
    'expenses': 'expenses.csv',
    'intentions': 'intentions.csv'
}

# Formato de data padrão
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
