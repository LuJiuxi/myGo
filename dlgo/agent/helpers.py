# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 下午3:42
# @Author  : Jiuxi
# @File    : helpers.py
# @Software: PyCharm 
# @Comment :

from dlgo.gotypes import Point


def is_point_an_eye(board, point, color):
    # 眼必须是空位
    if board.get(point) is not None:
        return False
    for neighbor in point.neighbors():
        if board.is_on_grid(neighbor):
            neighbor_color = board.get(neighbor)
            if neighbor_color != color:
                return False

    # 己方棋子必须控制4个对角相邻点中的3个，如果在边上，必须控制所有对角相邻点
    friendly_corners = 0
    off_board_corners = 0
    corners = [
        Point(point.row - 1, point.col - 1),
        Point(point.row - 1, point.col + 1),
        Point(point.row + 1, point.col - 1),
        Point(point.row + 1, point.col + 1)
    ]
    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
            else:
                off_board_corners += 1

    if off_board_corners > 0:
        return off_board_corners + friendly_corners == 4  # 眼在边缘或角上
    else:
        return friendly_corners >= 3  # 眼在棋盘内
