import base64
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests


DUNE_API='RzCWJATk8qbD35OPTFhm0M3BmeDPpc4J'
api = f'https://api.dune.com/api/v1/query/2638634/results?api_key={DUNE_API}'

# Define a function to get the price of an asset
def get_price(TIMESTAMP, TICKER):
    if TICKER is None:
        return 0
    url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={TICKER}&tsym=USD&limit=1&toTs={TIMESTAMP}'
    r = requests.get(url).json()['Data']['Data'][0]['close']
    return r

# Make a request to the API
r = requests.get(api).json()['result']['rows']
df = pd.DataFrame(r)

# Convert epochBegin to datetime format
df['epochBegin'] = pd.to_datetime(df['epochBegin'], unit='s')

# Sort by epochBegin and filter by 'weekly' epoch_type
df = df.sort_values('epochBegin', ascending=True)
df = df[df['epoch_type'].isin(['weekly'])]

# Calculate total value locked
df['total_value_locked'] = df['collateral_assets'] + df['premium_assets']

# Group by epochBegin and sum underlyingAssetvalue
grouped_df = df.groupby('epochBegin')['underlyingAssetvalue'].sum().reset_index()

# Create a bar chart
fig = px.bar(df, x='epochBegin', y='underlyingAssetvalue', color='name', title='Y2K.finance Market TVL', barmode='stack')

# Add a line plot for total TVL
fig.add_trace(go.Scatter(x=grouped_df['epochBegin'], y=grouped_df['underlyingAssetvalue'], mode='lines', name='Total TVL', line=dict(color='white', dash='dash')))

# Encode the image file to base64
with open("y2k.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Update the layout of the figure to add custom title, axis labels, legend, and dark theme
fig.update_layout(
    title={
        'text': 'Y2K.finance Market TVL',
        'y':0.93,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    title_font=dict(size=24, color='white', family="Courier New, monospace"),
    xaxis=dict(title='Date', title_font=dict(size=18, color='white', family="Courier New, monospace"), tickfont=dict(size=14, color='white', family="Courier New, monospace")),
    yaxis=dict(title='Value', title_font=dict(size=18, color='white', family="Courier New, monospace"), tickfont=dict(size=14, color='white', family="Courier New, monospace")),
    legend=dict(yanchor="top", y=1, xanchor="left", x=1, font=dict(size=16, color='white', family="Courier New, monospace")),
    template='plotly_dark',
    images=[dict(
        source=f'data:image/png;base64,{encoded_string}',
        xref="paper", yref="paper",
        x=1, y=0.92,
        sizex=0.12, sizey=0.12,
        xanchor="right", yanchor="middle"
    )]
)

# Save the plot as an HTML file and display the figure
fig.write_html("index.html")
