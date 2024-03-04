# Import Packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style='dark')

# Define Functions
def create_bycity_df(df):
    bycity_df = df.groupby(by="seller_city").seller_id.nunique().sort_values(ascending=False).reset_index()
    bycity_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)

    return bycity_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="seller_state").seller_id.nunique().sort_values(ascending=False).reset_index()
    bystate_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)

    return bystate_df

def create_sellers_by_revenue_df(df):
    sellers_by_revenue_df = df.groupby(by="seller_id").agg({
        "order_id": "nunique",
        "price": "sum"
    }).sort_values("price",ascending=False)

    sellers_by_revenue_df.rename(columns={
    "order_id": "order_count",
    "price": "revenue"
    }, inplace=True)

    return sellers_by_revenue_df

def create_monthly_orders_df(df):
    seller_top1_df = df[df.seller_id == "4869f7a5dfa277a7dca6462dcf3b52b2"]
    seller_top2_df = df[df.seller_id == "53243585a1d6dc2643021fd1853d8905"]
    seller_top3_df = df[df.seller_id == "4a3ca9315b744ce9f8e9374361493884"]

    monthly_orders_top1_df = seller_top1_df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_top1_df.index = monthly_orders_top1_df.index.strftime('%Y-%m')
    monthly_orders_top1_df = monthly_orders_top1_df.reset_index()
    monthly_orders_top1_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    monthly_orders_top1_df = pd.concat([monthly_orders_top1_df,pd.DataFrame({'order_approved_at':['2017-01', '2017-02'], 'order_count':[0,0], 'revenue':[0,0]})], ignore_index=True).sort_values("order_approved_at")
    monthly_orders_top1_df = monthly_orders_top1_df.reset_index(drop=True)

    monthly_orders_top2_df = seller_top2_df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_top2_df.index = monthly_orders_top2_df.index.strftime('%Y-%m')
    monthly_orders_top2_df = monthly_orders_top2_df.reset_index()
    monthly_orders_top2_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    monthly_orders_top2_df = pd.concat([monthly_orders_top2_df,pd.DataFrame({'order_approved_at':['2017-01', '2017-02','2017-03','2017-04','2017-05','2017-06','2017-07'], 'order_count':[0,0,0,0,0,0,0], 'revenue':[0,0,0,0,0,0,0]})], ignore_index=True).sort_values("order_approved_at")
    monthly_orders_top2_df = monthly_orders_top2_df.reset_index(drop=True)

    monthly_orders_top3_df = seller_top3_df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_top3_df.index = monthly_orders_top3_df.index.strftime('%Y-%m')
    monthly_orders_top3_df = monthly_orders_top3_df.reset_index()
    monthly_orders_top3_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return monthly_orders_top1_df, monthly_orders_top2_df, monthly_orders_top3_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="seller_id", as_index=False).agg({
        "order_approved_at": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "price": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["seller_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Import Data
file_path = 'https://raw.githubusercontent.com/Dustannum/dashboard/main/dashboard/all_data.csv'
all_df = pd.read_csv(file_path)

# Sort DataFrame by order_approved_at
datetime_columns = ["shipping_limit_date", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Add Filter by order_approved_at
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
sellers_by_revenue_df = create_sellers_by_revenue_df(main_df)
monthly_orders_top1_df, monthly_orders_top2_df, monthly_orders_top3_df = create_monthly_orders_df(main_df)
rfm_df = create_rfm_df(main_df)

# Add Header
st.header('Sellers Dashboard')

# Seller Origins
st.subheader("Seller Origins")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count",
        y="seller_state",
        data=bystate_df.sort_values(by="seller_count", ascending=False).head(),
        palette=colors_,
        ax=ax
    )
    ax.set_title("Top 5 States with the Most Sellers", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count",
        y="seller_city",
        data=bycity_df.sort_values(by="seller_count", ascending=False).head(10),
        palette=colors_,
        ax=ax
    )
    ax.set_title("Top 10 Cities with the Most Sellers", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

# Best & Worst Sellers by Revenue
st.subheader("Best & Worst Sellers by Revenue")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="revenue", y="seller_id", data=sellers_by_revenue_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Sellers by Revenue", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="revenue", y="seller_id", data=sellers_by_revenue_df.sort_values(by="revenue", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Sellers by Revenue", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

# Monthly Revenue vs Number of Orders Approved per Month by Top 3 Sellers (based on Revenue)
st.subheader("Monthly Revenue vs Number of Orders Approved per Month by Top 3 Sellers (based on Revenue)")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))

    plt.plot(monthly_orders_top1_df["order_approved_at"], monthly_orders_top1_df["revenue"], marker='o', linewidth=2, color="#ff0000")
    plt.plot(monthly_orders_top2_df["order_approved_at"], monthly_orders_top2_df["revenue"], marker='o', linewidth=2, color="#0000ff")
    plt.plot(monthly_orders_top3_df["order_approved_at"], monthly_orders_top3_df["revenue"], marker='o', linewidth=2, color="#009f00")
    plt.title("Monthly Revenue", loc="center", fontsize=20)
    plt.legend(['4869f7a5dfa277a7dca6462dcf3b52b2','53243585a1d6dc2643021fd1853d8905','4a3ca9315b744ce9f8e9374361493884'])
    plt.xticks(fontsize=10,rotation=90)
    plt.yticks(fontsize=10)
    
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))

    plt.plot(monthly_orders_top1_df["order_approved_at"], monthly_orders_top1_df["order_count"], marker='o', linewidth=2, color="#ff0000")
    plt.plot(monthly_orders_top2_df["order_approved_at"], monthly_orders_top2_df["order_count"], marker='o', linewidth=2, color="#0000ff")
    plt.plot(monthly_orders_top3_df["order_approved_at"], monthly_orders_top3_df["order_count"], marker='o', linewidth=2, color="#009f00")
    plt.title("Orders Approved per Month", loc="center", fontsize=20)
    plt.legend(['4869f7a5dfa277a7dca6462dcf3b52b2','53243585a1d6dc2643021fd1853d8905','4a3ca9315b744ce9f8e9374361493884'])
    plt.xticks(fontsize=10,rotation=90)
    plt.yticks(fontsize=10)

    st.pyplot(fig)

# Best Sellers Based on RFM Parameters
st.subheader("Best Sellers Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="seller_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', rotation=90, labelsize=15)

sns.barplot(y="frequency", x="seller_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', rotation=90, labelsize=15)

sns.barplot(y="monetary", x="seller_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', rotation=90, labelsize=15)

st.pyplot(fig)