# -*- coding: utf-8 -*-
# @Time    : 2023/1/7 下午3:59
# @Author  : Jiuxi
# @File    : gotypes.py
# @Software: PyCharm 
# @Comment :

import enum
from collections import namedtuple


class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


# row: 行  col: 列
class Point(namedtuple('Point', 'row col')):
    # 获取相邻的棋子的坐标
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        ]
