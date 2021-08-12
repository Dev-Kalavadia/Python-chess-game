import os, random, time
path = os.getcwd()
add_library('minim')
player = Minim(this)

DIM = 100
res_hor = 800
res_ver = 800 
IMAGES = {}

class sideBar(): #class to define the elements and methods of the sidebar displayed
    def __init__(self):
        self.piecesKilledW = []
        self.piecesKilledB = []
        self.promoteB = ['bB','bN','bR','bQ']
        self.promoteW = ['wB','wN','wR','wQ']
    
    def displayTurn(self): #method to display turn of the player
        if board.white_move:
            fill(255)
            rect(910,77,30,30)
        else:
            fill(0)
            rect(910,77,30,30)

    def Display(self): #display method to display the sidebar
        fill(r_board,g_board,b_board)
        rect(800,0,300,800)
        
side = sideBar() #instantiating the class

class GameBoard(): #class for the main game 
    def __init__(self):
        self.board = [['bR', 'bN', 'bB', 'bQ','bK','bB', 'bN','bR'], #2d Referrence board that controls the game 
                      ['bp', 'bp', 'bp', 'bp','bp','bp', 'bp','bp'],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['wp', 'wp', 'wp', 'wp','wp','wp', 'wp','wp'],
                      ['wR', 'wN', 'wB', 'wQ','wK','wB', 'wN','wR']]                    
        
        self.white_move = True # White to move first
        self.moves_made = [] # list of moves made
        self.reference_move = {'p': self.Pawn_moves,'N': self.Knight_moves,'R': self.Rook_moves, 'B': self.Bishop_moves, 'Q': self.Queen_moves, 'K': self.King_moves,  } #dictionary used to call the piece for each fucntion
        self.wKing_tracker = (7,4) # King coordinates to keep track of white king location (used in checkmate checking)
        self.bKing_tracker = (0,4) # King coordinates to keep track of black king location (used in checkmate checking)
        self.check_mate = False 
        self.stale_mate = False
        self.new_piece = "" # Pawn Promotion piece (Keyboard input sets the piece)
        self.possible_pawnPromotion = False

        #loading the required sounds for the game
        self.move_sound = player.loadFile(path + "/sounds/move.mp3")
        self.select_sound = player.loadFile(path + "/sounds/Blow.mp3")
        self.kill_sound = player.loadFile(path + "/sounds/kill.mp3")
        self.end_sound = player.loadFile(path + "/sounds/end.mp3")
        self.check_sound = player.loadFile(path + "/sounds/check.mp3")
        
        self.gameCastling = Castling(True, True, True, True) #Initial castling rights set to true for both sides
        self.castles = [Castling(self.gameCastling.wKing_side,self.gameCastling.bKing_side,self.gameCastling.wQueen_side,self.gameCastling.bQueen_side)] #list to keep track of castle and the rights 
    
    
    def makeMove(self,move): #method that makes the move
        self.board[move.square1_row][move.square1_col] = '  ' 
        self.board[move.square2_row][move.square2_col] = move.firstpiece #taking the first selected piece and moving it to the second square
        self.moves_made.append(move) #append the move to the moves list
        if move.secondpiece[0] == 'b' and board.white_move: # if white to move and capturing piece is black
            side.piecesKilledW.append(move.secondpiece) #Storing the piece in side pannel killed list
            board.kill_sound.play() #making kill sound
            board.kill_sound.rewind() #resetting the kill sound
        elif move.secondpiece[0] == 'w' and not board.white_move: # if black to move and capturing piece is white
            side.piecesKilledB.append(move.secondpiece) #Storing the piece in side pannel killed list
            board.kill_sound.play() #making kill sound
            board.kill_sound.rewind() #resetting the kill sound
        self.kill = False
        self.white_move = not self.white_move #swtiching turns (alternating)
        if move.firstpiece == 'wK': # Updating the white king location if king is moved
            self.wKing_tracker = (move.square2_row,move.square2_col) 
        elif move.firstpiece == 'bK': # Updating the black king location if king is moved
            self.bKing_tracker = (move.square2_row,move.square2_col)
        
        if move.pawn_promotion: # if pawn promotiion is true and possible
            self.possible_pawnPromotion = True
            self.board[move.square2_row][move.square2_col] = move.firstpiece[0] + self.new_piece #user input for new piece
            
        self.castle_update(move) # Updating the castle moves
        self.castles.append(Castling(self.gameCastling.wKing_side,self.gameCastling.bKing_side,self.gameCastling.wQueen_side,self.gameCastling.bQueen_side)) # Appending the castle already made with its new castle rights
               
        if move.castle: # if the move is a castle
            if move.square2_col - move.square1_col == 2: #King's side castle
                 self.board[move.square2_row][move.square2_col-1] = self.board[move.square2_row][move.square2_col+1] #swapping the rook and a king
                 self.board[move.square2_row][move.square2_col+1] = "  " # checking if space inbetween is empty

            else: #Queen's side castle 
                self.board[move.square2_row][move.square2_col+1] = self.board[move.square2_row][move.square2_col-2] #swapping the rook and a king
                self.board[move.square2_row][move.square2_col-2] = "  " # checking if space inbetween is empty 
              
    def Valid_Moves(self): #change valid to legal 
        temp_castle = Castling(self.gameCastling.wKing_side,self.gameCastling.bKing_side,self.gameCastling.wQueen_side,self.gameCastling.bQueen_side) # Temporary caslte variable 
        all_moves = self.all_possible_moves()  # storing all generated possible moves
        if self.white_move: # If white to move passing in white kings coordinated along with all moves to the caslte move method
            self.castle_moves(self.wKing_tracker[0],self.wKing_tracker[1],all_moves)
        else:
            self.castle_moves(self.bKing_tracker[0],self.bKing_tracker[1],all_moves)
            
        for i in range(len(all_moves)-1,-1,-1): #Iterating from the back in order going through all possible moves to not skip a element when removing and not getting index out of range error 
            self.makeMove(all_moves[i]) # Making each moves
            self.white_move = not self.white_move # swapping turns because makeMove method already alternates turn once
            if self.under_check(): # if under_check method returns true
                all_moves.remove(all_moves[i]) # remove all the moves that is invalid and doesnt remove the king from check           
            self.white_move = not self.white_move # swapping turns back to make it normal as before
            self.revert_moves() # Calling the revert method to undo all the possible moves made for check checking
            
        self.gameCastling = temp_castle # setting the game castling rights to the temporary castle variable 
        return all_moves # returning all valid moves 
    
    def check_gameover(self): #checking end of game
        if len(self.Valid_Moves())== 0: # if there are 0 valid moves left for a player
            if self.under_check(): #If under check game ends as checkmate
                self.check_mate = True
            else: #If not under check game ends as stalemate
                self.stale_mate = True 

    def revert_moves(self): # method to undo the move (for debugging and check function)
        if len(self.moves_made) != 0: # If there are more then 1 move in move log
            move = self.moves_made.pop() # remove the last move from the list 
            self.board[move.square1_row][move.square1_col] = move.firstpiece #swapping the pieces to the original sqaure
            self.board[move.square2_row][move.square2_col] = move.secondpiece
            self.white_move = not self.white_move # alternating turns back
            if move.secondpiece[0] == 'b' and board.white_move:  # if white to move and capturing piece is black
                side.piecesKilledW.pop() #Removing the last piece in side pannel killed list
            elif move.secondpiece[0] == 'w' and not board.white_move: # if black to move and capturing piece is white
                side.piecesKilledB.pop()  #Removing the last piece in side pannel killed list
            if move.firstpiece == 'wK': # set the king tracker locations back to original ones
                self.wKing_tracker = (move.square1_row,move.square1_col)
            elif move.firstpiece == 'bK':
                self.bKing_tracker = (move.square1_row,move.square1_col)
                
        self.castles.pop() #remove the last castle
        self.gameCastling = self.castles[-1] # set castling rights to previous one

        if move.castle: #Undoing castle moves
            if move.square2_col - move.square1_col == 2: # King's side
                 self.board[move.square2_row][move.square2_col+1] = self.board[move.square2_row][move.square2_col-1]
                 self.board[move.square2_row][move.square2_col-1] = "  "

            else: # Queen's side castle 
                self.board[move.square2_row][move.square2_col-2] = self.board[move.square2_row][move.square2_col+1]
                self.board[move.square2_row][move.square2_col+1] = "  "

    def under_check(self): #Check function to see if king is under attack
        if self.white_move:
            return (self.attacked_square(self.wKing_tracker[0],self.wKing_tracker[1])) # passing in the kings coordinates to the attacked sqaure method
        else:
            return (self.attacked_square(self.bKing_tracker[0],self.bKing_tracker[1])) # passing in the kings coordinates to the attacked sqaure method
        
    def attacked_square(self, r, c): #checking if the king sqaure is under attack
        self.white_move = not self.white_move #alternating turns to generate the opponent_moves
        opponent_moves = self.all_possible_moves() # Generating all opponent moves 
        self.white_move = not self.white_move #alternating turns again to make it back to normal 
        for move in opponent_moves: # for all moves in the the opponent's moves
            if move.square2_row == r and move.square2_col == c: #if move's row and col matcches the square passed 
                return True
        return False
    
    def castle_update(self, move): #Updating catle rights
        if move.firstpiece == "wK": # IF white king is moved
            self.gameCastling.wKing_side = False # white's king side castling set to false
            self.gameCastling.wQueen_side = False # white's queen side castling set to false
        elif move.firstpiece == "bK": # IF black king is moved
            self.gameCastling.bKing_side = False # black's king side castling set to false
            self.gameCastling.bQueen_side = False # Black's queen side castling set to false
        if move.firstpiece == "wR": #IF white rook is rook is moved
            if move.square1_row == 7: # if row is last one
                if move.square1_col == 0: # Rook on the queen's side
                    self.gameCastling.wQueen_side = False
                elif move.square1_col == 7: # Rook on the Kings's side
                    self.gameCastling.wKing_side = False
        if move.firstpiece == "bR": #IF black rook is moved
            if move.square1_col == 0: # Rook on the Queen's side
                self.gameCastling.bQueen_side = False
            elif move.square1_col == 7:  # Rook on the Kings's side
                self.gameCastling.bKing_side = False

    def all_possible_moves(self): # Generating all the moves for each piece
        possible_moves = [] #list for all possible moves
        for r in range(8):    # Going thorugh the board
            for c in range(8):
                player_turn = self.board[r][c][0] # the first charatcer to see which player B/W
                if (player_turn == 'w' and self.white_move) or (player_turn == 'b' and not self.white_move):
                    piece = self.board[r][c][1] # getting the piece char from the board index
                    self.reference_move[piece](r,c,possible_moves) #Calling the each piece move function from the refernc move dictioanry using piece key 
        return possible_moves
                        
    def Pawn_moves(self, r,c, possible_moves):  # function for Pawn moves
        if self.white_move:
            if self.board[r-1][c] == "  ": #white pawm can move 1 space up if the block above is empty
                possible_moves.append(MoveMade((r,c),(r-1,c),self.board)) # append the move to the possible moves list
                if r == 6 and self.board[r-2][c] == "  ": # white pawn move 2 space up 
                    possible_moves.append(MoveMade((r,c),(r-2,c), self.board))  # append the move to the possible moves list
                    
            if c-1>=0: #check out of bounds when caputring left
                if self.board[r-1][c-1][0] == "b": #opposite peice
                    possible_moves.append(MoveMade((r,c),(r-1,c-1), self.board)) 
            if c+1<=7: #check out of bounds when caputring right
                if self.board[r-1][c+1][0] == "b": #opposite peice
                    possible_moves.append(MoveMade((r,c),(r-1,c+1), self.board))
                    
        elif not self.white_move :
            if self.board[r+1][c] == "  ": #white pawm can move 1 space up
                possible_moves.append(MoveMade((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "  ": # white pawn move 2 space up
                    possible_moves.append(MoveMade((r,c),(r+2,c),self.board))
            if c-1>=0: #check out of bounds when caputring left
                if self.board[r+1][c-1][0] == "w": #opposite peice
                    possible_moves.append(MoveMade((r,c),(r+1,c-1), self.board))
            if c+1<=7: #check out of bounds when caputring right
                if self.board[r+1][c+1][0] == "w": #opposite peice
                    possible_moves.append(MoveMade((r,c),(r+1,c+1), self.board))
          
    def Rook_moves(self, r,c, possible_moves):  # function for Rook moves
        neighbours = [(-1,0),(0,-1),(1,0),(0,1)] # Directions for rook to move (Horizontal and vertical only)
        if self.white_move:
            enemy_player = 'b'
        else:
            enemy_player = 'w'
        for n in neighbours: # going through all possible directions
            for i in range(1,8):
                nextrow = r + n[0] * i #next row for the rook could move to 
                nextcol = c + n[1] * i #next col for the rook could move to 
                if 0 <= nextrow < 8 and 0 <= nextcol < 8: #checking if is on the board and not out of bounds
                    next_piece = self.board[nextrow][nextcol]
                    if next_piece == "  ": #if empty
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                    elif next_piece[0] == enemy_player: #if enemy piece 
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                        break
                    else:
                        break
                else:
                    break
                        
    def Bishop_moves(self, r,c, possible_moves):   # function for Bishop moves
        neighbours = [(-1,-1),(1,1),(-1,1),(1,-1)] # Directions for Bishop to move (Diagonals both up and down)
        if self.white_move:
            enemy_player = 'b'
        else:
            enemy_player = 'w'
        for n in neighbours:
            for i in range(1,8):
                nextrow = r + n[0] * i #next row for the Bishop could move to 
                nextcol = c + n[1] * i #next col for the Bishop could move to 
                if 0 <= nextrow < 8 and 0 <= nextcol < 8: #checking if is on the board and not out of bounds
                    next_piece = self.board[nextrow][nextcol]
                    if next_piece == "  ": #if empty
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                    elif next_piece[0] == enemy_player: #if enemy piece
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                        break # Breaking out 
                    else:
                        break # Breaking to avoid errors 
                else:
                    break # Breaking to avoid errors 
                        
    def Knight_moves(self, r,c, possible_moves): # function for Knight moves
        neighbours = [(2,1),(2,-1),(-2,-1),(-2,1),(1,2),(1,-2),(-1,-2),(-1,2)] #Sqaures Knight can jump to (all 8 possible moves in an L shape)
        if self.white_move:
            enemy_player = 'b'
        else:
            enemy_player = 'w'
            
        for n in neighbours:
            for i in range(1,8):
                nextrow = r + n[0]  #next row of the square the Knight can jump to 
                nextcol = c + n[1]  #next col of the square the Knight can jump to
                if 0 <= nextrow < 8 and 0 <= nextcol < 8: #checking if is on the board and not out of bounds
                    next_piece = self.board[nextrow][nextcol]
                    if next_piece == "  ": #if empty
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                    elif next_piece[0] == enemy_player:  # enemy piece
                        possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                        break # Breaking to avoid errors 
                    else:
                        break # Breaking to avoid errors 
                else:
                    break # Breaking to avoid errors 
    
    def Queen_moves(self, r,c, possible_moves): # function for Queen moves
        self.reference_move["R"](r,c,possible_moves)  #Simply calling rook moves
        self.reference_move["B"](r,c,possible_moves) #Simply calling bishop moves
        
    def King_moves(self, r,c, possible_moves): 
        neighbours = [(-1,-1),(1,1),(-1,1),(1,-1),(-1,0),(0,-1),(1,0),(0,1)] #ALl 8 neighbouring squares the king can move to
        if self.white_move:
            enemy_player = 'b'
        else:
            enemy_player = 'w'
        for n in neighbours:
            nextrow = r + n[0] 
            nextcol = c + n[1] 
            if 0 <= nextrow < 8 and 0 <= nextcol < 8: #checking if is on the board and not out of bounds
                next_piece = self.board[nextrow][nextcol]
                if next_piece == "  ": #if empty
                    possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
                elif next_piece[0] == enemy_player: #if enemy piece
                    possible_moves.append(MoveMade((r,c),(nextrow,nextcol), self.board))
        
    def castle_moves(self,r,c,possible_moves): 
        if self.attacked_square(r, c):
            return #cant castle (under check)
        if self.white_move and self.gameCastling.wKing_side: # If white to move and White king side castling is true 
            self.king_castle_moves(r,c,possible_moves) #Make the king side castle
        if not self.white_move and self.gameCastling.bKing_side:
            self.king_castle_moves(r,c,possible_moves) #Make the king side castle 
        if self.white_move and self.gameCastling.wQueen_side:
            self.queen_castle_moves(r,c,possible_moves) #Make the Queen side castle
        if not self.white_move and self.gameCastling.bQueen_side:
            self.queen_castle_moves(r,c,possible_moves) #Make the Queen side castle
        
    def king_castle_moves(self,r,c,possible_moves):
        if self.board[r][c+1] == "  " and self.board[r][c+2] == "  ": # If the 2 squares in between are empty
            if not self.attacked_square(r, c+1) and not self.attacked_square(r, c+2):  # If the squares in between are not under attack
                possible_moves.append(MoveMade((r,c),(r,c+2), self.board, castle=True)) #Make the move (swap)
  
    def queen_castle_moves(self,r,c,possible_moves):
        if self.board[r][c-1] == "  " and self.board[r][c-2] == "  " and self.board[r][c-3] == "  ": # If the 3 squares in between are empty
            if not self.attacked_square(r, c-1) and not self.attacked_square(r, c-2):  # If the squares in between are not under attack
                possible_moves.append(MoveMade((r,c),(r,c-2), self.board, castle=True)) #Make the move (swap)

class Castling(): #class for castling (used to store the castling rights as is accessed in multiple classes)
    def __init__(self, wKing_side ,wQueen_side, bKing_side, bQueen_side): # Default rights set in the gameboard class and is updated later
        self.wKing_side = wKing_side
        self.wQueen_side = wQueen_side
        self.bKing_side = bKing_side
        self.bQueen_side = bQueen_side

class MoveMade(): # Class more actual move made (setting row and col variables and swapping the pieces)
    def __init__(self,square1,square2, board, castle=False):
        self.square1_row = square1[0] # starting piece row
        self.square1_col = square1[1] # starting piece col
        self.square2_row = square2[0] # ending piece row
        self.square2_col = square2[1] # ending piece col
        self.firstpiece = board[self.square1_row][self.square1_col]  #accessing the first piece from the board with starting coordinates
        self.secondpiece = board[self.square2_row][self.square2_col] #accessing the second piece from the board with ending coordinates
        self.move_reference =  self.square1_row*1000 + self.square1_col*100 + self.square2_row*10 + self.square2_col #A unique ID for each piece movement (4 digit number used to make comparison) 
        self.pawn_promotion = False #Inital pawn promotion set to false
        if self.firstpiece == "wp" and self.square2_row == 1:
            self.possible_pawnPromotion = True #checking previous row for pawn promtion in order to print the piece promotion options on the sidepanel
        if self.firstpiece == "wp" and self.square2_row == 0:
            self.pawn_promotion = True # Actual pawn promtion set to true
        if self.firstpiece == "bp" and self.square2_row == 6:
            self.possible_pawnPromotion = True #checking previous row for pawn promtion in order to print the piece promotion options on the sidepanel
        if self.firstpiece == "bp" and self.square2_row == 7:
            self.pawn_promotion = True # Actual pawn promtion set to true
        
        
        
        self.castle = castle # castle value is default (later updated when castle made on the the respective side for each player)

    def __eq__(self, target): # overwritting the equal method to see if the target and move made are the same 
        if isinstance(target, MoveMade):
            return self.move_reference == target.move_reference
        return False
           
themes = [[[118,150,86],[234,240,206],["Green"]],[[75, 81, 152],[151, 147, 204],["Blue"]],[[125,135,150],[232,235,239],["Grayish"]],[[209, 139, 71],[255, 206, 158],["Brown"]]] #Color schemes for the board 
colour = random.choice(themes) # Randomizing the board colors at the start 
r1_col = colour[0][0] #Storing RGB values in a 2d array
g1_col = colour[0][1]
b1_col = colour[0][2]
r2_col = colour[1][0]
g2_col = colour[1][1]
b2_col = colour[1][2]
r_board = r2_col
g_board = g2_col
b_board = b2_col

    
class MainGame(): # chess game (displaying class)
    def __init__(self):
        self.game_over = False
        self.squares_clicked = [] # a list of the squares selected by the mouse
        self.square_selected = () # coordinates of the each square selected
        self.temp_moves = []
        
    def displayBoard(self): #Displaying the chess board (without pieces)
        for i in range(8):
            for j in range(8):
                if (i+j+1)%2 == 0: # Formula for the checkered board design
                    fill(r1_col,g1_col,b1_col) #getting the fill values 
                else:
                    fill(r2_col,g2_col,b2_col) 
                rect(i*DIM,j*DIM,(i+1)*DIM,(j+1)*DIM) #Drawing each rectangles 
            
    def displayPieces(self,board): # Method for displaying the respective pieces
        for i in range(8):
            for j in range(8):
                piece = board[j][i] # getting the piece name from our 2d Referrence board
                if piece != "  ": # If its not an empty piece 
                    image(IMAGES[piece], DIM*i, DIM*j, DIM, DIM) # get the image from the images folder (defined in the setup)
             
    def highlight(self,board):
        if self.square_selected != ():
            row,col = self.square_selected
            if board[row][col][0] == "w":
                for move in self.temp_moves:
                    if move.square1_col == col and move.square1_row == row:
                        fill(210)
                        rect(move.square2_col*DIM,move.square2_row*DIM,DIM,DIM)
            elif board[row][col][0] == "b":
                for move in self.temp_moves:
                    if move.square1_col == col and move.square1_row == row:
                        fill(210)
                        rect(move.square2_col*DIM,move.square2_row*DIM,DIM,DIM)
                            
game = MainGame() # Creating an instance of the main game class  (mostly displaying)                                                         
board = GameBoard()  # Creating an instance of the main game class (particularly the board)   
# validMoves = board.Valid_Moves()

def setup():
    size(res_hor + 300,res_ver) # Size 800x800 for the board and the the side panel of widht 300
    background(225) 
    board_pieces = ['bR', 'bN', 'bB', 'bQ','bK','bp','wR', 'wN', 'wB', 'wQ','wK','wp'] # possible pieces on the board (similar to the image name in the folder)
    for piece in board_pieces: # for each piece in the board list
        IMAGES[piece] = loadImage(path+'/images/'+piece+ '.png') # load the image of that piece from the file path

def draw(): 
    board.check_gameover() # constantly checking for end of game
    game.displayBoard() # displaying the checkered board
    
    game.highlight(board.board)
    
    game.displayPieces(board.board) # displaying the pieces on the board
    
    
    side.Display() #Displaying the sidepanel
    fill(0,0,0) 
    textSize(20)
    text("GAME STATS",890,50) #Game stats on the sidepanel
    fill(0)
    textSize(20)
    text("White : ",810,200)
    pos_r = 200
    pos_c = 805
    for pic in side.piecesKilledW: # Whites list of captured pieces
        image(IMAGES[pic],pos_c,pos_r,30,30) # displaying the killed pieces on the side 
        pos_c += 30
        if pos_c == 1075:
            pos_r += 40
            pos_c = 805
    fill(0,0,0)
    textSize(20)
    text("Black : ",810,300)
    pos_r = 300
    pos_c = 805
    for pic in side.piecesKilledB: # Blacks list of captured pieces
        image(IMAGES[pic],pos_c,pos_r,30,30) # displaying the killed pieces on the side 
        pos_c += 30
        if pos_c == 1075:
            pos_r += 40
            pos_c = 805
    fill(0,0,0)
    textSize(20)
    text("TURN -> ",810,100) 
    side.displayTurn() # Displaying player turn and alternating the color 
    if board.under_check() and board.check_mate == False:
        fill(255,0,0)
        textSize(50)
        text("CHECK! ",860,500) # print check on side panel
        board.check_sound.play() # play check sound
    else:    
        board.check_sound.rewind() # rewind check sound
        
    if board.check_mate:
        game.game_over = True
        if board.white_move:
            fill(255,0,0) # text color set to red
            textSize(32)
            text("GAME OVER!!", 850,500) # Printing endgame message 
            text("Black wins by",845,532) 
            text("CHECKMATE",850,564)
            board.end_sound.play()
            fill(0)
            text("Press A to restart",820,596) # restart option
        else:
            fill(255,0,0) # text color set to red
            textSize(32)
            text("GAME OVER!!", 850,500)  # Printing endgame message 
            text("White wins by",845,532) 
            text("CHECKMATE",850,564)
            board.end_sound.play()
            fill(0)         
            text("Press A to restart",820,596) # restart option
            
    elif board.stale_mate:
        game.game_over = True
        fill(255,0,0) # text color set to red
        textSize(32)
        text("STALEMATE",860,500)
    if board.possible_pawnPromotion:
        # game.game_over = True
        if board.white_move:
            fill(0) # text color set to black
            textSize(32)
            text("Possible Pawn", 830,450) # Displaying pawn prompromotion message 
            text("Promotion for ",830,490)
            text("White", 895,530)
            pos_c = 800
            pos_r = 570
            for pic in side.promoteW:
                image(IMAGES[pic],pos_c,pos_r,75,75) # Displaying possible pieces for pawn prompromotion  
                text(pic[-1],pos_c + 29, pos_r + 100)
                pos_c += 70
            if board.new_piece == "R":
                text("Rook selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "Q":
                text("Queen selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "N":
                text("Knight selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "B":
                text("Bishop selected ", 840,700)
                text("Make move now ", 835,740)
                
        else:
            fill(0) # text color set to black
            textSize(32)
            text("Possible Pawn", 830,450) # Displaying pawn prompromotion message 
            text("Promotion for ",830,490)
            text("Black", 895,530)
            pos_c = 800
            pos_r = 570
            for pic in side.promoteB:
                image(IMAGES[pic],pos_c,pos_r,75,75) # Displaying possible pieces for pawn prompromotion  
                text(pic[-1],pos_c + 29, pos_r + 100)
                pos_c += 70
            if board.new_piece == "R":
                text("Rook selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "Q":
                text("Queen selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "N":
                text("Knight selected ", 840,700)
                text("Make move now ", 835,740)
            elif board.new_piece == "B":
                text("Bishop selected ", 840,700)
                text("Make move now ", 835,740)

def mouseClicked(): #function for mouse clicked
    sidebar_click = False #to make sure that clicking on the sidebar does not affect the program
    if not game.game_over: # If game is not over clickling is possible
        validMoves = board.Valid_Moves() #assign (reassign everytime clicked) validMoves by calling the validmove method returning all valid moves
        game.temp_moves = validMoves
        coordinate = (mouseX,mouseY) # Getting the coordinates of the mouse clicekd 
        col = coordinate[0]//DIM # Double division of the the 1st value to get an integer col value
        row = coordinate[1]//DIM # Double division of the the 2st value to get an integer row value
        if col > 7: # if click is not on the board
            sidebar_click = True
        if sidebar_click == False:
            game.square_selected = (row,col) # set the clicked row and col coorcoordinates to the square selected
            
            game.squares_clicked.append(game.square_selected) # append the square selected to the squares clicked list
            if len(game.squares_clicked) == 1 or len(game.squares_clicked) == 2 and game.squares_clicked[0] == game.squares_clicked[1]: # if one click made or both made of if the double clicks on the same sqaure
                board.select_sound.play()
                board.select_sound.rewind()
            move_made = False #move made initally setaaa to false 
            
            
            if len(game.squares_clicked) == 2 and sidebar_click == False: # If there is 2 squares selected and click is on the board.
                move = MoveMade(game.squares_clicked[0],game.squares_clicked[1],board.board) #Make the move (passing the pair of coordinates)
                for i in range(len(validMoves)): 
                    if move == (validMoves[i]): # If the move is an valid move
                        board.makeMove(validMoves[i]) # Make the move on the board
                        move_made = True # Move made set to True
                        
                        board.move_sound.play() # playing move made sound
                        board.move_sound.rewind()
                        board.possible_pawnPromotion = False # possible pawn promotion set to false
                        game.squares_clicked = []  # reassigning the squares clicked list back to empty
                        game.square_selected = () # Emptying the coordinates for the next click
            if not move_made:
                game.squares_clicked = [game.square_selected] # If first move is invalid and player chooses to make a different move (Prevent clicking twice)
    sidebar_click = False
    
def keyPressed(): 
  #defining the keys required for pawn promotion and setting the key pressed to the new piece for pawn promotion
    if key == "r" or key == "R":
        board.new_piece = "R"
    if key == "q" or key == "Q":
        board.new_piece = "Q"
    if key == "n" or key == "N":
        board.new_piece = "N"
    if key == "b" or key == "B":
        board.new_piece = "B"
        
    if key == "A" or key == "a": # For restarting the game
        board.board = [['bR', 'bN', 'bB', 'bQ','bK','bB', 'bN','bR'], # Updating the board to a new one 
                      ['bp', 'bp', 'bp', 'bp','bp','bp', 'bp','bp'],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['  ','  ','  ','  ', '  ', '  ', '  ', '  '],
                      ['wp', 'wp', 'wp', 'wp','wp','wp', 'wp','wp'],
                      ['wR', 'wN', 'wB', 'wQ','wK','wB', 'wN','wR']]                    
        
        board.white_move = True # Setting whites turn
        board.moves_made = [] # emptying the move made list 
        board.wKing_tracker = (7,4) # intial king trackers
        board.bKing_tracker = (0,4) 
        board.check_mate = False # Inital conditons set to false
        board.stale_mate = False
        board.new_piece = " "
        board.gameCastling = Castling(True, True, True, True) # Castlign rights set back to true
        
        #Closing all sound files
        board.move_sound.close()
        board.select_sound.close()
        board.kill_sound.close()
        board.end_sound.close()
        board.check_sound.close()
        
        #Loading all the sounds back
        board.move_sound = player.loadFile(path + "/sounds/move.mp3")
        board.select_sound = player.loadFile(path + "/sounds/Blow.mp3")
        board.kill_sound = player.loadFile(path + "/sounds/kill.mp3")
        board.end_sound = player.loadFile(path + "/sounds/end.mp3")
        board.check_sound = player.loadFile(path + "/sounds/check.mp3")
        
        side.piecesKilledW = [] # Side panel list for killed pieces set to empty
        side.piecesKilledB = []
        side.check = False
        side.promoteB = ['bB','bN','bR','bQ'] #Pawn promtion option
        side.promoteW = ['wB','wN','wR','wQ']
        
        squares_clicked = [] # reassigning the squares clicked list back to empty
        square_selected = () # Emptying the coordinates for the next click
        game.__init__() 
        validMoves = board.Valid_Moves() # Getting valid moves
        game.displayBoard() #Displaying new board again
        game.displayPieces(board.board) #Displaying new pieces on the board again
        move_made = False # setting move_made back to False
