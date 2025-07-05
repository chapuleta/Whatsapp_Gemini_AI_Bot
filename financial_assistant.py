import pandas as pd
import csv
from datetime import datetime, timedelta
import os

class FinancialAssistant:
    def __init__(self, expenses_file="expenses.csv", intentions_file="intentions.csv"):
        self.expenses_file = expenses_file
        self.intentions_file = intentions_file
        self.init_csv_files()
    
    def init_csv_files(self):
        """Inicializa os arquivos CSV se não existirem"""
        if not os.path.exists(self.expenses_file):
            with open(self.expenses_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['data', 'valor', 'nome', 'local', 'acompanhantes', 'forma_pagamento', 'categoria'])
        
        if not os.path.exists(self.intentions_file):
            with open(self.intentions_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['item', 'valor', 'data_criacao', 'ativo'])
    
    def save_expense(self, date, amount, item, location, companions, payment_method, category):
        """Salva um gasto no arquivo CSV"""
        with open(self.expenses_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date, amount, item, location, companions, payment_method, category])
    
    def save_intention(self, item, amount):
        """Salva uma intenção de compra"""
        with open(self.intentions_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([item, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True])
    
    def get_expenses_dataframe(self):
        """Retorna o DataFrame com os gastos"""
        if not os.path.exists(self.expenses_file):
            return pd.DataFrame()
        
        df = pd.read_csv(self.expenses_file)
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
        return df
    
    def get_weekly_comparison(self):
        """Compara gastos desta semana com a semana passada"""
        df = self.get_expenses_dataframe()
        if df.empty:
            return None
        
        now = datetime.now()
        
        # Esta semana
        this_week_start = now - timedelta(days=now.weekday())
        this_week = df[df['data'] >= this_week_start]
        
        # Semana passada
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start
        last_week = df[(df['data'] >= last_week_start) & (df['data'] < last_week_end)]
        
        return {
            'this_week_total': this_week['valor'].sum(),
            'last_week_total': last_week['valor'].sum(),
            'this_week_count': len(this_week),
            'last_week_count': len(last_week)
        }
    
    def get_monthly_comparison(self):
        """Compara gastos deste mês com o mês passado"""
        df = self.get_expenses_dataframe()
        if df.empty:
            return None
        
        now = datetime.now()
        
        # Este mês
        this_month = df[df['data'].dt.month == now.month]
        
        # Mês passado
        last_month_date = now.replace(day=1) - timedelta(days=1)
        last_month = df[df['data'].dt.month == last_month_date.month]
        
        return {
            'this_month_total': this_month['valor'].sum(),
            'last_month_total': last_month['valor'].sum(),
            'this_month_count': len(this_month),
            'last_month_count': len(last_month)
        }
    
    def get_category_analysis(self, period_days=30):
        """Análise de gastos por categoria"""
        df = self.get_expenses_dataframe()
        if df.empty:
            return None
        
        # Últimos N dias
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_expenses = df[df['data'] >= cutoff_date]
        
        category_stats = recent_expenses.groupby('categoria').agg({
            'valor': ['sum', 'count', 'mean'],
            'data': 'max'
        }).round(2)
        
        return category_stats
    
    def get_junk_food_analysis(self):
        """Análise específica de gastos com junk food"""
        df = self.get_expenses_dataframe()
        if df.empty:
            return None
        
        junk_categories = ['lanche', 'pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
        
        # Esta semana
        this_week = df[df['data'] >= datetime.now() - timedelta(days=7)]
        this_week_junk = this_week[this_week['categoria'].isin(junk_categories)]
        
        # Semana passada
        last_week = df[(df['data'] >= datetime.now() - timedelta(days=14)) & 
                       (df['data'] < datetime.now() - timedelta(days=7))]
        last_week_junk = last_week[last_week['categoria'].isin(junk_categories)]
        
        return {
            'this_week_junk_total': this_week_junk['valor'].sum(),
            'last_week_junk_total': last_week_junk['valor'].sum(),
            'this_week_junk_count': len(this_week_junk),
            'last_week_junk_count': len(last_week_junk),
            'junk_items': this_week_junk['nome'].tolist()
        }
    
    def get_spending_alerts(self):
        """Gera alertas baseados nos padrões de gastos"""
        alerts = []
        
        # Comparação semanal
        weekly_comp = self.get_weekly_comparison()
        if weekly_comp and weekly_comp['last_week_total'] > 0:
            increase_pct = ((weekly_comp['this_week_total'] / weekly_comp['last_week_total']) - 1) * 100
            if increase_pct > 20:
                alerts.append(f"⚠️ Você gastou *R$ {weekly_comp['this_week_total']:.2f}* esta semana, {increase_pct:.1f}% a mais que a semana passada!")
        
        # Análise de junk food
        junk_analysis = self.get_junk_food_analysis()
        if junk_analysis and junk_analysis['this_week_junk_total'] > 50:
            alerts.append(f"🍔 Você gastou *R$ {junk_analysis['this_week_junk_total']:.2f}* com junk food esta semana!")
        
        # Frequência de gastos
        weekly_comp = self.get_weekly_comparison()
        if weekly_comp and weekly_comp['this_week_count'] > weekly_comp['last_week_count'] * 1.5:
            alerts.append(f"📊 Você fez {weekly_comp['this_week_count']} compras esta semana, muito mais que as {weekly_comp['last_week_count']} da semana passada!")
        
        return alerts
    
    def compare_with_intentions(self):
        """Compara gastos pequenos com intenções de compra"""
        if not os.path.exists(self.intentions_file):
            return []
        
        intentions_df = pd.read_csv(self.intentions_file)
        active_intentions = intentions_df[intentions_df['ativo'] == True]
        
        if active_intentions.empty:
            return []
        
        # Gastos da semana com junk food
        junk_analysis = self.get_junk_food_analysis()
        
        comparisons = []
        for _, intention in active_intentions.iterrows():
            if junk_analysis and junk_analysis['this_week_junk_total'] >= intention['valor']:
                comparisons.append({
                    'intention_item': intention['item'],
                    'intention_value': intention['valor'],
                    'junk_total': junk_analysis['this_week_junk_total'],
                    'message': f"💡 O dinheiro que você gastou com junk food esta semana (R$ {junk_analysis['this_week_junk_total']:.2f}) daria para comprar {intention['item']} (R$ {intention['valor']:.2f})!"
                })
        
        return comparisons
    
    def get_summary_report(self):
        """Gera um relatório resumido completo"""
        df = self.get_expenses_dataframe()
        if df.empty:
            return "📊 Nenhum gasto registrado ainda!"
        
        # Estatísticas básicas
        total_expenses = df['valor'].sum()
        avg_expense = df['valor'].mean()
        most_expensive = df.loc[df['valor'].idxmax()]
        
        # Gastos por categoria
        category_totals = df.groupby('categoria')['valor'].sum().sort_values(ascending=False)
        
        # Comparações
        weekly_comp = self.get_weekly_comparison()
        
        report = f"📊 *Relatório Financeiro*\n\n"
        report += f"💰 Total gasto: R$ {total_expenses:.2f}\n"
        report += f"📈 Gasto médio: R$ {avg_expense:.2f}\n"
        report += f"🎯 Maior gasto: R$ {most_expensive['valor']:.2f} em {most_expensive['nome']}\n\n"
        
        report += "*Gastos por categoria:*\n"
        for category, amount in category_totals.head(5).items():
            report += f"- _{category}_: R$ {amount:.2f}\n"
        
        if weekly_comp:
            report += f"\n*Comparação semanal:*\n"
            report += f"- Esta semana: R$ {weekly_comp['this_week_total']:.2f}\n"
            report += f"- Semana passada: R$ {weekly_comp['last_week_total']:.2f}\n"
        
        return report
