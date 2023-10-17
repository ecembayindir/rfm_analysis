###########################################################
# 1. Business Problem
###########################################################

# An online retail wants to segment its customers to shape the company's marketing strategy.

# Dataset
#
# https://archive.ics.uci.edu/dataset/502/online+retail+ii
# The data set belongs to an online retail based in the UK.
# It includes the sales between 01/12/2009 - 09/12/2011.

# Variables
#
# InvoiceNo: Each transaction belongs to different invoice number. Invoices starting with C are returns, remove them.
# StockCode: Product code, unique for each product.
# Description: Product name.
# Quantity: It represents the sales amount for each product.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price in GBP.
# CustomerID: Unique for each customer.
# Country: Country where customer lives.

###########################################################
# 2. Data Understanding
###########################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_csv('/kaggle/input/online-retail-ii-uci/online_retail_II.csv')
df_["InvoiceDate"] = pd.to_datetime(df_["InvoiceDate"])
start_date = "2009-01-01"
end_date = "2009-12-31"
df_ = df_[(df_["InvoiceDate"] >= start_date) & (df_["InvoiceDate"] <= end_date)]
df = df_.copy() #a copy as a backup.
df.head()
df.shape
df.isnull().sum()

# The quantity of unique products
df['Description'].nunique()

df['Description'].value_counts().head()

df.groupby('Description').agg({'Quantity': 'sum'}).head()

df.groupby('Description').agg({'Quantity': 'sum'}).sort_values('Quantity', ascending=False).head()

df['Invoice'].nunique()

df['TotalPrice'] = df['Quantity'] * df['Price']

df.groupby('Invoice').agg({'TotalPrice': 'sum'}).head()

###########################################################
# 3. Data Preparation
###########################################################

df.shape
df.isnull().sum()
df.dropna(inplace=True)
df.describe().T

df = df[~df['Invoice'].str.contains('C', na=False)]

###########################################################
# 4. Calculating RFM Metrics
###########################################################

# Recency, Frequency, Monetary
df.head()
df['InvoiceDate'].max()

today_date = dt.datetime(2010, 12, 11)
type(today_date)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice : Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T

rfm = rfm[rfm['monetary'] > 0]
rfm.shape

###########################################################
# 5. Calculating RFM Scores
###########################################################

rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels= [5, 4, 3, 2, 1])
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels= [1, 2, 3, 4, 5])
rfm['monetary_score'] = pd.qcut(rfm['monetary'],5, labels= [1, 2, 3, 4, 5])

rfm['RFM_SCORE'] = (rfm['recency_score'].astype(str)) + (rfm['frequency_score'].astype(str))

rfm.describe().T

###########################################################
# 6. Creating & Analysing RFM Segments
###########################################################

seg_map = {r'[1-2][1-2]': 'hibernating',
           r'[1-2][3-4]': 'at_risk',
           r'[1-2]5': 'cant_lose',
           r'3[1-2]': 'about_to_sleep',
           r'33': 'need_attention',
           r'[3-4][4-5]': 'loyal_customers',
           r'41': 'promising',
           r'51': 'new_customers',
           r'[4-5][2-3]': 'potential_loyalists',
           r'5[4-5]': 'champions'}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm[['segment', 'recency', 'frequency', 'monetary']].groupby('segment').agg(['mean', 'count'])

rfm[rfm['segment'] == 'cant_lose'].head()
rfm[rfm['segment'] == 'cant_lose'].index

# To access new costumers' IDs
new_df = pd.DataFrame()
new_df['new_customer_id'] = rfm[rfm['segment'] == 'new_customers'].index
new_df['new_customer_id'] = new_df['new_customer_id'].astype(int)

# To export new customers' IDs
new_df.to_csv('new_customer.csv')

# To export all segments
rfm.to_csv('rfm.csv')

###########################################################
# 7. Functionalization
###########################################################

def create_rfm(dataframe, csv=False):

    #Data Preparation
    dataframe['TotalPrice'] = dataframe['Quantity'] * dataframe['Price']
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe['Invoice'].str.contains('C', na=False)]

    #Calculating RFM Metrics
    today_date = dt.datetime(2010, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                         'Invoice': lambda Invoice: Invoice.nunique(),
                                         'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm[rfm['monetary'] > 0]

    #Calculating RFM Scores
    rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm['RFM_SCORE'] = (rfm['recency_score'].astype(str)) + (rfm['frequency_score'].astype(str))

    #Creating & Analysing RFM Segments
    seg_map = {r'[1-2][1-2]': 'hibernating',
               r'[1-2][3-4]': 'at_risk',
               r'[1-2]5': 'cant_lose',
               r'3[1-2]': 'about_to_sleep',
               r'33': 'need_attention',
               r'[3-4][4-5]': 'loyal_customers',
               r'41': 'promising',
               r'51': 'new_customers',
               r'[4-5][2-3]': 'potential_loyalists',
               r'5[4-5]': 'champions'}
    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[['segment', 'recency', 'frequency', 'monetary']]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv('rfm.csv')
    return rfm

#df = df_.copy()
#rfm_new = create_rfm(df)
