# public_waterfall2
The search and score-based waterfall optimization

This code aims to optimize waterfall auction strategy.
The code is based on Halbersberg et al., 2022 - https://arxiv.org/pdf/2201.06409.pdf
The code is inspired by the well known K2 algorithm (Cooper and Herscovits, 1992)

The repository is organized as follows:

classes - all the necessary classes

data - the synthetic datasets and waterfalls

models - the S&S algorithms: run_algorithms.py apply the S&S/MCTS while search_and_score.py contains the ulilizations - e.g., the neighbor selection

*Quick start*: run main.py
