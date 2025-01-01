import chess
import re

class Board:
    guide = False
    ascii = False
    board = None
    san_history = []
    san_pattern = re.compile(r"([pRNBQK])?([a-h])?([1-8])?(x)?([a-h])([1-8])( ?e\.?p\.? ?)?(=[RNBQ])?([+#])?", re.IGNORECASE)
    rank = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7}
    file = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    def __init__(self, init_fen: str = None, guide: bool=False, ascii: bool=False) -> None:
        self.guide = guide
        self.ascii = ascii
        if init_fen:
            self.board = chess.Board(init_fen)
        else:
            self.board = chess.Board()

    def __str__(self) -> str:
        board_str_ret = ""
        board_str = self.board.unicode() if not self.ascii else str(self.board)
        for idx, rank in enumerate(board_str.split("\n")):
            if self.guide:
                board_str_ret += f"{8-idx} | "
            
            for idx, square in enumerate(rank.split(" ")):
                board_str_ret += square + " "
            board_str_ret += "\n"

        if self.guide:
            cur_fen = self.board.fen()
            _, turn, castling_rights, en_passant_square, halfmove_counter, fullmove_counter = cur_fen.split(" ")
            board_str_ret += "   ----------------\n"
            board_str_ret += "    A B C D E F G H\n\n"
            board_str_ret += f"Turn:{turn:>15}\n"
            board_str_ret += f"Castling:{castling_rights:>11}\n"
            board_str_ret += f"En Passant:{en_passant_square:>9}\n"
            board_str_ret += f"Halfmove:{halfmove_counter:>11}\n"
            board_str_ret += f"Fullmove:{fullmove_counter:>11}\n\n"
            board_str_ret += f"FEN: {cur_fen}\n\n"
            board_str_ret += f"SAN: {self.get_san()}\n\n\n"

        return board_str_ret
    
    def get_san(self) -> str:
        san = ""

        for idx, move in enumerate(self.san_history):
            if idx % 2:
                san += f"{str((idx // 2) + 1)}...{move} "
            else:
                san += f"{str((idx // 2) + 1)}.{move} "

        return san
        
    def play(self, move: str) -> None:
        self.board.push_san(move)

        move_encoded = self.encode_san(move)
        move_encoded += self.check()
        self.san_history.append(move_encoded)

    def play_with_illegal(self, move: str) -> bool:
        try:
            self.board.push_san(move)

            move_encoded = self.encode_san(move)
            move_encoded += self.check()
            self.san_history.append(move_encoded)

            return True

        except:
            move_decoded = self.decode_san(move)
            if move_decoded is None:
                raise ValueError("Invalid move")
            
            if move_decoded[1] == "@":
                self.board.set_piece_at(chess.square(int(move_decoded[2]), int(move_decoded[3])), chess.Piece.from_symbol(move_decoded[0].upper()))

            else:
                move_uci = chess.Move.from_uci(move_decoded)
                self.board.push(move_uci)

            move_encoded = self.encode_san(move)
            move_encoded += self.check()

            self.san_history.append(move_encoded)

            return False
        
    def decode_san(self, san: str) -> str:
        san = san.lower()

        if san.startswith("o-o") or san.startswith("0-0"):
            return "e1g1" if self.board.turn else "e8g8"
        
        if san.startswith("o-o-o") or san.startswith("0-0-0"):
            return "e1c1" if self.board.turn else "e8c8"
        
        match = re.fullmatch(self.san_pattern, san)
        if not match:
            return None
        
        piece = match.group(1)
        origin_file = match.group(2)
        origin_rank = match.group(3)
        capture = match.group(4)
        dest_file = match.group(5)
        dest_rank = match.group(6)
        ep = match.group(7)
        promotion = match.group(8)
        castling = None
        check = match.group(9)

        if not piece:
            piece = "p"

        if self.board.turn:
            piece = piece.upper()
        else:
            piece = piece.lower()

        converted_dest_rank = self.rank[dest_rank]
        converted_dest_file = self.file[dest_file]

        found_piece = False
        nearest_coord = (100, 100)
        for rank in range(8):
            for file in range(8):
                if str(self.board.piece_at(chess.square(file, rank))) == piece:
                    if abs(converted_dest_rank - rank) + abs(converted_dest_file - file) < abs(converted_dest_rank - nearest_coord[0]) + abs(converted_dest_file - nearest_coord[1]):
                        nearest_coord = (rank, file)
                        found_piece = True

        if not found_piece:
            return f"{piece}@{converted_dest_file}{converted_dest_rank}"
        
        return f"{chess.square_name(chess.square(nearest_coord[1], nearest_coord[0]))}{dest_file}{dest_rank}"

    def encode_san(self, san: str) -> str:
        san = san.lower()

        if san.startswith("o-o") or san.startswith("0-0"):
            return "O-O"
        
        if san.startswith("o-o-o") or san.startswith("0-0-0"):
            return "O-O-O"
        
        match = re.fullmatch(self.san_pattern, san)
        if not match:
            return None
        
        piece = match.group(1)
        origin_file = match.group(2)
        origin_rank = match.group(3)
        capture = match.group(4)
        dest_file = match.group(5)
        dest_rank = match.group(6)
        ep = match.group(7)
        promotion = match.group(8)
        castling = None
        check = match.group(9)

        ret_san = ""

        if not piece:
            piece = "p"
        else:
            piece = piece.upper()
            ret_san += piece

        if origin_file:
            ret_san += origin_file
        if origin_rank:
            ret_san += origin_rank

        if self.board.piece_at(chess.square(self.file[dest_file], self.rank[dest_rank])):
            capture = "x"

        if capture:
            ret_san += capture

        ret_san += dest_file + dest_rank

        if ep:
            ret_san += " e.p. "
        
        if promotion:
            promotion = promotion.upper()
            ret_san += promotion

        return ret_san

    def is_checked(self) -> bool:
        return self.board.is_check()
    
    def is_checkmated(self) -> bool:
        return self.board.is_checkmate()
    
    def is_stalemated(self) -> bool:
        return self.board.is_stalemate()
    
    def check(self) -> str:
        if self.is_checked():
            return "+"
        if self.is_checkmated():
            return "#"
        return ""

    def is_ended(self) -> bool:
        return self.board.is_game_over()

if __name__ == "__main__":
    board = Board(guide=True, ascii=True)
    print(board)

    board.play_with_illegal("o-o")
    print(board)

    board.play_with_illegal("na1")
    print(board)

    board.play_with_illegal("qd7")
    print(board)