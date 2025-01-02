from pychess import Chess
from gpt import gpt_play

def gpt_pipeline(board):
    move, comment = gpt_play(board.get_info())

    print(move)
    board.make_illegal_move(move)
    print()
    print(f"GPT) {move}. \"{comment}\"")
    print()

def user_move(board):
    while True:
        move = input("Enter your move >> ")
        try:
            board.make_move(move)
            break
        except Exception as e:
            print()
            print(board)
            print("Invalid move. Try again.")

def pick_color():
    while True:
        user_color = input("w/b >> ")
        if user_color == "w" or user_color == "b":
            return user_color
        else:
            print("Invalid color. Try again.")

board = Chess(guide=True, ascii=True)
print(board)
user_color = pick_color()

if user_color == "w":
    print()
    print(board)
    user_move(board)

while True:
    if board.is_ended():
        print(board.game_result())
        break
    
    gpt_pipeline(board)
    user_move(board)