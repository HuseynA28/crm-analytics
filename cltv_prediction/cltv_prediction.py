##############################################################
# BG-NBD and Gamma-Gamma with CLTV Prediction
##############################################################

# 1. Data Preparation
# 2. Expected Number of Transactions with BG-NBD Model
# 3. Expected Average Profit with Gamma-Gamma Model
# 4. Calculating CLTV with BG-NBD and Gamma-Gamma Models
# 5. Segmenting Customers Based on CLTV
# 6. Function to Automate the Process

##############################################################
# 1. Data Preparation
##############################################################

# Import necessary libraries
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

# Load data
df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

# Check missing values
df.isnull().sum()

# Drop missing values
df.dropna(inplace=True)

# Remove canceled transactions
df = df[~df["Invoice"].str.contains("C", na=False)]

# Remove negative and zero quantities and prices
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

# Define outlier thresholds and replace outliers
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")

# Create TotalPrice column
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Set analysis date
today_date = dt.datetime(2011, 12, 11)

# Create the CLTV dataframe
cltv_df = df.groupby('Customer ID').agg(
    {'InvoiceDate': [lambda date: (date.max() - date.min()).days,
                     lambda date: (today_date - date.min()).days],
     'Invoice': lambda num: num.nunique(),
     'TotalPrice': lambda price: price.sum()})

cltv_df.columns = cltv_df.columns.droplevel(0)
cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']
cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]

# Filter out customers with only one purchase
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

# Convert recency and T to weeks
cltv_df["recency"] = cltv_df["recency"] / 7
cltv_df["T"] = cltv_df["T"] / 7

##############################################################
# 2. Expected Number of Transactions with BG-NBD Model
##############################################################

# Fit BG-NBD model
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])

# Predict expected purchases for 1 week, 1 month, and 3 months
cltv_df["expected_purc_1_week"] = bgf.predict(1, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])
cltv_df["expected_purc_1_month"] = bgf.predict(4, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])
cltv_df["expected_purc_3_month"] = bgf.predict(12, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])

# Plot period transactions
plot_period_transactions(bgf)
plt.show()

##############################################################
# 3. Expected Average Profit with Gamma-Gamma Model
##############################################################

# Fit Gamma-Gamma model
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

# Predict expected average profit
cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'], cltv_df['monetary'])

##############################################################
# 4. Calculating CLTV with BG-NBD and Gamma-Gamma Models
##############################################################

# Calculate CLTV
cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   time=3,  # 3 months
                                   freq="W",  # frequency in weeks
                                   discount_rate=0.01)

cltv = cltv.reset_index()
cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")

##############################################################
# 5. Segmenting Customers Based on CLTV
##############################################################

# Create segments
cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

# Display the top 10 customers
cltv_final.sort_values(by="clv", ascending=False).head(10)

# Group by segment
cltv_final.groupby("segment").agg({"count", "mean", "sum"})

##############################################################
# 6. Function to Automate the Process
##############################################################

def create_cltv_p(dataframe, month=3):
    # Data preprocessing
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    today_date = dt.datetime(2011, 12, 11)

    cltv_df = dataframe.groupby('Customer ID').agg(
        {'InvoiceDate': [lambda date: (date.max() - date.min()).days,
                         lambda date: (today_date - date.min()).days],
         'Invoice': lambda num: num.nunique(),
         'TotalPrice': lambda price: price.sum()})

    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']
    cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]
    cltv_df = cltv_df[(cltv_df['frequency'] > 1)]
    cltv_df["recency"] = cltv_df["recency"] / 7
    cltv_df["T"] = cltv_df["T"] / 7

    # BG-NBD model
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])
    cltv_df["expected_purc_1_week"] = bgf.predict(1, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])
    cltv_df["expected_purc_1_month"] = bgf.predict(4, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])
    cltv_df["expected_purc_3_month"] = bgf.predict(12, cltv_df['frequency'], cltv_df['recency'], cltv_df['T'])

    # Gamma-Gamma model
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df['frequency'], cltv_df['monetary'])
    cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'], cltv_df['monetary'])

    # Calculate CLTV
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df['frequency'],
                                       cltv_df['recency'],
                                       cltv_df['T'],
                                       cltv_df['monetary'],
                                       time=month,
                                       freq="W",
                                       discount_rate=0.01)
    cltv = cltv.reset_index()
    cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    return cltv_final

# Apply the function
df = df_.copy()
cltv_final2 = create_cltv_p(df)

# Save the results
cltv_final2.to_csv("cltv_prediction.csv")
