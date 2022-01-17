import os
import pandas as pd

from models.run_algorithms import run_model
from classes.waterfall import Waterfall


if __name__ == '__main__':

    csv_path_waterfall = f"data/waterfall_data/waterfall.csv"
    csv_path_users = "data/valuation_folder/users_valuations_beta.csv"
    waterfall_name = os.path.basename(csv_path_waterfall)
    ADNETWORKS = pd.read_csv(csv_path_users, sep=',', index_col=0, nrows=1)[4:]
    algo = 'SandS'
    global MAX_CAPACITY_PER_ADNETWORK
    waterfall = Waterfall(csv_path=csv_path_waterfall)
    MAX_CAPACITY_PER_ADNETWORK = {}
    for i in range(0, len(ADNETWORKS)):
        MAX_CAPACITY_PER_ADNETWORK["AdNetwork%d" % (i + 1)] = waterfall.adnetworks_capacities["AdNetwork%d" % (i + 1)] + 1

    final_waterfall = run_model(csv_path_waterfall, csv_path_users, waterfall_name,
                                'outputs', 'my_log', algo, ADNETWORKS, flag = False)