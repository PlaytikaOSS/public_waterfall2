# Defining a default instance with price 0 to capture all users that wasn't captured by any other instance.
DEFAULT_AD_NETWORK_NAME = "default_ad_network"
DEFAULT_AD_UNIT_NAME = "default_ad_unit"

ADNETWORKS = {"Facebook", "AppLovin", "Unity", "ironSource", "Cross", "Vungle", "Admob"}
ADNETWORKS_full = {"Facebook", "AppLovin", "Unity", "ironSource", "Cross", "Vungle", "HyprMx", "Admob", "Ogury"}
ADNETWORKS_viterbi = {"Facebook", "AppLovin", "Unity", "Cross", "Vungle", "ironSource", "Admob"}

# Columns needed in order to initialize a waterfall from a csv file.
DF_COLUMNS = ["adnetwork_name", "ad_unit_name", "order", "section", "price", "rpm", "impressions", "fill_rate", "revenue"]

MAX_CAPACITY_VITERBI = {"Facebook": 5,
                        "AppLovin": 2,
                        "Unity": 5,
                        "ironSource": 4,
                        "Cross": 4,
                        "Vungle": 1,
                        "HyprMx": 1,
                        "Admob": 4,
                        "Ogury": 0}

MAX_CAPACITY_PER_ADNETWORK = {"Facebook": 10,
                              "AppLovin": 30,
                              "Unity": 30,
                              "ironSource": 10,
                              "Cross": 10,
                              "Vungle": 30,
                              "HyprMx": 2,
                              "Admob": 3,
                              "Ogury": 5}

EPSILON = 1
THRESHOLD = 25
MAX_PRICE = 25
AD_UNIT_PRICES = [i for i in range(1, MAX_PRICE, 1)]