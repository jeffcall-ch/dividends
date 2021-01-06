import yfinance as yf

msft = yf.Ticker("KO")

# get stock info
msft.info

# get historical market data
hist = msft.history(period="max")

# show actions (dividends, splits)
msft.actions

# show dividends
msft.dividends

print(msft.dividends)