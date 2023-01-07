# -*- coding: utf-8 -*-
# @Time    : 2023/1/7 下午4:03
# @Author  : Jiuxi
# @File    : goboard_slow.py
# @Software: PyCharm 
# @Comment :

import copy
from dlgo.gotypes import Player


class Move:
    def __int__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign  # 至少采取落子、跳过、认输的任意一个动作
        self.is_play = (point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)


# 棋链
class GoString:
    def __init__(self, color, stones, liberties):
        """
        :param color: 颜色
        :param stones: 棋子 Point List
        :param liberties: 气 Point List
        """

        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merge_with(self, go_string):
        """
        合并两条棋链，返回一条新的棋链
        当一次落子将两个棋子连起来时需要调用此方法
        """
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        combined_liberties = self.liberties | go_string.liberties - combined_stones
        return GoString(self.color, combined_stones, combined_liberties)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # 存储棋链的字典 key: Point value: GoString

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)
        # 合并颜色相同的相邻棋链
        for same_color_string in adjacent_same_color:
            new_string = new_string.merge_with(same_color_string)
        # 更新字典
        for new_stone_point in new_string.stones:
            self._grid[new_stone_point] = new_string
        # 减少对方相邻棋链的气
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_liberty(point)
        # 提走气尽的棋链
        for other_color_string in adjacent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        """
        返回交叉点的内容，如果已经落子返回Player，否则返回None
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _remove_string(self, string):
        # 一个一个的提走棋子
        for point in string:
            # 为相邻的棋链增加气数
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:  # 保证不是自己
                    neighbor_string.add_libertiy(point)
            self._grid[point] = None
