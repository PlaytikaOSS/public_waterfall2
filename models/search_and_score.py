import random as rnd
import copy
import numpy as np
import pandas as pd
import itertools
import logging

from itertools import permutations
from classes.ad_unit import AdUnit
from classes.waterfall import Waterfall
from classes.consts import THRESHOLD, MAX_PRICE


def generate_valid_neighbors(waterfall):
    """this function searches for all possible neighbors"""

    neighbors = []
    for i in range(len(waterfall.ad_units)): # for each instance in the waterfall try to increse/decrease the price
        if waterfall.ad_units[i].ad_unit_name != 'Default': # do not change default prices
            # try to increase the price
            temp = copy.deepcopy(waterfall)
            if temp.ad_units[i].get_price() <= 11:
                temp.set_ad_unit_price(temp.ad_units[i], temp.ad_units[i].get_price() + 1, order=False) # add 1 dollar
            else:
                temp.set_ad_unit_price(temp.ad_units[i], temp.ad_units[i].get_price() + rnd.randint(1, 5), order=False)  # add 1-5 dollars
            id = temp.ad_units[i].ad_unit_id
            temp.reorder(sort_by='price', reverse=True)
            if validation_single_change(temp, i, waterfall) and validation_single_change(temp, temp.get_order_by_id(id) - 1, waterfall):
                neighbors.append(temp)
            # try to decrease the price
            temp = copy.deepcopy(waterfall)
            if temp.ad_units[i].get_price() <= 11:
                temp.set_ad_unit_price(temp.ad_units[i], temp.ad_units[i].get_price() - 1, order=False)  # reduce 1 dollar
            else:
                temp.set_ad_unit_price(temp.ad_units[i], temp.ad_units[i].get_price() - rnd.randint(1, 5), order=False) # reduce 1-5 dollars
            id = temp.ad_units[i].ad_unit_id
            temp.reorder(sort_by='price', reverse=True)
            if validation_single_change(temp, i, waterfall) and validation_single_change(temp, temp.get_order_by_id(id) - 1, waterfall):
                neighbors.append(temp)

    # try to add new instance
    valid_networks = list(MAX_CAPACITY_PER_ADNETWORK_paper.keys())
    for i in valid_networks:
        if waterfall.adnetwork_has_capacity(i):
            flag = 1
            cnt = 2
            while flag:
                temp = copy.deepcopy(waterfall)
                price = round(temp.get_df()["price"].nlargest(cnt).mean())
                if cnt > 5: # excelerate to improve runtime performance
                    cnt *=2
                if cnt > 30:
                    break
                ad_unit_name = f"{len(temp.ad_units)}_'new_inst'_US${price}"
                ad_unit = AdUnit(adnetwork_name=i,ad_unit_name=ad_unit_name,section='High',price=price)
                temp.add_ad_unit(ad_unit)
                temp.reorder(sort_by='price', reverse=True)
                if validation_single_change(temp,ad_unit.order - 1, waterfall):
                    flag = 0
                    neighbors.append(temp)
                else:
                    cnt += 1
            # update of capacity is in the main
    return neighbors

def delete_invalid_instances(waterfall, min_impressions = 50):
    """remove instances that are not working"""

    for ad_unit in waterfall.ad_units:
        if ad_unit.section != 'Auto' and ad_unit.revenue < 10 and ad_unit.impressions < min_impressions:
            waterfall.remove_ad_unit(ad_unit) #this will also update "capacities"
    return waterfall

def get_next_price(ad_units_list, ad_unit):
    """Returning the price of the instance before the given ad_unit from the same ad-network,
    according to the order given by ad_units_list."""

    price = None # there is no ad_unit of the same adNetwork above
    adnetwork_name = ad_unit.adnetwork_name
    for ad_unit_other in ad_units_list:
        if ad_unit.ad_unit_id == ad_unit_other.ad_unit_id:
            break
        if ad_unit_other.adnetwork_name == adnetwork_name:
            price = ad_unit_other.price
    return price

def validation_single_change(waterfall, j, waterfall_old):
    """validate specific neighbor waterfall"""

    # j is the index of the changed ad unit
    check = True
    # validate that another ad_unit of the same adNetwork with that price (or lower/higher) doesn't exist, two consecutive ad_units do not belong to the same ad-network, or that the difference is not greater than a certian threshold
    if j > 0 and j + 1 < len(waterfall.ad_units):
        val1 = get_next_price(waterfall.ad_units, waterfall.ad_units[j]) if get_next_price(waterfall.ad_units, waterfall.ad_units[j]) is not None else np.inf
        val2 = get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) if get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) is not None else 0
        if (waterfall.ad_units[j].get_price() >= val1 or
            waterfall.ad_units[j].get_price() <= val2 or
                abs(waterfall.ad_units[j].get_price() - waterfall.ad_units[j - 1].get_price()) > THRESHOLD or
                    abs(waterfall.ad_units[j].get_price() - waterfall.ad_units[j + 1].get_price()) > THRESHOLD or
                        waterfall.ad_units[j].get_price() > MAX_PRICE or
                            waterfall.ad_units[j].get_price() < 0 or
                                waterfall.ad_units[j].adnetwork_name == waterfall.ad_units[j - 1].adnetwork_name or
                                    waterfall.ad_units[j].adnetwork_name == waterfall.ad_units[j + 1].adnetwork_name):
            check = False
    # same but for the case that the changed ad_unit is the first instance
    elif j==0:
        val2 = get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) if get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) is not None else 0
        if j + 1 < len(waterfall.ad_units) and (waterfall.ad_units[j].get_price() <= val2 or
            abs(waterfall.ad_units[j].get_price() - waterfall.ad_units[j + 1].get_price()) > THRESHOLD or
                waterfall.ad_units[j].get_price() > MAX_PRICE or
                    waterfall.ad_units[j].get_price() < 0 or
                        waterfall.ad_units[j].adnetwork_name == waterfall.ad_units[j + 1].adnetwork_name):
            check = False
    else: # same but for the case that the changed ad_unit is the last instance
        val1 = get_next_price(waterfall.ad_units, waterfall.ad_units[j]) if get_next_price(waterfall.ad_units,waterfall.ad_units[j]) is not None else np.inf
        val2 = get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) if get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[j]) is not None else 0
        if (waterfall.ad_units[j].get_price() >= val1 or
                waterfall.ad_units[j].get_price() <= val2 or
                abs(waterfall.ad_units[j].get_price() - waterfall.ad_units[j - 1].get_price()) > THRESHOLD or
                waterfall.ad_units[j].get_price() > MAX_PRICE or
                waterfall.ad_units[j].get_price() < 0 or
                waterfall.ad_units[j].adnetwork_name == waterfall.ad_units[j - 1].adnetwork_name):
            check = False

    return check

def validation_entire_waterfall(waterfall):
    """validate entire waterfall"""

    checked = True

    price = waterfall.ad_units[0].get_price()
    name = waterfall.ad_units[0].adnetwork_name
    for i in range(len(waterfall.ad_units) - 1):
        # validate that two ad_units of same ad network don't have contradict prices or that the difference is not greater than a certian threshold
        val1 = get_next_price(waterfall.ad_units, waterfall.ad_units[i + 1]) if get_next_price(waterfall.ad_units,waterfall.ad_units[i + 1]) is not None else np.inf
        val2 = get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[i + 1]) if get_next_price(waterfall.ad_units[::-1], waterfall.ad_units[i + 1]) is not None else 0
        if (waterfall.ad_units[i + 1].get_price() >= val1 or
            waterfall.ad_units[i + 1].get_price() <= val2 or
                abs(waterfall.ad_units[i + 1].get_price() - price) > THRESHOLD or waterfall.ad_units[i + 1].get_price() > MAX_PRICE or
                    waterfall.ad_units[i + 1].get_price() < 0):
            checked = False
            break
        price = waterfall.ad_units[i + 1].get_price()
        # validate that two consecutive instances don't belong to the same ad network
        if waterfall.ad_units[i + 1].adnetwork_name == name:
            checked = False
            break
        name = waterfall.ad_units[i + 1].adnetwork_name

    return checked

def generate_all_neighbors(ADNETWORKS_list, prices, users, path_log):
    """apply exhaustive search"""

    def perm(n, seq):
        comb = []
        for p in itertools.product(seq, repeat=n):
            comb.append(p)
        return comb

    def create_waterfall(ADNETWORKS, comb):
        order = 1
        waterfall_list = []
        for i in range(len(ADNETWORKS)):
            waterfall_list.append('High,' + str(order) + ',' + ADNETWORKS[i] + ' $' + str(comb[i]) + ', 0, ' + str(
                0) + ', 0, ' + str(0) + ', 0, ' + str(0) + '_' + str(0))
        data = pd.DataFrame(data=[sub.split(",") for sub in waterfall_list[::-1]],
                     columns=['Section', 'Order', 'Ad unit', 'RPM', 'Impressions', 'Network fill rate',
                              'Revenue', 'Network RFM', 'Ad unit id'])
        return Waterfall(df=data)

    logging.basicConfig(filename=path_log, filemode = 'a', level=logging.INFO)
    logging.info("running global optimization")

    comb = []
    all_waterfall = []
    optimal_waterfall = []
    optimal_revenue = 0
    min_length = 2
    for i in range(min_length,len(ADNETWORKS_list) + 1):
        comb.append(perm(i, prices))
    for i in range(len(comb)):
        logging.info("running combination of size: " + str(i + min_length))
        curr_ADNETWORKS_list = list(permutations(ADNETWORKS_list,i+min_length))
        for k in curr_ADNETWORKS_list:
            logging.info("curr_ADNETWORKS_list: " + "".join(k))
            for j in comb[i]:
                waterfall = create_waterfall(k,j)
                waterfall.reorder(sort_by='price', reverse=True)
                _results = waterfall.run(users, reset_waterfall=True)
                revenue = waterfall.get_revenue()
                if revenue > optimal_revenue:
                    optimal_revenue = revenue
                    optimal_waterfall = copy.deepcopy(waterfall)
                all_waterfall.append(waterfall)

    return all_waterfall, optimal_waterfall, optimal_revenue
