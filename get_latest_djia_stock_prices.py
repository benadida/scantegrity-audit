# get_latest_djia_stock_prices.py
# by: Ronald L. Rivest
# last modified: October 11, 2009

# Usage:  python get_latest_djia_stock_prices.py

# This python program:
# * retrieves the latest DJIA stock data from Google's historical database,
#   and saves it in a file with name such as:
#      djia-stock-prices-21-Jun-09.txt

# The following improvements could be made in the future.
#   -- Adding error-handling if Google or internet is unavailable.
#   -- Adding error-handling for file open errors.

# global variable with date of data; format is e.g. "21-Jun-09"

# ben's modification for historical data
import sys

if len(sys.argv) > 1:
  data_date = sys.argv[1]
else:
  data_date = ""
  
# global variable date_width
date_width = 9

# global variable with width of stock symbols in output file
# large enough to include stock exchange symbol and blanks
# e.g. "NYSE:IBM        "
stock_symbol_width = 12

# global variable with filename for saved stock data
# (This gets initialized later, using latest close date.)
stock_data_filename = ""

# list of stock symbols for stocks in the DJIA
djia_stock_symbols = [ 
   "NYSE:MMM",      # 3M
   "NYSE:AA",       # Alcoa
   "NYSE:AXP",      # American Express
   "NYSE:T",        # AT&T
   "NYSE:BAC",      # Bank of America
   "NYSE:BA",       # Boeing
   "NYSE:CAT",      # Caterpillar
   "NYSE:CVX",      # Chevron
   "NASDAQ:CSCO",   # Cisco
   "NYSE:KO",       # Coca-Cola
   "NYSE:DD",       # DuPont
   "NYSE:XOM",      # Exxon Mobil
   "NYSE:GE",       # General Electric
   "NYSE:HPQ",      # Hewlett-Packard
   "NYSE:HD",       # Home Depot
   "NASDAQ:INTC",   # Intel
   "NYSE:IBM",      # IBM
   "NYSE:JNJ",      # Johnson & Johnson
   "NYSE:JPM",      # JPMorgan Chase
   "NYSE:KFT",      # Kraft Foods
   "NYSE:MCD",      # McDonalds
   "NYSE:MRK",      # Merk
   "NASDAQ:MSFT",   # Microsoft
   "NYSE:PFE",      # Pfizer
   "NYSE:PG",       # Proctor and Gamble
   "NYSE:TRV",      # Travelers
   "NYSE:UTX",      # United Technologies
   "NYSE:VZ",       # Verizon
   "NYSE:WMT",      # Wal-Mart Stores
   "NYSE:DIS"       # Walt Disney
]

import string
import urllib

def latest(stock_symbol):
    """
    Read the latest stock data from Google, for the given stock symbol.
    Input: stock symbol = "NYSE:IBM"  (for example)
    Output: Returns and prints string of form:
       NYSE:IBM    17-Jun-09,58.59,59.44,58.59,59.04,3826144.
    """

    global data_date

    url = "http://www.google.com/finance/historical?q=" + \
           stock_symbol + \
           "&output=csv"
           
    if data_date != "":
      url += "&startdate=%s&enddate=%s" % (data_date, data_date)
      
    u = urllib.urlopen(url)

    buffer = u.readlines()
    # buffer[0] is the first line, which contains label information
    # buffer[1] is the first real line of data, the latest quote information, e.g.
    #     17-Jun-09,416.19,419.72,411.56,415.16,3490947

    # modification by Ben to get historical data
    line_num = 1
    
    if data_date != "":
      while True:
        if buffer[line_num].split(",")[0] == data_date:
          break
        line_num += 1
        
    data_line = buffer[line_num]
    # make day have two-digit format always
    if data_line[1]=="-":
        data_line = "0" + data_line

    # Make data_line by prepending stock symbol in stock_symbol_width-char field,
    # with a period at the end, e.g.
    # NYSE:MMM    17-Jun-09,58.59,59.44,58.59,59.04,3826144.
    data_line = stock_symbol.ljust(stock_symbol_width)  + data_line

    # Remove trailing whitespace (e.g. CRLF)
    data_line = string.strip(data_line)

    # Print and return the result
    print "   ",data_line
    return data_line

def gather_stock_data():
    """
    Gather the latest stock data for the stocks in the DJIA.
    Return this as a list of strings, one per stock.
    """
    stock_data = []
    for stock_symbol in djia_stock_symbols:
        stock_data.append(latest(stock_symbol))
    return stock_data

def set_data_date(stock_data):
    """ 
    Set global variable data_date from given array of stock data strings
    """
    global data_date
    data_date = stock_data[0][stock_symbol_width:stock_symbol_width+date_width]

def save_stock_data(stock_data,stock_data_filename):
    """
    Write out file containing the seed for the PRNG; containing the stock data.
    Input: stock_data (array of strings, one per stock symbol)
    """
    f = open(stock_data_filename,"w")
    for line in stock_data:
        f.write(line + "\n")
    f.close()
        
def main():
    """
    Top-level routine to gather desired stock data and  save it.
    """

    print
    print "    Scantegrity II DJIA Stock Price Fetcher"
    print "    Version 1.0 (October 11, 2009)."
    print 

    print "    Step 1. Fetch latest DJIA stock quotes for each stock in DJIA."
    print "        Each line has: Exchange:Symbol, Date, Open, High, " \
          "Low, Close, Volume"

    stock_data = gather_stock_data()
    print

    print "Step 2. Write out stock data to files."
    
    stock_data_filename = "djia-stock-prices-"
    set_data_date(stock_data)
    stock_data_filename += data_date
    stock_data_filename += ".txt"
    save_stock_data(stock_data,stock_data_filename)
    print "    Stock data saved in file:                "+stock_data_filename

    stock_data_filename = "djia-stock-prices-latest.txt"
    save_stock_data(stock_data,stock_data_filename)
    print "    Second copy of stock data saved in file: "+stock_data_filename
    print

    # All done.
    print "Done. "
    print
    
# Call the main routine 
main()

# End of get_latest_djia_stock_prices.py
                       
