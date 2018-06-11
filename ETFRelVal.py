import requests
import re
import datetime
import time
import ssl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import seaborn as sns
import itertools

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# List of tickers - Benchmark must come LAST!!!
tickers = ['XLE', 'XLY', 'XLK', 'XLB', 'VFH', 'XLI', 'XLV', 'XLU', 'XLP', 'IYR', 'SPY']
#tickers = ['EWO', 'EWK', 'EWQ', 'EWG', 'EWI', 'EWN', 'EWP', 'EWD', 'EWL', 'EWU', 'VGK']
ETF_store = [] # Initialize an array for price series
PE_store = [] # Initialize an array for P/E ratios
PB_store = [] # Initialize an array for P/B ratios
PCF_store = [] # Initialize an array for P/CF ratios
yield_store = [] # Initialize an array for current TTM yields
start = datetime.date(2009,1,1) # YYYY,MM,DD
start_unix = str(int(time.mktime(start.timetuple()))) # Start in UNIX/Epoch time
end_unix = str(int(time.time())) # Today in UNIX/Epoch time
start_date = datetime.datetime.fromtimestamp(int(start_unix)).strftime('%Y-%m-%d') # Start in date time
end_date = datetime.datetime.fromtimestamp(int(end_unix)).strftime('%Y-%m-%d') # End in date time

# Main loop for scraping all data
for i in range(0, len(tickers)):
    # Retrieve html of ticker[i] for historical data
    url1 = 'https://finance.yahoo.com/quote/'
    url2 = '/history?period1='
    url3 = '&period2='
    url4 = '&interval=1d&filter=history&frequency=1d'
    url = url1 + tickers[i] + url2 + start_unix + url3 + end_unix + url4
    html = requests.get(url)
    html = html.text # Convert to text (adj_close prices not under a nice tag - thus won't use Beautifulsoup)
    trunc_string = '}],"isPending"' # Cut off from a point we no longer need html
    truncpos = html.find(trunc_string)
    html = html[:truncpos]
    # Now pull the holdings page - for this we can use BeautifulSoup tags
    url5 = '/holdings?p='
    url_holdings = url1 + tickers[i] + url5 + tickers[i]
    html2 = urllib.request.urlopen(url_holdings).read()
    soup_holdings = BeautifulSoup(html2, 'html.parser')

    # Retrieve the valuation ratios
    # P/E Ratio
    PE_box = soup_holdings.find('span', attrs={'data-reactid':'131'}) # Retrieve value
    PE_ratio = float(PE_box.text) # Convert to float
    PE_store.append(PE_ratio) # Store
    # P/B Ratio
    PB_box = soup_holdings.find('span', attrs={'data-reactid': '136'}) # Retrieve value
    PB_ratio = float(PB_box.text) # Convert to float
    PB_store.append(PB_ratio) # Store
    # P/CF Ratio
    PCF_box = soup_holdings.find('span', attrs={'data-reactid': '146'}) # Retrieve value
    PCF_ratio = float(PCF_box.text) # Convert to float
    PCF_store.append(PCF_ratio) # Store
    # Yield
    # Retrieve value - again for this one we'll just use text scrape as no nice tag
    yield_start = 'yield":{"raw":'
    yield_end = ',"fmt"'
    yield_startpos = html.find(yield_start) + len(yield_start) + 1
    yield_endpos = html.find(yield_end, yield_startpos)
    div_yield = 100*float(html[yield_startpos:yield_endpos]) # Convert to float and percents form
    yield_store.append(div_yield) # Store

    # Retrieve the adjusted close prices
    adj_close_prices = [] # Initialize an array
    string_start = 'adjclose'
    string_end = '}'
    endpos = 0 # Initialize endpos for first loop
    while endpos > -1:
        startpos = html.find(string_start) + len(string_start) + 2
        endpos = html.find(string_end, startpos)
        adj_close = float(html[startpos:endpos])
        adj_close_prices.append(adj_close) # Store the close price for each date on each loop
        html = html[endpos+1:] # Keep truncating on each loop to remove pirce we just used
    ETF_store.append(adj_close_prices) # Store all ETF price arrays
ETF_store = np.transpose(ETF_store)
ETF_normalized = 100*np.array(ETF_store / ETF_store[-1:]) # Normalize to starting value of 100
rel_prices = 100*np.transpose(np.transpose(ETF_normalized) / np.transpose(ETF_normalized)[-1:]) # Prices relative to bmark

# Performance metrics
# Calculate relative performance
rel_performance = rel_prices[0, :] / rel_prices[-1, :] - 1
column_names = ['Relative Return (to ' + tickers[-1] + ') ' + start_date + ' to Present'] # Name column
# Round values, create DataFrame, and remove the index
df_abs_pf = np.round(pd.DataFrame(np.transpose(np.transpose(rel_performance)),
                         index=tickers, columns=column_names), 4)[:-1]
# Sort relative performance descending
df_abs_pf = df_abs_pf.sort_values(column_names, ascending=False)

# Plots
# Initialize an array of colors (not happy with this, improvements welcome)
colors_line = itertools.cycle(sns.color_palette('husl', len(tickers) - 1))
n_groups = len(tickers)
index = np.arange(n_groups)
# Create a gridspec for subplots (x,y) creates a grid of x by y subgrids
gs1 = gridspec.GridSpec(3, 8)
# Position all the subplots as desired
ax = plt.subplot(gs1[0:2, :-4])
ax2 = plt.subplot(gs1[-1, 0:2])
ax3 = plt.subplot(gs1[-1, 2:4])
ax4 = plt.subplot(gs1[-1, 4:-2])
ax5 = plt.subplot(gs1[-1, -2:])
for i,c in zip(range(len(tickers) - 1),colors_line):
    ax.plot(np.flip(rel_prices, axis=0)[:, i], color=c) # Plot the relative time series
ax.set_ylabel('Price vs ' + tickers[-1] + ' ( ' + start_date + ' = 100)')
box = ax.get_position()
ax.legend(np.transpose(tickers[:-1]), loc='upper left', bbox_to_anchor=(-0.01, 1.15),
          fancybox=True, shadow=True, ncol=6)
ax.set_xticklabels([])
error_config = {'ecolor': '0.3'}
bar_width = 0.35
opacity = 0.8
for i,c in zip(range(len(tickers) -1),colors_line):
    ax2.bar(index[i], PE_store[i], bar_width, color=c,
                    alpha=opacity) # Bar plot of PE ratios
# Some formatting
ax2.set_ylim([0, np.amax(PE_store) + 5])
ax2.yaxis.set_tick_params(labelsize=6)
ax2.set_xticks(index[:-1])
ax2.set_xticklabels(tickers[:-1], rotation=90)
ax2.axhline(PE_store[-1], color="black")
ax2.text(.5,.9,'P/E Ratios (' + tickers[-1] + ' = Black Line)',
        horizontalalignment='center',
        transform=ax2.transAxes)
for i,c in zip(range(len(tickers) - 1),colors_line):
    ax3.bar(index[i], PB_store[i], bar_width, color=c,
                    alpha=opacity) # Bar plot of PB ratios
# Some formatting
ax3.set_ylim([0, np.amax(PB_store) + 1])
ax3.yaxis.set_tick_params(labelsize=6)
ax3.set_xticks(index[:-1])
ax3.set_xticklabels(tickers[:-1], rotation=90)
ax3.axhline(PB_store[-1], color="black")
ax3.text(.5,.9,'P/B Ratios (' + tickers[-1] + ' = Black Line)',
        horizontalalignment='center',
        transform=ax3.transAxes)
for i,c in zip(range(len(tickers) - 1),colors_line):
    ax4.bar(index[i], PCF_store[i], bar_width, color=c,
                    alpha=opacity) # Bar plot of PCF ratios
# Some formatting
ax4.set_ylim([0, np.amax(PCF_store) + 2])
ax4.yaxis.set_tick_params(labelsize=6)
ax4.set_xticks(index[:-1])
ax4.set_xticklabels(tickers[:-1], rotation=90)
ax4.axhline(PCF_store[-1], color="black")
ax4.text(.5,.9,'P/CF Ratios (' + tickers[-1] + ' = Black Line)',
        horizontalalignment='center',
        transform=ax4.transAxes)
for i,c in zip(range(len(tickers) - 1),colors_line):
    ax5.bar(index[i], yield_store[i], bar_width, color=c,
                    alpha=opacity) # Bar plot of yields
# Some formatting
ax5.set_ylim([0, np.amax(yield_store) + 1])
ax5.yaxis.set_tick_params(labelsize=6)
ax5.set_xticks(index[:-1])
ax5.set_xticklabels(tickers[:-1], rotation=90)
ax5.axhline(yield_store[-1], color="black")
ax5.text(.5,.9,'Div Yield (' + tickers[-1] + ' = Black Line)',
        horizontalalignment='center',
        transform=ax5.transAxes)
# Plot the table of relative performance
tabax = plt.subplot(gs1[0:2, -4:])
tabax.axis('off')
tabax.table(cellText=df_abs_pf.values,
          rowLabels=df_abs_pf.index,
          colLabels=df_abs_pf.columns,
          cellLoc='center', rowLoc='center',
          loc='center')
tabax.axis('off')
tabax.grid('off')
tabax.set_title("ETF Relative Value Monitor", {'fontsize': 20})
plt.show()
