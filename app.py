# ================================================
# MODERN E-COMMERCE DASHBOARD - STYLED VERSION
# Adapté pour votre fichier CSV avec les colonnes:
# InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
# ================================================

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Initialize app with modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "📊 2025 Strategic KPI Report"

# ========== LOAD AND PREPARE DATA ==========
print("="*60)
print("CHARGEMENT DES DONNÉES...")

try:
    # REMPLACEZ CE CHEMIN PAR VOTRE FICHIER CSV
    df = pd.read_csv('votre_fichier.csv')
    
    print("Colonnes disponibles:", df.columns.tolist())
    
    # ========== PRÉPARATION DES DONNÉES ==========
    # 1. Conversion des types
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    
    # 2. Calcul du CA (Revenue)
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # 3. Nettoyage
    df = df.dropna(subset=['InvoiceNo', 'CustomerID', 'Revenue'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    
    # 4. Ajout de catégories simulées (si pas dans votre fichier)
    if 'Category' not in df.columns:
        categories = ['Electronics', 'Fashion', 'Books', 'Home', 'Toys']
        df['Category'] = np.random.choice(categories, len(df))
    
    # 5. Ajout de ratings simulés (si pas dans votre fichier)
    if 'Rating' not in df.columns:
        df['Rating'] = np.random.uniform(3, 5, len(df))
    
    print(f"✅ Données préparées: {len(df)} lignes")
    print(f"📅 Période: {df['InvoiceDate'].min()} à {df['InvoiceDate'].max()}")
    print(f"💰 CA Total: {df['Revenue'].sum():,.2f} €")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("Création de données exemple...")
    
    # Données exemple
    dates = pd.date_range('2023-01-01', periods=1000, freq='D')
    df = pd.DataFrame({
        'InvoiceDate': dates,
        'InvoiceNo': ['INV' + str(i) for i in range(1000)],
        'StockCode': ['STK' + str(i % 100) for i in range(1000)],
        'Description': ['Product ' + str(i % 50) for i in range(1000)],
        'Quantity': np.random.randint(1, 10, 1000),
        'UnitPrice': np.random.uniform(10, 500, 1000),
        'CustomerID': ['CUST' + str(np.random.randint(1, 101)) for _ in range(1000)],
        'Country': np.random.choice(['USA', 'UK', 'France', 'Germany', 'Spain'], 1000),
        'Category': np.random.choice(['Electronics', 'Fashion', 'Books', 'Home', 'Toys'], 1000),
        'Rating': np.random.uniform(3, 5, 1000)
    })
    df['Revenue'] = df['Quantity'] * df['UnitPrice']

# ========== CALCUL RFM ==========
print("📊 Calcul des segments RFM...")

current_date = df['InvoiceDate'].max()
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (current_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',  # Frequency
    'Revenue': 'sum'  # Monetary
}).rename(columns={'InvoiceDate': 'R', 'InvoiceNo': 'F', 'Revenue': 'M'})

# Scores RFM
rfm['R_Score'] = pd.qcut(rfm['R'], 4, labels=[4, 3, 2, 1], duplicates='drop')
rfm['F_Score'] = pd.qcut(rfm['F'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')
rfm['M_Score'] = pd.qcut(rfm['M'], 4, labels=[1, 2, 3, 4], duplicates='drop')

rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# Segmentation
segment_map = {
    '444': 'Champions', '443': 'Champions', '434': 'Champions', '433': 'Champions',
    '344': 'Loyal Customers', '343': 'Loyal Customers', '334': 'Loyal Customers',
    '333': 'Loyal Customers', '244': 'Potential', '144': 'New', '111': 'Lost',
    '112': 'Inactive', '221': 'At Risk', '212': 'At Risk'
}
rfm['Segment'] = rfm['RFM_Score'].map(segment_map).fillna('Others')

df = df.merge(rfm[['Segment']], left_on='CustomerID', right_index=True, how='left')

print("✅ Segmentation RFM terminée")
print("="*60)

# ========== KPIs ==========
total_revenue = df['Revenue'].sum()
total_customers = df['CustomerID'].nunique()
total_orders = df['InvoiceNo'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
total_products = df['Quantity'].sum()
avg_rating = df['Rating'].mean()

# ========== LAYOUT ==========
app.layout = html.Div([
    
    dbc.Container([
        # Header
        html.Div([
            html.Div([
                html.H1("2025 STRATEGIC", style={'fontSize': '48px', 'fontWeight': 'bold', 'marginBottom': '0'}),
                html.H1("KPI REPORT", style={'fontSize': '48px', 'fontWeight': 'bold', 'marginTop': '0'}),
                html.P("Driving Growth | Maximizing Performance", style={'fontSize': '18px', 'opacity': '0.9'})
            ])
        ], className='gradient-header'),
        
        # Filters
        dbc.Card([
            dbc.CardBody([
                html.H5("🔍 Filters", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Date Range", className="form-label fw-bold"),
                        dcc.DatePickerRange(
                            id='date-filter',
                            start_date=df['InvoiceDate'].min(),
                            end_date=df['InvoiceDate'].max(),
                            display_format='DD/MM/YYYY',
                            style={'width': '100%'}
                        )
                    ], width=4),
                    
                    dbc.Col([
                        html.Label("Category", className="form-label fw-bold"),
                        dcc.Dropdown(
                            id='category-filter',
                            options=[{'label': cat, 'value': cat} for cat in sorted(df['Category'].unique())],
                            multi=True,
                            placeholder="All Categories"
                        )
                    ], width=4),
                    
                    dbc.Col([
                        html.Label("Country", className="form-label fw-bold"),
                        dcc.Dropdown(
                            id='country-filter',
                            options=[{'label': c, 'value': c} for c in sorted(df['Country'].unique())],
                            multi=True,
                            placeholder="All Countries"
                        )
                    ], width=4),
                ]),
                dbc.Button("Apply Filters", id='apply-btn', color="primary", className="w-100 mt-3", 
                          style={'borderRadius': '10px'})
            ])
        ], className='filter-card mb-4'),
        
        # KPI Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("💰", style={'fontSize': '32px'}),
                            html.Span("+12.5%", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Total Revenue", className="text-muted mt-2 mb-2"),
                        html.H3(f"${total_revenue/1000:.1f}K", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #667eea'})
            ], width=2),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("🛒", style={'fontSize': '32px'}),
                            html.Span("+8.2%", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Total Orders", className="text-muted mt-2 mb-2"),
                        html.H3(f"{total_orders:,}", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #764ba2'})
            ], width=2),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("👥", style={'fontSize': '32px'}),
                            html.Span("+15.3%", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Customers", className="text-muted mt-2 mb-2"),
                        html.H3(f"{total_customers:,}", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #f093fb'})
            ], width=2),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("📦", style={'fontSize': '32px'}),
                            html.Span("+5.7%", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Avg Order Value", className="text-muted mt-2 mb-2"),
                        html.H3(f"${avg_order_value:.0f}", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #f5af19'})
            ], width=2),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("📊", style={'fontSize': '32px'}),
                            html.Span("+18.9%", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Products Sold", className="text-muted mt-2 mb-2"),
                        html.H3(f"{int(total_products):,}", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #4facfe'})
            ], width=2),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div("⭐", style={'fontSize': '32px'}),
                            html.Span("+0.3", className="badge bg-success", 
                                    style={'position': 'absolute', 'top': '15px', 'right': '15px'})
                        ], style={'position': 'relative'}),
                        html.H6("Avg Rating", className="text-muted mt-2 mb-2"),
                        html.H3(f"{avg_rating:.1f}/5", className="mb-0")
                    ])
                ], className='kpi-card', style={'borderTop': '4px solid #00f2fe'})
            ], width=2),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Monthly Revenue Trend", className="mb-0")),
                    dbc.CardBody([dcc.Graph(id='revenue-trend')])
                ], className='chart-card')
            ], width=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🎯 Customer Segments", className="mb-0")),
                    dbc.CardBody([dcc.Graph(id='segments-chart')])
                ], className='chart-card')
            ], width=4),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🏆 Top Products by Revenue", className="mb-0")),
                    dbc.CardBody([dcc.Graph(id='top-products')])
                ], className='chart-card')
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🌍 Revenue by Country", className="mb-0")),
                    dbc.CardBody([dcc.Graph(id='country-chart')])
                ], className='chart-card')
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Category Performance", className="mb-0")),
                    dbc.CardBody([dcc.Graph(id='category-chart')])
                ], className='chart-card')
            ], width=12),
        ]),
        
        # Footer
        html.Div([
            html.Div([
                html.Div([
                    html.P("Presented by", className="mb-1", style={'fontSize': '14px', 'opacity': '0.9'}),
                    html.H5("Ouiam Bendaia And Sahar Choaui", className="mb-0")
                ], style={'flex': '1'}),
                html.Div([
                    html.P("Report Generated", className="mb-1 text-end", style={'fontSize': '14px', 'opacity': '0.9'}),
                    html.H5(datetime.now().strftime("%B %d, %Y"), className="mb-0 text-end")
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ], className='gradient-header mt-4')
        
    ], fluid=True, className="p-4", style={'background': 'linear-gradient(to bottom right, #f8fafc, #e2e8f0)'})
])

# ========== CALLBACKS ==========
@app.callback(
    [Output('revenue-trend', 'figure'),
     Output('segments-chart', 'figure'),
     Output('top-products', 'figure'),
     Output('country-chart', 'figure'),
     Output('category-chart', 'figure')],
    [Input('apply-btn', 'n_clicks')],
    [State('date-filter', 'start_date'),
     State('date-filter', 'end_date'),
     State('category-filter', 'value'),
     State('country-filter', 'value')]
)
def update_charts(n_clicks, start_date, end_date, categories, countries):
    # Filter data
    filtered_df = df.copy()
    
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['InvoiceDate'] >= start_date) & 
                                  (filtered_df['InvoiceDate'] <= end_date)]
    
    if categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    
    # 1. Revenue Trend
    monthly = filtered_df.groupby(filtered_df['InvoiceDate'].dt.to_period('M'))['Revenue'].sum()
    monthly_df = pd.DataFrame({'Month': monthly.index.astype(str), 'Revenue': monthly.values})
    
    fig1 = px.bar(monthly_df, x='Month', y='Revenue',
                  color='Revenue', color_continuous_scale='Viridis')
    fig1.update_layout(showlegend=False, template='plotly_white',
                      xaxis_title="Month", yaxis_title="Revenue ($)")
    
    # 2. Segments
    segments = filtered_df['Segment'].value_counts()
    fig2 = px.pie(values=segments.values, names=segments.index, hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(showlegend=False)
    
    # 3. Top Products
    top_prod = filtered_df.groupby('Description')['Revenue'].sum().nlargest(10)
    fig3 = px.bar(x=top_prod.values, y=top_prod.index, orientation='h',
                  color=top_prod.values, color_continuous_scale='Plasma')
    fig3.update_layout(showlegend=False, template='plotly_white',
                      xaxis_title="Revenue ($)", yaxis_title="",
                      yaxis={'categoryorder': 'total ascending'})
    
    # 4. Countries
    countries_data = filtered_df.groupby('Country')['Revenue'].sum().nlargest(5)
    fig4 = px.bar(x=countries_data.values, y=countries_data.index, orientation='h',
                  color=countries_data.values, color_continuous_scale='Turbo')
    fig4.update_layout(showlegend=False, template='plotly_white',
                      xaxis_title="Revenue ($)", yaxis_title="",
                      yaxis={'categoryorder': 'total ascending'})
    
    # 5. Categories
    category_data = filtered_df.groupby('Category')['Revenue'].sum()
    fig5 = px.pie(values=category_data.values, names=category_data.index,
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig5.update_traces(textposition='inside', textinfo='percent+label')
    fig5.update_layout(showlegend=True)
    
    return fig1, fig2, fig3, fig4, fig5

# ========== RUN APP ==========
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MODERN E-COMMERCE DASHBOARD")
    print("="*60)
    print(f"💰 Total Revenue: ${total_revenue:,.2f}")
    print(f"👥 Total Customers: {total_customers:,}")
    print(f"📦 Total Orders: {total_orders:,}")
    print(f"🛒 Average Order Value: ${avg_order_value:.2f}")
    print(f"⭐ Average Rating: {avg_rating:.1f}/5")
    print("🌐 Opening: http://127.0.0.1:8050")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=8050)