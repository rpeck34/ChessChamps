'''
Import into ChessEngine.  Gives base logic of chess piece moves.
Uses knowledge of players rank and class from Player module indirectly
through gamestate calls to add possible moves to global moves list
'''
import pygame as pg
import random as r #for gold piece generation

'''
Consider, but do not make, a move. Tracks if moves are castle, enPassant,
checks, etc.
'''
class Move():
  rowsToRanks = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}
  colsToFiles = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
  def __init__(self, startSq, endSq, board,
               specialMoves=(False, False, False, False), capSq = None):
    self.board = [list(row) for row in board] #state of board before move made
    self.startSq = startSq
    self.endSq = endSq
    if capSq == None:
      self.capSq = self.endSq
    else:
      self.capSq = capSq
    self.startRow = startSq[0]
    self.startCol = startSq[1]
    self.endRow = endSq[0]
    self.endCol = endSq[1]
    self.capRow = self.capSq[0]
    self.capCol = self.capSq[1]
    self.pieceMoved = '--'
    self.pieceCaptured = '--'
    self.stealth = False
    self.animateList = [] #list of moves to animate full move
    self.rookMove = None #for castle move
    self.specialMoves = specialMoves
    self.enPassant = specialMoves[0]  # ranged move
    self.castle = specialMoves[1]  # castle move
    self.pawnPromotion = specialMoves[2]  # pawn promotes
    self.power = specialMoves[3]  # power used
    self.enhanceName = '' #name of enhancement
    self.moveDir = (self.endRow - self.startRow,
                    self.endCol - self.startCol)
    #list of squares travelled through (including initial and final squares)
    self.path = []
    #number of squares travelled, starts at 0 from startSq
    self.rng = -1
    # normalize moveDir
    if self.pieceMoved[1] != 'N':
      if self.moveDir[0] != 0:
          self.moveDir = (self.moveDir[0] // abs(self.moveDir[0]),
                          self.moveDir[1] // abs(self.moveDir[0]))
      if self.moveDir[1] != 0:
          self.moveDir = (self.moveDir[0] // abs(self.moveDir[1]),
                          self.moveDir[1] // abs(self.moveDir[1]))
      #get path and rng
      delRow = abs(self.startRow - self.endRow) 
      delCol = abs(self.startCol - self.endCol)
      if delRow > 0 or delCol > 0:
        for i in range(max(delRow+1, delCol+1)):
          row = self.startRow + i*self.moveDir[0]
          col = self.startCol + i*self.moveDir[1]
          self.rng+=1
          self.path.append((row, col))
    #for knights, path is start and end sq only
    else:
      self.path = [self.startSq, self.endSq]
      self.rng = 3
    if not self.power:
      self.pieceMoved = board[self.startRow][self.startCol]
      self.pieceCaptured = board[self.capRow][self.capCol]
    else:
      self.targeted = [False,False] #target opponent, player piece
      self.targets = [] #only pieces in this list can be targetted
    #'effectStr',(row,col)... effects added to board from move
    self.effects = []
    #'terrainStr',(row,col)... terrain added to board from move
    self.terrain = []
    #When move is made, these new squares will be blocked to enemy
    self.blocked = [self.endSq]
    #When move is made, these new squares will be impassable to enemy
    self.impassable = []
    #these get updated in endTurn only for moves actually made
    self.check = False
    self.checkmate = False

  '''
  Needed so two moves can be compared properly.  This determines if
  two moves are the same.  Left ranged move and cap out because it
  made it easy to group these moves with regular moves in main loop.
  If this is changed in the future, would have to fix main loop.
  '''
  def __eq__(self, other):
    T1 = (self.startSq) == (other.startSq)
    T2 = (self.endSq) == (other.endSq)
    #T3 = (self.capSq) == (other.capSq)
    T3 = (self.pieceMoved) == (other.pieceMoved)
    T4 = (self.specialMoves[1]) == (other.specialMoves[1])
    T5 = (self.specialMoves[2]) == (other.specialMoves[2])
    T6 = (self.specialMoves[3]) == (other.specialMoves[3])
    #T5 = (self.animateList) == (other.animateList)
    return (T1 and T2 and T3 and T4 and T5 and T6)

  '''
  writes moves in chess notation.  Might need to come up with a
  notation just for misc moves alone if there are too many of them.
  '''
  def chessNotation(self, legalMoves=[]):
    notation = '' #initialize
    #if power used BEFORE move on same turn, add it to move name
    notation += self.enhanceName
    #if power used that ends turn
    if self.specialMoves[3] == True:
      #either no piece involved
      if self.pieceMoved == '--' and self.pieceCaptured == '--':
        return notation
      #or a captured piece involved
      elif self.pieceCaptured != '--':
        notation += self.pieceCaptured[1]
        notation += self.colsToFiles[self.endCol]
        notation += self.rowsToRanks[self.endRow]
        return notation
      #or an attacking piece involved
      elif self.pieceMoved != '--':
        notation += self.pieceMoved[1]
        notation += self.colsToFiles[self.startCol]
        notation += self.rowsToRanks[self.startRow] 
        return notation
    #add dash to join enhancement move with board move
    if self.enhanceName != '':
      notation += '-'
    place1 = ''  # usually don't specify location of attacking piece
    for move in legalMoves:
      if move != self:  # check moves other than the one made
        if self.pieceMoved == move.pieceMoved:
          if self.endSq == move.endSq:
            # if final board state ambiguous, need to specify
            place1 = self.colsToFiles[self.startCol] + self.rowsToRanks[self.startRow]
    if self.castle:
      return notation+"O-O" if self.endCol == 6 else notation+"O-O-O"
    piece1 = self.pieceMoved[1]
    takes = ''
    if not self.pieceCaptured == '--':  # if a piece is captured
      takes = 'x'
      if piece1 == 'P':  # pawn capture moves use coordinates of pawn
        place1 = self.colsToFiles[self.startCol] + self.rowsToRanks[self.startRow]
    if piece1 == 'P':
      piece1 = ''  # no need to specify piece is a pawn
    place2 = self.colsToFiles[self.endCol] + self.rowsToRanks[self.endRow]
    if self.specialMoves[0]:
      place3 = self.colsToFiles[self.capCol] + self.rowsToRanks[self.capRow]
      notation += piece1 + place1 + '>' + place2 + takes + place3
    else:
      notation += piece1 + place1 + takes + place2

    if self.stealth:
      notation = '???'

    if self.checkmate:
      notation += '#'
      return notation

    if self.check:
      notation += '+'
      return notation

    return notation

'''
Used in GameState to find piece moves. Parent class to champion piece subclasses.
'''
class PieceState():
  def __init__(self, gs):
    '''
    Might ONLY need to pass to BasePiece...Can delete pretty much everthing else
    '''
    self.pieceDict = {'P': self.Pawn,
                      'B': self.Bishop,
                      'N': self.Knight,
                      'R': self.Rook,
                      'Q': self.Queen,
                      'K': self.King}
    self.gs = gs
    self.bs = gs.bs
    self.board = gs.bs.board
    self.whiteTurn = gs.bs.whiteTurn
    self.player = gs.bs.player
    self.opp = gs.bs.opp
    self.playerTurn = gs.bs.playerTurn
    self.champ = gs.pi[self.playerTurn].champion
    self.talents = gs.pi[self.playerTurn].talents
    self.BasePiece.champ = self.champ
    self.BasePiece.talents = self.talents
    self.BasePiece.bs = self.bs
    self.BasePiece.board = self.bs.board
        
  class BasePiece():
    #These attributes are shared by ALL BasePieces (white and black)
    bs = None
    board = None
    idNum = 0
    def __init__(self, sq, piece, gold = True, effects = ()):
      self.id = self.__class__.idNum
      self.__class__.idNum += 1
      self.sq = sq
      self.row = sq[0]
      self.col = sq[1]
      self.piece = piece 
      self.me = piece[0]
      self.notMe = 'w' if self.me == 'b' else 'b'
      self.myTurn = 0 if self.me == 'w' else 1
      self.vision = [self.piece, self.piece]
      self.gold = 0
      if gold:
        x=r.randint(1,100) #1 in 100 chance, In practice make 1 in 1000 if not more
        self.gold=1 if x>90 else 0
      self.moves = []
      self.defended = []
      self.attacked = []
      self.pinned = []
      self.defendedBy = []
      self.attackedBy = []
      self.pinnedBy = []
      self.effects = list(effects)
      self.link = []
      #can be line or jump. line piece moves in straight line
      #jump piece moves only to ending square, no inbetween squares
      self.movement = 'line'
      #canBlock means terrain and pieces can prevent movement
      self.canBlock = True
      #means this piece can pin other pieces
      self.canPin = True
      #the furthest number of squares the piece can move, if none, then no limit to rng
      self.rng = None

    '''
    moves piece, called in makeMove
    '''
    def place(self, sq):
      self.sq = sq
      self.row = sq[0]
      self.col = sq[1]

    def getMoves(self, gen = False):
      pass

  class Pawn(BasePiece):
    #creates instance of pawn class on row,col on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())
      self.rng = 2
      self.canPin = False
      self.magicRow = 6 if self.me == 'w' else 1
      self.promoRow = 0 if self.me == 'w' else 7
      self.ep = False

    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs 
      board = bs.board #couldn't escape needing board.  Board for Move()
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []
      # print("in pawn moves")
      moveDir = (-1, 0) if self.me == 'w' else (1, 0)
      endRow = row + moveDir[0]
      endSq = (endRow,col)
      if 0 <= endRow < self.bs.numR:  # move lands on board
        # one move forward
        if bs.sq[endSq].moveable[pt] and not bs.sq[endSq].pc:  # if no blocking pieces
          moves.append(Move(sq, endSq, board))
          # two moves forward
          #if one square ahead not blocked
          if not bs.sq[endSq].blocked[pt]:
            if row == self.magicRow:  # if we are on the starting row
              endRow = row+2*moveDir[0]
              endSq = (endRow,col)
              if 0 <= endRow < self.bs.numR:  # move lands on board
                # if no blocking pieces
                if bs.sq[endSq].moveable[pt] and not bs.sq[endSq].pc:  
                  moves.append(Move(sq, endSq, board))
      # capture left
      moveDir = (-1, -1) if self.me == 'w' else (1, -1)
      endRow = row + moveDir[0]
      endCol = col + moveDir[1]
      endSq = (endRow, endCol)
      if 0 <= endRow < self.bs.numR:  # land on existing row
        if endCol >= 0:  # land on existing col
          if bs.sq[endSq].pc:  # if opponent piece here
            if bs.sq[endSq].pc.piece[0] == self.notMe:
              moves.append(Move(sq, endSq, board))
            elif bs.sq[endSq].pc.piece[0] == self.me:  # if player piece here
              defended.append(Move(sq, endSq, board))
            attacked.append(endSq)
      # capture right
      moveDir = (-1, 1) if self.me == 'w' else (1, 1)
      endRow = row + moveDir[0]
      endCol = col + moveDir[1]
      endSq = (endRow, endCol)
      if 0 <= endRow < bs.numR:  # land on existing row
        if endCol < bs.numC[endRow]:  # land on existing col
          if bs.sq[endSq].pc:
            if bs.sq[endSq].pc.piece[0] == self.notMe:  # if opponent piece here
              moves.append(Move(sq, endSq, board))
            elif bs.sq[endSq].pc.piece[0] == self.me:  # if player piece here
              defended.append(Move(sq, endSq, board))
            attacked.append(endSq)
      # capture en passant
      enPassantDir = [(0, -1), (0, 1)] #both left and right captures
      for ePDir in enPassantDir:
        ePRow = row + ePDir[0]
        ePCol = col + ePDir[1]
        moveDir = (-1, ePDir[1]) if self.me == 'w' else (1, ePDir[1])
        endRow = row + moveDir[0]
        endCol = col + moveDir[1]
        ePSq = (ePRow,ePCol)
        endSq = (endRow,endCol)
        if 0 <= endRow < bs.numR:  # land on existing row
          if 0 <= endCol < bs.numC[endRow]:  # land on existing col
          # if potential en passant column on board
            if 0 <= ePCol < bs.numC[endRow]:  # land on existing col
              # if there is an enemy pawn in correct position for en passant
              if bs.sq[ePSq].pc:
                if bs.sq[ePSq].pc.piece == self.notMe + 'P':
                  #if that pawn is enpassantable
                  if bs.sq[ePSq].pc.ep == True:
                    if bs.sq[ePSq].moveable[pt]:
                      moves.append(Move(sq, endSq, board,
                                        specialMoves=(True, False, False, False),
                                        capSq = ePSq))

      #convert generated moves to promo moves if any
      for m in moves:
        if m.endRow == self.promoRow:
          sp = m.specialMoves
          m.specialMoves = (sp[0],sp[1],True,sp[3])
          m.pawnPromotion = True
      #same for defending moves
      for d in defended:
        if d.endRow == self.promoRow:
          sp = d.specialMoves
          d.specialMoves = (sp[0],sp[1],True,sp[3])
          d.pawnPromotion = True
          
      if gen:
        return moves,defended,attacked
      self.moves = moves
      self.defended = defended
      self.attacked = attacked

  class Knight(BasePiece):
    movement = 'jump'
    canBlock = False
    canPin = False
    rng = 3
    #creates instance of knight class on sq on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())

    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = bs.board 
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []
      # print("in knight moves")
      moveDir = [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)]
      for direction in moveDir:
        endRow = row + direction[0]
        endCol = col + direction[1]
        endSq = (endRow,endCol)
        if (0 <= endRow < bs.numR  # move lands on board
            and 0 <= endCol < bs.numC[endRow]):
          # three cases: blocked by terrain, blocked by piece, open
          # empty square
          if not bs.sq[endSq].blocked[pt]:
            if bs.sq[endSq].moveable[pt]:
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue
          # blocked by piece
          elif bs.sq[endSq].pc:
            #friendly piece blocking
            if bs.sq[endSq].pc.piece[0] == self.me:  
              defended.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue  
            #enemy piece blocking
            elif bs.sq[endSq].pc.piece[0] == self.notMe:  
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue
          # blocked by terrain
          else: 
            if bs.sq[endSq].moveable[pt]: #can move to square
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue
      if gen:
        return moves,defended,attacked
      else:
        self.moves = moves
        self.defended = defended
        self.attacked = attacked

  class Bishop(BasePiece):
    #creates instance of bishop class on sq on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())

    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = bs.board 
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []
      #print("in bishop moves")
      moveDir = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
      for direction in moveDir:
        for i in range(1, len(board)):  # change to largest dimension of board if board is not square
          endRow = row + i * direction[0]
          endCol = col + i * direction[1]
          endSq = (endRow,endCol)
          if (0 <= endRow < bs.numR  # move lands on board
              and 0 <= endCol < bs.numC[endRow]):
            # three cases, empty square, enemy piece, own piece blocking
            if not bs.sq[endSq].blocked[pt]:
              if bs.sq[endSq].moveable[pt]:
                moves.append(Move(sq, endSq, board))
                attacked.append(endSq)
                continue
            elif bs.sq[endSq].pc:
              if bs.sq[endSq].pc.piece[0] == self.notMe:
                if bs.sq[endSq].moveable[pt]:
                  moves.append(Move(sq, endSq, board))
                  attacked.append(endSq)
                  break  
              elif bs.sq[endSq].pc.piece[0] == self.me:  # own piece here
                defended.append(Move(sq, endSq, board))
                attacked.append(endSq)
                break  
            else: #terrain blocking on empty sq, add move to square but stop searching
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              break
          else:
            break
      if gen:
        return moves,defended,attacked
      else:
        self.moves = moves
        self.defended = defended
        self.attacked = attacked

  class Rook(BasePiece):
    #creates instance of rook class on sq on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())

    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = bs.board 
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []
      # print("in rook moves")
      moveDir = [(1, 0), (0, -1), (-1, 0), (0, 1)]
      for direction in moveDir:
        for i in range(1, bs.numR):
          endRow = row + i * direction[0]
          endCol = col + i * direction[1]
          endSq = (endRow,endCol)
          if (0 <= endRow < bs.numR  # move lands on board
              and 0 <= endCol < bs.numC[endRow]):
            if not bs.sq[endSq].blocked[pt]:  # if no blocking pieces
              if bs.sq[endSq].moveable[pt]:
                moves.append(Move(sq, endSq, board))
                attacked.append(endSq)
                continue
            elif bs.sq[endSq].pc:
              if bs.sq[endSq].pc.piece[0] == self.notMe:  # opp piece here
                if bs.sq[endSq].moveable[pt]:
                  moves.append(Move(sq, endSq, board))
                  attacked.append(endSq)
                  break  
              elif bs.sq[endSq].pc.piece[0] == self.me:  # own piece blocking
                defended.append(Move(sq, endSq, board))
                attacked.append(endSq)
                break 
            else: #blocked on empty square, add move but stop looking in this direction
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              break
          else:
            break
      if gen:
        return moves,defended,attacked
      else:
        self.moves = moves
        self.defended = defended
        self.attacked = attacked

  class Queen(BasePiece):
    #creates instance of queen class on sq on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())

    def getMoves(self, gen = False):
      moves = []
      defended = []
      attacked = []
      moves,defended,attacked = PieceState.Bishop.getMoves(self, gen = True)
      rmoves,rdefended,rattacked = PieceState.Rook.getMoves(self, gen = True)
      moves.extend(rmoves)
      defended.extend(rdefended)
      attacked.extend(rattacked)
      if gen:
        return moves,defended,attacked
      else:
        self.moves = moves
        self.defended = defended
        self.attacked = attacked
        
  class King(BasePiece):
    rng = 2 #castle moves
    canPin = False
    #creates instance of king class on sq on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())
      self.castle = [True, True]
      if self.me == 'w':
        self.kingSpot = (7,4)
        self.kRookSpot = ((self.bs.numR-1), (self.bs.numC[(self.bs.numR - 1)] -1))
        self.qRookSpot = ((self.bs.numR-1), 0)
      else:
        self.kingSpot = (0,4)
        self.kRookSpot = (0, (self.bs.numC[(self.bs.numR-1)] -1))
        self.qRookSpot = (0, 0)

    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = bs.board 
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []

      #stop updating castle if both are False
      if self.castle[0] or self.castle[1]:
        #get updated castle bools
        self.updateCastle()
      #if still can castle, add castle moves if possible
      if self.castle[0] or self.castle[1]:
        moves.extend(self.castleMoves())
      moveDir = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
      for direction in moveDir:
        endRow = row + direction[0]
        endCol = col + direction[1]
        endSq = (endRow,endCol)
        if (0 <= endRow < bs.numR  # move lands on board
            and 0 <= endCol < bs.numC[endRow]):
          #if empty square
          if not bs.sq[endSq].blocked[pt]:
            if bs.sq[endSq].moveable[pt]:
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue
          #opponent on sq
          elif bs.sq[endSq].pc:
            if bs.sq[endSq].pc.piece[0] == self.notMe:
              if bs.sq[endSq].moveable[pt]:
                moves.append(Move(sq, endSq, board))
                attacked.append(endSq)
                continue
            #player on sq
            elif bs.sq[endSq].pc.piece[0] == self.me:  
              defended.append(Move(sq, endSq, board))
              attacked.append(endSq)
              continue
          #terrain blocking sq
          else:
            if bs.sq[endSq].moveable[pt]:
              moves.append(Move(sq, endSq, board))
              attacked.append(endSq)
      if gen:
        return moves,defended,attacked
      self.moves = moves
      self.defended = defended
      self.attacked = attacked

    '''
    Updates castle bools
    '''
    def updateCastle(self):
      bs = self.bs
      #if king not in correct spot, lose both castle rights
      if (self.row,self.col) != self.kingSpot:
        self.castle = [False, False]
      #if king rook not in correct spot, lose king side castle rights
      if bs.sq[self.kRookSpot].pc:
        if bs.sq[self.kRookSpot].pc.piece != self.me+'R':
          self.castle[0] = False
      else:
        self.castle[0] = False
      #if queen rook not in correct spot, lose queen side castle rights
      if bs.sq[self.qRookSpot].pc:
        if bs.sq[self.qRookSpot].pc.piece != self.me+'R':
          self.castle[1] = False
      else:
        self.castle[1] = False

    '''
    Uses castle bools to add castling moves to moves list.
    '''
    def castleMoves(self):
      castleMoves = []
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = self.board
      pt = self.myTurn
      #ksc
      if self.castle[0]:
        castleRow = self.kingSpot[0]
        for i in range(1,3):
          castleCol = self.kingSpot[1] + i
          cSq = (castleRow,castleCol)
          #if sq on castle path blocked or not moveable don't generate castle move
          if bs.sq[cSq].blocked[pt] or not bs.sq[cSq].moveable[pt]:
            break
        else:
          kendSq = cSq
          rendSq = (kendSq[0], kendSq[1] - 1)
          KSC = Move(sq, kendSq, board, specialMoves=(False, True, False, False))
          km = Move(sq, kendSq, board) 
          rm = Move(self.kRookSpot, rendSq, board)
          KSC.animateList=[km, rm]
          KSC.rookMove = rm
          castleMoves.append(KSC)            
      #qsc
      if self.castle[1]:
        castleRow = self.kingSpot[0]
        for i in range(1,4):
          castleCol = self.kingSpot[1] - i
          cSq = (castleRow,castleCol)
          #if sq on castle path blocked or not moveable don't generate castle move
          if bs.sq[cSq].blocked[pt] or not bs.sq[cSq].moveable[pt]:
            break
        else:
          kendSq = (castleRow, castleCol + 1)
          rendSq = (kendSq[0], kendSq[1] + 1)
          QSC = Move(sq, kendSq, board, specialMoves=(False, True, False, False))
          km = Move(sq, kendSq, board)
          rm = Move(self.qRookSpot, rendSq, board)
          QSC.animateList=[km, rm]
          QSC.rookMove = rm
          castleMoves.append(QSC)
      return castleMoves
          
'''
WARLOCK
The pieces don't move differently for Warlock class.
Super aggro class.  All about time control, playing fast and pressuring.
If in a time scramble, warlocks become unstoppable.
No upgraded pieces, Warlocks rely completely on abilities.
'''
class WarlockPieceState(PieceState):
  pass

'''
ROGUE
Rogue focus on pawn enhancements
Can't make pawns too strong since there are 8 or more of them.
Equal enhancement to a pawn is four to eight times more
effective than similar enhancements to other pieces
'''
class RoguePieceState(PieceState):
  class Pawn(PieceState.BasePiece):
    #creates instance of pawn class on row,col on board
    def __init__(self, sq, piece, gold = True, effects = ()):
      super().__init__(sq, piece, gold = True, effects = ())
      self.rng = 2
      self.canPin = False
      self.magicRow = 6 if self.me == 'w' else 1
      if (5,2) in self.talents:
        self.promoRow = (0,1) if self.me == 'w' else (6,7)
      else:
        self.promoRow = (0) if self.me == 'w' else (7)
      self.ep = False
      
    def getMoves(self, gen = False):
      row = self.row
      col = self.col
      sq = (row,col)
      bs = self.bs
      board = bs.board 
      pt = self.myTurn
      moves = []
      defended = []
      attacked = []
      # print("in pawn moves")
      moveDir = (-1, 0) if self.me == 'w' else (1, 0)
      endRow = row+moveDir[0]
      endSq = (endRow,col)
      if 0 <= endRow < bs.numR:  # move lands on board
        #if pawns can't attack forwards
        if (4,1) not in self.talents:
          # one move forward
          if bs.sq[endSq].moveable[pt] and not bs.sq[endSq].pc: # if no blocking pieces
            moves.append(Move(sq, endSq, board))
            # two moves forward
            # first square not blocked
            if not bs.sa[endSq].blocked[pt]:
              endRow = row + 2*moveDir[0]
              endSq = (endRow,col)
              #if pawns can always move two squares forward or if on start row
              if ((1,1) in self.talents or row == self.magicRow and
                  0 <= endRow < bs.numR and  # move on board
                  bs.sq[endSq].moveable[pt] and
                  not bs.sq[endSq].pc):  # if no blocking pieces
                moves.append(Move(sq, endSq, board))
                #backstab
                if (2,1) in self.talents:
                  capRow = row + moveDir[0]
                  for capCol in [col+1,col-1]:
                    capSq = (capRow,capCol)
                    if (0 <= capCol < bs.numC[capRow]):
                      #if enemy pawn in backstab position
                      if bs.sq[capSq].pc:
                        if bs.sq[capSq].pc.piece == self.notMe + 'P':
                          rMove = Move(sq, endSq, board,
                                       specialMoves=(True, False, False, False),
                                       capSq = capSq)
                          moves.append(rMove)
        #if pawns can attack forwards
        elif (4,1) in self.talents:
          # one move forward
          endRow = row + moveDir[0]
          endSq = (endRow,col)
          if bs.sq[endSq].moveable[pt]:
            attacked.append(endSq)
            if bs.sq[endSq].pc:
              if bs.sq[endSq].pc.piece[0] == self.me:  # if player
                defended.append(Move(sq, endSq, board))
              elif bs.sq[endSq].pc.piece[0] == self.notMe:  # if enemy piece
                moves.append(Move(sq, endSq, board))
            else: #if empty
              moves.append(Move(sq, endSq, board))
            # two moves forward
            # first square moveable and not blocked
            if not bs.sq[endSq].blocked[pt]:
              endRow = row + 2*moveDir[0]
              endSq = (endRow,col)
              if (((1,1) in self.talents or row == self.magicRow)
                  and 0 <= endRow < bs.numR):  # move on board
                if bs.sq[endSq].moveable[pt]: #if can move to square
                  #if pawns can always move two squares forward or if on start row
                  attacked.append(endSq) #always attacked at this point
                  if bs.sq[endSq].pc:
                    if bs.sq[endSq].pc.piece[0] == self.me:  #if player
                      defended.append(Move(sq, endSq, board))
                    else:  # if empty or enemy peice
                      moves.append(Move(sq, endSq, board))
                  #if no piece on sq
                  else:
                    moves.append(Move(sq, endSq, board))
                  #backstab
                  if (2,1) in self.talents:
                    capRow = row + moveDir[0]
                    for capCol in [col+1,col-1]:
                      capSq = (capRow,capCol)
                      if (0 <= capCol < bs.numC[capRow]):
                        #if enemy pawn in backstab position
                        if bs.sq[capSq].pc:
                          if bs.sq[capSq].pc.piece == self.notMe + 'P':
                            rMove = Move(sq, endSq, board,
                                         specialMoves=(True, False, False, False),
                                         capSq = capSq)
                            moves.append(rMove)
        #move sideways near king (no attack)
        if (5,1) in self.talents:
          for (kRow, kCol) in self.bs.kingLoc[pt]:
            endCol = kCol
            #front or back
            for endRow in (kRow + moveDir[0], kRow - moveDir[0]):
              endSq = (endRow,endCol)
              if (0 <= endRow < bs.numR):
                #if empty and moveable square in front/behind king
                if (bs.sq[endSq].moveable[pt] and not bs.sq[endSq].pc):
                  for delCol in (-1,1):
                    #if pawn in correct position to move in front of king
                    if (col + delCol == endCol) and row == endRow:
                      moves.append(Move(sq, endSq, board))
        #capture left
        moveDir = (-1, -1) if self.me == 'w' else (1, -1)
        endRow = row + moveDir[0]
        endCol = col + moveDir[1]
        endSq = (endRow,endCol)
        if 0 <= endRow < bs.numR:  # land on existing row
          if endCol >= 0:  # land on existing col
            attacked.append(endSq)
            if bs.sq[endSq].pc:
              if bs.sq[endSq].pc.piece[0] == self.notMe:  # if opponent piece here
                moves.append(Move(sq, endSq, board))
              elif bs.sq[endSq].pc.piece[0] == self.me:  # if player piece here
                defended.append(Move(sq, endSq, board))
        #capture right
        moveDir = (-1, 1) if self.me == 'w' else (1, 1)
        endRow = row + moveDir[0]
        endCol = col + moveDir[1]
        endSq = (endRow,endCol)
        if 0 <= endRow < bs.numR:  # land on existing row
          if endCol < bs.numC[endRow]:  # land on existing col
            attacked.append(endSq)
            if bs.sq[endSq].pc:
              if bs.sq[endSq].pc.piece[0] == self.notMe:  # if opponent piece here
                moves.append(Move(sq, endSq, board))
              elif bs.sq[endSq].pc.piece[0] == self.me:  # if player piece here
                defended.append(Move(sq, endSq, board))
      # capture en passant
      # can capture to left or right, consider both
      enPassantDir = [(0, -1), (0, 1)]
      for ePDir in enPassantDir:
        ePRow = row + ePDir[0]
        ePCol = col + ePDir[1]
        ePSq = (ePRow,ePCol)
        moveDir = (-1, ePDir[1]) if self.me == 'w' else (1, ePDir[1])
        endRow = row + moveDir[0]
        endCol = col + moveDir[1]
        endSq = (endRow,endCol)
        if 0 <= endRow < bs.numR:  # land on existing row
          if 0 <= endCol < bs.numC[endRow]:  # land on existing col
            # if potential en passant column on board
            if 0 <= ePCol < bs.numC[endRow]:  # land on existing col
              # if there is an enemy pawn in correct position for en passant
              if bs.sq[ePSq].pc:
                if bs.sq[ePSq].pc.piece == self.notMe + 'P':
                  #if that pawn is enpassantable
                  if bs.sq[(ePRow,ePCol)].pc.ep == True:
                    if bs.sq[endSq].moveable[pt]:
                      moves.append(Move(sq, endSq, board,
                                        specialMoves=(True, False, False, False),
                                        capSq = ePSq))

      #convert generated moves to promo moves if any
      for m in moves:
        if m.endRow in self.promoRow:
          sp = m.specialMoves
          m.specialMoves = (sp[0],sp[1],True,sp[3])
          m.pawnPromotion = True
      #same for defending moves
      for d in defended:
        if d.endRow in self.promoRow:
          sp = d.specialMoves
          d.specialMoves = (sp[0],sp[1],True,sp[3])
          d.pawnPromotion = True
          
      if gen:
        return moves,defended,attacked
      else:
        self.moves = moves
        self.defended = defended
        self.attacked = attacked

'''
PALADIN
update Knight moves
'''
class PaladinPieceState(PieceState):
  pass

'''
PRIEST
update bishop moves.
'''
class PriestPieceState(PieceState):
  pass

'''
Marksman
update rook moves
'''
class MarksmanPieceState(PieceState):
  pass

'''
MAGE
update Queen moves.  For pieces with long range 'sniper' attacks, like the Mage,
will be able to click sq to attack piece, then click a legal sq, including start
sq, to end on.
'''
class MagePieceState(PieceState):
  pass

'''
WARRIOR
update King moves.
'''
class WarriorPieceState(PieceState):
  pass
