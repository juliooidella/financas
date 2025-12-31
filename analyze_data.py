import pandas as pd
import os

def clean_currency(value):
    if isinstance(value, str):
        # Remove 'R$', replace dot with nothing, replace comma with dot
        # Watch out for cases like 1.234,56 -> 1234.56
        clean = value.replace('R$', '').strip()
        clean = clean.replace('.', '').replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return 0.0
    return value

def clean_quantity(value):
    if isinstance(value, str):
        clean = value.replace(',', '.').strip()
        try:
            return float(clean)
        except ValueError:
            return 1.0
    return value

def analyze():
    csv_path = "notas_parana_completo.csv"
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado.")
        return

    df = pd.read_csv(csv_path)
    
    # 1. Cleaning types
    df['Valor Item'] = df['Valor Item'].apply(clean_currency)
    df['Quantidade'] = df['Quantidade'].apply(clean_quantity)
    df['Produto Norm'] = df['Produto'].str.upper().str.strip()
    df['Estabelecimento Norm'] = df['Estabelecimento'].str.upper().str.strip()
    
    # Calculate Total per Line (since Valor Item is usually Unitary, but sometimes Total depending on extraction)
    # The script extracted 'Valor Item' from class 'valor'.
    # In NFC-e snippet provided earlier: 
    # <span class="RvlUnit"> Vl. Unit.: 4,25 </span> ... <span class="valor">4,25</span> (Total line value)
    # So 'Valor Item' in CSV is likely the Total Value of that line item.
    df['Total Linha'] = df['Valor Item'] 

    # 2. Overall Top Products by Frequency
    product_freq = df.groupby('Produto Norm').agg({
        'Quantidade': 'sum',
        'Total Linha': 'sum',
        'URL': 'count' # using URL count as frequency of lines
    }).rename(columns={'URL': 'Frequência'}).sort_values(by='Frequência', ascending=False)

    top_freq = product_freq.head(20)

    # 3. Top Products by Spend
    top_spend = product_freq.sort_values(by='Total Linha', ascending=False).head(20)

    # 4. Analysis by Establishment Type (Heuristic)
    def categorize_est(name):
        name = name.upper()
        if any(x in name for x in ['FARMACIA', 'DROGARIA', 'FARM', 'DROG']):
            return 'Farmácia'
        if any(x in name for x in ['SUPERMERCADO', 'MERCADO', 'ATACADO', 'SUPER', 'VILA', 'CENTER']):
            return 'Mercado'
        if any(x in name for x in ['POSTO', 'COMBUSTIVEL', 'AUTO POSTO', 'GASOLINA']):
            return 'Combustível'
        if any(x in name for x in ['RESTAURANTE', 'LANCHES', 'BURGER', 'FOOD', 'PIZZA']):
            return 'Alimentação'
        return 'Outros'

    df['Categoria Estabelecimento'] = df['Estabelecimento Norm'].apply(categorize_est)
    
    # 5. Generate Report
    report_lines = []
    report_lines.append("# Relatório de Compras - Nota Paraná\n")
    
    # Overview
    total_gasto = df['Total Linha'].sum()
    total_itens = df['Quantidade'].sum()
    report_lines.append(f"**Total Gasto Analisado**: R$ {total_gasto:,.2f}")
    report_lines.append(f"**Total de Itens**: {total_itens:,.2f}\n")

    # Top Produtos Recorrentes
    report_lines.append("## Top 20 Produtos Mais Recorrentes (Frequência)\n")
    report_lines.append("| Produto | Frequência | Qtd Total | Total Gasto |")
    report_lines.append("|---|---|---|---|")
    for prod, row in top_freq.iterrows():
        report_lines.append(f"| {prod} | {int(row['Frequência'])} | {row['Quantidade']:.2f} | R$ {row['Total Linha']:.2f} |")
    
    report_lines.append("\n## Top 20 Produtos por Maior Gasto\n")
    report_lines.append("| Produto | Total Gasto | Frequência | Qtd Total |")
    report_lines.append("|---|---|---|---|")
    for prod, row in top_spend.iterrows():
        report_lines.append(f"| {prod} | R$ {row['Total Linha']:.2f} | {int(row['Frequência'])} | {row['Quantidade']:.2f} |")

    # Category Breakdown
    report_lines.append("\n## Análise por Categoria de Estabelecimento (Estimado)\n")
    
    cats = df.groupby('Categoria Estabelecimento').agg({
        'Total Linha': 'sum',
        'Produto Norm': 'count'
    }).sort_values(by='Total Linha', ascending=False)
    
    report_lines.append("| Categoria | Total Gasto | Itens Comprados |")
    report_lines.append("|---|---|---|")
    for cat, row in cats.iterrows():
        report_lines.append(f"| {cat} | R$ {row['Total Linha']:.2f} | {row['Produto Norm']} |")

    # Deep dive into "Farmácia" and "Mercado"
    for target_cat in ['Mercado', 'Farmácia']:
        report_lines.append(f"\n### Top 10 Itens em {target_cat}\n")
        subset = df[df['Categoria Estabelecimento'] == target_cat]
        if subset.empty:
            report_lines.append(f"_Nenhum dado encontrado para {target_cat}._\n")
            continue
            
        sub_group = subset.groupby('Produto Norm').agg({
            'Quantidade': 'sum',
            'Total Linha': 'sum',
            'URL': 'count'
        }).sort_values(by='URL', ascending=False).head(10)
        
        report_lines.append("| Produto | Frequência | Total Gasto |")
        report_lines.append("|---|---|---|")
        for prod, row in sub_group.iterrows():
            report_lines.append(f"| {prod} | {int(row['URL'])} | R$ {row['Total Linha']:.2f} |")

    # Write to file
    with open("analise_compras.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    print("Relatório gerado em 'analise_compras.md'")

if __name__ == "__main__":
    analyze()
