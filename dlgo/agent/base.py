# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 下午3:57
# @Author  : Jiuxi
# @File    : base.py
# @Software: PyCharm 
# @Comment :

class Agent:
    def __init__(self):
        pass

    def select_move(self, game_state):
        """
        AI的基础接口
        :param game_state: GameState
        :return: Move
        """
        raise NotImplementedError()


