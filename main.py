import os
import pandas as pd

from models.run_algorithms import run_model
from classes.waterfall import Waterfall


if __name__ == '__main__':

    csv_path_waterfall = f"data/waterfall_data/init_synth_waterfall1.csv"
    csv_path_users = "data/valuation_folder/synthetic_valuation_matrix.csv"
    waterfall_name = os.path.basename(csv_path_waterfall)
    ADNETWORKS = pd.read_csv(csv_path_users, sep=',', index_col=0, nrows=1).columns[3:]
    algo = 'SandS'
    waterfall = Waterfall(csv_path=csv_path_waterfall)

    final_waterfall = run_model(csv_path_waterfall, csv_path_users, waterfall_name,
                                'outputs', 'my_log', algo, ADNETWORKS, flag = False)
