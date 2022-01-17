# Defining a default instance with price 0 to capture all users that wasn't captured by any other instance.
DEFAULT_AD_NETWORK_NAME = "default_ad_network"
DEFAULT_AD_UNIT_NAME = "default_ad_unit"

# Columns needed in order to initialize a waterfall from a csv file.
DF_COLUMNS = ["adnetwork_name", "ad_unit_name", "order", "section", "price", "rpm", "impressions", "fill_rate", "revenue"]

MAX_PRICE = 150
THRESHOLD = 30 # maximal difference in price between two successive ad-units

# For search and score
VALIDATION = 1  # number of cross validation
MAX_ITER = 40
EPSILON = 0.1 # minimum improvement required in $$