# -*- coding: utf-8 -*-
# @Time    : 2023/1/15 上午9:27
# @Author  : Jiuxi
# @File    : mcts.py
# @Software: PyCharm 
# @Comment :
import math
import random
from dlgo import agent
from dlgo.gotypes import Player


class MCTSNode(object):
    """
    蒙特卡洛树节点
    """

    def __init__(self, game_state, parent=None, move=None):
        """
        game_state: GameState 搜索树当前节点游戏状态
        parent: MCTSNode 父节点
        move: Move 触发当前棋局的上一步动作
        children：list 子结点列表
        win_counts: 记录黑白的获胜次数
        num_rollouts: 推演的次数
        unvisited_moves：从当前棋局开始所有的合法动作列表
        """
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            Player.black: 0,
            Player.white: 0
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.legal_moves()

    def add_random_child(self):
        """
        添加新的子节点
        :return: MCTSNode
        """
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        """
        更新统计信息
        :param winner: Player
        :return: None
        """
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        """
        检查是否还有合法动作未添加
        :return: bool
        """
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        """
        判断是否是终盘
        :return: bool
        """
        return self.game_state.is_over()

    def winning_frac(self, player):
        """
        求某一方的胜率
        :param player: Player
        :return: float
        """
        return float(self.win_counts[player]) / float(self.num_rollouts)


class MCTSAgent(agent.Agent):
    """
    蒙特卡洛树搜索算法
    """

    def __init__(self, num_rounds, temperature):
        agent.Agent.__init__(self)
        self.num_rounds = num_rounds
        self.temperature = temperature

    def select_move(self, game_state):
        root = MCTSNode(game_state)

        for i in range(self.num_rounds):
            node = root
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            if node.can_add_child():
                node = node.add_random_child()

            winner = self.simulate_random_game(node.game_state)

            while node is not None:
                node.record_win(winner)
                node = node.parent

        best_move = None
        best_pct = -1.0

        for child in root.children:
            child_pct = child.winning_frac(game_state.next_player)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.move

        return best_move

    def select_child(self, node):
        """
        Select a child according to the upper confidence bound for trees (UCT) metric.
        """
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None
        # Loop over each child.
        for child in node.children:
            # Calculate the UCT score.
            win_percentage = child.winning_frac(node.game_state.next_player)
            exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
            uct_score = win_percentage + self.temperature * exploration_factor
            # Check if this is the largest we've seen so far.
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child

    @staticmethod
    def simulate_random_game(game):
        bots = {
            Player.black: agent.FastRandomBot(),
            Player.white: agent.FastRandomBot(),
        }
        while not game.is_over():
            bot_move = bots[game.next_player].select_move(game)
            game = game.apply_move(bot_move)
        return game.winner()
