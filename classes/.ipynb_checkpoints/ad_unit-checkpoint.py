import numpy as np

from classes.user import User
from classes.consts import DEFAULT_AD_NETWORK_NAME, DEFAULT_AD_UNIT_NAME, MAX_PRICE


class AdUnit:
    n_ad_unit = 0

    def __init__(self, adnetwork_name, ad_unit_name, order=0, section='Auto', price=None,
                 p_acceptance=1, rpm=0.0, impressions=0, fill_rate=0.0, revenue=0.0, ad_unit_id=None, **kwrgs):

        self.ad_unit_id = AdUnit.get_next_ad_unit_id(ad_unit_id)

        self.adnetwork_name = adnetwork_name
        self.ad_unit_name = ad_unit_name
        self.order = order

        self.section = section
        self.price = price if price is not None else self.get_initialize_price()
        self.p_acceptance = p_acceptance

        self.rpm = rpm
        self.impressions = impressions
        self.fill_rate = fill_rate
        self.revenue = revenue

        # The optimal revenue that could have been obtained from all users run through the ad-unit, i.e. the sum of all
        # real valuations of the users, as opposed to the revenue variable which is the sum of the floor price of the
        # ad-unit over all accepted impressions.
        self.opt_revenue = revenue

        self.views = 0 if self.fill_rate == 0 else int(self.impressions / self.fill_rate)

        self.kwrgs = kwrgs

    def get_initialize_price(self):
        return np.random.randint(min(5, MAX_PRICE - 1), MAX_PRICE)

    @staticmethod
    def get_next_ad_unit_id(proposed_ad_unit_id):
        """Automaticly defines an id for each new ad-unit"""

        if proposed_ad_unit_id is not None and proposed_ad_unit_id >= AdUnit.n_ad_unit:
            next_ad_unit_id = proposed_ad_unit_id
        else:
            next_ad_unit_id = AdUnit.n_ad_unit
        AdUnit.n_ad_unit += 1
        return next_ad_unit_id

    @staticmethod
    def get_default_ad_unit():
        return AdUnit(adnetwork_name=DEFAULT_AD_NETWORK_NAME, ad_unit_name=DEFAULT_AD_UNIT_NAME, order=np.inf,
                      section='Auto', price=0, p_acceptance=1)

    @staticmethod
    def copy_ad_unit(old_ad_unit, new_ad_unit_name, new_price):
        return AdUnit(adnetwork_name=old_ad_unit.adnetwork_name, ad_unit_name=new_ad_unit_name,
                      section=old_ad_unit.section, price=new_price, p_acceptance=old_ad_unit.p_acceptance)

    def reset(self):
        self.rpm = 0.0
        self.impressions = 0
        self.fill_rate = 0.0
        self.revenue = 0.0

        self.opt_revenue = 0.0
        self.views = 0

    def get_fill_rate(self):
        if self.views > 0:
            self.fill_rate = self.impressions / self.views
        return self.fill_rate

    def get_revenue(self):
        return self.revenue

    def ask_impression(self, user):
        self.views += user.valuations['impressions']
        user_valuation = user.get_valuation(self.adnetwork_name)
        if self.ad_unit_name.find('Med') != -1: #for Admob Med only
            user_valuation *= 1.1
        price = self.price / 1000
        if user_valuation is not None and price <= user_valuation and np.random.uniform() < self.p_acceptance:
            # Accepted impression
            self.impressions += user.valuations['impressions']
            self.revenue += price * user.valuations['impressions']
            self.opt_revenue += user_valuation * user.valuations['impressions']
            return user.user_id, self.get_name(), user_valuation, self.price
        return None

    def get_name(self):
        return f"{self.ad_unit_id}_{self.adnetwork_name}_{self.ad_unit_name}"

    def set_price(self, price):
        self.price = int(price)

    def get_price(self):
        return self.price

    def get_rpm(self):
        if self.impressions > 0:
            self.rpm = 1000 * self.revenue / self.impressions
        return self.rpm

    def get_tuple(self):
        # Should maintain the order from simulator.consts.DF_COLUMNS
        return self.adnetwork_name, self.ad_unit_name, self.order, self.section,\
               self.get_price(), self.get_rpm(), self.impressions, self.get_fill_rate(), self.get_revenue()

    def __repr__(self):
        return f"{self.order:2n}  {self.get_name():25s}-\tprice={self.get_price():2n},\trpm={self.get_rpm():5.2f},\t" \
            f"Impr={self.impressions:5n},\tfill_rate={self.get_fill_rate():5.2%},\t" \
            f"revenue={self.get_revenue():7.2f},\to_revenue={self.opt_revenue:6.2f}"


if __name__ == "__main__":

    print('hi')
