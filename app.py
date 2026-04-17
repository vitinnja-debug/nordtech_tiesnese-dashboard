import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DATU IELĀDE
df = pd.read_csv('enriched_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

# --- SĀNU JOSLA (FILTRI) ---
st.sidebar.header("Datu atlase")
categories = df['Product_Category'].unique().tolist()
selected_category = st.sidebar.multiselect("Izvēlies kategoriju", categories, default=categories)

# Datuma filtrs
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Izvēlies laika periodu", [min_date, max_date])

# Filtrēšana
mask = (df['Product_Category'].isin(selected_category))
if len(date_range) == 2:
    mask = mask & (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
filtered_df = df.loc[mask]

# --- VIRSRAKSTS ---
st.title("🚀 NordTech Biznesa Krīzes Analītika")

# --- KPI ---
col1, col2, col3, col4, col5 = st.columns(5)
total_rev = filtered_df['Total_Price'].sum()
ref_rate = (filtered_df['Is_Returned'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
ref_amt = filtered_df['Refund_Amount'].sum()
compl_rate = (filtered_df[filtered_df['Ticket_Count'] > 0]['Transaction_ID'].nunique() / filtered_df['Transaction_ID'].nunique() * 100) if len(filtered_df) > 0 else 0
tickets = filtered_df['Ticket_Count'].sum()

col1.metric("Ieņēmumi", f"${total_rev:,.0f}")
col2.metric("Atgriezts %", f"{ref_rate:.1f}%")
col3.metric("Atgriezts $", f"${ref_amt:,.0f}")
col4.metric("Sūdzības %", f"{compl_rate:.1f}%", help="Procents no unikālajiem pasūtījumiem")
col5.metric("Tiketi", int(tickets), help="Kopējais sūdzību skaits")

# --- GRAFIKI ---
st.subheader("📊 Ieņēmumi VS atgriezumi")
fig1 = px.bar(filtered_df.groupby('Product_Name').agg({'Total_Price':'sum', 'Refund_Amount':'sum'}).reset_index(), 
             x='Product_Name', y=['Total_Price', 'Refund_Amount'], barmode='group')
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Sūdzību sadalījums (visi pieteikumi)")
fig2 = px.line(filtered_df.groupby(filtered_df['Date'].dt.date)['Ticket_Count'].sum().reset_index(), x='Date', y='Ticket_Count')
st.plotly_chart(fig2, use_container_width=True)

# --- TABULA ---
st.subheader("📋 Problemātiskie produkti (zaudējumu analīze)")
tabula = filtered_df.groupby('Product_Name').agg({'Total_Price':'sum', 'Refund_Amount':'sum', 'Ticket_Count':'sum'}).sort_values('Refund_Amount', ascending=False)
st.dataframe(tabula, use_container_width=True)
