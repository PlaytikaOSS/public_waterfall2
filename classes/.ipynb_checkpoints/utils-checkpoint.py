import numpy as np
import pandas as pd
import copy
import pickle
from sklearn.utils import shuffle as sklearn_shuffle

from scipy.stats import beta
from classes.ad_unit import AdUnit
from classes.user import User


def create_real_users(path, init_waterfall, adnetwork_names, shuffle_users=False, Utype=False, Ufactors=False):
    """Creating users valuations from real data.
    shuffle_users = True will return the users in random order.
    Utype = True if valuations are Beta dist
    Ufactors = True learn the factors"""

    users_df = pd.read_csv(path)
    users_df.columns = [col.replace("_rpi", "") for col in users_df.columns]
    valuations_cols = [col for col in users_df.columns if col not in {'revenue', 'rpi'}]
    users_df = users_df[valuations_cols]

    # validation for the sampling process
    if abs(init_waterfall.get_impressions() - sum(users_df.impressions)) / init_waterfall.get_impressions() > 0.2:
        print('error. sum impression in valuation and waterfall does not match')

    if shuffle_users:
        sample_size = 10000
        users_df = sklearn_shuffle(users_df, n_samples=int(sample_size))
        users_df.reset_index(inplace=True, drop=True)

    users = []
    for i in range(len(users_df)):
        valuations = dict(users_df.iloc[i])
        user_id = valuations.pop("user_id")
        user = User(user_id=user_id, adnetwork_names=adnetwork_names, valuations=valuations)
        users.append(user)

    # handle users with beta distribution
    if Utype:
        if Ufactors: # init factors
            Factors = {"Facebook": 1,
                   "AppLovin": 1,
                   "Unity": 1,
                   "ironSource": 1,
                   "Cross": 1,
                   "Vungle": 1,
                   "HyprMx": 1,
                   "Admob": 1,
                   "Ogury": 1}
        else:
            with open(f"{path[:-4]}_factors.txt", "rb") as fp:
                Factors = pickle.load(fp)

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
                        user.valuations[adNetwork] = np.mean(beta.rvs(*_results, size=3))
                        user.valuations[adNetwork] *= Factors[adNetwork]
                except:
                    print('error')

        if Ufactors:
            cp_users = copy.deepcopy(users)
            new_factors = optimize_factors(cp_users, init_waterfall, Factors)

            for user in users:
                for adNetwork in adnetwork_names:
                    user.valuations[adNetwork] *= new_factors[adNetwork]

            with open(f"{path[:-4]}_factors.txt", "wb") as fp:
                pickle.dump(new_factors, fp)
    # end handle users with beta distribution

    return users


def optimize_factors(cp_users, init_waterfall, Factors):

    def objective(Ad_unitsA, Ad_unitsB):
        """This function measure how close are two waterfalls in terms of weighted impressions"""
        wMAE = 0
        for i in range(len(Ad_unitsA)):
            wMAE += abs(Ad_unitsA[i].impressions-Ad_unitsB[i].impressions) * Ad_unitsA[i].weight
        return wMAE

    # init indicators
    Indicators = {"Facebook": False,
               "AppLovin": False,
               "Unity": False,
               "ironSource": False,
               "Cross": False,
               "Vungle": False,
               "HyprMx": False,
               "Admob": False,
               "Ogury": False}

    # define the weights according to revenue
    total_revenue = init_waterfall.get_revenue()
    for ad_unit in init_waterfall.ad_units:
        ad_unit.weight = ad_unit.revenue / total_revenue

    for ad_unit in init_waterfall.ad_units:
        adNetwork = ad_unit.adnetwork_name
        if Indicators[adNetwork] == False:
            Indicators[adNetwork] = True
            best_score = np.inf
            for i in range(80,122,2):
                if (adNetwork != 'Facebook' and adNetwork != 'Unity') or i > 99: # don't decrease Facebook
                    val = i / 100
                    curr_waterfall = copy.deepcopy(init_waterfall)
                    curr_users = copy.deepcopy(cp_users)
                    for user in curr_users:
                        user.valuations[adNetwork] *= val
                    _results = curr_waterfall.run(curr_users, reset_waterfall=True)  # run users in the waterfall
                    score = objective(init_waterfall.ad_units,curr_waterfall.ad_units)
                    if score < best_score:
                        best_score = score
                        Factors[adNetwork] = val
            for user in cp_users:
                user.valuations[adNetwork] *= Factors[adNetwork]

    return Factors


def create_ad_units(ad_units_params_per_adnetwork, default_p_acceptance=None, add_default=False):
    """Creating ad-units from a dictionary of lists, per ad-network a list of dictionaries containing all information
    to initiallize a new instance, e.g., adnetwork_name, ad_unit_name, order, section, price, ...
    For example, ad_units_params_per_adnetwork['Admob'] can be:
    [{'adnetwork_name': 'Admob',
      'ad_unit_name': 'A_US:$80',
      'order': 2,
      'section': 'High',
      'price': 80,
      'rpm': 84.56,
      'impressions': 4528,
      'fill_rate': 0.059000000000000004,
      'revenue': 382.89},
     {'adnetwork_name': 'Admob',
      'ad_unit_name': 'B_US:$20',
      'order': 10,
      'section': 'High',
      'price': 20,
      'rpm': 20.18,
      'impressions': 33447,
      'fill_rate': 0.442,
      'revenue': 675.12},
     {'adnetwork_name': 'Admob',
      'ad_unit_name': 'D_Med',
      'order': 22,
      'section': 'High',
      'price': 8,
      'rpm': 8.15,
      'impressions': 2551,
      'fill_rate': 0.271,
      'revenue': 20.79}]"""

    n_adnetwork = len(ad_units_params_per_adnetwork)
    if default_p_acceptance is None:
        p_acceptance = np.clip(np.random.normal(loc=1, scale=0.25, size=n_adnetwork), a_min=0.25, a_max=1)
        p_acceptance = {adnetwork: p_acceptance[i] for i, adnetwork in enumerate(ad_units_params_per_adnetwork)}
    elif type(default_p_acceptance) == dict:
        p_acceptance = default_p_acceptance
    elif type(default_p_acceptance) == int:
        p_acceptance = {adnetwork: default_p_acceptance for adnetwork in ad_units_params_per_adnetwork}
    else:
        p_acceptance = False

    if p_acceptance:
        for adnetwork in ad_units_params_per_adnetwork:
            for ad_unit_params in ad_units_params_per_adnetwork[adnetwork]:
                ad_unit_params["p_acceptance"] = p_acceptance[adnetwork]

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
