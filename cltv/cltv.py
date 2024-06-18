############################################
# CUSTOMER LIFETIME VALUE
############################################

# 1. Data Preparation
# 2. Average Order Value (average_order_value = total_price / total_transaction)
# 3. Purchase Frequency (total_transaction / total_number_of_customers)
# 4. Repeat Rate & Churn Rate (number of customers who purchased more than once / total number of customers)
# 5. Profit Margin (profit_margin = total_price * 0.10)
# 6. Customer Value (customer_value = average_order_value * purchase_frequency)
# 7. Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
# 8. Creating Segments


##################################################
# 1. Data Preparation
##################################################

# Dataset Story
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# The Online Retail II dataset contains sales of an online store based in the UK 
# from 01/12/2009 to 09/12/2011.

# Variables
# InvoiceNo: Invoice number. A unique number for each transaction, starting with C indicates a canceled transaction.
# StockCode: Product code. A unique number for each product.
# Description: Product name
# Quantity: Number of products. Indicates how many of each product were sold in the invoices.
# InvoiceDate: Date and time of the invoice.
# UnitPrice: Product price (in Sterling)
# CustomerID: Unique customer number
# Country: Country name. The country where the customer resides.

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()
df.head()
df.isnull().sum()
df = df[~df["Invoice"].str.contains("C", na=False)]
df.describe().T
df = df[(df['Quantity'] > 0)]
df.dropna(inplace=True)

df["TotalPrice"] = df["Quantity"] * df["Price"]

cltv_c = df.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(),
                                        'Quantity': lambda x: x.sum(),
                                        'TotalPrice': lambda x: x.sum()})

cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']

##################################################
# 2. Average Order Value (average_order_value = total_price / total_transaction)
##################################################

cltv_c.head()
cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]

##################################################
# 3. Purchase Frequency (total_transaction / total_number_of_customers)
##################################################

cltv_c.head()
cltv_c.shape[0]
cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]

##################################################
# 4. Repeat Rate & Churn Rate (number of customers who purchased more than once / total number of customers)
##################################################

repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]

churn_rate = 1 - repeat_rate

##################################################
# 5. Profit Margin (profit_margin = total_price * 0.10)
##################################################

cltv_c['profit_margin'] = cltv_c['total_price'] * 0.10


##################################################
# 6. Customer Value (customer_value = average_order_value * purchase_frequency)
##################################################

cltv_c['customer_value'] = cltv_c['average_order_value'] * cltv_c["purchase_frequency"]

##################################################
# 7. Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
##################################################

cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]

cltv_c.sort_values(by="cltv", ascending=False).head()


##################################################
# 8. Creating Segments
##################################################

cltv_c.sort_values(by="cltv", ascending=False).tail()

cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])

cltv_c.sort_values(by="cltv", ascending=False).head()

cltv_c.groupby("segment").agg({"count", "mean", "sum"})

cltv_c.to_csv("cltc_c.csv")

# 18102.00000       A
# 14646.00000       A
# 14156.00000       A
# 14911.00000       A
# 13694.00000       A

# Customer ID
# 18102.00000       A
# 14646.00000       A
# 14156.00000       A
# 14911.00000       A
# 13694.00000       A


