#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 20:08:18 2020

@author: berube
"""
import os
from random import choice
from itertools import combinations, product
import pygame
from array import array
import ctypes
from ctypes import c_int, c_float
import pickle
from math import log
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def choose(n, k):
    if k < 0 or k > n:
        return 0
    res = 1
    for i in range(k):
        res *= (n-i)/(k-i)
    return int(res+0.5)


def bisect(func, a, b, args=None, xtol=10**-8):
    if args is None:
        args = []
    x0 = a
    x1 = b
    if func(x0, *args)*func(x1, *args) > 0:
        raise NameError('No zeros in given interval')
    while abs(x1-x0) > xtol:
        xt = (x0 + x1)/2
        if func(x0, *args)*func((x0 + x1)/2, *args) > 0:
            x0 = xt
        else:
            x1 = xt
    return (x0+x1)/2


class hashcards():
    def __init__(self,
                 hand_size=7,
                 deck_size=52):
        self.hand_size = hand_size
        self.deck_size = deck_size
        # self.handidx_table = np_zeros((self.hand_size, self.deck_size),
        #                               dtype='i4')
        self.handidx_table = [[0]*self.deck_size
                              for _ in range(self.hand_size)]
        for i in range(self.hand_size):
            for j in range(self.deck_size-1):
                if j == 0:
                    self.handidx_table[i][j] = choose(self.deck_size-1-j,
                                                      self.hand_size-1-i)
                else:
                    self.handidx_table[i][j] = (
                        self.handidx_table[i][j-1] *
                        (self.deck_size-j-self.hand_size+1+i) //
                        (self.deck_size-j)
                        )
        # self.handidx_table = self.handidx_table.tolist()

    def idx(self,
            cards):
        ordered_cards = [-1] + sorted(cards)
        handidx = 0
        for i, card in enumerate(ordered_cards[1:]):
            handidx += sum(self.handidx_table[i][ordered_cards[i]+1:card])
        return handidx


def detect_straight(cards):
    # Should be between 0 and 12
    holes = []
    if len(cards) < 3:
        return holes

    loop_cards = sorted([c+1 for c in cards], key=lambda x: -x)
    if loop_cards[-1] == 1:
        loop_cards = [14]+loop_cards

    # If the straight already there
    if len(cards) >= 5:
        diffs = [loop_cards[i]-loop_cards[i+4]
                 for i in range(len(loop_cards)-4)]
        for i, d in enumerate(diffs):
            if d == 4:
                hole = None
                holes.append([hole, loop_cards[i]])

    # If one card is missing
    if len(cards) >= 4:
        diffs = [loop_cards[i]-loop_cards[i+3]
                 for i in range(len(loop_cards)-3)]
        for i, d in enumerate(diffs):
            if d == 4:
                for h in range(loop_cards[i+3]+1, loop_cards[i]):
                    if h != loop_cards[i+1] and h != loop_cards[i+2]:
                        hole = h
                        break
                holes.append([hole, loop_cards[i]])
            if d == 3:
                hole = loop_cards[i+3]-1
                if hole >= 1:
                    holes.append([hole, loop_cards[i]])
                hole = loop_cards[i]+1
                if hole <= 14:
                    holes.append([hole, hole])

    # If two cards are missing
    diffs = [loop_cards[i]-loop_cards[i+2]
             for i in range(len(loop_cards)-2)]
    for i, d in enumerate(diffs):
        if d == 4:
            hole = [c for c in range(loop_cards[i+2]+1, loop_cards[i])
                    if c != loop_cards[i+1]]
            holes.append([hole, loop_cards[i]])
        if d == 3:
            hole = [loop_cards[i+2] - 1,
                    loop_cards[i+2] + loop_cards[i] - loop_cards[i+1]]
            if hole[0] >= 1:
                holes.append([hole, loop_cards[i]])
            hole = [loop_cards[i+2] + loop_cards[i] - loop_cards[i+1],
                    loop_cards[i] + 1]
            if hole[1] <= 14:
                holes.append([hole, hole[1]])
        if d == 2:
            hole = [loop_cards[i+2]-2, loop_cards[i+2]-1]
            if hole[0] >= 1:
                holes.append([hole, loop_cards[i]])
            hole = [loop_cards[i+2]-1, loop_cards[i]+1]
            if hole[0] >= 1 and hole[1] <= 14:
                holes.append([hole, hole[1]])
            hole = [loop_cards[i]+1, loop_cards[i]+2]
            if hole[1] <= 14:
                holes.append([hole, hole[1]])
    return holes


class cards_functions():
    def __init__(self):
        self.hash_5num = hashcards(hand_size=5, deck_size=13)
        self.hash_2dim = hashcards(hand_size=2, deck_size=12)
        self.hash_2num = hashcards(hand_size=2, deck_size=13)
        self.hash_3dim = hashcards(hand_size=3, deck_size=12)
        self.hash_7all = hashcards(hand_size=7, deck_size=52)
        self.hash_5all = hashcards(hand_size=5, deck_size=52)
        self.hole_idx = {}
        for i, (c1, c2) in enumerate(combinations(range(52), 2)):
            self.hole_idx[(c1, c2)] = i
            self.hole_idx[(c2, c1)] = i

        self.c_single = [[] for _ in range(52)]
        self.c_single_n = [[] for _ in range(13)]
        for idx, (c1, c2) in enumerate(combinations(range(52), 2)):
            self.c_single[c1].append(idx)
            self.c_single[c2].append(idx)
            self.c_single_n[c1 % 13].append(idx)
            self.c_single_n[c2 % 13].append(idx)
        self.c_double_n = [[] for _ in range(13*13)]
        for num1, num2 in product(range(13), repeat=2):
            idx = num1*13 + num2
            for s1, s2 in product(range(4), repeat=2):
                hole = (num1+(s1*13), num2+(s2*13))
                if num1 == num2:
                    if s1 < s2:
                        self.c_double_n[idx].append(self.hole_idx[hole])
                else:
                    self.c_double_n[idx].append(self.hole_idx[hole])
        self.c_all = array('i', range(choose(52, 2)))
        self.c_single = [array('i', row) for row in self.c_single]
        self.c_single_n = [array('i', row) for row in self.c_single_n]
        self.c_double_n = [array('i', row) for row in self.c_double_n]
        self.all_p = ctypes.cast(self.c_all.buffer_info()[0],
                                 ctypes.POINTER(c_float))
        self.single_p = [ctypes.cast(row.buffer_info()[0],
                                     ctypes.POINTER(c_float))
                         for row in self.c_single]
        self.single_n_p = [ctypes.cast(row.buffer_info()[0],
                                       ctypes.POINTER(c_float))
                           for row in self.c_single_n]
        self.double_n_p = [ctypes.cast(row.buffer_info()[0],
                                       ctypes.POINTER(c_float))
                           for row in self.c_double_n]
        with open(resource_path('preflop.pkl'), 'rb') as f:
            self.preflop = pickle.load(f)

        self.c_holes_score = array('i', [-1]*choose(52, 2))
        self.holes_score_p = ctypes.cast(self.c_holes_score.buffer_info()[0],
                                         ctypes.POINTER(c_float))
        if os.name == 'nt':
            dll = ctypes.CDLL(resource_path('holes_operations.dll'))
            winftype = ctypes.WINFUNCTYPE(None)
            self.min_update = winftype(("min_update", dll))
            self.is_under = winftype(("is_under", dll))
            self.is_equal = winftype(("is_equal", dll))
        elif os.name == 'posix':
            holes_op = ctypes.cdll.LoadLibrary('holes_operations.so')
            self.min_update = holes_op.min_update
            self.is_under = holes_op.is_under
            self.is_equal = holes_op.is_equal
        else:
            raise NameError('Unknown OS')

        # Pointer to holes float array
        # Pointer to sub_index int array
        # int Score value to update
        # int Size of the sub_index
        self.min_update.argtypes = [ctypes.POINTER(c_float),
                                    ctypes.POINTER(c_float),
                                    c_int,
                                    c_int]
        self.min_update.restype = None

        # Pointer to holes float array
        # int Score value to compare against
        # int Size of the holes array
        self.is_under.argtypes = [ctypes.POINTER(c_float),
                                  c_int,
                                  c_int]
        # Number of elements under the value
        self.is_under.restype = c_int

        # Pointer to holes float array
        # int Score value to compare against
        # int Size of the holes array
        self.is_equal.argtypes = [ctypes.POINTER(c_float),
                                  c_int,
                                  c_int]
        # Number of elements under the value
        self.is_equal.restype = c_int

    def cards_to_idx(self, cards):
        hand_size = len(cards)
        if hand_size == 7:
            return self.hash_7all.idx(cards)
        elif hand_size == 5:
            return self.hash_5all.idx(cards)
        elif hand_size == 2:
            # c1, c2 = sorted(cards)
            # return int(c1*(51-(c1-1)/2-1)+c2-0.5)
            return self.hole_idx[tuple(cards)]
        else:
            raise NameError('Invalid hand_size')

    def scores_to_hand(self, score):
        if score == 0:
            return 'Royal flush', 14

        if score < 10:
            return 'Straight flush', 14-score
        score -= 10

        if score < 156:
            values = [14 - (score // 12), 14-(score % 12)]
            if values[1] <= values[0]:
                values[1] -= 1
            return 'Four of a kind', values
        score -= 156

        if score < 156:
            values = [14 - (score // 12), 14-(score % 12)]
            if values[1] <= values[0]:
                values[1] -= 1
            return 'Full house', values
        score -= 156

        if score < 1277:
            for cards in combinations(range(13), 5):
                if cards != (0, 9, 10, 11, 12):
                    s = self.hash_5num.idx(cards) - cards[0] - 2
                    if cards[0] == 0:
                        s += 1
                    if s == score:
                        return 'Flush', [14-c for c in cards]
            raise NameError('score bug')
        score -= 1277

        if score < 10:
            return 'Straight', 14-score
        score -= 10

        if score < 858:
            c1 = score//66
            for i, hv in enumerate(combinations(range(12), 2)):
                if i == score % 66:
                    values = [14-c1] + [14 - c - (c >= c1) for c in hv]
                    return 'Three of a kind', values
        score -= 858

        if score < 858:
            for i, hv in enumerate(combinations(range(13), 2)):
                if i == score//11:
                    values = [14 - c for c in hv] + [14 - (score % 11)]
                    values[2] -= values[2] <= values[0]
                    values[2] -= values[2] <= values[1]
                    return 'Two pairs', values
        score -= 858

        if score < 2860:
            for i, hv in enumerate(combinations(range(12), 3)):
                if i == score % 220:
                    values = ([14 - score//220] +
                              [14 - c - (c >= score//220) for c in hv])
                    return 'Pair', values
        score -= 2860

        if score < 1277:
            for cards in combinations(range(13), 5):
                if cards != (0, 9, 10, 11, 12):
                    s = self.hash_5num.idx(cards) - cards[0] - 2
                    if cards[0] == 0:
                        s += 1
                    if s == score:
                        return 'High card', [14-c for c in cards]
        raise NameError('invalid score')

    def cards_to_score(self, cards):
        score = 0

        # Royal & straight-flush
        loop_cards = [c+c//13 for c in cards]
        for c in [0, 14, 28, 42]:
            if c in loop_cards:
                loop_cards.append(c+13)
        loop_cards = sorted(loop_cards)
        diffs = [0 for _ in range(len(loop_cards)-4)]
        for i in range(1, len(loop_cards)):
            if loop_cards[i]-loop_cards[i-1] == 1:
                for k in range(len(loop_cards)-4):
                    if k+1 <= i <= k+4:
                        diffs[k] += 1
        wrong_idx = {10, 11, 12, 13,
                     24, 25, 26, 27,
                     38, 39, 40, 41}

        hand_values = [loop_cards[i] % 14 + 5 for i, d in enumerate(diffs)
                       if d == 4 and loop_cards[i] not in wrong_idx]
        if hand_values:
            hand_values = [max(hand_values)]
            score += 14 - hand_values[0]
            if score == 0:
                return score, 'Royal flush', hand_values
            else:
                return score, 'Straight flush', hand_values
        score += 10

        # Four of a kind
        hand = [[0]*13 for _ in range(4)]
        for card in cards:
            suit = card//13
            numb = card-suit*13
            hand[suit][numb] = 1
        num_groups = [sum(n) for n in zip(*hand)]
        num_groups = num_groups[1:] + num_groups[0:1]
        num_present = [i+2 for i, x in enumerate(num_groups) if x != 0][::-1]

        fours = [i+2 for i, x in enumerate(num_groups) if x == 4][::-1]
        if fours:
            if num_present[0] == fours[0]:
                high_card = num_present[1]
            else:
                high_card = num_present[0]
            hand_values = [fours[0], high_card]
            score += 12*(14-hand_values[0]) + (14-hand_values[1])
            if hand_values[0] > hand_values[1]:
                score -= 1
            return score, 'Four of a kind', hand_values
        score += 156

        # Full house
        trios = [i+2 for i, x in enumerate(num_groups) if x == 3][::-1]
        pairs = [i+2 for i, x in enumerate(num_groups) if x == 2][::-1]
        if len(trios) and len(trios)+len(pairs) >= 2:
            if len(trios) >= 2:
                hand_values = [trios[0], trios[1]]
            else:
                hand_values = [trios[0], pairs[0]]
            score += 12*(14-hand_values[0]) + (14-hand_values[1])
            if hand_values[1] < hand_values[0]:
                score -= 1
            return score, 'Full house', hand_values
        score += 156

        # Flush
        suit_groups = [sum(s) for s in hand]
        flush = [i for i, x in enumerate(suit_groups) if x >= 5]
        if flush:
            hand_values = hand[flush[0]]
            hand_values = hand_values[1:] + hand_values[0:1]
            hand_values = [i for i, x in enumerate(hand_values)
                           if x != 0][::-1][:5]
            score += (self.hash_5num.idx([12-x for x in hand_values]) +
                      hand_values[0] - 14)
            if hand_values[0] == 12:
                score += 1
            hand_values = [x+2 for x in hand_values]
            return score, 'Flush', hand_values
        score += 1277

        # Straight
        loop_cards = [x-1 for x in num_present[::-1]]
        if 13 in loop_cards:
            loop_cards = [0] + loop_cards
        diffs = [0 for _ in range(len(loop_cards)-4)]
        for i in range(1, len(loop_cards)):
            if loop_cards[i]-loop_cards[i-1] == 1:
                for k in range(len(loop_cards)-4):
                    if k+1 <= i <= k+4:
                        diffs[k] += 1
        hand_values = [loop_cards[i] + 5 for i, d in enumerate(diffs)
                       if d == 4 and loop_cards[i] not in wrong_idx]
        if hand_values:
            hand_values = [max(hand_values)]
            score += 14 - hand_values[0]
            return score, 'Straight', hand_values
        score += 10

        # Threes
        if trios:
            hand_values = [c for c in num_present
                           if c not in trios]
            hand_values = [trios[0]]+hand_values[:2]
            hv = [14-v-(v < hand_values[0]) for v in hand_values[1:]]
            score += 66*(14-hand_values[0]) + self.hash_2dim.idx(hv)
            return score, 'Three of a kind', hand_values
        score += 858

        # Two pairs
        if len(pairs) >= 2:
            hand_values = [c for c in num_present
                           if c not in pairs[:2]]
            hand_values = [pairs[0], pairs[1], hand_values[0]]
            hv = [14-v for v in hand_values[:2]]
            score += 11*self.hash_2num.idx(hv) + 14-hand_values[2]
            score -= (hand_values[2] < hand_values[0])
            score -= (hand_values[2] < hand_values[1])
            return score, 'Two pairs', hand_values
        score += 858

        # Pairs
        if pairs:
            hand_values = [c for c in num_present
                           if c != pairs[0]]
            hand_values = [pairs[0]]+hand_values[:3]
            hv = [14-v-(v < hand_values[0]) for v in hand_values[1:]]
            score += 220*(14-hand_values[0]) + self.hash_3dim.idx(hv)
            return score, 'Pair', hand_values
        score += 2860

        # High card
        hand_values = [x-2 for x in num_present[:5]]
        score += (self.hash_5num.idx([12-x for x in hand_values]) +
                  hand_values[0] - 14)
        if hand_values[0] == 12:
            score += 1
        hand_values = [x+2 for x in hand_values]
        return score, 'High card', hand_values

    def update_holes_score(self,
                           hole,
                           score,
                           hole_type='hole'):
        if hole is None or hole_type == 'all':
            self.min_update(self.holes_score_p,
                            self.all_p,
                            score,
                            len(self.c_all))
            self.break_flag = True
        elif hole_type == 'hole':
            idx = self.cards_to_idx(hole)
            if self.c_holes_score[idx] > score:
                self.c_holes_score[idx] = score
        elif hole_type == 'card':
            self.min_update(self.holes_score_p,
                            self.single_p[hole],
                            score,
                            len(self.c_single[hole]))
        elif hole_type == 'num':
            num = ((hole - 1) % 13)
            self.min_update(self.holes_score_p,
                            self.single_n_p[num],
                            score,
                            len(self.c_single_n[num]))
        elif hole_type == 'numnum':
            nums = sorted(hole)
            idx = ((nums[0] - 1) % 13)*13 + ((nums[1] - 1) % 13)
            self.min_update(self.holes_score_p,
                            self.double_n_p[idx],
                            score,
                            len(self.c_double_n[idx]))
        else:
            raise NameError('Unknown hole_type')

    def table_holes(self,
                    cards):
        if len(cards) != 5:
            raise NameError('Should be table (n=5) cards')
        hand_score = 0
        self.c_holes_score = array('i', [7462]*choose(52, 2))
        self.holes_score_p = ctypes.cast(self.c_holes_score.buffer_info()[0],
                                         ctypes.POINTER(c_float))
        self.break_flag = False

        # Royal & straight-flush
        for s in range(4):
            sub_cards = [c % 13 for c in cards if c//13 == s]
            for miss_cards, high_card in detect_straight(sub_cards):
                score = hand_score + 14 - high_card
                if miss_cards is None:
                    self.update_holes_score(None, score, 'all')
                elif isinstance(miss_cards, int):
                    hole = (miss_cards - 1) % 13 + s*13
                    self.update_holes_score(hole, score, 'card')
                else:
                    hole = [(c - 1) % 13 + s*13 for c in miss_cards]
                    self.update_holes_score(hole, score, 'hole')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 10

        # Four of a kind
        numbs = [((c-1) % 13) + 2 for c in cards]
        numbs_count = {}
        for n in numbs:
            if n in numbs_count:
                numbs_count[n] += 1
            else:
                numbs_count[n] = 1
        suits = [c//13 for c in cards]
        suits_count = {}
        for s in suits:
            if s in suits_count:
                suits_count[s] += 1
            else:
                suits_count[s] = 1

        for num in [k for k, v in numbs_count.items() if v >= 2]:
            high_card = max([n for n in numbs_count if n != num])
            score = (hand_score + 12*(14-num) +
                     (14-high_card) - 1*(num > high_card))
            suits_present = [suits[i] for i, n in enumerate(numbs)
                             if n == num]
            if len(suits_present) == 4:
                self.update_holes_score(None, score, 'all')
                for new_high_card in range(high_card+1, 15):
                    if new_high_card != num:
                        score = (hand_score + 12*(14-num) +
                                 (14-new_high_card) - 1*(num > new_high_card))
                        self.update_holes_score(new_high_card,
                                                score,
                                                'num')
            elif len(suits_present) == 3:
                miss_suits = [s for s in range(4) if s not in suits_present]
                miss_card = (num-1) % 13 + miss_suits[0]*13
                self.update_holes_score(miss_card, score, 'card')
                for new_high_card in range(high_card+1, 15):
                    if new_high_card != num:
                        score = (hand_score + 12*(14-num) +
                                 (14-new_high_card) - 1*(num > new_high_card))
                        for s in range(4):
                            hole = (miss_card, (new_high_card-1) % 13 + s*13)
                            self.update_holes_score(hole, score, 'hole')
            else:
                miss_suits = [s for s in range(4) if s not in suits_present]
                hole = ((num-1) % 13 + miss_suits[0]*13,
                        (num-1) % 13 + miss_suits[1]*13)
                self.update_holes_score(hole, score, 'hole')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 156

        # Full house
        trios = [k for k, v in numbs_count.items() if v == 3]
        pairs = [k for k, v in numbs_count.items() if v == 2]
        ones = [k for k, v in numbs_count.items() if v == 1]

        if len(trios) == 1:
            high_card_1 = trios[0]
            if len(pairs) == 1:
                high_card_2 = pairs[0]
                score = (hand_score + 12*(14-high_card_1) +
                         (14-high_card_2) - 1*(high_card_2 < high_card_1))
                self.update_holes_score(None, score, 'all')
                if high_card_2 > high_card_1:
                    score = (hand_score + 12*(14-high_card_2) +
                             (14-high_card_1) - 1*(high_card_1 < high_card_2))
                    self.update_holes_score(high_card_2, score, 'num')
                for new_high_card_2 in range(high_card_2 + 1, 15):
                    if new_high_card_2 != high_card_1:
                        score = (hand_score + 12*(14-high_card_1) +
                                 (14-new_high_card_2) -
                                 1*(new_high_card_2 < high_card_1))
                        self.update_holes_score([new_high_card_2,
                                                 new_high_card_2],
                                                score,
                                                'numnum')
            else:
                for high_card_2 in ones:
                    score = (hand_score + 12*(14-high_card_1) +
                             (14-high_card_2) - 1*(high_card_1 > high_card_2))
                    self.update_holes_score(high_card_2, score, 'num')
                for new_high_card_2 in range(2, 15):
                    if (new_high_card_2 != high_card_1 and
                            new_high_card_2 not in ones):
                        score = (hand_score + 12*(14-high_card_1) +
                                 (14-new_high_card_2) -
                                 1*(new_high_card_2 < high_card_1))
                        self.update_holes_score([new_high_card_2,
                                                 new_high_card_2],
                                                score,
                                                'numnum')
                    if (new_high_card_2 in ones and
                            new_high_card_2 > high_card_1):
                        score = (hand_score + 12*(14-new_high_card_2) +
                                 (14-high_card_1) -
                                 1*(high_card_1 < new_high_card_2))
                        self.update_holes_score([new_high_card_2,
                                                 new_high_card_2],
                                                score,
                                                'numnum')
        elif len(pairs) == 2:
            for i, high_card_1 in enumerate(pairs):
                high_card_2 = pairs[1-i]
                score = (hand_score + 12*(14-high_card_1) +
                         (14-high_card_2) - 1*(high_card_1 > high_card_2))
                self.update_holes_score(high_card_1, score, 'num')
                if ones[0] > high_card_2:
                    new_high_card_2 = ones[0]
                    score = (hand_score + 12*(14-high_card_1) +
                             (14-new_high_card_2) -
                             1*(new_high_card_2 < high_card_1))
                    self.update_holes_score([high_card_1, new_high_card_2],
                                            score,
                                            'numnum')
            high_card_1 = ones[0]
            high_card_2 = max(pairs)
            score = (hand_score + 12*(14-high_card_1) +
                     (14-high_card_2) - 1*(high_card_1 > high_card_2))
            self.update_holes_score([high_card_1, high_card_1],
                                    score,
                                    'numnum')
        elif len(pairs) == 1:
            high_card_1 = pairs[0]
            for high_card_2 in ones:
                score = (hand_score + 12*(14-high_card_1) +
                         (14-high_card_2) - 1*(high_card_2 < high_card_1))
                self.update_holes_score([high_card_1, high_card_2],
                                        score,
                                        'numnum')
                score = (hand_score + 12*(14-high_card_2) +
                         (14-high_card_1) - 1*(high_card_1 < high_card_2))
                self.update_holes_score([high_card_2, high_card_2],
                                        score,
                                        'numnum')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 156

        # Flush
        possible_flush = [k for k, v in suits_count.items() if v >= 3]
        for suit in possible_flush:
            numbs_present = [numbs[i] for i, s in enumerate(suits)
                             if s == suit]
            if len(numbs_present) == 5:
                high_cards = sorted(numbs_present, key=lambda x: -x)
                high_cards_idx = [14-c for c in high_cards]
                score = (hand_score + self.hash_5num.idx(high_cards_idx) +
                         high_cards[0] - 16 + 1*(high_cards[0] == 14))
                self.update_holes_score(None, score, 'all')
                for new_1 in range(high_cards[4]+1, 15):
                    if new_1 not in high_cards:
                        new_card_1 = (new_1-1) % 13 + suit*13
                        new_high_cards_idx = sorted(
                            high_cards_idx + [14 - new_1]
                            )[:5]
                        h0 = max(high_cards[0], new_1)
                        score = (hand_score +
                                 self.hash_5num.idx(new_high_cards_idx) +
                                 h0 - 16 + 1*(h0 == 14))
                        self.update_holes_score(new_card_1, score, 'card')
                        for new_2 in range(new_1+1, 15):
                            if new_2 not in high_cards:
                                new_card_2 = (new_2-1) % 13 + suit*13
                                hole = (new_card_1, new_card_2)
                                new_high_cards_idx = sorted(
                                    high_cards_idx + [14 - new_1, 14 - new_2]
                                    )[:5]
                                h0 = max(high_cards[0], new_1, new_2)
                                score = (
                                    hand_score +
                                    self.hash_5num.idx(new_high_cards_idx) +
                                    h0 - 16 + 1*(h0 == 14))
                                self.update_holes_score(hole,
                                                        score,
                                                        'hole')
            elif len(numbs_present) == 4:
                for new_1 in range(2, 15):
                    if new_1 not in numbs_present:
                        new_card_1 = (new_1-1) % 13 + suit*13
                        high_cards = sorted(numbs_present+[new_1],
                                            key=lambda x: -x)
                        high_cards_idx = [14-c for c in high_cards]
                        score = (hand_score +
                                 self.hash_5num.idx(high_cards_idx) +
                                 high_cards[0] - 16 + 1*(high_cards[0] == 14))
                        self.update_holes_score(new_card_1, score, 'card')
                        for new_2 in range(new_1+1, 15):
                            if new_2 not in numbs_present:
                                new_card_2 = (new_2-1) % 13 + suit*13
                                hole = (new_card_1, new_card_2)
                                new_high_cards_idx = sorted(
                                    high_cards_idx + [14 - new_2]
                                    )[:5]
                                h0 = max(high_cards[0], new_2)
                                score = (
                                    hand_score +
                                    self.hash_5num.idx(new_high_cards_idx) +
                                    h0 - 16 + 1*(h0 == 14))
                                self.update_holes_score(hole,
                                                        score,
                                                        'hole')
            elif len(numbs_present) == 3:
                for new_1 in range(2, 15):
                    new_card_1 = (new_1-1) % 13 + suit*13
                    for new_2 in range(new_1+1, 15):
                        if (new_1 not in numbs_present and
                                new_2 not in numbs_present):
                            new_card_2 = (new_2-1) % 13 + suit*13
                            hole = (new_card_1, new_card_2)
                            high_cards = sorted(numbs_present+[new_1, new_2],
                                                key=lambda x: -x)
                            high_cards_idx = [14-c for c in high_cards]
                            score = (hand_score +
                                     self.hash_5num.idx(high_cards_idx) +
                                     high_cards[0] - 16 +
                                     1*(high_cards[0] == 14))
                            self.update_holes_score(hole, score, 'hole')
        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 1277

        # Straight
        sub_cards = list(set([c % 13 for c in cards]))
        for miss_cards, high_card in detect_straight(sub_cards):
            score = hand_score + 14 - high_card
            if miss_cards is None:
                self.update_holes_score(None, score, 'all')
            elif isinstance(miss_cards, int):
                for s in range(4):
                    hole = (miss_cards - 1) % 13 + s*13
                    self.update_holes_score(hole, score, 'card')
            else:
                self.update_holes_score([miss_cards[0], miss_cards[1]],
                                        score,
                                        'numnum')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 10

        # Three of a kind
        if len(trios) == 1:
            high_card_1 = trios[0]
            high_cards = sorted(ones, key=lambda x: -x)
            high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
            score = (hand_score + 66*(14-high_card_1) +
                     self.hash_2dim.idx(high_cards_idx))
            self.update_holes_score(None, score, 'all')
            for new_1 in [c1 for c1 in range(high_cards[1]+1, 15)
                          if c1 not in numbs_count]:
                new_high_cards_idx = sorted(
                    high_cards_idx + [14-new_1-(new_1 < high_card_1)]
                    )[:2]
                score = (hand_score + 66*(14-high_card_1) +
                         self.hash_2dim.idx(new_high_cards_idx))
                self.update_holes_score(new_1, score, 'num')
                for new_2 in [c2 for c2 in range(new_1+1, 15)
                              if c2 not in numbs_count]:
                    new_high_cards_idx = sorted(
                        high_cards_idx + [14-new_1-(new_1 < high_card_1),
                                          14-new_2-(new_2 < high_card_1)]
                        )[:2]
                    score = (hand_score + 66*(14-high_card_1) +
                             self.hash_2dim.idx(new_high_cards_idx))
                    self.update_holes_score([new_1, new_2], score, 'numnum')
        elif len(pairs) == 1:
            high_card_1 = pairs[0]
            high_cards = sorted(ones, key=lambda x: -x)[:2]
            high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
            score = (hand_score + 66*(14-high_card_1) +
                     self.hash_2dim.idx(high_cards_idx))
            self.update_holes_score(high_card_1, score, 'num')
            for new_1 in [c1 for c1 in range(high_cards[1]+1, 15)
                          if c1 not in numbs_count]:
                new_high_cards_idx = sorted(
                    high_cards_idx + [14-new_1-(new_1 < high_card_1)]
                    )[:2]
                score = (hand_score + 66*(14-high_card_1) +
                         self.hash_2dim.idx(new_high_cards_idx))
                self.update_holes_score([high_card_1, new_1], score, 'numnum')
        else:
            for high_card_1 in ones:
                high_cards = sorted([c for c in ones if c != high_card_1],
                                    key=lambda x: -x)[:2]
                high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
                score = (hand_score + 66*(14-high_card_1) +
                         self.hash_2dim.idx(high_cards_idx))
                self.update_holes_score([high_card_1, high_card_1],
                                        score,
                                        'numnum')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 858

        # Two pairs
        if len(pairs) == 2:
            high_cards = sorted(pairs, key=lambda x: -x)
            high_cards_idx = [14-v for v in high_cards]
            high_card_3 = ones[0]
            score = (hand_score +
                     11*self.hash_2num.idx(high_cards_idx) +
                     14-high_card_3 -
                     1*(high_card_3 < high_cards[0]) -
                     1*(high_card_3 < high_cards[1]))
            self.update_holes_score(None, score, 'all')
            for new_1 in [c1 for c1 in range(high_card_3+1, 15)
                          if c1 not in numbs_count]:
                score = (hand_score +
                         11*self.hash_2num.idx(high_cards_idx) +
                         14-new_1 -
                         1*(new_1 < high_cards[0]) -
                         1*(new_1 < high_cards[1]))
                self.update_holes_score(new_1, score, 'num')
            if ones[0] > high_cards[1]:
                new_high_cards = sorted([high_cards[0], ones[0]],
                                        key=lambda x: -x)
                new_high_cards_idx = [14-v for v in new_high_cards]
                new_high_card_3 = high_cards[1]
                score = (hand_score +
                         11*self.hash_2num.idx(new_high_cards_idx) +
                         14-new_high_card_3 -
                         1*(new_high_card_3 < new_high_cards[0]) -
                         1*(new_high_card_3 < new_high_cards[1]))
                self.update_holes_score(ones[0], score, 'num')
                for new_1 in [c1 for c1 in range(new_high_card_3+1, 15)
                              if c1 not in numbs_count]:
                    score = (hand_score +
                             11*self.hash_2num.idx(new_high_cards_idx) +
                             14-new_1 -
                             1*(new_1 < new_high_cards[0]) -
                             1*(new_1 < new_high_cards[1]))
                    self.update_holes_score([new_1, ones[0]], score, 'numnum')
            for new_1 in [c2 for c2 in range(high_cards[1]+1, 15)
                          if c2 not in numbs_count]:
                new_high_cards = sorted([high_cards[0], new_1],
                                        key=lambda x: -x)
                new_high_cards_idx = [14-v for v in new_high_cards]
                new_high_card_3 = max(ones[0], high_cards[1])
                score = (hand_score +
                         11*self.hash_2num.idx(new_high_cards_idx) +
                         14-new_high_card_3 -
                         1*(new_high_card_3 < new_high_cards[0]) -
                         1*(new_high_card_3 < new_high_cards[1]))
                self.update_holes_score([new_1, new_1], score, 'numnum')

        elif len(pairs) == 1:
            high_card_1 = pairs[0]
            for high_card_2 in ones:
                for new_1 in [c1 for c1 in ones
                              if (c1 != high_card_2 and c1 > high_card_1)]:
                    high_cards = sorted([new_1, high_card_2],
                                        key=lambda x: -x)
                    high_card_3 = max([c for c in ones if c not in high_cards])
                    high_cards_idx = [14-v for v in high_cards]
                    score = (hand_score +
                             11*self.hash_2num.idx(high_cards_idx) +
                             14-high_card_3 -
                             1*(high_card_3 < high_cards[0]) -
                             1*(high_card_3 < high_cards[1]))
                    self.update_holes_score([new_1, high_card_2],
                                            score,
                                            'numnum')
                high_cards = sorted([high_card_1, high_card_2],
                                    key=lambda x: -x)
                high_card_3 = max([c for c in ones if c != high_card_2])
                high_cards_idx = [14-v for v in high_cards]
                score = (hand_score +
                         11*self.hash_2num.idx(high_cards_idx) +
                         14-high_card_3 -
                         1*(high_card_3 < high_cards[0]) -
                         1*(high_card_3 < high_cards[1]))
                self.update_holes_score(high_card_2, score, 'num')
                for new_1 in [c1 for c1 in range(high_card_3+1, 15)
                              if c1 not in numbs_count]:
                    score = (hand_score +
                             11*self.hash_2num.idx(high_cards_idx) +
                             14-new_1 -
                             1*(new_1 < high_cards[0]) -
                             1*(new_1 < high_cards[1]))
                    self.update_holes_score([high_card_2, new_1],
                                            score,
                                            'numnum')
            for high_card_2 in [c for c in range(2, 15)
                                if c not in numbs_count]:
                high_cards = sorted([high_card_1, high_card_2],
                                    key=lambda x: -x)
                high_card_3 = max(ones)
                high_cards_idx = [14-v for v in high_cards]
                score = (hand_score +
                         11*self.hash_2num.idx(high_cards_idx) +
                         14-high_card_3 -
                         1*(high_card_3 < high_cards[0]) -
                         1*(high_card_3 < high_cards[1]))
                self.update_holes_score([high_card_2, high_card_2],
                                        score,
                                        'numnum')
        else:
            for i, high_card_1 in enumerate(ones):
                for high_card_2 in ones[i+1:]:
                    high_cards = sorted([high_card_1, high_card_2],
                                        key=lambda x: -x)
                    high_cards_idx = [14-v for v in high_cards]
                    high_card_3 = max([c for c in ones if c not in high_cards])
                    score = (hand_score +
                             11*self.hash_2num.idx(high_cards_idx) +
                             14-high_card_3 -
                             1*(high_card_3 < high_cards[0]) -
                             1*(high_card_3 < high_cards[1]))
                    self.update_holes_score([high_card_1, high_card_2],
                                            score,
                                            'numnum')
        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 858

        # Pair
        if len(pairs) == 1:
            high_card_1 = pairs[0]
            high_cards = sorted(ones, key=lambda x: -x)
            high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
            score = (hand_score + 220*(14-high_card_1) +
                     self.hash_3dim.idx(high_cards_idx))
            self.update_holes_score(None, score, 'all')
            for new_1 in [c for c in range(high_cards[2]+1, 15)
                          if c not in numbs_count]:
                new_high_cards_idx = sorted(
                    high_cards_idx + [14-new_1-(new_1 < high_card_1)]
                    )[:3]
                score = (hand_score + 220*(14-high_card_1) +
                         self.hash_3dim.idx(new_high_cards_idx))
                self.update_holes_score(new_1, score, 'num')
                for new_2 in [c for c in range(new_1+1, 15)
                              if c not in numbs_count]:
                    new_high_cards_idx = sorted(
                        high_cards_idx + [14-new_1-(new_1 < high_card_1),
                                          14-new_2-(new_2 < high_card_1)]
                        )[:3]
                    score = (hand_score + 220*(14-high_card_1) +
                             self.hash_3dim.idx(new_high_cards_idx))
                    self.update_holes_score([new_1, new_2], score, 'numnum')
        else:
            for high_card_1 in ones:
                high_cards = sorted([c for c in ones if c != high_card_1],
                                    key=lambda x: -x)[:3]
                high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
                score = (hand_score + 220*(14-high_card_1) +
                         self.hash_3dim.idx(high_cards_idx))
                self.update_holes_score(high_card_1, score, 'num')
                for new_1 in [c for c in range(high_cards[2]+1, 15)
                              if (c not in high_cards and c != high_card_1)]:
                    new_high_cards_idx = sorted(
                        high_cards_idx + [14-new_1-(new_1 < high_card_1)]
                        )[:3]
                    score = (hand_score + 220*(14-high_card_1) +
                             self.hash_3dim.idx(new_high_cards_idx))
                    self.update_holes_score([high_card_1, new_1],
                                            score,
                                            'numnum')
            for high_card_1 in [c for c in range(2, 15) if c not in ones]:
                high_cards = sorted(ones, key=lambda x: -x)[:3]
                high_cards_idx = [14-v-(v < high_card_1) for v in high_cards]
                score = (hand_score + 220*(14-high_card_1) +
                         self.hash_3dim.idx(high_cards_idx))
                self.update_holes_score([high_card_1, high_card_1],
                                        score,
                                        'numnum')

        if self.break_flag:
            for c in cards:
                self.update_holes_score(c, -1, 'card')
            return self.c_holes_score
        hand_score += 2860

        # High card
        high_cards = sorted(ones, key=lambda x: -x)
        high_cards_idx = [14-v for v in high_cards]
        score = (hand_score + self.hash_5num.idx(high_cards_idx) +
                 high_cards[0] - 16 + 1*(high_cards[0] == 14))
        self.update_holes_score(None, score, 'all')
        for new_1 in [c for c in range(high_cards[4]+1, 15)
                      if c not in high_cards]:
            new_high_cards_idx = sorted(high_cards_idx + [14 - new_1])[:5]
            h0 = max(high_cards[0], new_1)
            score = (hand_score +
                     self.hash_5num.idx(new_high_cards_idx) +
                     h0 - 16 + 1*(h0 == 14))
            self.update_holes_score(new_1, score, 'num')
            for new_2 in [c for c in range(new_1+1, 15)
                          if c not in high_cards]:
                new_high_cards_idx = sorted(
                    high_cards_idx + [14 - new_1, 14 - new_2]
                    )[:5]
                h0 = max(high_cards[0], new_1, new_2)
                score = (hand_score +
                         self.hash_5num.idx(new_high_cards_idx) +
                         h0 - 16 + 1*(h0 == 14))
                self.update_holes_score([new_1, new_2], score, 'numnum')

        for c in cards:
            self.update_holes_score(c, -1, 'card')
        return self.c_holes_score


def gamblers_ruin(bet, pr, b1, b2, tol=0):
    return (pr**(b2/bet)-1)/(pr**((b1+b2)/bet)-1) - tol


class Card():
    def __init__(self,
                 card_idx):
        self.card_idx = card_idx
        self.value_int = card_idx % 13 + 1
        self.suit_int = card_idx//13 + 1
        value_special = {1: 'A',
                         11: 'J',
                         12: 'Q',
                         13: 'K'}
        if self.value_int in value_special:
            self.value = value_special[self.value_int]
        else:
            self.value = str(self.value_int)
        suit_symbols = {1: '\u2660',
                        2: '\u2661',
                        3: '\u2662',
                        4: '\u2663'}
        self.suit_symbol = suit_symbols[self.suit_int]
        suit_letter = {1: 'S',
                       2: 'H',
                       3: 'D',
                       4: 'C'}
        self.suit = suit_letter[self.suit_int]
        self.code = self.value+self.suit
        suit_path = {1: 'spade',
                     2: 'heart',
                     3: 'diamond',
                     4: 'club'}
        self.path = resource_path(
            f"assets/Playing_card_{suit_path[self.suit_int]}"
            f"_{self.value}.svg.png"
            )

    def __repr__(self):
        return self.value+self.suit_symbol


class Table():
    def __init__(self,
                 n_players=2,
                 dealer_hand_size=5,
                 initial_pot=2000,
                 debug=False,
                 screen=None):
        self.n_players = n_players
        self.dealer_hand_size = dealer_hand_size
        self.player_hands = [[] for _ in range(self.n_players)]
        self.player_banks = [initial_pot for _ in range(self.n_players)]
        self.player_bets = [0 for _ in range(self.n_players)]
        self.table_cards = []
        self.dealer_hand = []
        self.funcs = cards_functions()
        self.blinds = 20
        self.pidx_blind = 0
        self.pidx_current = 0
        self.player_tolerances = [0.001 for _ in range(self.n_players)]
        self.bet_quanta = 5
        self.player_states = ['wait' for _ in range(self.n_players)]
        self.message = None
        for _ in range(self.dealer_hand_size):
            self.draw_card()
        self.screen = screen
        self.state = 'deal'
        self.winners = []

        self.debug = debug
        self.player_probs_win = [0 for _ in range(self.n_players)]
        self.player_probs_lose = [0 for _ in range(self.n_players)]
        self.player_probs_fold = [0 for _ in range(self.n_players)]
        self.player_probs_call = [0 for _ in range(self.n_players)]
        self.player_ideal_bets = [0 for _ in range(self.n_players)]

    def __repr__(self):
        string = ' '*10+'HAND  MONEY   BET\n'
        for player_idx, player_hand in enumerate(self.player_hands):
            hand = ' '.join(str(card) for card in player_hand)
            bank = self.player_banks[player_idx]
            bet = self.player_bets[player_idx]
            string += f'PLAYER {player_idx+1}: {hand:6} {bank:4}  {bet:4}'
            if bet == bank:
                string += ' ALL-IN!'
            string += '\n'

        hand = ' '.join(str(card) for card in self.table_cards)
        string += f'\nBOARD: {hand}\n\n'
        hand = ' '.join(str(card) for card in self.dealer_hand)
        string += f'AVAILABLE CARDS: {hand}'
        return string

    def click_map(self,
                  pos):
        if self.dealer_hand_size > 5:
            x, y = pos
            if y < 480:
                return None
            dealer_cards = [c.card_idx for c in self.dealer_hand]
            for i in range(52):
                card_idx = 51-i
                x_start = 40 + (card_idx % 26)*25
                y_start = 540-60*(card_idx < 26)
                if (x_start <= x <= x_start+96 and
                        y_start <= y <= y_start+120 and
                        card_idx in dealer_cards):
                    return dealer_cards.index(card_idx)
            return None
        x, y = pos
        if y < 540:
            return None
        for i in range(self.dealer_hand_size):
            start = 402 - 50*self.dealer_hand_size + i*100
            if start <= x <= start+96:
                return i
        return None

    def blit(self):
        if self.screen is None:
            if self.message is not None:
                print()
                print(self.message)
                self.message = None
            print()
            print(str(self))
            if self.debug:
                print('p_win: ', self.player_probs_win)
                print('p_lose:', self.player_probs_lose)
                print('p_fold:', self.player_probs_fold)
                print('p_call:', self.player_probs_call)
                print('id_bet:', self.player_ideal_bets)
            return

        screen = self.screen
        screen.fill((85, 170, 85))
        try:
            frozen_flag = getattr(sys, "frozen")
        except AttributeError:
            frozen_flag = False
        if frozen_flag:
            font = pygame.font.Font(resource_path('freesansbold.ttf'), 32)
            font_debug = pygame.font.Font(resource_path('freesansbold.ttf'),
                                          10)
        else:
            font = pygame.font.Font(pygame.font.get_default_font(), 32)
            font_debug = pygame.font.Font(pygame.font.get_default_font(), 10)
        white = (255, 255, 255)
        gray = (50, 50, 50)
        red = (150, 0, 0)
        blue = (0, 0, 150)
        black = (0, 0, 0)

        text = font.render('Money', True, white)
        textRect = text.get_rect()
        textRect.center = (401, 41)
        screen.blit(text, textRect)
        text = font.render('Money', True, gray)
        textRect = text.get_rect()
        textRect.center = (400, 40)
        screen.blit(text, textRect)

        text = font.render('Bet', True, white)
        textRect = text.get_rect()
        textRect.center = (401, 141)
        screen.blit(text, textRect)
        text = font.render('Bet', True, gray)
        textRect = text.get_rect()
        textRect.center = (400, 140)
        screen.blit(text, textRect)

        # Dealer
        if self.dealer_hand_size > 5:
            dealer_cards = [c.card_idx for c in self.dealer_hand]
            for card_idx in range(52):
                if card_idx in dealer_cards:
                    card = Card(card_idx)
                    image = pygame.transform.scale(
                        pygame.image.load(card.path),
                        (96, 120)
                        )
                    screen.blit(image,
                                (40 + (card_idx % 26)*25,
                                 540-60*(card_idx < 26)))
        else:
            for i, card in enumerate(self.dealer_hand):
                image = pygame.transform.scale(
                    pygame.image.load(card.path),
                    (96, 120)
                    )
                screen.blit(image,
                            (402 - 50*self.dealer_hand_size + i*100, 540))
        # Table
        for i, card in enumerate(self.table_cards):
            image = pygame.transform.scale(
                pygame.image.load(card.path),
                (96, 120)
                )
            screen.blit(image,
                        (112 + i*120, 300))

        # Player 1
        text = font.render('Player 1', True, blue)
        textRect = text.get_rect()
        textRect.center = (110, 50)
        screen.blit(text, textRect)
        if self.pidx_blind == 0:
            text = font.render('*', True, blue)
            textRect = text.get_rect()
            textRect.center = (40, 50)
            screen.blit(text, textRect)
        if self.player_banks[0] == 0:
            text = font.render('(all-in)', True, blue)
            textRect = text.get_rect()
            textRect.center = (250, 50)
            screen.blit(text, textRect)

        text = font.render(f'{self.player_banks[0]} $', True, blue)
        textRect = text.get_rect()
        textRect.center = (325, 90)
        screen.blit(text, textRect)

        text = font.render(f'{self.player_bets[0]} $', True, blue)
        textRect = text.get_rect()
        textRect.center = (325, 190)
        screen.blit(text, textRect)

        for i, card in enumerate(self.player_hands[0]):
            image = pygame.transform.scale(
                pygame.image.load(card.path),
                (96, 120)
                )
            screen.blit(image,
                        (10 + i*100, 100))

        if self.debug:
            text = font_debug.render(
                f'p_win  = {self.player_probs_win[0]:.3f}',
                True,
                black)
            screen.blit(text, (20, 230))

            text = font_debug.render(
                f'p_lose = {self.player_probs_lose[0]:.3f}',
                True,
                black)
            screen.blit(text, (20, 240))

            text = font_debug.render(
                f'p_fold = {self.player_probs_fold[0]:.3f}',
                True,
                black)
            screen.blit(text, (20, 250))

            text = font_debug.render(
                f'p_call = {self.player_probs_call[0]:.3f}',
                True,
                black)
            screen.blit(text, (20, 260))

            text = font_debug.render(
                f'1/tol  = {1/self.player_tolerances[0]:.1f}',
                True,
                black)
            screen.blit(text, (20, 270))

            text = font_debug.render(
                f'id_bet = {self.player_ideal_bets[0]}',
                True,
                black)
            screen.blit(text, (20, 280))

        # Player 2
        text = font.render('Player 2', True, red)
        textRect = text.get_rect()
        textRect.center = (690, 50)
        screen.blit(text, textRect)
        if self.pidx_blind == 1:
            text = font.render('*', True, red)
            textRect = text.get_rect()
            textRect.center = (620, 50)
            screen.blit(text, textRect)
        if self.player_banks[1] == 0:
            text = font.render('(all-in)', True, red)
            textRect = text.get_rect()
            textRect.center = (550, 50)
            screen.blit(text, textRect)

        text = font.render(f'{self.player_banks[1]} $', True, red)
        textRect = text.get_rect()
        textRect.center = (475, 90)
        screen.blit(text, textRect)

        text = font.render(f'{self.player_bets[1]} $', True, red)
        textRect = text.get_rect()
        textRect.center = (475, 190)
        screen.blit(text, textRect)

        for i, card in enumerate(self.player_hands[1]):
            image = pygame.transform.scale(
                pygame.image.load(card.path),
                (96, 120)
                )
            screen.blit(image,
                        (590 + i*100, 100))

        if self.debug:
            text = font_debug.render(
                f'p_win  = {self.player_probs_win[1]:.3f}',
                True,
                black)
            screen.blit(text, (700, 230))

            text = font_debug.render(
                f'p_lose = {self.player_probs_lose[1]:.3f}',
                True,
                black)
            screen.blit(text, (700, 240))

            text = font_debug.render(
                f'p_fold = {self.player_probs_fold[1]:.3f}',
                True,
                black)
            screen.blit(text, (700, 250))

            text = font_debug.render(
                f'p_call = {self.player_probs_call[1]:.3f}',
                True,
                black)
            screen.blit(text, (700, 260))

            text = font_debug.render(
                f'1/tol  = {1/self.player_tolerances[1]:.1f}',
                True,
                black)
            screen.blit(text, (700, 270))

            text = font_debug.render(
                f'id_bet = {self.player_ideal_bets[1]}',
                True,
                black)
            screen.blit(text, (700, 280))

        # Message
        if self.message is not None:
            text = font.render(self.message, True, black, white)
            textRect = text.get_rect()
            textRect.center = (400, 250)
            screen.blit(text, textRect)

    def round_bet(self,
                  bet):
        return int(bet/self.bet_quanta+0.5)*self.bet_quanta

    def draw_card(self):
        out_cards = set([card.card_idx for hand in self.player_hands
                         for card in hand] +
                        [card.card_idx for card in self.table_cards] +
                        [card.card_idx for card in self.dealer_hand])
        remaining_cards = [card_idx for card_idx in range(52)
                           if card_idx not in out_cards]
        if remaining_cards:
            new_card = Card(choice(remaining_cards))
            self.dealer_hand.append(new_card)

    def give_card(self,
                  dealer_idx,
                  player_idx):
        card = self.dealer_hand.pop(dealer_idx)
        if player_idx == 0:
            self.table_cards.append(card)
        else:
            self.player_hands[player_idx-1].append(card)

    def call_bet(self,
                 player_idx):
        current_bet = min(
            max(self.player_bets),
            self.player_banks[player_idx] + self.player_bets[player_idx]
            )
        self.player_banks[player_idx] -= (current_bet -
                                          self.player_bets[player_idx])
        self.player_bets[player_idx] = current_bet
        self.player_states[player_idx] = 'call'
        if self.player_banks[player_idx] == 0:
            self.message = (f'Player {player_idx+1} '
                            f'goes all-in with {current_bet} $')
        else:
            self.message = f'Player {player_idx+1} calls to {current_bet} $'

    def raise_bet(self,
                  player_idx,
                  raised_bet):
        if raised_bet > self.player_bets[player_idx]:
            raised_bet = min(
                raised_bet,
                self.player_bets[player_idx]+self.player_banks[player_idx]
                )
            self.player_banks[player_idx] -= (raised_bet -
                                              self.player_bets[player_idx])
            self.player_bets[player_idx] = raised_bet
            self.player_states[player_idx] = 'raise'
            if self.player_banks[player_idx] == 0:
                self.message = (f'Player {player_idx+1} '
                                f'goes all-in with {raised_bet} $')
            else:
                self.message = (f'Player {player_idx+1} '
                                f'raises to {raised_bet} $')

    def fold_bet(self,
                 player_idx):
        self.player_states[player_idx] = 'fold'
        self.message = f'Player {player_idx+1} folds'

    def bets_step(self):
        player_idx = self.pidx_current
        current_bet = max(self.player_bets)
        ideal_bet = self.player_ideal_bets[player_idx]
        bet = self.player_bets[player_idx]
        factor = 6-len(self.table_cards)
        if factor == 6:
            factor = 4
        raised_bet = self.round_bet(ideal_bet/factor)

        if raised_bet > current_bet:
            self.raise_bet(player_idx, raised_bet)
        elif current_bet <= ideal_bet or current_bet == bet:
            self.call_bet(player_idx)
        elif ideal_bet == 1:
            self.fold_bet(player_idx)
        else:
            pr = (self.player_probs_win[player_idx] /
                  max(self.player_probs_lose[player_idx], 10**-5))
            b1 = (self.player_banks[player_idx] +
                  self.player_bets[player_idx])
            b2 = (sum(self.player_banks) +
                  sum(self.player_bets) - b1)

            prob_fold = gamblers_ruin(max(ideal_bet, bet), pr, b1-bet, b2+bet)
            self.player_probs_fold[player_idx] = prob_fold
            prob_call = gamblers_ruin(current_bet, pr, b1, b2)
            self.player_probs_call[player_idx] = prob_call
            if prob_fold < prob_call:
                self.fold_bet(player_idx)
            else:
                self.call_bet(player_idx)
        self.pidx_current = (player_idx + 1) % self.n_players
        while self.player_states[self.pidx_current] == 'fold':
            self.pidx_current = (player_idx + 1) % self.n_players

    def compute_bets(self):
        if len(self.table_cards) == 0:
            self.player_probs_lose = []
            self.player_probs_win = []
            for player_idx in range(self.n_players):
                player_hole = [c.card_idx
                               for c in self.player_hands[player_idx]]
                hole_idx = self.funcs.cards_to_idx(player_hole)
                self.player_probs_win.append(self.funcs.preflop[hole_idx][0])
                self.player_probs_lose.append(self.funcs.preflop[hole_idx][1])

            self.raise_bet(self.pidx_blind, self.blinds)
            self.raise_bet(((self.pidx_blind+1) % self.n_players),
                           self.blinds//2)
            self.message = None
            self.pidx_current = ((self.pidx_blind+2) % self.n_players)
            self.blit()

        else:
            cards = [c.card_idx for c in self.table_cards]
            self.player_probs_lose = [0 for _ in range(self.n_players)]
            self.player_probs_win = [0 for _ in range(self.n_players)]
            for remain_cards in combinations(range(52), 5 - len(cards)):
                valid_flag = all([c not in cards for c in remain_cards])
                if valid_flag:
                    holes = self.funcs.table_holes(cards + list(remain_cards))

                    for player_idx in range(self.n_players):
                        player_hole = [c.card_idx
                                       for c in self.player_hands[player_idx]]
                        if any([c in remain_cards for c in player_hole]):
                            continue
                        score = holes[self.funcs.cards_to_idx(player_hole)]
                        holes_temp = array('i', holes)
                        holes_temp_p = ctypes.cast(holes_temp.buffer_info()[0],
                                                   ctypes.POINTER(c_float))
                        for card_idx in player_hole:
                            for idx in self.funcs.c_single[card_idx]:
                                holes_temp[idx] = -1
                            self.funcs.min_update(
                                holes_temp_p,
                                self.funcs.single_p[card_idx],
                                -1,
                                len(self.funcs.c_single[card_idx]))
                        better_hands = self.funcs.is_under(
                            holes_temp_p,
                            score,
                            len(holes_temp)
                            ) - 336
                        tied_hands = self.funcs.is_equal(
                            holes_temp_p,
                            score,
                            len(holes_temp))
                        self.player_probs_lose[player_idx] += better_hands
                        self.player_probs_win[player_idx] += (990 -
                                                              better_hands -
                                                              tied_hands)

            self.player_probs_lose = [p/990/choose(50 - len(cards),
                                                   5 - len(cards))
                                      for p in self.player_probs_lose]
            self.player_probs_win = [p/990/choose(50 - len(cards),
                                                  5 - len(cards))
                                     for p in self.player_probs_win]
            self.pidx_current = self.pidx_blind

        # Solve for ideal bet with tolerance level with bisect algorithm
        # and Huygens's formula of gambler's ruin
        self.player_ideal_bets = []
        for player_idx in range(self.n_players):
            pr = (self.player_probs_win[player_idx] /
                  max(self.player_probs_lose[player_idx], 10**-5))
            b1 = (self.player_banks[player_idx] +
                  self.player_bets[player_idx])
            b2 = (sum(self.player_banks) + sum(self.player_bets) - b1)
            tol = self.player_tolerances[player_idx]
            lower_bound = -log(pr)*b1/log(tol)-1

            if lower_bound < 1:
                ideal_bet = 1
            elif lower_bound > b1 or gamblers_ruin(b1, pr, b1, b2, tol) < 0:
                ideal_bet = b1
            else:
                ideal_bet = bisect(gamblers_ruin,
                                   a=lower_bound,
                                   b=b1,
                                   args=(pr, b1, b2, tol),
                                   xtol=0.1)
                ideal_bet = self.round_bet(ideal_bet)
            self.player_ideal_bets.append(ideal_bet)
        self.player_probs_fold = [0 for _ in range(self.n_players)]
        self.player_probs_call = [0 for _ in range(self.n_players)]
        for i, s in enumerate(self.player_states):
            if s != 'fold':
                self.player_states[i] = 'wait'

    def ask_card(self):
        if len(self.player_hands[-1]) == 2:
            if len(self.table_cards) < 3:
                name = 'flop'
            elif len(self.table_cards) == 3:
                name = 'turn'
            elif len(self.table_cards) == 4:
                name = 'river'
            card_code = input(f'What card to give the {name}?\n')
        else:
            player_ncards = [len(hand) for hand in self.player_hands]
            for idx, ncard in enumerate(player_ncards):
                if ncard == min(player_ncards):
                    break
            idx += 1
            card_code = input(f'What card to give player {idx}?\n')
        card_code = card_code.upper()
        dealer_idx = [i for i, card in enumerate(self.dealer_hand)
                      if (str(card_code).upper() ==
                          card.code[:len(str(card_code))])]
        while len(dealer_idx) != 1:
            if len(dealer_idx) == 0:
                card_code = input('Invalid card code, try again\n')
                dealer_idx = [i for i, card in enumerate(self.dealer_hand)
                              if (str(card_code).upper() ==
                                  card.code[:len(str(card_code))])]
            elif len(dealer_idx) > 1:
                card_code = input('Multiple card found, '
                                  'try adding suit (S, H, D, C)\n')
                dealer_idx = [i for i, card in enumerate(self.dealer_hand)
                              if (str(card_code).upper() ==
                                  card.code[:len(str(card_code))])]
        return dealer_idx[0]

    def compute_winner(self):
        competing = [player_idx
                     for player_idx, s in enumerate(self.player_states)
                     if s != 'fold']
        if len(competing) == 1:
            self.winners = competing
            pot = sum(self.player_bets)//len(self.winners)
            self.message = f'Player {competing[0]+1} wins {pot}$!'
        else:
            scores = []
            hands = []
            for i in competing:
                cards = [c.card_idx
                         for c in (self.table_cards +
                                   self.player_hands[i])]
                score, hand_name, hand_value = \
                    self.funcs.cards_to_score(cards)
                scores.append(score)
                hands.append((hand_name, hand_value))
            self.winners = [player_idx
                            for i, player_idx in enumerate(competing)
                            if scores[i] == min(scores)]
            pot = sum(self.player_bets)//len(self.winners)
            if len(self.winners) == 1:
                self.message = f'Player {self.winners[0]+1} wins {pot}$ '
            else:
                winner_string = ' and '.join([f'{i+1}' for i in self.winners])
                self.message = f'Players {winner_string} win {pot}$ '
            if hands[self.winners[0]][0] == 'Two pairs':
                self.message += f'with {hands[self.winners[0]][0]}'
            else:
                self.message += f'with a {hands[self.winners[0]][0]}'

    def reset(self):
        pot = sum(self.player_bets)//len(self.winners)
        for player_idx in self.winners:
            self.player_banks[player_idx] += pot
        self.winners = [i for i, b in enumerate(self.player_banks)
                        if b == sum(self.player_banks)]
        self.pidx_blind = (self.pidx_blind + 1) % self.n_players
        self.player_hands = [[] for _ in range(self.n_players)]
        self.player_bets = [0 for _ in range(self.n_players)]
        self.table_cards = []
        self.dealer_hand = []
        self.player_states = ['wait' for _ in range(self.n_players)]
        for _ in range(self.dealer_hand_size):
            self.draw_card()
        self.state = 'deal'
        if self.winners:
            self.state = 'close'
        self.player_probs_win = [0 for _ in range(self.n_players)]
        self.player_probs_lose = [0 for _ in range(self.n_players)]
        self.player_probs_fold = [0 for _ in range(self.n_players)]
        self.player_probs_call = [0 for _ in range(self.n_players)]
        self.player_ideal_bets = [0 for _ in range(self.n_players)]

    def step(self,
             dealer_idx=None):
        if self.message is not None and self.state != 'comp_bet':
            self.message = None
            self.blit()
        elif self.state == 'deal' and dealer_idx is not None:
            if len(self.player_hands[-1]) == 2:
                player_idx = 0
            else:
                player_ncards = [len(hand) for hand in self.player_hands]
                for player_idx, ncard in enumerate(player_ncards):
                    if ncard == min(player_ncards):
                        break
                player_idx += 1
            self.give_card(dealer_idx, player_idx)
            self.draw_card()
            if (len(self.player_hands[-1]) == 2 and
                    len(self.table_cards) in {0, 3, 4, 5}):
                self.message = 'thinking...'
                self.state = 'comp_bet'
            self.blit()
        elif self.state == 'comp_bet':
            self.compute_bets()
            self.blit()
            self.message = None
            self.state = 'bet'
        elif self.state == 'bet':
            self.bets_step()
            n_folds = len([s for s in self.player_states if s == 'fold'])
            if n_folds >= self.n_players - 1:
                self.state = 'end'
            elif ('wait' not in self.player_states and
                  'raise' not in [s for i, s in enumerate(self.player_states)
                                  if i != self.pidx_current]):
                if len(self.table_cards) == 5:
                    self.state = 'end'
                else:
                    self.state = 'deal'
            self.blit()
        elif self.state == 'end':
            self.compute_winner()
            self.blit()
            self.reset()
        elif self.state == 'close':
            if self.winners[0] == 0:
                self.message = ('Player 1 wins! You cheated successfully!')
            if self.winners[0] == 1:
                self.message = ('Player 1 lost... you\'re a terrible friend.')
            self.winners = []
            self.blit()


def blit_text(screen, text, pos, font, color=(0, 0, 0)):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = screen.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 1, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            screen.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height


class start_screen():
    def __init__(self,
                 screen):
        self.screen = screen
        self.debug = 0
        self.debug_code = [100, 101, 98, 117, 103]
        self.blit()

    def blit(self):
        self.screen.fill((85, 170, 85))
        try:
            frozen_flag = getattr(sys, "frozen")
        except AttributeError:
            frozen_flag = False
        if frozen_flag:
            print(os.getcwd())
            font = pygame.font.Font(resource_path('freesansbold.ttf'), 32)
            font_debug = pygame.font.Font(resource_path('freesansbold.ttf'),
                                          10)
        else:
            font = pygame.font.Font(pygame.font.get_default_font(), 32)
            font_debug = pygame.font.Font(pygame.font.get_default_font(), 10)
        white = (255, 255, 255)
        black = (0, 0, 0)
        gray = (50, 50, 50)
        red = (150, 0, 0)
        blue = (0, 0, 150)
        green = (0, 150, 0)

        blit_text(self.screen,
                  ('Your friend Player 1 asked you to be the dealer at a '
                   'Texas Hold\'em poker game\n'
                   'Being a good friend with questionable morals, '
                   'you would like to make your friend Player 1 win.\n'
                   'You have the ability to peek the next few cards in '
                   'the deck and choose which ones to deal to the players '
                   ' and to the table\n'
                   'It\'s up to you to get your friend to win the big bucks!'),
                  (10, 10),
                  font)
        text = font_debug.render(
            ('Created by Nicolas Bérubé, original idea by Tom O\'Regan.'
             ' Prototype version.'),
            True,
            black)
        self.screen.blit(text, (10, 310))

        text = font.render('Choose a difficulty', True, white)
        textRect = text.get_rect()
        textRect.center = (401, 391)
        self.screen.blit(text, textRect)
        text = font.render('Choose a difficulty', True, gray)
        textRect = text.get_rect()
        textRect.center = (400, 390)
        self.screen.blit(text, textRect)
        pygame.display.flip()

        text_easy = font.render('Easy (all cards)', True, green, white)
        self.textRect_easy = text_easy.get_rect()
        self.textRect_easy.center = (400, 450)
        self.screen.blit(text_easy, self.textRect_easy)
        text_norm = font.render('Normal (5 cards)', True, blue, white)
        self.textRect_norm = text_norm.get_rect()
        self.textRect_norm.center = (400, 500)
        self.screen.blit(text_norm, self.textRect_norm)
        text_hard = font.render('Hard (2 cards)', True, red, white)
        self.textRect_hard = text_hard.get_rect()
        self.textRect_hard.center = (400, 550)
        self.screen.blit(text_hard, self.textRect_hard)

        if self.debug == len(self.debug_code):
            text = font_debug.render('debug', True, black)
            self.screen.blit(text, (10, 10))

    def click_map(self,
                  pos):
        if self.textRect_easy.collidepoint(pos):
            return 'easy'
        if self.textRect_norm.collidepoint(pos):
            return 'normal'
        if self.textRect_hard.collidepoint(pos):
            return 'hard'
        return None

    def detect_debug(self,
                     key):
        if self.debug < len(self.debug_code):
            if key == self.debug_code[self.debug]:
                self.debug += 1
            else:
                self.debug = 0
        if self.debug == len(self.debug_code):
            self.blit()


def game_ui(screen):

    start = start_screen(screen)
    pygame.display.flip()

    running = True
    debug = 0
    debug_code = [100, 101, 98, 117, 103]
    while running:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pos = pygame.mouse.get_pos()
            difficulty = start.click_map(pos)
            if difficulty is not None:
                if difficulty == 'easy':
                    dealer_hand_size = 52
                if difficulty == 'normal':
                    dealer_hand_size = 5
                if difficulty == 'hard':
                    dealer_hand_size = 2
                running = False

        elif event.type == pygame.KEYUP and debug != len(debug_code):
            start.detect_debug(event.key)
            pygame.display.flip()

    game = Table(debug=(start.debug == len(start.debug_code)),
                 screen=screen,
                 dealer_hand_size=dealer_hand_size)
    game.blit()
    pygame.display.flip()
    # print(game.state, game.message)

    # clock = pygame.time.Clock()
    while True:
        # clock.tick(20)
        if game.message is None and game.state != 'deal':
            pygame.time.wait(100)
            if game.state == 'close' and not game.winners:
                return True
            game.step()
            pygame.display.flip()
            pygame.event.clear()
            # print('B', game.state, game.message)
        elif game.state == 'comp_bet':
            pygame.time.wait(100)
            game.step()
            pygame.display.flip()
            pygame.event.clear()
            # print('C', game.state, game.message)
        else:
            # event handling, gets all event from the event queue
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if game.state == 'deal' and game.message is None:
                    pos = pygame.mouse.get_pos()
                    dealer_idx = game.click_map(pos)
                    # print(pos, dealer_idx)
                    if dealer_idx is not None:
                        game.step(dealer_idx)
                else:
                    game.step()
                pygame.display.flip()
                pygame.event.clear()
                # print('A', game.state, game.message)


if __name__ == "__main__":

    pygame.init()
    # load and set the logo
    # pygame.display.set_icon(image)
    pygame.display.set_caption("Stack The Deck")
    screen_width, screen_height = (800, 600)
    screen = pygame.display.set_mode((screen_width, screen_height))
    loop_flag = True
    while loop_flag:
        loop_flag = game_ui(screen)

"""
# CONSOLE-VIEW GAME
game = Table(debug=True)
game.blit()
while True:
    if game.state == 'deal':
        dealer_idx = game.ask_card()
    else:
        game.step()
"""
