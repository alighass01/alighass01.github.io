from modulefinder import AddPackagePath
import pandas as pd
import time
import sys

# function to add entire sets to collection
def add_setparts(inv_id):

    # Read the existing CSV file into a DataFrame or create an empty DataFrame if the file doesn't exist
    try:
        existing_df = pd.read_csv('pers_parts_collection.csv')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=['inventory_id', 'part_num', 'quantity', 'img_url'])


    # Read the CSV file into a DataFrame
    df = pd.read_csv('inventory_parts.csv.gz', compression='gzip')

    # Filter rows where inventory_id is equal to inv_id
    filtered_df = df[df['inventory_id'] == inv_id]

    # Remove rows where 'is_spare' column is equal to 't' from filtered_df
    filtered_df = filtered_df[filtered_df['is_spare'] != 't']
    #print(filtered_df)

    parts_list = filtered_df['part_num'].unique()
    parts_list = parts_list.tolist()

    #num_entries = len(filtered_df)
    #print(num_entries)

    # Select specific columns for the new CSV file
    selected_columns = ['inventory_id', 'part_num', 'quantity', 'img_url']

    # Create a new DataFrame with only the selected columns
    new_entries_df = filtered_df[selected_columns]

    # Append new entries to the existing DataFrame
    combined_df = existing_df.append(new_entries_df, ignore_index=True)

    combined_df = combined_df.groupby('part_num', as_index=False).agg({
        'inventory_id': 'first',  # Take the first value (assuming it's constant for each 'part_num')
        'quantity': 'sum',
        'img_url': 'first'  # Take the first value (assuming it's constant for each 'part_num')
    })
    combined_df = combined_df[combined_df['quantity'] != 0]

    #print(combined_df)
    #print(len(combined_df))

    combined_df.to_csv('pers_parts_collection.csv', index=False)

    return parts_list


# function to remove entire sets from collection
def remove_setparts(inv_id):

    # Read 'pers_parts_collection.csv' into a DataFrame
    pers_parts_collection_df = pd.read_csv('pers_parts_collection.csv')

    # Combine 'quantity' for duplicate 'part_num' and remove rows with resulting quantity of 0
    pers_parts_collection_df = pers_parts_collection_df.groupby(['inventory_id','part_num','img_url'], as_index=False)['quantity'].sum()
    pers_parts_collection_df = pers_parts_collection_df[pers_parts_collection_df['quantity'] != 0]
    
    # Read 'inventory_parts.csv' into a DataFrame and filter rows where 'inventory_id' matches
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz')
    filtered_inventory_parts_df = inventory_parts_df[inventory_parts_df['inventory_id'] == inv_id]

    filtered_inventory_parts_df = filtered_inventory_parts_df[filtered_inventory_parts_df['is_spare'] != 't']

    filtered_inventory_parts_df = filtered_inventory_parts_df.groupby('part_num', as_index=False).agg({
        'inventory_id': 'first',  # Take the first value (assuming it's constant for each 'part_num')
        'quantity': 'sum',
        'img_url': 'first'  # Take the first value (assuming it's constant for each 'part_num')
    })

    # Iterate over the rows in filtered_inventory_parts_df and update 'quantity' in pers_parts_collection_df
    for index, row in filtered_inventory_parts_df.iterrows():
        part_num = row['part_num']
        quantity_to_remove = row['quantity']

        # Find the rows in pers_parts_collection_df with matching 'part_num'
        matching_rows = pers_parts_collection_df[pers_parts_collection_df['part_num'] == part_num]

        if not matching_rows.empty:
            # Update 'quantity' by subtracting the quantity_to_remove
            pers_parts_collection_df.loc[matching_rows.index, 'quantity'] -= quantity_to_remove

    # Save the updated pers_parts_collection_df to 'pers_parts_collection.csv'
    pers_parts_collection_df.to_csv('pers_parts_collection.csv', index=False)

    #print(pers_parts_collection_df)
    #print(len(pers_parts_collection_df))


# this was my attempt at implementing a way to add and remove individual parts from a user's collection
"""def add_indivparts(part_num,num2add):

    # Read the existing CSV file into a DataFrame or create an empty DataFrame if the file doesn't exist
    try:
        pers_parts_collection_df = pd.read_csv('pers_parts_collection.csv')
    except FileNotFoundError:
        pers_parts_collection_df = pd.DataFrame(columns=['inventory_id', 'part_num', 'quantity', 'img_url'])


    # Read the CSV file into a DataFrame
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz', compression='gzip')

    filtered_inventory_parts_df = inventory_parts_df[inventory_parts_df['part_num'] == part_num]
    filtered_inventory_parts_df = filtered_inventory_parts_df[filtered_inventory_parts_df['is_spare'] != 't']
    filtered_inventory_parts_df = filtered_inventory_parts_df.groupby('part_num', as_index=False).agg({
        'inventory_id': 'first',  # Take the first value (assuming it's constant for each 'part_num')
        'quantity': lambda x: num2add,
        'img_url': 'first'  # Take the first value (assuming it's constant for each 'part_num')
    })

    pers_parts_collection_df = pers_parts_collection_df.append(filtered_inventory_parts_df, ignore_index=True)
    pers_parts_collection_df.to_csv('pers_parts_collection.csv', index=False)


def remove_indivparts(part_num,num2rem):

    pers_parts_collection_df = pd.read_csv('pers_parts_collection.csv')
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz', compression='gzip')"""

# function to add sets to collection
def addset(set_num,parts_list):

    try:
        existing_pers_set_collection = pd.read_csv('pers_set_collection.csv')
    except FileNotFoundError:
        existing_pers_set_collection = pd.DataFrame(columns=['inventory_id', 'set_num', 'parts','name', 'year', 'img_url'])

    inventory_sets_df = pd.read_csv('inventory_sets.csv.gz')
    sets_df = pd.read_csv('sets.csv.gz')
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz')

    inv_id = setn2invid(set_num)

    matching_inventoryset_row = inventory_sets_df[inventory_sets_df['inventory_id'] == inv_id]



    matching_set_row = sets_df[sets_df['set_num'] == set_num]

    if not matching_set_row.empty:
        # Get the value of the inventory_id column corresponding to set_num
        name = matching_set_row.iloc[0]['name']
        year = matching_set_row.iloc[0]['year']
        num_parts = matching_set_row.iloc[0]['num_parts']
        img_url = matching_set_row.iloc[0]['img_url']

    inv_id = setn2invid(set_num)

    pers_set_collection_df = pd.DataFrame({
        'inventory_id': [inv_id], 
        'set_num': [set_num],
        'parts': [parts_list],
        'img_url': [img_url]
    })

    updated_pers_set_collection = pd.concat([existing_pers_set_collection, pers_set_collection_df], ignore_index=True)
    updated_pers_set_collection.to_csv('pers_set_collection.csv', index=False)

    #print(updated_pers_set_collection)


# function to remove sets from collection
def removeset(inv_id):
    existing_pers_set_collection = pd.read_csv('pers_set_collection.csv')

    matching_rows = existing_pers_set_collection[existing_pers_set_collection['inventory_id'] == inv_id]

    if not matching_rows.empty:
        index_to_remove = matching_rows.index[0]
        existing_pers_set_collection = existing_pers_set_collection.drop(index_to_remove)

    else:
        typingPrint("That set is not currenlty in your collection")

    existing_pers_set_collection.to_csv('pers_set_collection.csv', index=False)

    #print(existing_pers_set_collection)


def matchset():
    existing_pers_parts_collection_df = pd.read_csv('pers_parts_collection.csv')
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz')
    set_info_df = pd.read_csv('sets.csv.gz')

    compressed_pers_parts_collection_df = existing_pers_parts_collection_df.groupby('part_num', as_index=False)['quantity'].sum()
    compressed_pers_parts_collection_df = compressed_pers_parts_collection_df[compressed_pers_parts_collection_df['quantity'] != 0]
    #print(compressed_pers_parts_collection_df)

    cinventory_parts_df = inventory_parts_df[inventory_parts_df['is_spare'] != 't']

    remaining_parts_perset_df = pd.DataFrame(columns=['inventory_id', 'part_num', 'remainder'])

    for inventory_id in cinventory_parts_df['inventory_id'].unique()[:100]:

        cinventory_parts_subset = pd.DataFrame(columns=['inventory_id', 'part_num', 'quantity'])
        # Filter rows in 'cinventory_parts_df' for the current inventory_id
        cinventory_parts_subset = cinventory_parts_df[cinventory_parts_df['inventory_id'] == inventory_id]
        cinventory_parts_subset = cinventory_parts_subset.groupby(['part_num', 'inventory_id'], as_index=False)['quantity'].sum()
        #cinventory_parts_subset = cinventory_parts_subset[cinventory_parts_subset['quantity'] != 0]

        #print(cinventory_parts_subset)

        for part_num in compressed_pers_parts_collection_df['part_num'].unique():

            pn_row = compressed_pers_parts_collection_df[compressed_pers_parts_collection_df['part_num'] == part_num]

            quantity_have = pn_row.iloc[0]['quantity']
            #print(quantity_have)
            #print(part_num)

            required_part_row = cinventory_parts_subset[cinventory_parts_subset['part_num'] == part_num]
            
            if not required_part_row.empty:
                # Get the value of the inventory_id column corresponding to set_num 'YTERRIER-1'
                quantity_need = required_part_row.iloc[0]['quantity']
                #print(quantity_need)
                remainder = quantity_have - quantity_need
                rem_parts_perset_df = pd.DataFrame({
                    'inventory_id': [inventory_id],  # Change this if you want to use a different inventory_id
                    'part_num': [part_num],
                    'coverage': [quantity_have],
                    'needed': [quantity_need],
                    'remainder': [remainder]
                })

                remaining_parts_perset_df = remaining_parts_perset_df.append(rem_parts_perset_df, ignore_index=True)

    #print(remaining_parts_perset_df)
    remaining_parts_perset_df.to_csv('remaining_parts.csv', index=False)

    sets_to_build = pd.DataFrame(columns=['inventory_id', 'set_num','percent_complete','num_pneeded'])

    for inventory_id in remaining_parts_perset_df['inventory_id'].unique():

        cremaining_parts_subset = pd.DataFrame(columns=['inventory_id','remainder','coverage','needed'])
        cremaining_parts_subset = remaining_parts_perset_df[remaining_parts_perset_df['inventory_id'] == inventory_id]
        cremaining_parts_subset = cremaining_parts_subset.groupby('inventory_id', as_index=False)['coverage'].sum()
        
        num_matching_piece_types = remaining_parts_perset_df['inventory_id'].value_counts()
        
        set_num = invid2setn(inventory_id)  

        required_set_row = set_info_df[set_info_df['set_num'] == set_num]
        np_needed = required_set_row.iloc[0]['num_parts']

        np_have = cremaining_parts_subset.iloc[0]['coverage']

        percent_complete = np_have/np_needed

        buildset_info_df = pd.DataFrame({
            'inventory_id': [inventory_id],  # Change this if you want to use a different inventory_id
            'set_num': [set_num],
            'percent_complete': [percent_complete],
            'num_pneeded': [np_needed]
        })

        sets_to_build = sets_to_build.append(buildset_info_df, ignore_index=True)
        sets_to_build = sets_to_build.sort_values(by='percent_complete', ascending=False)

    sets_to_build.to_csv('sets_to_build.csv', index=False)
    #print(sets_to_build)


# function for retrieving set information
def grabset(inv_id,set_num):

    # Read 'inventory_parts.csv.gz' into a DataFrame 
    df = pd.read_csv('inventory_parts.csv.gz', compression='gzip')

    # Find corresponding rows for given inventory id
    filtered_df = df[df['inventory_id'] == inv_id]

    # Name and return file given set_num
    filename = "set" + set_num + ".csv"
    filtered_df.to_csv(filename)


# function for finding set number corresponding to inventory id
def invid2setn(id):

    # Read 'inventories.csv.gz' into a DataFrame 
    inventory_set_df = pd.read_csv('inventories.csv.gz', compression='gzip')

    # find corresponding row for given id
    subset = inventory_set_df[inventory_set_df['id'] == id]

    if not subset.empty:
        # Return the set_num from the first matching row
        return subset['set_num'].iloc[0]
    else:
        # Return None if no matching row was found
        return None

    #return set_num


# function for finding inventory id corresponding to set number
def setn2invid(set_num):

    # Read 'inventories.csv.gz' into a DataFrame 
    inventory_set_df = pd.read_csv('inventories.csv.gz', compression='gzip')

    # Find corresponding row for given set number
    subset = inventory_set_df[inventory_set_df['set_num'] == set_num]

    if not subset.empty:
        # Return the id from the first matching row
        return subset['id'].iloc[0]
    else:
        # Return None if no matching row was found
        return None


def typingPrint(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)


def typingInput(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    value = input()  
    return value


def main():

    global typingInput

    running = True
    while running == True:

        typingPrint("Welcome to BrickedUp!....\n")
        time.sleep(1)
        go = typingInput("Are you ready to digitize your own LEGO collection? (Y/N) --> ")

        if go == 'Y':

            typingPrint("Let's start with adding.\n")

            question = True
            while question == True:

                a_parts = typingInput("Do you have any LEGO sets you would like to add to your collection? (Y/N) --> ")

                if a_parts == "Y":
                    adding_parts = True
                    question = False

                elif a_parts == "N":
                    adding_parts = False
                    question = False

                else:
                    typingPrint("I didn't catch that, sorry.\n")
            
            time.sleep(1)

            while adding_parts == True:

                typingPrint("Please be aware all entries are case sensitive, and most LEGO sets use capitalized letters!\n")
                typingPrint("Additionally, the functionality of inputting sets in this program requires adding '-1' to the end of the set number (e.g. set 30277 should be entered as 30277-1)\n")
                time.sleep(1)
                set_num = typingInput("Please type the set number of the LEGO set you would like to add: ")
                
                inv_id = setn2invid(set_num)
                parts_list = add_setparts(inv_id)
                time.sleep(1)
                typingPrint("Set pieces added!\n")
                addset(set_num,parts_list)
                time.sleep(1)
                typingPrint("Set added!\n")
                typingPrint('Your pers_parts_collection.csv and pers_set_collection.csv files have been updated!\n')
                time.sleep(1)
                
                question = True
                while question == True:

                    cont_add_parts = typingInput("Would you like to add another set? (Y/N) --> ")

                    if cont_add_parts == "Y":
                        question = False
                        continue

                    elif cont_add_parts == "N":
                        adding_parts = False
                        question = False

                    else:
                        typingPrint("I didn't catch that, sorry.\n")

            typingPrint("Before we move ahead, here's your chance to remove any sets from your collection.\n")
            
            question = True
            while question == True:

                rem_parts = typingInput("Are there any sets you would like to remove? (Y/N) --> ")

                if rem_parts == "Y":
                    removing_parts = True
                    question = False

                elif rem_parts == "N":
                    removing_parts = False
                    question = False

                else:
                    typingPrint("I didn't catch that, sorry.\n")
                

            while removing_parts == True:

                set_num = typingInput("Please type the set number of the LEGO set you would like to remove: ")
                
                inv_id = setn2invid(set_num)
                parts_list = remove_setparts(inv_id)
                time.sleep(1)
                typingPrint("Set pieces removed!\n")
                removeset(inv_id)
                time.sleep(1)
                typingPrint("Set removed!\n")
                typingPrint('Your pers_parts_collection.csv and pers_set_collection.csv files have been updated!\n')


                time.sleep(1)

                question = True
                while question == True:

                    cont_rem_parts = typingInput("Would you like to remove another set? (Y/N) --> ")

                    if cont_rem_parts == "Y":
                        question = False
                        continue

                    elif cont_rem_parts == "N":
                        removing_parts = False
                        question = False

                    else:
                        typingPrint("I didn't catch that, sorry.\n")
                        

            question = True
            while question == True:

                matchtime = typingInput("Now for the fun part! Are you ready to see what LEGO sets you could build? (Y/N) --> ")
            
                if matchtime == "Y":
                    matchset()
                    typingPrint("Sets have been matched!\n")
                    question = False

                elif matchtime == "N":
                    question = False

                else:
                    typingPrint("I didn't catch that, sorry.\n")

            typingPrint("Take a moment to view the results of the matching algorithm (if any). Results are compiled in the sets_to_build.csv file.\n")
            
            question = True
            while question == True:

                vsets = typingInput("After looking at the results, would you like to look at the requirements of a potential set? (Y/N) --> ")

                if vsets == "Y":
                    viewsets = True
                    question = False

                elif vsets == "N":
                    viewsets = False

                else:
                    typingPrint("I didn't catch that, sorry.\n")

            while viewsets == True:

                set_num = typingInput("What set would you like to recieve information on (please enter set number + '-1'): ")
                inv_id = setn2invid(set_num)
                grabset(inv_id,set_num)
                typingPrint("Set data has been downloaded!\n")
                time.sleep(1)

                question = True
                while question == True:
                    again = typingInput("Would you like to retrieve information on another set? (Y/N) --> ")
                
                    if again == "Y":
                        question = False
                        continue

                    elif again == "N":
                        viewsets = False
                        question = False

                    else:
                        typingPrint("I didn't catch that, sorry.\n")

            typingPrint("For building instructions, go to: https://www.lego.com/en-us/service/buildinginstructions?locale=en-us\n")
            typingPrint("Thanks for using BrickedUp. See you next time ;^)\n")
            running = False


        elif go == 'N':
            typingPrint("Understood...see you next time\n")
            running = False

        else:
            typingPrint("I didn't catch that, sorry.\n")


if __name__ == "__main__":
    main()


