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
