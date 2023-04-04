# IMPORTS
import argparse
import calendar
import csv
import sys
import os
import pandas as pd
from datetime import datetime ,timedelta
from datetime import date as d
from tabulate import tabulate
from rich.console import Console
from helpers import create_file, add_row_to_file, remove_row_from_file, get_next_id

# FORMATTING
console = Console()

# MAIN 
def main():
    # validate input arguments
    try:
        argument = sys.argv[1]
    except:
        error = "Please provide an argument, use '--help' to get a list of valid arguments"
        console.print(":warning:", error, style="red" ) 
        raise ValueError(error)

    # before taking any action, check if the tool already has its own internal conception of what day it is, if not set it to today's date
    if os.path.exists(file_path_today) != True and argument != '--set-time': # skip this action when the 'set-time' argument is entered
        # get current date
        current_date = d.today()
        # set the date
        set_time(current_date)            

    # also, before taking any action, first check if products have been expired, to keep inventory up to date at all times
    check_expired_products() 

    # check if there is a date argument given
    if '--today' in sys.argv or '--now' in sys.argv:
        # get current date
        input_date = get_current_date_from_file()
        # it is about 1 specific day, so set the start and end of period to this same date
        period_start = input_date
        period_end = input_date
    elif '--yesterday' in sys.argv: 
        today = get_current_date_from_file()
        input_date = today + timedelta(days=-1) 
        # it is about 1 specific day, so set the start and end of period to this same date
        period_start = input_date
        period_end = input_date  
    elif '--date' in sys.argv: 
        input_date = args.date 
        # check if it is a specific date (month + year + day) or a period (month + year)
        try:
            # it is a date
            specific_date = datetime.strptime(input_date, r"%Y-%m-%d").date()
            # it is about 1 specific day, so set the start and end of period to this same date
            period_start = specific_date
            period_end = specific_date
        except:
            try:
                # it is a period
                period = datetime.strptime(input_date, r"%Y-%m")
                # set first day of the month as start
                period_start = datetime(period.year, period.month, 1).date()
                # retrieve last day of the month
                res = calendar.monthrange(period.year, period.month)
                last_day_of_month = res[1]
                period_end = datetime(period.year, period.month, last_day_of_month).date()
            except:
                error = "Please provide a valid date/period"
                console.print(":warning:", error, style="red" ) 
                raise ValueError(error)
    elif '--period' in sys.argv:                     
        input_date = args.period 
        try:
            period = datetime.strptime(input_date, r"%Y-%m")
            # set first day of the month as start
            period_start = datetime(period.year, period.month, 1).date()
            # retrieve last day of the month
            res = calendar.monthrange(period.year, period.month)
            last_day_of_month = res[1]
            period_end = datetime(period.year, period.month, last_day_of_month).date()
        except:
            error = "Please provide a valid date/period"
            console.print(":warning:", error, style="red" ) 
            raise ValueError(error)
    elif '--set-time' in sys.argv: 
        input_date = args.set_time
        # it is about 1 specific day, so set the start and end of period to this same date
        period_start = input_date
        period_end = input_date
    else:
        input_date = None
        period_start = None
        period_end = None

    # Define which function matches the argument and call its function
    if argument == 'buy':
        product_name = args.product_name 
        price = args.price 
        expiration_date = args.expiration_date 
        console.print( buy(product_name,price,expiration_date) , style="green" )
    elif argument == 'sell':
        product_name = args.product_name 
        price = args.price 
        console.print( sell(product_name, price) , style="green" )
    elif argument == 'report':        
        sub_argument = args.report # options: 'inventory'/ 'revenue'/ 'profit'
        if sub_argument == 'inventory':
            console.print(get_inventory_report(period_start), style="green" )
        if sub_argument == 'revenue':
            console.print(get_revenue_report(period_start,period_end), style="green" )
        if sub_argument == 'profit':
            console.print(get_total_profit(period_start,period_end), style="green" )
    elif argument == 'chart':
        sub_argument = args.chart # options: 'profit'
        if sub_argument == 'profit':
            console.print(get_profit_chart(period_start,period_end), style="green" )
    elif argument == '--advance-time':
        days = args.advance_time
        console.print( advance_time(days), style="green" )
    elif argument == '--set-time':
        days = args.set_time
        console.print( set_time(period_start), style="green" )

    # After every action, check if products have expired, to keep inventory up to date at all times
    check_expired_products()
    
# DEFAULTS 
# static directories
current_dir = os.getcwd()
file_path_bought = os.path.join(current_dir,'bought.csv')
file_path_sold = os.path.join(current_dir,'sold.csv')
file_path_inventory = os.path.join(current_dir,'inventory.csv')
file_path_trash = os.path.join(current_dir,'trash.csv')
file_path_today = os.path.join(current_dir,'today.csv')

# file headers
headers_buy = ["id", "product_name", "buy_date", "buy_price","expiration_date","bought_date"]
headers_sell = ["bought_id", "sell_date", "sell_price"]
headers_inventory = ["bought_id", "product_name", "buy_price", "expiration_date", "bought_date"]
headers_inventory_report = ["Product Name", "Count", "Buy Price", "Expiration Date"]
headers_trash = ["bought_id", "product_name", "buy_price", "expiration_date", "bought_date"]
headers_today = ["date"]

# excel sheet names
sheet_name_profit_chart = 'Profit'

# FUNCTIONS
def set_time(date_to_set):
    # set the internal date for this tool
    if os.path.exists(file_path_today) != True:
        # create file
        create_file(file_path_today,headers_today)
    # set date in file 
    row = [date_to_set]
    add_row_to_file(file_path_today,row,headers_today,'w') # (OVER)WRITE
    return 'OK'
       
def get_current_date_from_file():
    # get current date from file (the internal date)
    with open(file_path_today, 'r', newline='') as csvfile: # READ      
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_in_file_str = str(row['date'])
            date_in_file = datetime.strptime(date_in_file_str, r'%Y-%m-%d').date()          
    return date_in_file

def advance_time(nr_of_days):
    # get current date
    date = get_current_date_from_file()
    # calculate new date
    new_date = date + timedelta(days=nr_of_days) 
    # overwrite date in file
    row = [new_date]
    add_row_to_file(file_path_today,row,headers_today,'w')
    return 'OK'

def buy(product_name, price, expiration_date):
    # get current date, this will be the bought date
    bought_date = get_current_date_from_file()

    # create buy row
    bought_id = get_next_id(file_path_bought,'id')
    current_date = get_current_date_from_file()
    buy_row = [bought_id, product_name, current_date, price, expiration_date, bought_date]

    # first create new files if needed
    if bought_id == 1:
        create_file(file_path_bought,headers_buy)
        create_file(file_path_inventory,headers_inventory)

    # update bought
    add_row_to_file(file_path_bought,buy_row,headers_buy)

    # update inventory
    inventory_row = [bought_id, product_name, price ,expiration_date, bought_date]
    add_row_to_file(file_path_inventory,inventory_row,headers_inventory)
    return 'OK'

def sell(product_name, price):
    # check which item to sell
    bought_id = get_best_item_to_sell(product_name)
    if bought_id is None:
        return 'ERROR: Product not in stock.'
    else:
        # remove from inventory
        remove_row_from_file(file_path_inventory, headers_inventory,'bought_id', bought_id)

        # add to sold
        if os.path.exists(file_path_sold) != True:
            # create file
            create_file(file_path_sold,headers_sell)
           
        date = get_current_date_from_file()
        row = [bought_id, date, price]
        add_row_to_file(file_path_sold,row,headers_sell)
    return 'OK'       

def get_best_item_to_sell(product_name):
    # returns a bought id if the product is available or None if the product is out of stock 
    # this function relays on the 'first in first out' principle

    # check if inventory file exists
    if os.path.exists(file_path_inventory) != True:
        # no inventory available
        return None
    with open(file_path_inventory, 'r', newline='') as csvfile:       
        reader = csv.DictReader(csvfile)
        dates = []
        for row in reader:
            if row['product_name'] == product_name:
                # get expiration date and add to list
                expiration_date = row['expiration_date']
                # add to list 
                dates.append(expiration_date)
        if len(dates) > 0:
            with open(file_path_inventory, 'r', newline='') as csvfile:        
                reader = csv.DictReader(csvfile)
                # get product that expires first
                min_date = min(dates)
                for x in reader:
                    if x['product_name'] == product_name and x['expiration_date'] == min_date:
                        # product available
                        return x['bought_id']     
        else:
            # product out of stock
            return None  

def check_expired_products():
    # the expiration date is the LAST day that a product can be sold, after this day it will be added to the trash
    
    # check if inventory file exists
    if os.path.exists(file_path_inventory) != True:
        # no inventory available, so no expired products either
        return     
    
    # check all products in the inventory for their expiration date, if expired move product out of inventory into trash
    with open(file_path_inventory, 'r', newline='') as csvfile:        
        reader = csv.DictReader(csvfile)
        remove_product = False
        for row in reader:
            # get expiration date
            expiration_date = datetime.strptime(row['expiration_date'], r"%Y-%m-%d").date()
            # check if this product is expired
            if expiration_date < get_current_date_from_file():          
                # check if trash file exists
                if os.path.exists(file_path_trash) != True:
                    create_file(file_path_trash,headers_trash)

                # add product to trash     
                new_row = list(row.values())      
                add_row_to_file(file_path_trash,new_row,headers_trash)

                # go outside this for loop, so that we close the inventory file
                remove_product = True
                bought_id = row['bought_id']
                break
    if remove_product == True:
        # remove product from inventory
        remove_row_from_file(file_path_inventory,headers_inventory ,'bought_id', bought_id)
        # run function again
        check_expired_products()
    else:
        # no (more) expired products
        return
 
def get_inventory_report(report_date: d):
        # raise an error if report date is in the future, since we do not do inventory predictions
        if report_date > get_current_date_from_file():
            error = "Report dates in the future are not allowed"
            console.print(":warning:", error, style="red" ) 
            raise ValueError(error)

        # get current inventory
        try:
            # create dataframe from file
            df_inventory = pd.read_csv(file_path_inventory)
            # exclude products that were bought after the report date, since we do want to return the inventory for the given report date
            df_inventory = df_inventory[df_inventory['bought_date'] <= str(report_date)]
        except:
            # create empty dataframe
            df_inventory = pd.DataFrame()

        # get products in trash (= expired inventory)
        try:
            df_trash = pd.read_csv(file_path_trash)
            # get expired products bought before or on the report date and not yet expired on the report date
            df_trash = df_trash[(df_trash['bought_date'] <= str(report_date)) & (df_trash['expiration_date'] >= str(report_date))]
        except:
            # create empty dataframe
            df_trash = pd.DataFrame()

        # include the expired products to the inventory dataframe
        df = pd.concat([df_inventory,df_trash])

        # generate inventory output table
        if len(df) > 0:
            # add a 'count' column with value 1 to each row
            df['Count'] = 1
            # count how many rows match based on product, price and expiration date
            dfg = df.groupby(['product_name','buy_price','expiration_date'])['Count'].sum().reset_index()

            # generate report
            # first, change the column order
            dfg = dfg[['product_name','Count','buy_price','expiration_date']]
            # then, rename the colums
            dfg = dfg.rename(columns={'product_name': 'Product Name', 'buy_price': 'Buy Price', 'expiration_date': 'Expiration Date'})      
            # finally, print the table
            table = tabulate(dfg, headers='keys', tablefmt='psql',showindex=False)
            return table
        else:
            # generate empty table
            empty_df = pd.DataFrame()
            empty_df['Product Name'] = None
            empty_df['Count'] = None
            empty_df['Buy Price'] = None
            empty_df['Expiration Date'] = None
            empty_table = tabulate(empty_df, headers='keys', tablefmt='psql',showindex=False)
            return empty_table

def get_revenue_report(period_start: d, period_end: d):
    # get revenue
    revenue = get_total_revenue(period_start, period_end)
    # generate result based on input dates
    today = get_current_date_from_file()
    if period_start == period_end:
        # it is a specific date
        if period_start == today:
            result = f"Today's revenue so far: {revenue}"
        elif period_start == (today + timedelta(days=-1) ):
            result = f"Yesterday's revenue: {revenue}"
        else:
            result = f"Revenue from {period_start}: {revenue}"
    else:
        # it is a period
        period = datetime.strptime(str(period_start), r"%Y-%m-%d")
        year =  period.year
        month = calendar.month_name[period.month] 
        result = f"Revenue from {month} {year}: {revenue}"        
    return result

def get_total_revenue(period_start: d, period_end: d): 
    revenue = 0
    if os.path.exists(file_path_sold) == True:
        # get sold items within period
        with open(file_path_sold, 'r', newline='') as csvfile:       
            reader = csv.DictReader(csvfile)            
            for row in reader:
                if str(row['sell_date']) >= str(period_start) and str(row['sell_date']) <= str(period_end):    
                    # get sell price
                    revenue += float(row['sell_price'])   
    return revenue

def get_total_costs(period_start: d, period_end: d): 
    cost = 0
    if os.path.exists(file_path_bought) == True:
        with open(file_path_bought, 'r', newline='') as csvfile_bought:       
            reader_bought = csv.DictReader(csvfile_bought)            
            for x in reader_bought:
                if str(x['buy_date']) >= str(period_start) and str(x['buy_date']) <= str(period_end):                
                    cost += float(x['buy_price'])
    return cost

def get_total_profit(period_start: d, period_end: d):
    revenue = get_total_revenue(period_start, period_end)
    cost = get_total_costs(period_start, period_end)
    profit = revenue - cost
    return round(profit,1)

def get_profit_chart(period_start: d, period_end: d):
    # generate dynamic file path
    file_path_profit_chart = os.path.join(current_dir,f'profit chart - {period_start} - {period_end}.xlsx')

    # delete existing file
    if os.path.exists(file_path_profit_chart) == True:
        os.remove(file_path_profit_chart)

    # generate DAILY profit chart
    period_start_date = datetime.strptime(str(period_start), r"%Y-%m-%d").date()   
    period_end_date = datetime.strptime(str(period_end), r"%Y-%m-%d").date()        
    number_of_days = (period_end_date - period_start_date).days + 1 
    chart_list = []
    for x in range(number_of_days):
        row = []
        if x > 0:
            specific_date = period_start_date + timedelta(days=x)
        else:
            specific_date = period_start_date
        row.append(str(specific_date))
        # get profit of this specific date
        profit = get_total_profit(specific_date, specific_date)
        row.append(profit)
        # add to chart list
        chart_list.append(row)

    # create a dataframe
    df = pd.DataFrame(chart_list,columns = ["date","profit"])

    # add dataframe to excel
    writer = pd.ExcelWriter(file_path_profit_chart, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name_profit_chart)

    # define workbook and worksheet
    workbook = writer.book
    worksheet = writer.sheets[sheet_name_profit_chart]

    # create chart of type 'column'
    chart = workbook.add_chart({'type': 'column'})

    # define row and column positions of input data
    first_row = 1               # always 1, because 0 is the header
    last_row = len(chart_list)
    profit_first_column = 2     # profit column, because 0 = the index id and 1 = date
    profit_last_column = 2      # profit column, because 0 = the index id and 1 = date
    date_first_column = 1       # date column, because 0 = the index id 
    date_last_column = 1        # date column, because 0 = the index id 

    # add series to the chart
    chart.add_series({
        'values':        [sheet_name_profit_chart, first_row, profit_first_column, last_row, profit_last_column],
        'categories':    [sheet_name_profit_chart, first_row, date_first_column, last_row, date_last_column]
    })
     
    # hide chart legend
    chart.set_legend({'position': 'none'})

    # add title
    chart.set_title({'name': 'Daily profit'})

    # insert the chart into the worksheet
    worksheet.insert_chart('E2', chart) # add in cell E2, because columns A,B and C have data, D and E are empty

    # close excel 
    writer.close()
    return f'file generated: {file_path_profit_chart}'

# PARSER
# create argument parser
parser = argparse.ArgumentParser(prog="SuperPy",description='Keeps track of a supermarket inventory.')

# add generic arguments
parser.add_argument('--set-time',type=str,help='Set the internal date')
parser.add_argument('--advance-time',type=int,help='Adds days to the internal date')

# create subparser for underlying argument groups
subparser = parser.add_subparsers(dest='command')

# create buy subparser with arguments
buy_parser = subparser.add_parser('buy',help='Registers a bought product')
buy_parser.add_argument('--product-name',type= str,help='Name of the bought product')
buy_parser.add_argument('--price',type=float,help='Price of the the bought product')
buy_parser.add_argument('--expiration-date',type=str, help='Expiration date of the bought product')

# create sell subparser with arguments
sell_parser = subparser.add_parser('sell',help='Registers a sold product')
sell_parser.add_argument('--product-name',type= str,help='Name of the sold product')
sell_parser.add_argument('--price',type=float,help='Price of the sold product')

# create report subparser with arguments
report_parser = subparser.add_parser('report',help='Generates a report')
report_parser.add_argument('report', help='inventory, revenue or profit', nargs='?', choices=('inventory', 'revenue', 'profit'))
command_group = report_parser.add_mutually_exclusive_group()
command_group.add_argument('--today','--now', help='Base the report on todays date', nargs='?')
command_group.add_argument('--yesterday', help='Base the report on yesterdays date', nargs='?')
command_group.add_argument('--date', type=str, help='Base the report on a specific date or period')

# create chart subparser with arguments
chart_parser = subparser.add_parser('chart',help='Generates a chart')
chart_parser.add_argument('chart', help='profit', nargs='?', choices=('profit'))
command_group = chart_parser.add_mutually_exclusive_group()
command_group.add_argument('--period', type=str, help='Base the chart on a specific period')
command_group.add_argument('--today','--now', help='Base the chart on todays date', nargs='?')
command_group.add_argument('--yesterday', help='Base the chart on yesterdays date', nargs='?')
command_group.add_argument('--date', type=str, help='Base the chart on a specific date or period')

args = parser.parse_args()

# call main function
if __name__ == "__main__":
    main()
