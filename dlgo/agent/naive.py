# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 下午3:59
# @Author  : Jiuxi
# @File    : naive.py
# @Software: PyCharm 
# @Comment :


import random
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point


class RandomBot(Agent):
    """
    25级的围棋AI
    """

    def select_move(self, game_state):
        candidates = []  # 候选点
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(row=r, col=c)
                if game_state.is_valid_move(Move.play(candidate)) and \
                        not is_point_an_eye(game_state.board, candidate, game_state.next_player):
                    # 有效落子，且不在眼中落子
                    candidates.append(candidate)
        if not candidates:
            return Move.pass_turn()
        return Move.play(random.choice(candidates))