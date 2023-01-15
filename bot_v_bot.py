# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 下午4:25
# @Author  : Jiuxi
# @File    : bot_v_bot.py
# @Software: PyCharm 
# @Comment :

from dlgo.agent import naive
from dlgo import goboard_slow
from dlgo import gotypes
from dlgo.utils import print_board, print_move
import time


def main():
    board_size = 9
    game = goboard_slow.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: naive.RandomBot(),
        gotypes.Player.white: naive.RandomBot()
    }

    while not game.is_over():
        time.sleep(0.3)

        os.system('clear')
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)


if __name__ == "__main__":
    main()
