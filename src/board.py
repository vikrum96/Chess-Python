from constants import *
from move import Move
from square import Square
from piece import *
import copy

class Board:
    def __init__(self):
        # self.board = [
        #     ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        #     ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        #     ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        # ]
        # self.white_to_move = True
        # self.move_log = []
        
        self.squares = [[0,0,0,0,0,0,0,0] for row in range(ROWS)]
        self._create()
        self._add_pieces("white")
        self._add_pieces("black")

    def move(self, piece, move, copying=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if piece.name == "pawn":
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
            else:
                self.prommotion_check(piece, final)
        
        if piece.name == "king":
            if self.castling(initial, final) and not copying:
                diff = final.col - initial.col
                rook = piece.left_rook if  diff < 0 else piece.right_rook
                self.move(rook, rook.moves[-1])
                if piece.color == "white":
                    self.white_king_location = final.row, final.col
                else:
                    self.black_king_location = final.row, final.col
            elif piece.color == "white":
                self.white_king_location = final.row, final.col
            else:
                self.black_king_location = final.row, final.col

        self.last_move = move

        piece.moved = True
        piece.clear_moves()

    def valid_move(self, piece, move): 
        return move in piece.moves
        # since move is a constructed object, this statement 
        # basically does this based on the equality functions of the other classes
        # for this_move in piece.moves:
        #     if move.initial.row == this_move.initial.row and move.final.col == this_move.final.col:
        #         return True
        # return False
    
    def set_true_en_passant(self, piece):
        if piece.name != "pawn":
            return
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        piece.en_passant = True

    def prommotion_check(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, copying=True)
        
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_oppose_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for k in p.moves:
                        if isinstance(k.final.piece, King):
                            return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
        # Calculates all possible moves of a piece
        def pawn_moves():
            steps = 1 if piece.moved else 2
            
            # vertical moves
            start = row + piece.dir
            end = row + (piece.dir*(1+steps))
            
            for possible_row in range(start, end, piece.dir):
                if Square.in_range(possible_row):
                    if self.squares[possible_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(possible_row, col)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    else: break
                else: break
            
            # diagonal moves
            possible_row = row + piece.dir
            possible_cols = [col-1, col+1]
            for possible_col in possible_cols:
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].has_oppose_piece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
            
            r = 3 if piece.color == "white" else 4
            fr = 2 if piece.color == "white" else 5
            # left en pessant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_oppose_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if p.name == "pawn":
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            
            # right en pessant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_oppose_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if p.name == "pawn":
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

        def knight_moves():
            # There are 8 "possible" moves
            possible_moves = [
                (row-2, col+1),
                (row-2, col-1),
                (row-1, col+2),
                (row-1, col-2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row+1, col+2)
            ]

            for possible_move in possible_moves:
                possible_row, possible_col = possible_move
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].isempty_or_oppose(piece.color):
                        # initialize initial and final squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        # create new valid move
                        move = Move(initial, final)
                        # append valid move
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

        
        def straightLine_moves(increments):
            for increment in increments:
                row_inc, col_inc = increment
                possible_row = row + row_inc
                possible_col = col + col_inc

                while True:
                    if Square.in_range(possible_row, possible_col):
                        # initialize initial and final squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        # create new possible move
                        move = Move(initial, final)

                        if self.squares[possible_row][possible_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                        elif self.squares[possible_row][possible_col].has_oppose_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break
                        elif self.squares[possible_row][possible_col].has_player_piece(piece.color):
                            break

                    else: break
                        
                    possible_row, possible_col = possible_row + row_inc, possible_col + col_inc

        def king_moves():
            adjs = [(row-1, col),(row-1, col+1),(row, col+1),(row+1, col+1),(row+1, col),(row+1, col-1),(row, col-1),(row-1, col-1)]
            for possible_move in adjs:
                possible_row, possible_col = possible_move
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].isempty_or_oppose(piece.color):
                        # initialize initial and final squares
                        initial = Square(row, col)
                        final = Square(possible_row, possible_col)
                        # create new possible move
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)
            
            if not piece.moved:
                # long castle
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for j in range(1, 4):
                            if self.squares[row][j].has_piece():
                                break
                            if j == 3:
                                # adds left rook to king
                                piece.left_rook = left_rook

                                initial = Square(row, 0)
                                final = Square(row, 3)
                                move_rook = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, 2)
                                move_king = Move(initial, final)

                                # check potencial checks
                                if bool:
                                    if not self.in_check(piece, move_king) and not self.in_check(left_rook, move_rook):
                                        left_rook.add_move(move_rook)
                                        piece.add_move(move_king)
                                else:
                                    left_rook.add_move(move_rook)
                                    piece.add_move(move_king)

                # short castle
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for j in range(5, 7):
                            if self.squares[row][j].has_piece():
                                break

                            if j == 6:
                                # adds right rook to king
                                piece.right_rook = right_rook

                                initial = Square(row, 7)
                                final = Square(row, 5)
                                move_rook = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, 6)
                                move_king = Move(initial, final)

                                # check checks
                                if bool:
                                    if not self.in_check(piece, move_king) and not self.in_check(right_rook, move_rook):
                                        right_rook.add_move(move_rook)
                                        piece.add_move(move_king)
                                else:
                                    right_rook.add_move(move_rook)
                                    piece.add_move(move_king)

        
        if piece.name == "pawn": #if doesn't work try isinstance(piece, Pawn)
            pawn_moves()
        elif piece.name == "knight":
            knight_moves()
        elif piece.name == "bishop":
            straightLine_moves([(-1, 1), (-1, -1), (1, 1), (1,-1)])
        elif piece.name == "rook":
            straightLine_moves([(-1, 0) , (0, 1), (1, 0), (0, -1)])
        elif piece.name == "queen":
            straightLine_moves([(-1, 1) , (-1, -1), (1, 1), (1,-1), (-1, 0), (0, 1), (1, 0), (0, -1)])
        elif piece.name == "king":
            king_moves()

    def _create(self): #is a private function, denoted as '_'create
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)    

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # Pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        
        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color))

        # Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # Knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))
    
