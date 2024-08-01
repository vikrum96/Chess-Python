import pygame
from constants import *
from board import Board
from dragger import Dragger

class Game:
    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()
        self.curr_player = "white"

    def show_board(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = (234, 235, 200) #Light green color (represents white)
                else:
                    color = (119, 154, 88) #Dark green color (represents black)
                
                rectangle = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE) #(x-axis point, y-axis point, width, height)
                pygame.draw.rect(surface, color, rectangle)
    
    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                
                    if piece is not self.dragger.piece:
                        image = pygame.image.load(piece.texture)
                        image_center = col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2

                        piece.texture_rect = image.get_rect(center=image_center)
                        surface.blit(image, piece.texture_rect)
    
    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece
            # Loop through valid moves
            for move in piece.moves:
                color = '#ffdf78' if (move.final.row + move.final.col) % 2 == 0 else '#feecb1'
                rect  = (move.final.col * SQ_SIZE, move.final.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(surface, color, rect)
    
    def next_turn(self):
        self.curr_player = "white" if self.curr_player == "black" else "black"