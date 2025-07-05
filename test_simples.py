#!/usr/bin/env python3
"""
Teste simples direto das funções
"""
import sys
import os
from datetime import datetime

# Simular variáveis de ambiente
os.environ['WA_TOKEN'] = 'test_token'
os.environ['GEN_API'] = 'test_api'
os.environ['PHONE_ID'] = 'test_phone_id'
os.environ['PHONE_NUMBER'] = 'test_phone'

# Configurar o PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar funções para testar
try:
    print("🧪 TESTE SIMPLES DE FUNÇÕES")
    print("=" * 50)
    
    # Importar apenas as funções necessárias
    exec(open('main.py').read())
    
    print("\n1. Testando detecção de gasto:")
    prompt = "gastei r$ 8 com pastel"
    
    # Simular a lógica do bot
    import re
    money_pattern = r'(?:r\$|rs|reais?)\s*(\d+(?:,\d{2})?)'
    money_match = re.search(money_pattern, prompt)
    
    if money_match:
        amount = float(money_match.group(1).replace(',', '.'))
        print(f"   ✅ Valor detectado: R$ {amount:.2f}")
        
        # Extrair item
        item_keywords = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'lanche', 'comida', 'café', 'água']
        item_found = None
        for keyword in item_keywords:
            if keyword in prompt:
                item_found = keyword
                break
        
        if item_found:
            print(f"   ✅ Item detectado: {item_found}")
            
            # Simular pending_expense
            pending_expense = {
                'amount': amount,
                'item': item_found,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            print(f"   ✅ Gasto pendente criado: {pending_expense}")
            
            # Simular resposta com detalhes
            details = "na cantina, sozinho, dinheiro"
            print(f"\n2. Processando detalhes: '{details}'")
            
            # Extrair informações
            location = "cantina"
            companions = "sozinho"
            payment_method = "dinheiro"
            
            # Categorizar
            junk_foods = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
            category = 'lanche' if item_found in junk_foods else 'alimentação'
            
            # Salvar gasto
            print(f"\n3. Salvando gasto...")
            print(f"   Gastos antes: {len(EXPENSES_DATA)}")
            
            success = save_expense(
                pending_expense['date'],
                pending_expense['amount'],
                pending_expense['item'],
                location,
                companions,
                payment_method,
                category
            )
            
            print(f"   Gastos depois: {len(EXPENSES_DATA)}")
            
            if EXPENSES_DATA:
                print(f"   ✅ Gasto salvo com sucesso!")
                ultimo_gasto = EXPENSES_DATA[-1]
                print(f"   Dados: {ultimo_gasto}")
                
                # Testar resumo
                print(f"\n4. Testando resumo...")
                summary = get_expenses_summary()
                if summary:
                    print(f"   ✅ Resumo gerado:")
                    print(f"   Total gastos: {summary['total_expenses']}")
                    print(f"   Valor semanal: R$ {summary['this_week_total']:.2f}")
                    print(f"   Categorias: {summary['category_spending']}")
                else:
                    print(f"   ❌ Erro ao gerar resumo")
            else:
                print(f"   ❌ Gasto não foi salvo")
        else:
            print(f"   ❌ Item não detectado")
    else:
        print(f"   ❌ Valor não detectado")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
