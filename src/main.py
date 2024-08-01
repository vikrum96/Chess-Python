import pygame, sys

from constants import *
from game import Game
from square import Square
from move import Move


# NOTE:
# Pygame x-axis increses from left to right, y-axis increases from top to bottom

class Main:
    
    # Default constructor
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.game = Game()

    def main_loop(self):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            game.show_board(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            # player_move = []

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                # Click
                if event.type == pygame.QUIT: #if player exits the game
                    pygame.quit()
                    sys.exit() #terminates script
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    # Gives the row and col of the clicked square
                    clicked_row = dragger.mouseY // SQ_SIZE
                    clicked_col = dragger.mouseX // SQ_SIZE
                    
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        if piece.color == game.curr_player:
                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                            game.show_board(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                # Mouse moving
                elif event.type == pygame.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_board(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        dragger.update_blit(screen)
                # Released Click
                elif event.type == pygame.MOUSEBUTTONUP: #this is fine
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        new_row = dragger.mouseY // SQ_SIZE
                        new_col = dragger.mouseX // SQ_SIZE
                        
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(new_row, new_col)
                        move = Move(initial, final)
                        if board.valid_move(dragger.piece, move):
                            board.move(dragger.piece, move)
                            board.set_true_en_passant(dragger.piece)
                            game.show_board(screen) 
                            game.show_pieces(screen)
                            game.next_turn()

                    dragger.undrag_piece()

            pygame.display.update()

main = Main()
main.main_loop()