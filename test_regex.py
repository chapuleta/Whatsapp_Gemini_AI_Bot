#!/usr/bin/env python3
"""
Teste específico dos padrões regex
"""
import re

# Teste do padrão regex
test_messages = [
    "gastei R$ 8 com pastel",
    "gastei r$ 8 com pastel", 
    "gastei 8 reais com pastel",
    "comprei um pastel por R$ 8",
    "R$ 8,50 pastel",
    "rs 8 pastel"
]

money_pattern = r'(?:r\$|rs|reais?)\s*(\d+(?:,\d{2})?)'

print("🧪 TESTE DO PADRÃO REGEX")
print("=" * 50)

for msg in test_messages:
    print(f"\nTeste: '{msg}'")
    
    # Teste original
    money_match = re.search(money_pattern, msg.lower())
    if money_match:
        amount = float(money_match.group(1).replace(',', '.'))
        print(f"   ✅ Valor encontrado: R$ {amount:.2f}")
    else:
        print(f"   ❌ Valor não encontrado")
    
    # Teste de item
    item_keywords = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'lanche', 'comida', 'café', 'água']
    item_found = None
    for keyword in item_keywords:
        if keyword in msg.lower():
            item_found = keyword
            break
    
    if item_found:
        print(f"   ✅ Item encontrado: {item_found}")
    else:
        print(f"   ❌ Item não encontrado")

print("\n" + "=" * 50)
print("🔍 TESTANDO PADRÕES ALTERNATIVOS")

# Padrão mais flexível
better_pattern = r'(?:r\$|rs|reais?)\s*(\d+(?:[,\.]\d{2})?)|(\d+(?:[,\.]\d{2})?)\s*(?:r\$|rs|reais?)'

for msg in test_messages:
    print(f"\nTeste: '{msg}'")
    match = re.search(better_pattern, msg.lower())
    if match:
        amount_str = match.group(1) or match.group(2)
        amount = float(amount_str.replace(',', '.'))
        print(f"   ✅ Valor encontrado: R$ {amount:.2f}")
    else:
        print(f"   ❌ Valor não encontrado")
