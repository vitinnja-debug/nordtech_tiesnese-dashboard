import streamlit as st
import pandas as pd
import plotly.express as px

# Ielādējam datus (izmantojot tavu jau sagatavoto enriched_data.csv)
df = pd.read_csv('enriched_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

# --- SĀNU JOSLA (FILTRI) ---
st.sidebar.header("Filtri")
selected_category = st.sidebar.multiselect("Izvēlies kategoriju", options=df['Product_Category'].unique(), default=df['Product_Category'].unique())
date_range = st.sidebar.date_input("Izvēlies laika periodu", [df['Date'].min(), df['Date'].max()])

# Datu filtrēšana
mask = (df['Product_Category'].isin(selected_category)) & (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
filtered_df = df.loc[mask]

# --- KPI APRĒĶINI ---
st.title("💡 Biznesa Analīzes Panelis")

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

total_revenue = filtered_df['Total_Price'].sum()
refund_rate = (filtered_df['Is_Returned'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
total_refund_amount = filtered_df['Refund_Amount'].sum()

# Pasūtījumi ar sūdzībām
unique_orders_with_tickets = filtered_df[filtered_df['Ticket_Count'] > 0]['Transaction_ID'].nunique()
total_unique_orders = filtered_df['Transaction_ID'].nunique()
complaint_rate = (unique_orders_with_tickets / total_unique_orders * 100) if total_unique_orders > 0 else 0
total_tickets = filtered_df['Ticket_Count'].sum()

with col1:
    st.metric("Kopējie Ieņēmumi", f"${total_revenue:,.2f}")
with col2:
    st.metric("Atgrieztais procents", f"{refund_rate:.1f}%")
with col3:
    st.metric("Atgrieztā summa", f"${total_refund_amount:,.2f}")

# KPI ar paskaidrojumiem
with col4:
    st.metric("Pasūtījumi ar sūdzībām", f"{complaint_rate:.1f}%", 
              help="Procents no unikālajiem pasūtījumiem, par kuriem saņemta vismaz viena sūdzība")
with col5:
    st.metric("Kopējais sūdzību skaits", int(total_tickets), 
              help="Reģistrētie tiketi")

# --- VIZUALIZĀCIJAS ---
st.subheader("📊 Ieņēmumi VS atgriezumi")
fig1 = px.bar(filtered_df.groupby('Product_Name').agg({'Total_Price':'sum', 'Refund_Amount':'sum'}).reset_index(), 
             x='Product_Name', y=['Total_Price', 'Refund_Amount'], barmode='group',
             title="Ieņēmumu un atgriezumu salīdzinājums pa produktiem")
st.plotly_chart(fig1)

st.subheader("📈 Sūdzību sadalījums (visi pieteikumi)")
fig2 = px.line(filtered_df.groupby(filtered_df['Date'].dt.date)['Ticket_Count'].sum().reset_index(), 
              x='Date', y='Ticket_Count', title="Sūdzību dinamika laika griezumā")
st.plotly_chart(fig2)

# --- TABULA ---
st.subheader("📋 Problemātiskie produkti (zaudējumu analīze)")
problem_table = filtered_df.groupby('Product_Name').agg({
    'Total_Price': 'sum',
    'Refund_Amount': 'sum',
    'Ticket_Count': 'sum',
    'Is_Returned': 'sum'
}).reset_index()
problem_table['Zaudējumu_Likme'] = (problem_table['Refund_Amount'] / problem_table['Total_Price'] * 100)
st.dataframe(problem_table.sort_values(by='Refund_Amount', ascending=False))
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NordTech Dashboard", layout="wide")

# Ielādējam datus, kurus tu jau notīrīji
try:
    df = pd.read_csv('enriched_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
except:
    st.error("Fails 'enriched_data.csv' nav atrasts! Vispirms palaid datu tīrīšanas kodu.")
    st.stop()

st.title("🛡️ NordTech Biznesa Krīzes Analītika")

# Sidebar
st.sidebar.header("Filtri")
cat_filter = st.sidebar.multiselect("Produktu kategorija", df['Product_Category'].unique(), default=df['Product_Category'].unique())
df_filtered = df[df['Product_Category'].isin(cat_filter)]

# KPI
c1, c2, c3 = st.columns(3)
c1.metric("Kopējie Ieņēmumi", f"${df_filtered['Total_Price'].sum():,.2f}")
c2.metric("Atgriešanas %", f"{(df_filtered['Is_Returned'].mean()*100):.1f}%")
c3.metric("Sūdzību skaits", int(df_filtered['Ticket_Count'].sum()))

# Grafiki
col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(df_filtered.groupby('Product_Name')['Ticket_Count'].sum().reset_index(),
                  x='Product_Name', y='Ticket_Count', title="Sūdzības pa produktiem")
    st.plotly_chart(fig1)
with col2:
    fig2 = px.line(df_filtered.groupby('Date')['Total_Price'].sum().reset_index(),
                   x='Date', y='Total_Price', title="Ieņēmumu dinamika")
    st.plotly_chart(fig2)
