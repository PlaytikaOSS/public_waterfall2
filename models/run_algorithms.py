import copy
import os
import pickle
import pandas as pd
import logging

from classes.waterfall import Waterfall
from classes.utils import create_real_users
from classes.consts import EPSILON, MAX_ITER, VALIDATION
from models.search_and_score import generate_valid_neighbors, delete_invalid_instances, generate_all_neighbors


def run_model(csv_path_waterfall, csv_path_users, waterfall_name, save_path, path_log, alg, ADNETWORKS_list, flag = False):


    logging.basicConfig(filename=path_log, filemode = 'a', level=logging.INFO)
    logging.info("running search procedure")

    all_neighbors = []
    optimal_waterfall = []
    optimal_revenue = []

    ################################
    # here search and score starts #
    ################################
    if alg == 'SandS':
        for i in range(VALIDATION): # for the S&S we use cross validation

            convergence = 1
            iter = 0
            cnt = 0

            waterfall = Waterfall(csv_path=csv_path_waterfall)  # init waterfall with Anna's waterfall
            if not os.path.exists(f"{save_path}/users_synth_{i}.txt"):
                users = create_real_users(path=csv_path_users, init_waterfall=waterfall, adnetwork_names=ADNETWORKS_list,
                                          beta_size=1)
                with open(f"{save_path}/users_synth_{i}.txt", "wb") as fp:
                    pickle.dump(users, fp)
            else:
                with open(f"{save_path}/users_synth_{i}.txt", "rb") as fp:
                    users = pickle.load(fp)

            save_best_revenue = []
            waterfall = delete_invalid_instances(waterfall)
            _results = waterfall.run(users, reset_waterfall=True)  # run users in the waterfall
            logging.info("VALIDATION: " + str(i))
            logging.info("init waterfall:")
            logging.info('waterfall - {}'.format(waterfall.get_df().to_string()))
            init_revenue = waterfall.get_revenue()
            save_best_revenue.append(init_revenue)
            logging.info(f"init revenue: {init_revenue}")

            # start search and score
            iter_revenue = init_revenue
            revenue = init_revenue
            save_waterfalls = []
            num_neighbors = [0]
            while convergence:
                logging.info(f"validation: {i}. iteration: {iter}.")
                iter += 1
                neighbors = generate_valid_neighbors(waterfall)  # neighbors is a list of waterfalls
                for n in neighbors:
                    cnt += 1
                    _results = n.run(users, reset_waterfall=True)  # run validation users in the waterfall
                    n = delete_invalid_instances(n)
                    _results = n.run(users, reset_waterfall=True)  # run validation users in the waterfall
                    curr_revenue = n.get_revenue()
                    if curr_revenue > revenue:  # adopt new waterfall
                        waterfall = copy.deepcopy(n)
                        save_waterfalls.append(waterfall)
                        revenue = curr_revenue
                        save_best_revenue.append(revenue)
                        logging.info(f"curr_revenue: {revenue} curr_num_neighbors: {cnt}")
                        logging.info('curr_waterfall - {}'.format(waterfall.get_df().to_string()))
                num_neighbors.append(cnt - sum(num_neighbors[:iter]))
                if iter >= MAX_ITER or revenue - iter_revenue <= EPSILON:  # stop conditions
                    convergence = 0
                iter_revenue = revenue  # the revenue in the current iteration (best neighbor)
            logging.info("final S&S waterfall")
            logging.info('waterfall - {}'.format(waterfall.get_df().to_string()))
            best_waterfall = copy.deepcopy(waterfall)
            waterfall.get_df().to_csv(f"{save_path}/final_SandS_waterfall_{waterfall_name}_{i}.csv", index=False)
            logging.info(f"total number of neighbors S: {cnt}")
            logging.info(f"final S&S revenue: {revenue}")
            save_best_revenue.append(revenue)
            pd.DataFrame(save_best_revenue).to_csv(f"{save_path}/revenue_SandS_{waterfall_name}_{i}.csv", index=False)
            pd.DataFrame(num_neighbors).to_csv(f"{save_path}/neighbors_SandS_{waterfall_name}_{i}.csv", index=False)

            with open(f"{save_path}/SandS_All_{waterfall_name}_{i}.txt", "wb") as fp:
                pickle.dump(save_waterfalls, fp)
            if flag == True:
                all_neighbors, optimal_waterfall, optimal_revenue = generate_all_neighbors(ADNETWORKS_list, range(0,21), users, path_log)

        else:
            #######################################
            # here monte carlo tree search starts #
            #######################################

            convergence = 1
            iter = 0
            cnt = 0
            
            waterfall = Waterfall(csv_path=csv_path_waterfall)  # init waterfall with Anna's waterfall
            if not os.path.exists(f"{save_path}/users_synth.txt"):
                users = create_real_users(path=csv_path_users, init_waterfall=waterfall, adnetwork_names=ADNETWORKS_list,
                                          beta_size=1)
                with open(f"{save_path}/users_synth.txt", "wb") as fp:
                    pickle.dump(users, fp)
            else:
                with open(f"{save_path}/users_synth.txt", "rb") as fp:
                    users = pickle.load(fp)
            
            save_best_revenue = []
            waterfall = delete_invalid_instances(waterfall)
            _results = waterfall.run(users, reset_waterfall=True)  # run users in the waterfall
            logging.info("init waterfall:")
            logging.info('waterfall - {}'.format(waterfall.get_df().to_string()))
            init_revenue = waterfall.get_revenue()
            save_best_revenue.append(init_revenue)
            logging.info(f"init revenue: {init_revenue}")

            # start monte carlo search
            iter_revenue = init_revenue
            revenue = init_revenue
            save_waterfalls = []
            num_neighbors = [0]
            while convergence:
                logging.info(f"iteration: {iter}.")
                iter += 1
                neighbors1 = generate_valid_neighbors(waterfall)  # neighbors is a list of waterfalls
                for n1 in neighbors1:
                    cnt += 1
                    _results = n1.run(users, reset_waterfall=True)  # run validation users in the waterfall
                    n1 = delete_invalid_instances(n1)
                    _results = n1.run(users, reset_waterfall=True)  # run validation users in the waterfall
                    neighbors2 = generate_valid_neighbors(n1)  # neighbors is a list of waterfalls:
                    for n2 in neighbors2:  # depth is two
                        cnt += 1
                        _results = n2.run(users, reset_waterfall=True)  # run validation users in the waterfall
                        n2 = delete_invalid_instances(n2)
                        _results = n2.run(users, reset_waterfall=True)  # run validation users in the waterfall
                        neighbors3 = generate_valid_neighbors(n2)  # neighbors is a list of waterfalls:
                        top_scores_level3 = []
                        for n3 in neighbors3:  # depth is three
                            cnt += 1
                            _results = n3.run(users, reset_waterfall=True)  # run validation users in the waterfall
                            n3 = delete_invalid_instances(n3)
                            _results = n3.run(users, reset_waterfall=True)  # run validation users in the waterfall
                            top_scores_level3.append(n3.get_revenue())
                        n2.set_best_child(neighbors3[top_scores_level3.index(max(top_scores_level3))])
                        curr_revenue = max(n2.best_child.get_revenue(), n1.get_revenue(), n2.get_revenue())
                        if curr_revenue > revenue:  # adopt new waterfall
                            if n2.best_child.get_revenue() == max(n2.best_child.get_revenue(), n1.get_revenue(),
                                                                  n2.get_revenue()):
                                n1.set_best_grandchild(n2.best_child)
                            elif n2.get_revenue() == max(n2.best_child.get_revenue(), n1.get_revenue(), n2.get_revenue()):
                                n1.set_best_child(n2)
                            waterfall = copy.deepcopy(n1)
                            save_waterfalls.append(waterfall)
                            revenue = curr_revenue
                            save_best_revenue.append(revenue)
                            print("curr_revenue: " + str(revenue) + " curr_num_neighbors: " + str(cnt))
                            logging.info('curr_waterfall - {}'.format(waterfall.get_df().to_string()))

                num_neighbors.append(cnt - sum(num_neighbors[:iter]))
                if iter >= MAX_ITER or revenue - iter_revenue <= EPSILON:  # stop conditions
                    convergence = 0
                iter_revenue = revenue  # the revenue in the current iteration (best neighbor)

            best_waterfall = copy.deepcopy(save_waterfalls[-1])
            if best_waterfall.best_child != [] and best_waterfall.best_child.get_revenue() > best_waterfall.get_revenue():
                save_waterfalls.append(best_waterfall.best_child)
            if best_waterfall.best_grandchild != [] and best_waterfall.best_grandchild.get_revenue() > best_waterfall.get_revenue():
                save_waterfalls.append(best_waterfall.best_grandchild)
            best_waterfall = copy.deepcopy(save_waterfalls[-1])
            print("Optimize Monte-Carlo tree search waterfall:")
            print(best_waterfall.get_df())
            best_waterfall.get_df().to_csv(f"{save_path}/final_MCTS_waterfall_{waterfall_name}.csv", index=False)
            print("total number of neighbors S: " + str(cnt))
            print("final Monte-Carlo tree search revenue: " + str(revenue))
            save_best_revenue.append(revenue)
            pd.DataFrame(save_best_revenue).to_csv(f"{save_path}/revenue_MCTS_{waterfall_name}.csv", index=False)
            pd.DataFrame(num_neighbors).to_csv(f"{save_path}/neighbors_MCTS_{waterfall_name}.csv", index=False)
            with open(f"{save_path}/MCTS_All_{waterfall_name}.txt", "wb") as fp:
                pickle.dump(save_waterfalls, fp)

        return best_waterfall, save_best_revenue, all_neighbors, optimal_waterfall, optimal_revenue
