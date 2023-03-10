# imports
import pytest
import os
import csv
import random
from super import advance_time
from super import buy
from super import get_best_item_to_sell
from super import get_current_date_from_file
from super import sell
from datetime import date, timedelta

# directories
current_dir = os.getcwd()
file_path_bought = os.path.join(current_dir,'bought.csv')
file_path_sold = os.path.join(current_dir,'sold.csv')
file_path_inventory = os.path.join(current_dir,'inventory.csv')
file_path_trash = os.path.join(current_dir,'trash.csv')
file_path_today = os.path.join(current_dir,'today.csv')

# RANDOMIZER 
# use a randomizer to avoid testing with the same values over and over again, since that may cause invalid successfull tests
products = ["orange","apple","banana","cherry","potato","spinach","broccoli"]
product = random.choice(products) 
print(product)
buy_price = round(random.uniform(0.6,1.5),1)
print(buy_price)
sell_price = round(random.uniform(1.5,2.5),1)
print(sell_price)
# generate a random expiration date between today and 14 days in the future
today =  date.today()
random_number_of_days = random.randrange(14)
expiration_date = today + timedelta(days=random_number_of_days)
print(expiration_date)

# TESTS
def test_get_current_date_from_file_type():
    assert type(get_current_date_from_file()) == date 

def test_advance_time_response_increase():
    assert advance_time(2) == 'OK'

def test_advance_time_response_decrease():
    assert advance_time(-2) == 'OK'

def test_advance_time_file_output_increase():
    # first check current date in file
    current_date = get_current_date_from_file()
    # then add 2 days
    advance_time(2)
    # finally check if date in file is increased by 2 days
    assert get_current_date_from_file() == current_date + timedelta(days=2) 

def test_advance_time_file_output_decrease():
    # first check current date in file
    current_date = get_current_date_from_file()
    # then take 2 days
    advance_time(-2)
    # finally check if date in file is decreased by 2 days
    assert get_current_date_from_file() == current_date + timedelta(days=-2) 

def test_buy_response_non_expired():
    # generate a date in the future
    current_date = get_current_date_from_file()
    future_date = current_date + timedelta(days=2)
    # use future date as expiration date of product that is bought
    assert buy(product, buy_price, str(future_date)) == 'OK'

def test_buy_response_expired():
    # generate a date in the past
    current_date = get_current_date_from_file()
    past_date = current_date + timedelta(days=-2)
    # use past date as expiration date of product that is bought
    assert buy(product,buy_price, str(past_date)) == 'OK'

def test_buy_file_output():   
    buy(product, buy_price, str(expiration_date))
    # check if product is added to bought file
    with open(file_path_bought, 'r', newline='') as csvfile: # READ    
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        print(len(rows))
        last_row_nr = len(rows) -1
        assert rows[last_row_nr]['id'] ==  str(len(rows))
        assert rows[last_row_nr]['product_name'] ==  product
        assert rows[last_row_nr]['buy_price'] ==  str(buy_price)
        assert rows[last_row_nr]['expiration_date'] ==  str(expiration_date) 

def test_get_best_item_to_sell_success():   # this test only succeeds if the test_buy functions are executed first
    result = get_best_item_to_sell(product)
    # check if this is indeed a product that is in inventory
    with open(file_path_inventory, 'r', newline='') as csvfile: # READ    
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        list_of_ids = [x['bought_id'] for x in rows]
        assert result in list_of_ids

def test_get_best_item_to_sell_failure(): 
    # try to get a product that is not in the list of products
    assert get_best_item_to_sell("coconut") == None

def test_sell_response_success(): # this test only succeeds if the test_buy functions are executed first
    assert sell(product, sell_price) == 'OK'

def test_sell_response_failure():
    # try to sell a product that is not in the list of products
    assert sell('coconut', sell_price) == 'ERROR: Product not in stock.'


# FUTURE TESTS 
# I noticed that testing was not part of the requirements of the superpy assignment, so I stopped writing more tests

# python super.py chart profit --period 2023-01
#> file generated: C:\Winc\superpy\profit chart - 2023-01-01 - 2023-01-31.xlsx

# python super.py report inventory --now
# python super.py report inventory --yesterday
#> table

# python super.py --advance-time 2
#> OK

# python super.py report revenue --yesterday
#> Yesterday's revenue: 0

# python super.py report revenue --today
#> Today's revenue so far: 2

# python super.py report revenue --date 2019-12
#> Revenue from December 2019: 0

# python super.py report profit --today
#> 1.2

# ALL OTHER FUNCTIONS THAT ARE NOT INCLUDED YET