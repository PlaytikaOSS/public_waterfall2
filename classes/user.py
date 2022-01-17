import numpy as np
import pprint

from classes.consts import DEFAULT_AD_NETWORK_NAME

class User:

    def __init__(self, user_id, adnetwork_names=None, beta_param=None, max_price=1, valuations=None,
                 constant_valuation=False, use_default_ad_network=False):
        self.user_id = user_id
        self.adnetwork_names = adnetwork_names if adnetwork_names is not None else list(valuations.keys())
        self.beta_param = beta_param
        self.constant_valuation = constant_valuation
        self.max_price = max_price

        self.default_valuation = 0 if self.beta_param is None else np.random.beta(*self.beta_param) * self.max_price

        # Use default ad-network with price 0 to capture every user that is not captured by any other ad-network.
        self.use_default_ad_network = use_default_ad_network

        self.valuations = valuations
        self.init_valuation()

    def init_valuation(self):
        if self.valuations is None:
            self.valuations = {adnetworks_name: self.set_valuation() for adnetworks_name in self.adnetwork_names}

        if self.use_default_ad_network:
            self.valuations[DEFAULT_AD_NETWORK_NAME] = 0

    def set_valuation(self):
        if self.constant_valuation:
            return self.default_valuation
        else:
            return np.random.beta(*self.beta_param) * self.max_price

    def get_valuation(self, adnetworks_name):
        return self.valuations.get(adnetworks_name)

    def __repr__(self):
        return f"user_id = {self.user_id}\nvaluations:\n{pprint.pformat(self.valuations)}"




