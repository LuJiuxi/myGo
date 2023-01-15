# -*- coding: utf-8 -*-
# @Time    : 2023/1/7 下午4:03
# @Author  : Jiuxi
# @File    : goboard.py
# @Software: PyCharm
# @Comment :

import copy
from dlgo.gotypes import Player, Point
from dlgo import zobrist


class Move:
    """
    动作：
    - 落子 play
    - 跳过 pass
    - 认输 resign
    """

    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign  # 至少采取落子、跳过、认输的任意一个动作
        self.point = point
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


class GoString:
    """
    棋链: 颜色相同且连续的棋子构成的集合
    """

    def __init__(self, color, stones, liberties):
        """
        :param color: 颜色
        :param stones: 棋子 Point List
        :param liberties: 气 Point List
        """

        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    # def remove_liberty(self, point):
    #     self.liberties.remove(point)

    def without_liberty(self, point):
        new_liberties = self.liberties - {point}
        return GoString(self.color, self.stones, new_liberties)

    # def add_liberty(self, point):
    #     self.liberties.add(point)

    def with_liberty(self, point):
        new_liberties = self.liberties | {point}
        return GoString(self.color, self.stones, new_liberties)

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
    """
    棋盘
    """

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # 存储棋链的字典 key: Point value: GoString
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, player, point):
        """
        处理落子的相关动作，包括
        - 创建合并棋链
        - 更新气数
        - 提子
        """
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

        # 更新棋盘的hash
        self._hash ^= zobrist.HASH_CODE[point, player]

        # 减少对方相邻棋链的气, 提走气尽的棋链
        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(replacement)
            else:
                self._remove_string(other_color_string)

    def is_on_grid(self, point):
        """
        判断Point是否在棋盘上
        """

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
        """
        获取Point所在棋链
        """

        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _replace_string(self, new_string):
        """
        更新棋盘网络
        :param new_string:
        :return: None
        """
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        """
        移除棋链即提子
        """
        # 一个一个的提走棋子
        for point in string.stones:
            # 为相邻的棋链增加气数
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:  # 保证不是自己
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None
            # 逆用hash来提子
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def zobrist_hash(self):
        """
        返回当前棋盘的hash
        :return: int
        """
        return self._hash


class GameState:
    """
    跟踪游戏状态，最终形成一个动作序列
    """

    def __init__(self, board, next_player, previous, move):
        """
        :param board: Board
        :param next_player: Player 下一位下棋的人
        :param previous: GameState 上一轮的游戏状态
        :param move: Move 上一步动作
        """

        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        # 添加新的成员previous_states来记录过去所有的状态
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())}
            )
        self.last_move = move

    def apply_move(self, move):
        """
        添加新的动作，返回新的状态
        :param move: Move
        :return GameState
        """

        if move.is_play:
            # 深拷贝，保存每一步的棋盘状态，这也是为什么叫goboard_slow的原因，但是实现比较简单
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        """
        创建新游戏
        :param board_size: int or tuple 棋盘大小
        :return GameState
        """

        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        """
        判断游戏结束
        :return: bool
        """

        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        # 判断倒数第二手
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        # 双方都选择停一手时游戏结束
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        """
        检查自吃
        :param player: Player
        :param move: Move
        :return: bool
        """

        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        # 如果新的棋链的气为0，则发生了自吃
        return new_string.num_liberties == 0

    @property
    def situation(self):
        return self.next_player, self.board

    def does_move_violate_ko(self, player, move):
        """
        检查是否违反劫争规则
        :param player: Player
        :param move: Move
        :return: bool
        """

        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        """
        检查动作的合法性
        :param move: Move
        :return: bool
        """

        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
                self.board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))

    def legal_moves(self):
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
