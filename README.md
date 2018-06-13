# ETFRelativeValueMonitor
Performs a quick relative value analysis of user-defined set of ETFs by scraping data from Yahoo Finance. All you need to do is define the set of ETFs in the array 'tickers', with the benchmark in the last spot as instructed and also the start date you would like in the variable 'start' (need to check that all of your ETFs were trading at the start date). For instance, let's say you wanted a quick relative value view of the SPY ETF versus the GICs sectors since January 1st, 2009. You would set tickers and start to (note VFH is chosen for Financials due to the extraordinary distribution of XLF in 2016, and IYR is used for its longer history than XLRE):

tickers = ['XLE', 'XLY', 'XLK', 'XLB', 'VFH', 'XLI', 'XLV', 'XLU', 'XLP', 'IYR', 'SPY']

start = datetime.date(2009,1,1)

and the output is

![Screenshot1](https://github.com/ZackPolaski/ETFRelativeValueMonitor/blob/master/ETFval1.JPG)

Similarly, if you wanted to say view an analysis of some European country performance vs a broad European ETF, you could do

tickers = ['EWO', 'EWK', 'EWQ', 'EWG', 'EWI', 'EWN', 'EWP', 'EWD', 'EWL', 'EWU', 'VGK']

start = datetime.date(2009,1,1)

and the otuput is


![Screenshot2](https://github.com/ZackPolaski/ETFRelativeValueMonitor/blob/master/ETFval2.JPG)

** Of course, all of this is dependent on the quality of data available on Yahoo Finance**

Update 6/13/2018 - Some technicals related to 200D EWMA added




