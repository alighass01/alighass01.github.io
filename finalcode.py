import pandas as pd



# function to add entire sets to collection
def add_setparts(inv_id):

    # Read the existing CSV file into a DataFrame or create an empty DataFrame if the file doesn't exist
    try:
        existing_df = pd.read_csv('pers_parts_collection.csv')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=['inventory_id', 'part_num', 'quantity', 'img_url'])


    # Read the CSV file into a DataFrame
    df = pd.read_csv('inventory_parts.csv.gz', compression='gzip')

    #inv_id = input('What LEGO set would you like to add? ')

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

    # Save the combined DataFrame to the existing CSV file
    combined_df.to_csv('pers_parts_collection.csv', index=False)

    combined_df = combined_df.groupby(['inventory_id','part_num','img_url'], as_index=False)['quantity'].sum()
    combined_df = combined_df[combined_df['quantity'] != 0]

    print(combined_df)
    print(len(combined_df))

    combined_df.to_csv('pers_parts_collection.csv', index=False)

    return parts_list


# function to remove entire sets from collection
def remove_setparts(inv_id):

    # Read 'pers_parts_collection.csv' into a DataFrame
    pers_parts_collection_df = pd.read_csv('pers_parts_collection.csv')

    # Combine 'quantity' for duplicate 'part_num' and remove rows with resulting quantity of 0
    pers_parts_collection_df = pers_parts_collection_df.groupby(['inventory_id','part_num','img_url'], as_index=False)['quantity'].sum()
    pers_parts_collection_df = pers_parts_collection_df[pers_parts_collection_df['quantity'] != 0]
    
    # Read 'inventory_parts.csv' into a DataFrame and filter rows where 'inventory_id' is 22
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz')
    filtered_inventory_parts_df = inventory_parts_df[inventory_parts_df['inventory_id'] == inv_id]

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

    print(pers_parts_collection_df)
    print(len(pers_parts_collection_df))


def addset(set_num,parts_list):

    try:
        existing_pers_set_collection = pd.read_csv('pers_set_collection.csv')
    except FileNotFoundError:
        existing_pers_set_collection = pd.DataFrame(columns=['inventory_id', 'set_num', 'parts','name', 'year', 'img_url'])

    inventory_sets_df = pd.read_csv('inventory_sets.csv.gz')
    sets_df = pd.read_csv('sets.csv.gz')
    inventory_parts_df = pd.read_csv('inventory_parts.csv.gz')

    matching_inventoryset_row = inventory_sets_df[inventory_sets_df['set_num'] == set_num]

    if not matching_inventoryset_row.empty:
        # Get the value of the inventory_id column corresponding to set_num 'YTERRIER-1'
        inventory_id = matching_inventoryset_row.iloc[0]['inventory_id']
        print(inventory_id)
    else:
        print("No matching rows found for set_num 'YTERRIER-1'")

    matching_set_row = sets_df[sets_df['set_num'] == set_num]

    if not matching_set_row.empty:
        # Get the value of the inventory_id column corresponding to set_num 'YTERRIER-1'
        name = matching_set_row.iloc[0]['name']
        year = matching_set_row.iloc[0]['year']
        num_parts = matching_set_row.iloc[0]['num_parts']
        img_url = matching_set_row.iloc[0]['img_url']

    inv_id = setn2invid(set_num)

    pers_set_collection_df = pd.DataFrame({
        'inventory_id': [inv_id],  # Change this if you want to use a different inventory_id
        'set_num': [set_num],
        'parts': [parts_list],
        'img_url': [img_url]
    })

    updated_pers_set_collection = pd.concat([existing_pers_set_collection, pers_set_collection_df], ignore_index=True)
    updated_pers_set_collection.to_csv('pers_set_collection.csv', index=False)

    print(updated_pers_set_collection)

def removeset(inv_id):
    existing_pers_set_collection = pd.read_csv('pers_set_collection.csv')

    index_to_remove = existing_pers_set_collection[existing_pers_set_collection['inventory_id'] == inv_id].index[0]

    existing_pers_set_collection = existing_pers_set_collection.drop(index_to_remove)
    existing_pers_set_collection.to_csv('pers_set_collection.csv', index=False)

    print(existing_pers_set_collection)


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

            #remaining_parts_perset_df = pd.concat([remaining_parts_perset_df, rem_parts_perset_df], ignore_index=True)
                remaining_parts_perset_df = remaining_parts_perset_df.append(rem_parts_perset_df, ignore_index=True)

    # Display the resulting DataFrame
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


    print(sets_to_build)


def invid2setn(id):

    inventory_set_df = pd.read_csv('inventories.csv.gz', compression='gzip')
    #set_info_df = pd.read_csv('sets.csv.gz')

    subset = inventory_set_df[inventory_set_df['id'] == id]

    if not subset.empty:
        # Return the set_num from the first matching row
        return subset['set_num'].iloc[0]
    else:
        # Return None if no matching row was found
        return None
    #set_num = i_s_rowofinterest.iloc[0]['set_num']

    #return set_num

def setn2invid(set_num):

    inventory_set_df = pd.read_csv('inventories.csv.gz', compression='gzip')
    subset = inventory_set_df[inventory_set_df['set_num'] == set_num]

    if not subset.empty:
        # Return the set_num from the first matching row
        return subset['set_num'].iloc[0]
    else:
        # Return None if no matching row was found
        return None





add_setparts(22)
matchset()
"""set_num = invid2setn(35)
print(set_num)
pers_parts_collection = 'pers_parts_collection.csv'
parts = add_setparts(inventory_partsDB,pers_parts_collection)
addset(parts

parts_list = add_setparts()
print(parts_list)
addset(parts_list"""


"""poop = pd.read_csv('inventory_sets.csv.gz')
print(poop)

poop2 = pd.read_csv('sets.csv.gz')
print(poop2)"""


"""inventory_partsDB = 'inventory_parts.csv.gz'
pers_parts_collection = 'pers_parts_collection.csv'

q_addset = input('Would you like to add a LEGO Set to your collection (Y/N)? ')

if q_addset == "Y":
    add_setparts(inventory_partsDB,pers_parts_collection)


def match_set():
poop = pd.read_csv(inventory_partsDB)
print(poop)

row_num = 1
row = poop.iloc[row_num,:]
url = row['img_url']

from PIL import Image
import requests
from io import BytesIO

response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.show()
"""