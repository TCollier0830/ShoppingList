from __future__ import division
#!/usr/bin/env python
'''
Shopping Helper

Given a list of store inventories and a shopping list, return the minimum number of
store visits required to satisfy the shopping list.

For example, given the following stores & shopping list:

  Shopping List: 10 apples, 4 pears, 3 avocados, 1 peach

  Kroger: 4 apples, 5 pears, 10 peaches
  CostCo: 3 oranges, 4 apples, 4 pears, 3 avocados
  ALDI: 1 avocado, 10 apples
  Meijer: 2 apples

The minimum number of stores to satisfy this shopping list would be 3:
Kroger, CostCo and ALDI.
or
Kroger, CostCo and Meijer.

Shopping lists and store inventories will be passed in JSON format,
an example of which will be attached in the email.  Sample outputs for the
given inputs should also be attached as well.

Use the helper provided to print.

Usage: shopping_helper.py (shopping_list.json) (inventories.json)
'''

import argparse
import copy
import json
from operator import itemgetter
from itertools import combinations
from timeit import timeit

def FilteredInventory(stores, shopping_list_json):
    '''
    Filter our stores for unwanted information, empty shelves, and the like. Also, we pad empty keys with a value of 0 so we can use
    the built-in "all" function to see if our list can be satisfied

    Method:
        Make a list of stores, a list of fruits, and a running tally of the difference of our desired number of each fruit and the quantity at the store.

    Args:
        shopping_list_json: What we want
        type: dict
        stores: List of stores we may visit
        type: dict
    '''

    ### IMPROVEMENTS THAT NEED TO BE MADE ###
    """
    Ideally I would find all the items that could only be satisfied by a single store as well, 
    and I'll probably do that for fun later but I have too much homework right now.

    Peach Store would serve as a perfect example, it's the only place with peaches (which we want), 
    and ideally I would then be able to omit it from the search space and just append it to each list at the end.

    Also, unsure how we would handle "negative" fruit, for now just set it to 0.
    """
    ### IMPROVEMENTS THAT NEED TO BE MADE ###
    inventory, stores_with_fruit_that_we_care_about = ([] for i in xrange(2))
    TotalInventory = shopping_list_json.copy()
    for store in stores:
        TheyHaveTheFruits = False
        FilteredInventory = {}
        if len(store.get("inventory")) > 0:
            stores_with_fruit_that_we_care_about.append(store.get("name"))
            for fruit in shopping_list_json.keys():
                if fruit in store.get("inventory").keys():
                    TheyHaveTheFruits = True
                    if store.get("inventory")[fruit] > 0:
                        TotalInventory[fruit] -= store.get("inventory")[fruit]
                        FilteredInventory.update({fruit : store.get("inventory")[fruit]})
                    else:
                        FilteredInventory.update({fruit : 0})
                else:
                    FilteredInventory.update({fruit : 0})
            if TheyHaveTheFruits == False:
                stores_with_fruit_that_we_care_about.remove(store.get("name"))
            else:
                inventory.append(FilteredInventory)
    return inventory, TotalInventory, stores_with_fruit_that_we_care_about

def FindLowestOrderList(shopping_list,inventory,stores):
    '''
    
    Find a lowest order list

    Method:
        Buy every item that we can from the current store, and  delete that item from the list if
        the store has enough to satisfy our urge for that sweet sweet fruit. If our list is empty after this, then we're done.
        Else we will need to rescore the remaining stores and repeat until we have a list. This list should have the lowest possible order.    

    Args:
        shopping_list: What we want
        type: dict
        inventory: What the stores have
        type: dict
        stores: List of stores we may visit
        type: dict
    '''
    shopping_trip = []
    while len(shopping_list) > 0:
        scores = []
        for current_Store, current_inventory in enumerate(inventory):
            score= 0
            for Desired_Item, Desired_Quantity in shopping_list.items():
                if Desired_Item in current_inventory.keys():
                    if current_inventory[Desired_Item] >= Desired_Quantity:
                        score += 1
                    else:
                        score += (current_inventory[Desired_Item]/Desired_Quantity)
            scores.append((score, current_Store))
    
        #Sort the list in descending order, then add the top graded store to the shopping trip
        scores.sort(key=itemgetter(0), reverse=True)
        shopping_trip.append(stores[scores[0][1]])
    
        # Buy every item that we can from the current store, and  delete that item from the list if
        # the store has enough to satisfy our urge for that sweet sweet fruit. If our list is empty after this, then we're done.
        # Else we will need to rescore the remaining stores and repeat until we have a list. This list should have the lowest possible order.
        Current_best_store = scores[0][1]
        Fruits_we_have_enough_of = []
        for Desired_Item, Desired_Quantity in shopping_list.items():
            if Desired_Item in inventory[Current_best_store].keys():
                if Desired_Quantity - inventory[Current_best_store][Desired_Item] <= 0:
                    Fruits_we_have_enough_of.append(Desired_Item)
                else:
                    shopping_list[Desired_Item] = Desired_Quantity - inventory[Current_best_store][Desired_Item]
    
        for fruit in Fruits_we_have_enough_of:
            shopping_list.pop(fruit)

    return shopping_trip

def GetAllLists(stores,OptLength,shopping_list_json_compare,inventory):
    Final = []
    #Stores_mod = copy.copy(stores)
    #Stores_mod.remove('peach store')
    combs = combinations(stores, OptLength)
    for comb in combs:
        comb = list(comb)
        #comb.append('peach store')
        ValidList = [(shopping_list_json_compare[item] - sum([inventory[stores.index(comb[i])][item] for i in xrange(OptLength)])) for item in list(shopping_list_json_compare.keys())]
        if all(val <= 0 for val in ValidList):
            Final.append(comb)
    return Final

def satisfy_shopping_list(shopping_list_json, inventory_json):
    '''
    Find all of the possible combinations of stores such that the shopping list is satisfied and the number of stores is minimized.

    Method:
        The problem doesn't seem to be P-solvable, and if it is then I don't know the algorithm for it which is why I need to get a CS masters.
        Using a score heuristic we shall find a best possible list, and from there we can calculate all combinations of that many objects that 
        satisfies the shopping list.

    Args:
        shopping_list_json: What we want
        type: dict
        inventory_json: What the stores have
        type: dict
    '''

    #TC: Strip all of the stores that have nothing in inventory, and also don't consider any of the items that we don't want.
    shopping_list_json = {fruit: val for fruit, val in shopping_list_json.items() if val > 0 and type(val)==int}
    if len(shopping_list_json) > 0:
        inventory, TotalInventory, stores = FilteredInventory(inventory_json['stores'], shopping_list_json)

        #If all these values are less than or equal to zero then we can be sure the list is satisfiable.

        #The basic idea is to "grade" each store based on how well it can satisfy the need for each item in the shopping list,
        #then prioritize the stores with the highest combined scores. This system will assign at most a score of 1 per item, that way
        #we don't over prioritize the places like  the place with a jillion apples.
        if all(value <= 0 for value in TotalInventory.values()):

            shopping_trip = FindLowestOrderList(shopping_list_json.copy(),inventory,stores)

            #Finally, we should now have an example of a shortest possible list. Now we construct all permutations of this length
            #and test them, the built in combinations tool does this for unique combinations in the fastest possible way (for python).
            #Peach store is the only place with peaches, there's a better way to do this, but for testing this works.
            Final = GetAllLists(stores,len(shopping_trip),shopping_list_json.copy(),inventory)
            [print_store_combination(trip) for trip in Final]
        else:
            print("No combination of given stores can satisfy this shopping list :(")
            pass
    else:
        print("No combination of given stores can satisfy this shopping list :(")
        pass
    return

def print_store_combination(store_combination):
    '''
    Print store combination in the desired format.

    Args:
        store_combination: store list to print
        type: list of str
    '''
    store_combination_copy = copy.deepcopy(store_combination)
    store_combination_copy.sort()
    print(", ".join(store_combination_copy))
    return

def main():
    args = parse_args()
    with open(args.shopping_list_json_path) as shopping_list_json_file, open(args.inventory_json_path) as inventory_json_file:
        shopping_list_json = json.load(shopping_list_json_file)
        inventory_json = json.load(inventory_json_file)
        satisfy_shopping_list(shopping_list_json, inventory_json)
    return

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('shopping_list_json_path')
    p.add_argument('inventory_json_path')

    args = p.parse_args()
    return args

if __name__ == '__main__':
    # I added this for timing purposes, even if you don't accept my candidacy 
    # can you let me know what the result was and one what hardware it was ran?
    timing = False
    if(timing):
        iters = 1000
        print('On average I took: ' + str(timeit(main, number=iters)*1000./iters) + ' milliseconds')
    else:
        main()
