import openai
import os
import dotenv

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def render_requests(system: str) -> list:
    return [{
        "role": "system",
        "content": system
    }]

def render_san_request(board_state: str, turn: str, board_fen: str, san_history: str, legal_moves: str=None) -> list:
    system = f"""You are playing as {turn}.
You MUST answer in following format:

SAN(Standard Algebraic Notation) of the move you want to make.
short comment about the move.

Example:

Nf3
Developed the pawn to control the center and opened the path for the bishop.

This is current state of the board:

{board_state}

This is fen of the board:

{board_fen}

This is the history of the moves:

{san_history}
"""
    if legal_moves:
        system += f"""\nThese are the legal moves you can make. You MUST choose one of these moves:

        {legal_moves}"""
        
    return render_requests(system)

def openai_request(query: list, model: str="gpt-4o-mini") -> str:
    completion = openai.chat.completions.create(
        model=model,
        messages=query,
        stream=False
    )

    return completion.choices[0].message.content

def gpt_play(board_info: tuple) -> tuple:
    board_state, turn, board_fen, san_history, legal_moves = board_info

    query = render_san_request(board_state, turn, board_fen, san_history, legal_moves)
    response = openai_request(query)
    move, comment = response.split("\n")
    move = move.strip()
    return move, comment

if __name__ == "__main__":
    board = """♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 
♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ 
⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ 
⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ 
⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ 
⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ ⭘ 
♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ 
♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖
"""
    turn = "black"

    query = render_san_request(board, turn)
    print(query)
    response = openai_request(query)
    print(response)