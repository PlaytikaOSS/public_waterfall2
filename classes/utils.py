import numpy as np
import pandas as pd
import copy
import pickle
import os
import logging

from scipy.stats import beta
from classes.ad_unit import AdUnit
from classes.user import User


def create_real_users(path, init_waterfall, adnetwork_names, users_df=None, path_log=None, beta_size=3):
    """Creating users valuations from real data.
    Utype = True if valuations are Beta dist
    Ufactors = True learn the factors"""

    if path_log is not None:
        logging.basicConfig(filename=path_log, filemode='a', level=logging.INFO)

    if users_df is None: users_df = pd.read_csv(path)
    users_df.columns = [col.replace("_rpi", "") for col in users_df.columns]
    valuations_cols = [col for col in users_df.columns if col not in {'revenue', 'rpi'}]
    users_df = users_df[valuations_cols]

    # validation for the sampling process
    if abs(init_waterfall.get_impressions() - sum(users_df.impressions)) / init_waterfall.get_impressions() > 0.2:
        if path_log is not None: logging.info("error. sum impressions in valuation and waterfall do not match")

    users = []
    for i in range(len(users_df)):
        valuations = dict(users_df.iloc[i])
        user_id = valuations.pop("user_id")
        user = User(user_id=user_id, adnetwork_names=adnetwork_names, valuations=valuations)
        users.append(user)

    # handle users with beta distribution
    if not os.path.exists(f"{path[:-4]}_factors.txt"): # if factors file does not exist
        if path_log is not None: logging.info("Beta factors do not exists. Function will now estimate them")
        Factors = copy.deepcopy(MAX_CAPACITY_PER_ADNETWORK)
        for i in range(0, len(Factors)): Factors[i] = 1
    else:
        with open(f"{path[:-4]}_factors.txt", "rb") as fp:
            Factors = pickle.load(fp)

    cnt = 0
    for user in users:
        for adNetwork in adnetwork_names:
            try:
                _results = np.array(user.valuations[adNetwork].split(','), dtype=float)
            except:
                _results = np.array(user.valuations[adNetwork], dtype=float)
            try:
                if _results.size == 1:
                    user.valuations[adNetwork] = np.mean(_results)
                    user.valuations[adNetwork] *= Factors[adNetwork]
                else:
                    user.valuations[adNetwork] = np.mean(beta.rvs(*_results, size=beta_size))
                    user.valuations[adNetwork] *= Factors[adNetwork]
            except:
                cnt += 1
    if path_log is not None: logging.info(f"Total beta estimation errors: {cnt}")

    if not os.path.exists(f"{path[:-4]}_factors.txt"):
        cp_users = copy.deepcopy(users)
        new_factors = optimize_factors(cp_users, init_waterfall, Factors)

        for user in users:
            for adNetwork in adnetwork_names:
                user.valuations[adNetwork] *= new_factors[adNetwork]

        with open(f"{path[:-4]}_factors.txt", "wb") as fp:
            pickle.dump(new_factors, fp)

    return users

def optimize_factors(cp_users, init_waterfall, Factors):
    """Learn the coefficients to map the valuation mat to the real waterfall numberr of impressions"""

    def objective(Ad_unitsA, Ad_unitsB):
        """This function measure how close are two waterfalls in terms of weighted impressions"""
        wMAE = 0
        for i in range(len(Ad_unitsA)):
            wMAE += abs(Ad_unitsA[i].impressions-Ad_unitsB[i].impressions) * Ad_unitsA[i].weight
        return wMAE

    # define the weights according to prices
    total_prices = sum(ad_unit.price for ad_unit in init_waterfall.ad_units)
    for ad_unit in init_waterfall.ad_units:
        ad_unit.weight = ad_unit.price / total_prices

    for ad_unit in init_waterfall.ad_units:
        curr_adNetwork = ad_unit.adnetwork_name
        curr_users = copy.deepcopy(cp_users)
        for user in curr_users:
            for adNetwork in user.adnetwork_names:
                if adNetwork != curr_adNetwork:
                    user.valuations[adNetwork] *= Factors[adNetwork]
        best_score = np.inf
        for i in range(80,122,4): # check between 0.8 and 1.2
            val = i / 100
            curr_waterfall = copy.deepcopy(init_waterfall)
            curr_users_temp = copy.deepcopy(curr_users)
            for user in curr_users_temp:
                user.valuations[curr_adNetwork] *= val
            _results = curr_waterfall.run(curr_users_temp, reset_waterfall=True)  # run users in the waterfall
            score = objective(init_waterfall.ad_units,curr_waterfall.ad_units)
            if score < best_score:
                best_score = score
                Factors[curr_adNetwork] = val

    return Factors

def get_user_by_id(users, user_id):
    """find user in users list according to user_id"""

    for user in users:
        if user.user_id == user_id:
            return user
    return None # if user wasn't found


def create_ad_units(ad_units_params_per_adnetwork, add_default=False):
    """Creating ad-units from a dictionary of lists, per ad-network a list of dictionaries containing all information
    to initiallize a new instance, e.g., adnetwork_name, ad_unit_name, order, section, price"""

    ad_units = []
    for adnetwork in ad_units_params_per_adnetwork:
        for params in ad_units_params_per_adnetwork[adnetwork]:
            if 'adnetwork_name' not in params:
                params['adnetwork_name'] = adnetwork
            ad_unit = AdUnit(**params)
            ad_units.append(ad_unit)

    if add_default:
        ad_units.append(AdUnit.get_default_ad_unit())

    return ad_units


if __name__ == "__main__":

    print('hi')
