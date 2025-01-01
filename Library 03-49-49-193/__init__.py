import board as bd
import play as pl
import utils as ut

class Board:
    def __init__(self, initial_board_fen: str = None, guide: bool = False):
        self.guide = guide
        self.fen_history = []
        self.san_history = []
        self.turn = "w"
        self.castling_rights = "KQkq"
        self.en_passant_square = "-"
        self.halfmove_counter = 0
        self.fullmove_counter = 0
        self.board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

        if initial_board_fen:
            self.set_fen(initial_board_fen)

        cur_fen = self.get_fen(fen_history=True)
        self.fen_history.append(cur_fen)
    
    def __str__(self):
        board_str = ""
        for idx, rank in enumerate(self.board):
            if self.guide:
                board_str += f"{8-idx} | "

            for idx, square in enumerate(rank):
                board_str += square + " "
            board_str += "\n"

        if self.guide:
            board_str += "   ----------------\n"
            board_str += "    A B C D E F G H\n\n"
            board_str += f"Turn:{self.turn:>15}\n"
            board_str += f"Castling:{self.castling_rights:>11}\n"
            board_str += f"En Passant:{self.en_passant_square:>9}\n"
            board_str += f"Halfmove:{self.halfmove_counter:>11}\n"
            board_str += f"Fullmove:{self.fullmove_counter:>11}\n\n"
            board_str += f"FEN:{self.get_fen()}\n\n"
            board_str += f"SAN:{self.get_san()}\n"

        return board_str
    
    def set_fen(self, fen: str):
        fen = fen.split()
        self.turn = fen[1]
        self.castling_rights = fen[2]
        self.en_passant_square = fen[3]
        self.halfmove_counter = int(fen[4])
        self.fullmove_counter = int(fen[5])

        rank = 0
        file = 0
        for code in fen[0]:

            if code == "/":
                rank += 1
                file = 0

            else:
                try:
                    code = int(code)
                    for _ in range(code):
                        self.board[rank][file] = "."
                        file += 1
                
                except:
                    self.board[rank][file] = code
                    file += 1

        self.castling_rights = self.check_castling_rights()

        try:
                self.turn = fen[1]
                self.castling_rights = fen[2]
                self.en_passant_square = fen[3]
                self.halfmove_counter = int(fen[4])
                self.fullmove_counter = int(fen[5])

        except:
            pass

    def get_fen(self, history: bool = False):
        fen = ""
        for idx, rank in enumerate(self.board):
            if idx:
                fen += "/"

            space = 0
            for square in rank:
                if square == ".":
                    space += 1
                else:
                    if space:
                        fen += str(space)
                        space = 0
                    fen += square
            
            if space:
                fen += str(space)

        fen += " " + self.turn
        fen += " " + self.castling_rights
        fen += " " + self.en_passant_square
        if not history:
            fen += " " + str(self.halfmove_counter)
            fen += " " + str(self.fullmove_counter)

        return fen
    
    def get_san(self):
        san = ""

        for move in self.san_history:
            san += move + " "

        return san

    def san_decode(self, move: str):
        pass

    def san(self, move: str):
        pass

    def check_castling_rights(self):
        castling_rights = ""
        if self.board[0][4] == "K":
            if self.board[0][7] == "R":
                castling_rights += "K"
            if self.board[0][0] == "R":
                castling_rights += "Q"

        if self.board[7][4] == "k":
            if self.board[7][7] == "r":
                castling_rights += "k"
            if self.board[7][0] == "r":
                castling_rights += "q"

        if not castling_rights:
            castling_rights = "-"

        return castling_rights
    
    def en_passant_rights(self):
        pass
    
    def is_valid_coord(self, coord: tuple):
        rank, file = coord
        if rank < 0 or rank > 7 or file < 0 or file > 7:
            return False

        return True
        
    def is_checked(self):
        king = "K" if self.turn == "w" else "k"
        position = tuple()
        for rank in range(8):
            for file in range(8):
                if self.board[rank][file] == king:
                    position = (rank, file)
                    break

        return
    
    def is_king_stuck(self):
        pass

    def is_checkmated(self):
        pass
    
    def is_stalemated(self):
        pass
    
    def is_threefold_repetition(self):
        cur_fen = self.get_fen(history=True)
        
        if self.fen_history.count(cur_fen) == 3:
            return True
        
        return False
    
    def is_fifty_move_rule(self):
        pass
    
    def is_insufficient_material(self):
        pass


if __name__ == "__main__":
    board = Board(guide=True)
    print(board)