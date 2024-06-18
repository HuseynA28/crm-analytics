import datetime as dt
import pandas as pd

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Load the dataset
df_ = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()

# Display the first few rows and shape of the dataset
print(df.head())
print(df.shape)

# Check for missing values
print(df.isnull().sum())

# Number of unique products
unique_products = df["Description"].nunique()
print(f"Unique products: {unique_products}")

# Top 5 most frequently purchased products
print(df["Description"].value_counts().head())

# Aggregating the quantity by product description
print(df.groupby("Description").agg({"Quantity": "sum"}).head())

# Top 5 products by quantity
print(df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head())

# Number of unique invoices
unique_invoices = df["Invoice"].nunique()
print(f"Unique invoices: {unique_invoices}")

# Creating TotalPrice column
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Aggregating total price by invoice
print(df.groupby("Invoice").agg({"TotalPrice": "sum"}).head())

###############################################################
# 3. Veri Hazırlama (Data Preparation)
###############################################################

# Filtering out non-positive quantities and dropping missing values
df = df[(df['Quantity'] > 0)]
df.dropna(inplace=True)

# Removing canceled orders
df = df[~df["Invoice"].str.contains("C", na=False)]

###############################################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
###############################################################

# Define the current date
today_date = dt.datetime(2010, 12, 11)

# Calculate RFM metrics
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
    'Invoice': lambda Invoice: Invoice.nunique(),
    'TotalPrice': lambda TotalPrice: TotalPrice.sum()
})

rfm.columns = ['recency', 'frequency', 'monetary']

# Filter out customers with non-positive monetary value
rfm = rfm[rfm["monetary"] > 0]
print(rfm.describe().T)

###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################

# Calculate RFM scores
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# Combine RFM scores into a single score
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

print(rfm.describe().T)

# Display top customers with the highest RFM score
print(rfm[rfm["RFM_SCORE"] == "55"].head())

# Display customers with the lowest RFM score
print(rfm[rfm["RFM_SCORE"] == "11"].head())

###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analyzing RFM Segments)
###############################################################

# Define segment mapping
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# Map RFM scores to segments
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# Display segment analysis
print(rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"]))

# Save new customers to CSV
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index.astype(int)
new_df.to_csv("new_customers.csv", index=False)

# Save RFM dataframe to CSV
rfm.to_csv("rfm.csv")

###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması (Function for the Entire Process)
###############################################################

def create_rfm(dataframe, csv=False):
    # Data preparation
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # Calculate RFM metrics
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({
        'InvoiceDate': lambda date: (today_date - date.max()).days,
        'Invoice': lambda num: num.nunique(),
        "TotalPrice": lambda price: price.sum()
    })
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # Calculate RFM scores
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # Combine RFM scores into a single score
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

    # Define segment mapping
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    # Map RFM scores to segments
    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    # Save to CSV if needed
    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

# Apply the function to the dataset
df = df_.copy()
rfm_new = create_rfm(df, csv=True)
