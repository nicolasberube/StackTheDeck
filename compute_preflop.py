#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:20:37 2020

@author: berube
"""
import os
from tqdm import tqdm
from itertools import combinations
import time
import numpy as np
from StackTheDeck import choose, cards_functions
import pickle


def compute_preflop():
    CF = cards_functions()
    single = np.zeros((52, choose(52, 2)), dtype='bool')
    for idx, (c1, c2) in enumerate(combinations(range(52), 2)):
        single[c1, idx] = 1
        single[c2, idx] = 1
    doubles = ~(single.T@single)
    start_iter = 0
    for file_name in os.listdir():
        if file_name[:13] == 'preflop_hash_' and file_name[-4:] == '.npy':
            start_iter = max(int(file_name[13:-4]), start_iter)
    if start_iter == 0:
        holes_data = np.zeros((choose(52, 2), 2), dtype=float)
    else:
        holes_data = np.load(f'preflop_hash_{start_iter}.npy')
    save_dt = 60
    t_start = time.time()
    with tqdm(total=choose(52, 5), initial=start_iter) as pbar:
        for n_iter, table in enumerate(combinations(range(52), 5)):
            if n_iter < start_iter:
                continue
            pbar.update(1)
            if pbar.last_print_t > t_start+save_dt:
                t_start += save_dt
                names_remove = [file_name for file_name in os.listdir()
                                if (file_name[:13] == 'preflop_hash_' and
                                    file_name[-4:] == '.npy')]
                np.save(f'preflop_hash_{n_iter}.npy', holes_data)
                for file_name in names_remove:
                    os.remove(file_name)
            holes = np.array(CF.table_holes(table))
            for hole_idx in range(holes.shape[0]):
                if holes[hole_idx] != -1:
                    losing_holes = holes < holes[hole_idx]
                    winning_holes = holes > holes[hole_idx]
                    holes_data[hole_idx, 1] += \
                        (losing_holes*doubles[hole_idx]).sum() - 245
                    holes_data[hole_idx, 0] += \
                        (winning_holes*doubles[hole_idx]).sum()
    names_remove = [file_name for file_name in os.listdir()
                    if (file_name[:13] == 'preflop_hash_' and
                        file_name[-4:] == '.npy')]
    np.save(f'preflop_hash_{n_iter+1}.npy', holes_data)
    for file_name in names_remove:
        os.remove(file_name)
    holes_data = holes_data/choose(47, 2)/choose(50, 5)
    np.save(f'preflop_hash.npy', holes_data)
    with open('preflop.pkl', 'wb') as f:
        pickle.dump(holes_data.tolist(), f)


if __name__ == "__main__":
    compute_preflop()
