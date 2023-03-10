# Generic functions to help other python scripts

# IMPORTS
import csv
import os

# FUNCTIONS
def create_file(file_path,headers):
    # create file (by openening the file it will automatically be created if not existing)
    with open(file_path, 'a', newline='') as csvfile: # APPEND
        # add headers
        writer = csv.writer(csvfile) 
        writer.writerow(headers)
    return

def add_row_to_file(file_path,new_row,headers = None,mode = 'a'):
    # check if file exists
    if os.path.exists(file_path) != True:
        raise FileNotFoundError
    if mode == 'a':
        # open file in APPEND mode and create new row
        with open(file_path, 'a', newline='') as csvfile: # APPEND
            # add row
            writer = csv.writer(csvfile) 
            writer.writerow(new_row)
    elif mode == 'w':
        # open file in (OVER)WRITE mode and create new row with headers (because headers get overwritten as well)
        with open(file_path, 'w', newline='') as csvfile: # (OVER)WRITE  
            writer = csv.writer(csvfile) 
            writer.writerow(headers)
            writer.writerow(new_row)
    return new_row

def remove_row_from_file(file_path,headers,column_name,value):
    # get rows to keep
    rows_to_keep = []
    with open(file_path, 'r', newline='') as csvfile: # READ
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[column_name] != value:
                rows_to_keep.append(row)  

    # delete file
    os.remove(file_path) 

    # create file again, with headers 
    create_file(file_path, headers)

    # add rows 
    #print('len rows_to_keep =',len(rows_to_keep))
    if len(rows_to_keep) > 0:
        for x in rows_to_keep:
            #print('x =',x)
            row = list(x.values())
            #print('row =',row)
            add_row_to_file(file_path,row,headers)
    return        

def get_next_id(file_path, column_name): 
    # get max id in bought file
    if os.path.exists(file_path) == True:
        with open(file_path, 'r', newline='') as csvfile: # open file in read mode     
            reader = csv.DictReader(csvfile)
            max_id = max(int(row[column_name]) for row in reader)
            new_id = max_id + 1
    else:
        new_id = 1
    return new_id