import re

class Board:
    def __init__(self, initial_board_fen: str = None, guide: bool = False, ascii: bool = False) -> None:
        self.guide = guide
        self.ascii = ascii
        self.san_pattern = re.compile(r"([pRNBQK])?([a-h])?([1-8])?(x)?([a-h])([1-8])( ?e\.?p\.? ?)?(=[RNBQ])?([+#])?", re.IGNORECASE)
        self.rank = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
        self.file = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        self.convert_rank = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
        self.convert_file = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
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

        cur_fen = self.get_fen(history=True)
        self.fen_history.append(cur_fen)

    def __str__(self) -> str:
        board_str = ""
        for idx, rank in enumerate(self.board):
            if self.guide:
                board_str += f"{8-idx} | "

            for idx, square in enumerate(rank):
                if not self.ascii:
                    if square == "r":
                        square = "♜"
                    elif square == "n":
                        square = "♞"
                    elif square == "b":
                        square = "♝"
                    elif square == "q":
                        square = "♛"
                    elif square == "k":
                        square = "♚"
                    elif square == "p":
                        square = "♟"
                    elif square == "R":
                        square = "♖"
                    elif square == "N":
                        square = "♘"
                    elif square == "B":
                        square = "♗"
                    elif square == "Q":
                        square = "♕"
                    elif square == "K":
                        square = "♔"
                    elif square == "P":
                        square = "♙"
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
            board_str += f"FEN: {self.get_fen()}\n\n"
            board_str += f"SAN: {self.get_san()}\n"

        return board_str
    
    def set_fen(self, fen: str) -> None:
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

    def get_fen(self, history: bool = False) -> str:
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
    
    def get_san(self) -> str:
        san = ""

        for idx, move in enumerate(self.san_history):
            if idx % 2:
                san += f"{str((idx // 2) + 1)}...{move} "
            else:
                san += f"{str((idx // 2) + 1)}.{move} "

        return san

    def is_valid_coord(self, rank: int, file: int) -> bool:
        if rank < 0 or rank > 7 or file < 0 or file > 7:
            return False

        return True

    def is_threefold_repetition(self) -> bool:
        cur_fen = self.get_fen(history=True)
        
        if self.fen_history.count(cur_fen) == 3:
            return True
        
        return False
    
    def is_fifty_move_rule(self) -> bool:
        if self.halfmove_counter == 50:
            return True
        
        return False

    def can_move(self, piece: str, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if piece == "R":
            return self.can_move_rook(origin_rank, origin_file, target_rank, target_file)
        elif piece == "N":
            return self.can_move_knight(origin_rank, origin_file, target_rank, target_file)
        elif piece == "B":
            return self.can_move_bishop(origin_rank, origin_file, target_rank, target_file)
        elif piece == "Q":
            return self.can_move_queen(origin_rank, origin_file, target_rank, target_file)
        elif piece == "K":
            return self.can_move_king(origin_rank, origin_file, target_rank, target_file)
        
    def can_move_pawn(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if origin_file == target_file:
            if self.board[origin_rank][origin_file] == "p":
                if origin_rank - target_rank == 1:
                    return self.board[target_rank][target_file] == "."
            elif self.board[origin_rank][origin_file] == "P":
                if target_rank - origin_rank == 1:
                    return self.board[target_rank][target_file] == "."
            
        elif abs(origin_file - target_file) == 1:
            if self.board[origin_rank][origin_file] == "p":
                if origin_rank - target_rank == 1:
                    return (self.board[target_rank][target_file].isupper())
            elif self.board[origin_rank][origin_file] == "P":
                if target_rank - origin_rank == 1:
                    return (self.board[target_rank][target_file].islower())

        return False
    
    def can_move_pawn_two_squares(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if self.board[origin_rank][origin_file] == "p":
            if origin_rank == 1 and target_rank == 3 and origin_file == target_file:
                return self.board[2][origin_file] == "." and self.board[3][origin_file] == "."
        elif self.board[origin_rank][origin_file] == "P":
            if origin_rank == 6 and target_rank == 4 and origin_file == target_file:
                return self.board[4][origin_file] == "." and self.board[5][origin_file] == "."

        return False
    
    def can_en_passant(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if self.en_passant_square != "-":
            if self.board[origin_rank][origin_file] == "p":
                if origin_rank == 2 and target_rank == 3 and target_file == self.file[self.en_passant_square[0]]:
                    return True
            elif self.board[origin_rank][origin_file] == "P":
                if origin_rank == 5 and target_rank == 4 and target_file == self.file[self.en_passant_square[0]]:
                    return True

    def can_move_rook(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if origin_rank == target_rank:
            if origin_file < target_file:
                for file in range(origin_file + 1, target_file):
                    if self.board[origin_rank][file] != ".":
                        return False
            else:
                for file in range(target_file + 1, origin_file):
                    if self.board[origin_rank][file] != ".":
                        return False
                    
            return True
        
        elif origin_file == target_file:
            if origin_rank < target_rank:
                for rank in range(origin_rank + 1, target_rank):
                    if self.board[rank][origin_file] != ".":
                        return False
            else:
                for rank in range(target_rank + 1, origin_rank):
                    if self.board[rank][origin_file] != ".":
                        return False
                    
            return True

        return False

    def can_move_knight(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if abs(origin_rank - target_rank) == 2 and abs(origin_file - target_file) == 1:
            return True
        elif abs(origin_rank - target_rank) == 1 and abs(origin_file - target_file) == 2:
            return True
        
        return False

    def can_move_bishop(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if abs(origin_rank - target_rank) == abs(origin_file - target_file):
            if origin_rank < target_rank:
                if origin_file < target_file:
                    for i in range(1, abs(origin_rank - target_rank)):
                        if self.board[origin_rank + i][origin_file + i] != ".":
                            return False
                else:
                    for i in range(1, abs(origin_rank - target_rank)):
                        if self.board[origin_rank + i][origin_file - i] != ".":
                            return False
            else:
                if origin_file < target_file:
                    for i in range(1, abs(origin_rank - target_rank)):
                        if self.board[origin_rank - i][origin_file + i] != ".":
                            return False
                else:
                    for i in range(1, abs(origin_rank - target_rank)):
                        if self.board[origin_rank - i][origin_file - i] != ".":
                            return False

            return True
        
        return False

    def can_move_queen(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if self.can_move_rook(origin_rank, origin_file, target_rank, target_file):
            return True
        elif self.can_move_bishop(origin_rank, origin_file, target_rank, target_file):
            return True

        return False
    
    def can_move_king(self, origin_rank: int, origin_file: int, target_rank: int, target_file: int) -> bool:
        if abs(origin_rank - target_rank) <= 1 and abs(origin_file - target_file) <= 1:
            return True
        
        return False

    def san_decode(self, move: str) -> tuple:
        move = move.lower()
        
        if move.startswith("o-o") or move.startswith("0-0"):
            return ("C", None, None, None, None, None, None, None, "K", None, None)
        elif move.startswith("o-o-o") or move.startswith("0-0-0"):
            return ("C", None, None, None, None, None, None, None, "Q", None, None)
        
        match = re.fullmatch(self.san_pattern, move)
        if not match:
            return (None, None, None, None, None, None, None, None, None, None, "0")
        
        else:
            piece = match.group(1)
            origin_file = match.group(2)
            origin_rank = match.group(3)
            takes = match.group(4)
            target_file = match.group(5)
            target_rank = match.group(6)
            en_passant = match.group(7)
            promotion = match.group(8)
            castling = None
            check = match.group(9)
            error = None

            converted_target_rank = self.rank[target_rank]
            converted_target_file = self.file[target_file]

            if self.board[converted_target_rank][converted_target_file] == ".":
                takes = None
            else:
                takes = "x"

            if not piece:
                piece = "p"
            else:
                piece = piece.upper()
            promotion = promotion[1].upper() if promotion else None

            if piece == "p":
                if not origin_file:
                    if self.is_valid_coord(converted_target_rank+1, converted_target_file) and self.can_move_pawn(converted_target_rank+1, converted_target_file, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank+1]
                    elif self.is_valid_coord(converted_target_rank+1, converted_target_file-1) and self.can_move_pawn(converted_target_rank+1, converted_target_file-1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank+1]
                    elif self.is_valid_coord(converted_target_rank+1, converted_target_file+1) and self.can_move_pawn(converted_target_rank+1, converted_target_file+1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank+1]
                    elif self.is_valid_coord(converted_target_rank+2, converted_target_file) and self.can_move_pawn_two_squares(converted_target_rank+2, converted_target_file, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank+2]
                        en_passant = f"{self.convert_file[converted_target_file]}{self.convert_rank[converted_target_rank]}"
                    elif self.is_valid_coord(converted_target_rank+1, converted_target_file-1) and self.can_en_passant(converted_target_rank+1, converted_target_file-1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file-1]
                        origin_rank = self.convert_rank[converted_target_rank+1]
                    elif self.is_valid_coord(converted_target_rank+1, converted_target_file+1) and self.can_en_passant(converted_target_rank+1, converted_target_file+1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file+1]
                        origin_rank = self.convert_rank[converted_target_rank+1]

                    elif self.is_valid_coord(converted_target_rank-1, converted_target_file) and self.can_move_pawn(converted_target_rank-1, converted_target_file, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank-1]
                    elif self.is_valid_coord(converted_target_rank-1, converted_target_file-1) and self.can_move_pawn(converted_target_rank-1, converted_target_file-1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank-1]
                    elif self.is_valid_coord(converted_target_rank-1, converted_target_file+1) and self.can_move_pawn(converted_target_rank-1, converted_target_file+1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank-1]
                    elif self.is_valid_coord(converted_target_rank-2, converted_target_file) and self.can_move_pawn_two_squares(converted_target_rank-2, converted_target_file, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file]
                        origin_rank = self.convert_rank[converted_target_rank-2]
                        en_passant = f"{self.convert_file[converted_target_file]}{self.convert_rank[converted_target_rank]}"
                    elif self.is_valid_coord(converted_target_rank-1, converted_target_file-1) and self.can_en_passant(converted_target_rank-1, converted_target_file-1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file-1]
                        origin_rank = self.convert_rank[converted_target_rank-1]
                    elif self.is_valid_coord(converted_target_rank-1, converted_target_file+1) and self.can_en_passant(converted_target_rank-1, converted_target_file+1, converted_target_rank, converted_target_file):
                        origin_file = self.convert_file[converted_target_file+1]
                        origin_rank = self.convert_rank[converted_target_rank-1]                    
                    
                    else:
                        for file in range(8):
                            if self.board[1][file] == "p":
                                if self.can_move_pawn(1, file, converted_target_rank, converted_target_file):
                                    origin_file = self.convert_file[file]
                                    origin_rank = self.convert_rank[1]
                                    break

            else:
                if not origin_file:
                    if not origin_rank:
                        for rank in range(8):
                            for file in range(8):
                                if rank == converted_target_rank and file == converted_target_file:
                                    continue

                                if self.board[rank][file].upper() == piece:
                                    if self.can_move(piece, rank, file, converted_target_rank, converted_target_file):
                                        origin_file = self.convert_file[file]
                                        origin_rank = self.convert_rank[rank]
                                        break
                
                else:
                    if not origin_rank:
                        for rank in range(8):
                            if self.board[rank][self.file[origin_file]] == piece:
                                if self.can_move(piece, rank, self.file[origin_file], converted_target_rank, converted_target_file):
                                    origin_rank = self.convert_rank[rank]
                                    break

            return (piece, origin_file, origin_rank, takes, target_file, target_rank, en_passant, promotion, castling, check, error)
        
    def san_encode(self, move: str) -> str:
        return move

    def play(self, move: str) -> bool:
        piece, origin_file, origin_rank, takes, target_file, target_rank, en_passant, promotion, castling, check, error = self.san_decode(move)
        origin_rank = self.rank[origin_rank] if origin_rank else None
        origin_file = self.file[origin_file] if origin_file else None
        target_rank = self.rank[target_rank] if target_rank else None
        target_file = self.file[target_file] if target_file else None

        if error:
            return False
        
        if piece == "C":
            self.en_passant_square = "-"

            if castling == "K":
                if self.turn == "w":
                    self.board[7][6] = "K"
                    self.board[7][5] = "R"

                    for rank in range(8):
                        for file in range(8):
                            if rank == 7 and file == 6:
                                continue

                            if self.board[rank][file] == "K":
                                self.board[rank][file] = "."
                                break

                else:
                    self.board[0][6] = "k"
                    self.board[0][5] = "r"

                    for rank in range(8):
                        for file in range(8):
                            if rank == 0 and file == 6:
                                continue

                            if self.board[rank][file] == "k":
                                self.board[rank][file] = "."
                                break

            elif castling == "Q":
                if self.turn == "w":
                    self.board[7][2] = "K"
                    self.board[7][3] = "R"

                    for rank in range(8):
                        for file in range(8):
                            if rank == 7 and file == 2:
                                continue

                            if self.board[rank][file] == "K":
                                self.board[rank][file] = "."
                                break

                else:
                    self.board[0][2] = "k"
                    self.board[0][3] = "r"

                    for rank in range(8):
                        for file in range(8):
                            if rank == 0 and file == 2:
                                continue

                            if self.board[rank][file] == "k":
                                self.board[rank][file] = "."
                                break

        elif piece == "p":
            self.board[target_rank][target_file] = "P" if self.turn == "w" else "p"
            self.board[origin_rank][origin_file] = "."

            if en_passant:
                self.en_passant_square = f"{self.convert_file[target_file]}{self.convert_rank[target_rank]}"

            else:
                self.en_passant_square = "-"

            if promotion:
                if self.turn == "w":
                    self.board[target_rank][target_file] = promotion
                else:
                    self.board[target_rank][target_file] = promotion.lower()

        else:
            self.en_passant_square = "-"

            if self.turn == "w":
                self.board[target_rank][target_file] = piece
            else:
                self.board[target_rank][target_file] = piece.lower()
            self.board[origin_rank][origin_file] = "."

        if piece == "R":
            if origin_file == 0:
                if origin_rank == 0:
                    self.castling_rights = self.castling_rights.replace("q", "")
                elif origin_rank == 7:
                    self.castling_rights = self.castling_rights.replace("Q", "")
            elif origin_file == 7:
                if origin_rank == 0:
                    self.castling_rights = self.castling_rights.replace("k", "")
                elif origin_rank == 7:
                    self.castling_rights = self.castling_rights.replace("K", "")

        if piece == "K":
            if origin_rank == 0:
                self.castling_rights = self.castling_rights.replace("k", "")
                self.castling_rights = self.castling_rights.replace("q", "")
            elif origin_rank == 7:
                self.castling_rights = self.castling_rights.replace("K", "")
                self.castling_rights = self.castling_rights.replace("Q", "")

        self.halfmove_counter += 1

        if piece == "p":
            self.halfmove_counter = 0
        if takes:
            self.halfmove_counter = 0
        
        if self.turn == "b":
            self.fullmove_counter += 1

        if self.turn == "w":
            self.turn = "b"
        else:
            self.turn = "w"

        fen = self.get_fen(history=True)
        self.fen_history.append(fen)
        san = self.san_encode(move)
        self.san_history.append(san)

        return True

if __name__ == "__main__":
    board = Board(guide=True, ascii=True)
    print(board)

    board.play("O-O-O")
    print(board)