'''
Module to import to chess engine.  Tracks specific board state info using
the BoardState and SqInfo classes.  BoardState vars are quicked and more efficient
than going through all sqs individually every time a variable is needed.  Basically
BoardState exists to summarize all the square info and perform some useful functions
with this info.  All game state changes operate on the SqInfo classes held in
Board State, then when a turn is ended this info gets updated to the BoardState class
'''
import copy #for deep copy
from time import time #for profiling
import sys
'''
contains all SqInfo for current gs and stores extra summarized info
about full board state used in gs.  Provides quick access to board state info
'''
class BoardState():
  def __init__(self, board, terrain, effects):
    self.idNum = 0
    self.player = 'w'
    self.opp = 'b'
    self.whiteTurn = True
    self.playerTurn = 0
    self.numR = 8
    self.numC = [self.numR] *self.numR
    self.board = board
    self.sq = {}
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        piece = board[row][col]
        self.sq[sq] = SqInfo(sq)
    self.vision = [copy.deepcopy(board),copy.deepcopy(board)]
    self.terrain = copy.deepcopy(terrain)
    self.effects = copy.deepcopy(effects)
    self.gold = [[0]*self.numR for i in range(self.numC[0])]
    #current pieces at start of turn
    self.pieces = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                   'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
    #pieces removed this turn
    self.removed = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                    'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
    #pieces created this turn
    self.created = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                    'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
    self.terrainCount = {'wh':0, 'bl':0}
    self.effectsCount = {'sn':0, 'st':0, 'rt':0, 'im':0, 'cs':0, 'dc':0}
    self.moves = [[],[]] #list of all possible moves of player / opp
    self.defended = [[],[]] #list of all moves that player/ opp defend pieces
    self.attacked = [[],[]] #list of squares that can be attacked by player / opp
    self.pins = [[],[]] #pins by player/opp on opp/player
    self.truePins = [[],[]] #true pins by player/opp on opp/player
    self.checks = [[],[]] #checks by player/opp on opp/player
    self.checkmate = [False, False]
    #link sqs -[terrainType, (row,col)]
    self.link = {}
    #link pieces -[effectType, (row,col)]
    self.pcLink = {}
    self.trueLinks = []
    self.truePcLinks = []
    #lists of all possible terrain and effects types to parse through
    #avoids having to go through logic for ones that will never show up
    #used to be noMove, list of impassable terrain
    self.impass = []
    #list of terrain that blocks
    self.block = []
    #list of moveable squares for white/black (boolean)
    self.moveable = []
    self.moveable.append(copy.deepcopy(board))
    self.moveable.append(copy.deepcopy(board))
    #list of blocked squares for white/black (boolean)
    self.blocked = []
    self.blocked.append(copy.deepcopy(board))
    self.blocked.append(copy.deepcopy(board))
    #location of white/black king
    self.kingLoc=[[],[]]  
    self.findKings()
    self.getAdjacent()

  '''
  prints out info about the full board state
  '''
  def __str__(self):
    print('board')
    for row in self.board:
      print(row)
##    print('blocked')
##    for row in self.blocked[self.playerTurn]:
##      print(row)
##    print('moveable')
##    for row in self.moveable[self.playerTurn]:
##      print(row)
    print('terrain')
    for row in self.terrain:
      print(row)
    print('effects')
    for row in self.effects:
      print(row)
    #print(f'kings: \n {self.kingLoc[0]} {self.kingLoc[1]}')
    return '' #have to return a string...

  '''
  Use the full board state to update the individual squares.
  Only done in boardSetup
  '''
  def updateSqs(self):
    for sq in self.sq.values():
      sq.update(self)
                
  '''
  At the end of each turn, use the individual SqInfo classes to
  update the full board state
  '''
  #Any variables dealing exclusively with mutables (effects, terrain)
  #might not need to be updated at all.  Try to see.
  def update(self, reset = False):
    self.pieces = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                   'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
    if reset:
      self.removed = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                      'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
      self.created = {'wP':0, 'wN':0, 'wB':0, 'wR':0, 'wQ':0, 'wK':0,
                      'bP':0, 'bN':0, 'bB':0, 'bR':0, 'bQ':0, 'bK':0}
    self.link = {}
    self.pcLink = {}
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        self.terrain[row][col] = self.sq[sq].terrain
        for pt in (0,1):
            self.blocked[pt][row][col] = self.sq[sq].blocked[pt]
            self.moveable[pt][row][col] = self.sq[sq].moveable[pt]
        if len(self.sq[sq].link) > 0:
          for link in self.sq[sq].link:
            self.link[(link[0],sq)] = link
            
        if self.sq[sq].pc:
          #opponent pawns have en passant reset at beginning of their turn
          if self.sq[sq].pc.piece == self.opp+'P':
            self.sq[sq].pc.ep = False
          self.board[row][col] = self.sq[sq].pc.piece
          self.pieces[self.sq[sq].pc.piece] += 1
          self.vision[0][row][col] = self.sq[sq].pc.vision[0]
          self.vision[1][row][col] = self.sq[sq].pc.vision[1]
          self.effects[row][col] = self.sq[sq].pc.effects
          self.gold[row][col] = self.sq[sq].pc.gold
          if len(self.sq[sq].pc.link) > 0:
            for link in self.sq[sq].pc.link:
              self.pcLink[(link[0], sq)] = link
        else:
          self.board[row][col] = '--'
          self.vision[0][row][col] = '--'
          self.vision[1][row][col] = '--'
          self.effects[row][col] = []
          self.gold[row][col] = 0
        
    self.findKings()
    for p in [0,1]:
      if len(self.kingLoc[p]) < 1:
        self.checkmate[p] = True
    str(self)

  '''
  Combines two dictionaries and removes duplicate entries.  Duplicates
  become the most recent entry.  Can make this cleaner with items() and *
  '''
  @staticmethod
  def combineDict(dict1, dict2):
    combined = {}
    k1 = list(dict1.keys())
    k2 = list(dict2.keys())
    v1 = list(dict1.values())
    v2 = list(dict2.values())
    k1.extend(k2)
    v1.extend(v2)
    for k,v in zip(k1,v1):
      combined[k] = v
    return combined
  
  '''
  finds shortest distance between two squares
  Doesn't consider complications such as wormholes.
  '''
  @staticmethod
  def distance(sq1, sq2):
    row1 = sq1[0]
    col1 = sq1[1]
    row2 = sq2[0]
    col2 = sq2[1]
    distance = max(abs(row1-row2),abs(col1-col2))
    return distance

  #gets area n squares from sq1. returns list of sqs.
  #board only passed in to get size of board
  def area(self, sq1, n, board):
    area = []
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq2 = (row, col)
        if self.distance(sq1, sq2) <= n:
          area.append(sq2)
    return area

  '''
  Gets all adjacent squares for each SqInfo square.
  '''
  def getAdjacent(self):
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        for delRow in [-1,0,1]:
          adjRow = row+delRow
          if 0 <= adjRow < self.numR:
            for delCol in [-1,0,1]:
              adjCol = col + delCol
              if 0 <= adjCol < self.numC[adjRow]:
                adjSq = (adjRow, adjCol)
                if adjSq != sq:
                  self.sq[sq].adjacent.append(adjSq)

  '''
  Finds where kings are using current board state.
  Allows for multiple kings.  If can get away with
  using self.board, use that instead.
  '''
  def findKings(self):
    self.kingLoc = [[],[]] #reset
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        if self.sq[sq].pc:
          if self.sq[sq].pc.piece=='wK':
            self.kingLoc[0].append((row, col))
          elif self.sq[sq].pc.piece=='bK':
            self.kingLoc[1].append((row, col))

  '''
  Find moveable and blocked squares.  Moveable squares can
  still be sniped through, unlike blocked squares.  blocked
  squares can be moved onto, but not moved past
  '''
  def findMoveable(self):
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        self.sq[sq].moveable[self.playerTurn] = True
        self.sq[sq].blocked[self.playerTurn] = False
        if self.sq[sq].pc != None: #if any piece on square
          self.sq[sq].blocked[self.playerTurn] = True
          if self.sq[sq].pc.piece[0] == self.player:
            self.sq[sq].moveable[self.playerTurn] = False
        #if impassable terrain
        for impass in self.impass:
          ind,i = self.sq[sq].getTerrain(impass)
          if i:
            self.sq[sq].moveable[self.playerTurn] = False
            break
        #if terrain blocks square
        for block in self.block:
          ind,b = self.sq[sq].getTerrain(block)
          if b:
            self.sq[sq].blocked[self.playerTurn] = True
            break

  '''
  Generates all piece moves based on current board state
  '''
  def getMoves(self):
    #always reset these
    pt = self.playerTurn
    self.moves[pt] = [] 
    self.defended[pt] = [] 
    self.attacked[pt] = []
    #find blocked and impassable squares for player
    self.findMoveable()
    #generate and store all possible piece moves
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        if self.sq[sq].pc:
          #reset these
          self.sq[sq].pc.pinned.clear()
          self.sq[sq].pc.defendedBy.clear()
          self.sq[sq].pc.attackedBy.clear()
          self.sq[sq].pc.pinnedBy.clear()
          if self.sq[sq].pc.piece[0] == self.player:
            self.sq[sq].pc.getMoves()
            self.moves[pt].extend(self.sq[sq].pc.moves)
            self.defended[pt].extend(self.sq[sq].pc.defended)
            self.attacked[pt].extend(self.sq[sq].pc.attacked)

  '''
  Go through each square's existing moves,attacked,defended to get
  total moves,attacked,defended for player
  '''
  def sumMoves(self):
    #always reset these
    pt = self.playerTurn
    self.moves[pt] = [] 
    self.defended[pt] = [] 
    self.attacked[pt] = []
    for row in range(self.numR):
      for col in range(self.numC[row]):
        sq = (row,col)
        if self.sq[sq].pc:
          if self.sq[sq].pc.piece[0] == self.player:
            self.moves[pt].extend(self.sq[sq].pc.moves)
            self.defended[pt].extend(self.sq[sq].pc.defended)
            self.attacked[pt].extend(self.sq[sq].pc.attacked)

  '''
  Checks current board for all pins and checks
  from the player against the opponent
  Input: all possible player moves from generateMoves()
  Output: directions and pieces involved for each pin, checks, check blocks
  '''
  def getPinsAndChecks(self):
    pins = []
    truePins = []
    checks = []
    for move in self.defended[self.playerTurn]:
      sq1 = move.startSq
      sq2 = move.capSq
      if self.sq[sq2].pc:
        self.sq[sq2].pc.defendedBy.append(move)
    for move in self.moves[self.playerTurn]:
      sq1 = move.startSq
      sq2 = move.capSq
      #look at all moves attacking opponent pieces
      if (move.pieceCaptured[0] == self.opp):
        #this will also be done already if change above made
        self.sq[move.capSq].pc.attackedBy.append(move)
        #first get checks
        if (move.pieceCaptured[1] == 'K'):
          checks.append(move)
        #now get pins
        if self.sq[sq1].pc.canPin:
          #is there a piece behind the blocking piece in the pin direction
          if self.sq[sq1].pc.rng:
            pinRange = self.sq[sq1].pc.rng - move.rng + 1
          else:
            pinRange = self.numR
          for i in range(1,pinRange):
            endRow = move.endRow + i*move.moveDir[0]
            endCol = move.endCol + i*move.moveDir[1]
            sq = (endRow,endCol)
            if 0 <= endRow < self.numR: #don't go off board
              if 0 <= endCol < self.numC[endRow]:
                #if can't move on sq, break
                if not self.sq[sq].moveable[self.playerTurn]:
                  break
                if self.sq[sq].blocked[self.playerTurn]:
                  #if there is another enemy piece behind the pinned piece
                  if self.sq[sq].pc:
                    if self.sq[sq].pc.piece[0] == self.opp:
                      piece = self.sq[sq].pc.piece[1]
                      pins.append((move, piece))
                      self.sq[sq1].pc.pinned.append(move)
                      self.sq[sq2].pc.pinnedBy.append(move)
                      break #stop looking for pins after one found
                    #friendly piece here
                    else:
                      break
                  else:
                    break
    for pin in pins:
      if pin[1] == 'K':
        truePins.append(pin)
    self.pins[self.playerTurn] = pins
    self.truePins[self.playerTurn] = truePins
    self.checks[self.playerTurn] = checks
    self.extendAttacked() #adds extra attacked squares

  '''
  Correctly prevents enemy king from blocking its own attack, by extending
  attacked squares of long range pieces beyond the current enemy king position
  '''
  def extendAttacked(self):
    for move in self.checks[self.playerTurn]: #player checks on opp
      sq = move.startSq #square checking piece starts on
      if self.sq[sq].pc.canPin:
        #extend attacked sqs past king to end of board (or end of range)
        if self.sq[sq].pc.rng:
          extendRng = self.sq[sq].pc.rng + 1
        else:
          extendRng = self.numR
        for i in range(1, extendRng):
          row = move.endRow + i*move.moveDir[0]
          col = move.endCol + i*move.moveDir[1]
          sq = (row,col)
          #if still on board
          if (0 <= row < self.numR and (0 <= col < self.numC[row])):
            self.attacked[self.playerTurn].append((row, col))
            #if immoveable sq, break
            if not self.sq[sq].moveable[self.playerTurn]:
              break
            #if blocked sq, add to attacked and break
            if self.sq[sq].blocked[self.playerTurn]:
              self.attacked[self.playerTurn].append((row, col))
              break
            self.attacked[self.playerTurn].append((row, col))
          else:
            break #once off board stop extending attacked squares

  '''
  removes illegal moves from current player moves removes moves that
  attack pieces with immunity adds pawn promotion.  In
  future modularize the in check logic.  Right now it is gross to follow.
  '''
  def findLegalMoves(self):
    kings = self.kingLoc[self.playerTurn] #player king location(s)
    playerMoves = self.moves[self.playerTurn] #all possible player moves
    attackedSquares = self.attacked[~self.playerTurn] #squares the enemy attacks
    #at moment don't need this, but might in future
    oppDefended = self.defended[~self.playerTurn] #opp moves defending opp pieces
    checks = self.checks[~self.playerTurn] #opponent checks on player
    doubleCheck = [] #one opp piece attacks multiple kings

    #check if opponent has immunity to capture under special conditions
    #remove moves if condition is satisfied
    '''
    imm = self.immunities(playerMoves)
    for move in imm:
      playerMoves.remove(move)
    '''

    #check if single piece checking multiple kings
    for cM1 in checks[:]:
      for cM2 in checks[:]:
        #different attacked kings
        if cM1.capSq != cM2.capSq:
          #same attacking piece
          if cM1.startSq == cM2.startSq:
            doubleCheck.append(cM1)

    #When two separate kings checked by same piece, only option is to remove piece
    if len(doubleCheck) > 0:
      for possibleMove in copy.deepcopy(playerMoves):
        for chk in doubleCheck:
          if possibleMove.capSq != chk.startSq:
            if possibleMove in playerMoves:
              playerMoves.remove(possibleMove)

    #print('possible moves')
    #for possibleMove in playerMoves[:]:
      #print(possibleMove.chessNotation())
    #make copy of playerMoves
    pM = copy.deepcopy(playerMoves)
    #parse through copy of all of the players possible moves
    for possibleMove in pM:
      #Under no circumstances can you move a king into or through check
      if (possibleMove.pieceMoved[1] == 'K'):
        for sq in attackedSquares:
          if possibleMove.castle:
            #cant castle if starting in check
            consider = possibleMove.path
          else:
            #otherwise don't care if move starts in check
            consider = possibleMove.path[1:]
          if sq in consider: 
            playerMoves.remove(possibleMove)
            break
      
      #Can't move a piece blocking check out of the pin
      for block in self.truePins[~self.playerTurn]:
        blockMove = block[0]
        blockDir = blockMove.moveDir
        blockDir2 = (-blockDir[0], -blockDir[1])
        pieceBlocked = block[1]
        #if the current possibleMove piece is one blocking check
        if possibleMove.startSq == blockMove.endSq:
          #only if move is along or against pin direction, keep move
          if not (possibleMove.moveDir == blockDir or
              possibleMove.moveDir == blockDir2):
            playerMoves.remove(possibleMove)
            break

      #can't enPassant into check
      if possibleMove.enPassant:
        #if player king on same row as enpassant pawns
        for king in kings:
          if king[0] == possibleMove.startRow:
            #+1 or -1, the direction you check across row
            dCol = -(king[1] - possibleMove.startCol)
            dCol = dCol//abs(dCol)
            for i in range(1, self.numR):
              #start searching one column over from captured en passant pawn
              col = possibleMove.endCol + i*dCol
              sq = (king[0],col)
              #if col to search is on board
              if 0 <= col < self.numR:
                #if opponent can't move through sq
                if not self.sq[sq].moveable[~self.playerTurn]:
                  break
                #if sq is blocked to opp
                if self.sq[sq].blocked[~self.playerTurn]:
                  #if opp piece on board
                  if self.sq[sq].pc:
                    if self.sq[sq].pc.piece[0]==self.opp:
                      #if opp piece is long range piece
                      if self.sq[sq].pc.canPin:
                        #generate moves for this piece and store in mo,de,at
                        mo,de,at = self.sq[sq].pc.getMoves(gen = True)
                        #if long range piece is attacking towards king
                        if (king[0], col - dCol) in at:
                          playerMoves.remove(possibleMove)
                          break
                      #if first opp piece is not long range
                      else:
                        break
                    #friendly piece first
                    else:
                      break
                  #terrain blocking, not piece
                  else:
                    break
              #if searched column off board
              else:
                break
                  
      #if in check, have to prevent all checks on all kings simultaneously.
      #checks can be avoided by blocking, removing, or moving king out of the way.
      if self.checks[~self.playerTurn]:
        #flag for checking if all check moves are dealt with
        flag = [0]* len(checks)
        j = -1
        for checkMove in checks:
          #don't filter and remove checked king moves.  
          if checkMove.capSq == possibleMove.startSq:
            flag = [1]*len(checks)
            break
          j+=1
          flag[j] = self.checkPieceRemoved(possibleMove,checkMove)
          #if check piece was not removed, check for blocks
          if flag[j] != 1:
            flag[j] = self.checkPieceBlocked(possibleMove,checkMove)
        #if all flags are raised, then move is legal
        if sum(flag) == len(flag): 
          continue
        else:
          playerMoves.remove(possibleMove)
          continue
  '''
  Helper function for findLegalMoves that raises flag if current move can
  remove checking piece
  '''
  def checkPieceRemoved(self,possibleMove,checkMove):
    sqCheck = [checkMove.startSq]
    #if checking piece has a terrain link add to squares to consider
    for t,sq in self.sq[checkMove.startSq].link:
      #accept attacks to linked square if true link
      if t in self.trueLinks:
        sqCheck.append(sq)
    for e,sq in self.sq[checkMove.startSq].pc.link:
      #accept attacks to linked square if true link
      if e in self.truePcLinks:
        sqCheck.append(sq)
    #scan through sqCheck squares
    for sq in sqCheck:
      #if possibleMove attacks square, flag is raised
      if possibleMove.endSq == sq:
        return 1
    return 0

  '''
  Helper function for findLegalMoves that raises flag if current move can
  block checking piece
  '''
  def checkPieceBlocked(self,possibleMove,checkMove):
    #If checking piece can be blocked
    sq = checkMove.startSq
    if self.sq[sq].pc.canBlock:
      for blocked in possibleMove.blocked:
        #if king is on blocked square, can still be attacked
        if blocked in checkMove.path[:-1]:
          return 1
      #similarly... if checkMove.piece.impassable:
      for impass in possibleMove.impassable:
        if impass in checkMove.path:
          return 1
    return 0

  '''
  Find better way to deal with this?
  send player moves here to see if opponent has any special immunities to them.
  Returns the moves the opponent is immune to so they may be removed in findLegalMoves
  '''
  '''
  def immunities(self, moves):
    immunityMoves = []
    if self.pi[~self.playerTurn].champion == 'Rogue':
      if (1,1) in self.pi[~self.playerTurn].talents:
        for move in moves:
          if move.specialMoves[0] == True:  # if ranged move
            #only ranged pawn moves are en passant or backstab
            if move.pieceMoved[1] == 'P':
              immunityMoves.append(move)
    return immunityMoves
  '''

  '''
  switches turns but does not end turn
  '''
  def switchTurns(self):
    self.whiteTurn = not self.whiteTurn
    self.playerTurn = ~self.playerTurn #careful, -1, 0, -1, 0...etc
    self.player, self.opp= self.opp, self.player

  '''
  swaps two whole squares including pieces
  '''
  def swapSquares(self, sq1, sq2, pcs = True):
    self.sq[sq1], self.sq[sq2] = self.sq[sq2], self.sq[sq1]
    self.movePcLink(sq1,sq2)
    self.movePcLink(sq2,sq1)
    if not pcs:
      self.swapPieces(sq1,sq2)
      
  '''
  swaps two pieces
  '''
  def swapPieces(self, sq1, sq2):
    self.sq[sq1].pc, self.sq[sq2].pc = self.sq[sq2].pc, self.sq[sq1].pc
    self.sq[sq1].pc.place(sq1)
    self.sq[sq2].pc.place(sq2)
    self.movePcLink(sq1,sq2)
    self.movePcLink(sq2,sq1)

  '''
  Runs in makeMove, logic for moving a piece from sq1 to sq2
  '''
  def movePiece(self, sq1, sq2):
    #some moves allow piece to not move at all
    #don't move piece if that is the case
    if sq1 != sq2:
      #if pawn moves 2 or more squares, it is enpassantable
      if self.sq[sq1].pc.piece[1] == 'P':
        if self.distance(sq1,sq2) > 1:
          self.sq[sq1].pc.ep = True
      self.sq[sq2].pc = self.sq[sq1].pc
      self.sq[sq2].pc.place(sq2)
      #linked pieces update pcLinks to moved sq
      self.movePcLink(sq1, sq2)
      #empty square left behind where piece was
      self.sq[sq1].pc = None
      #now that piece has moved, recalculate blocked and moveable for each sq
      #might be overkill, could just check related squares.
      self.findMoveable()

  '''
  When a pcLink moves with piece, need to update all existing links
  to the moved piece to the new square
  '''
  def movePcLink(self, sq1, sq2):
    sqs = []
    #get sqs that moved piece is linked to
    for link in self.sq[sq2].pc.link:
      if link[1] not in sqs:
        sqs.append(link[1])
    for sq in sqs:
      #go through all pcLinks in linked sq
      for i in range(len(self.sq[sq].pc.link)):
        #if link to OLD square, set it to NEW
        link = self.sq[sq].pc.link[i]
        if link[1] == sq1:
          self.sq[sq].pc.link[i] = (link[0], sq2)

  '''
  change to click on UI pop up menu eventually, with images of each piece to promote to.
  no while loop, UI will check in gs.moveLog for a pawnPromotion move, if
  it finds one, it will open a popup that cannot be closed until one of
  the options is clicked.  Time will still tick while popup is open.
  '''
  def pawnPromotion(self, pieceMoved, sq, removePiece, createPiece):
    promoList = ['N','B','R','Q']
    pieceInput = '-'
    #instead of while here, change for UI popup.  Can't click anywher except
    #popup when live.  Need to copy this behaviour so generalize it (no click).
    while pieceInput not in promoList:
      pieceInput = input("Enter N,B,R,Q for a knight, bishop, rook or queen: ")
    #remove pawn
    removePiece(sq, fake = False, erase = True)
    #create new piece
    createPiece(sq, self.player+pieceInput, fake = False, gold = True, effects = ())

'''
Contains all info about each square of the board and if there is
a piece on it, contains that info too.  Each square has its own status object
that is updated each turn after the gamestate changes.
If gameplay slows too much from holding all this info in a log
form, can make log auto remove like 5 turns later.  Hopefully
doesn't affect game speed though.
'''
class SqInfo():
  def __init__(self, sq):
    self.sq = sq
    self.row = sq[0]
    self.col = sq[1]
    self.pc = None
    #What terrain is drawn under piece on board
    self.terrainIm = ''
    self.terrain = []
    self.moveable = [True, True]
    self.blocked = [False, False]
    self.link = []
    self.adjacent = []

  '''
  updates sq with info from board state
  '''
  def update(self, bs):
    #piece vision and gold taken care of by createPiece() in boardSetup()
    #to use bs info for the above would actually undo desirable changes -> not good.
    self.terrain = bs.terrain[self.row][self.col]
    if self.pc:
      self.pc.effects = bs.effects[self.row][self.col]

  '''
  outputs this info into popup box when hovering over the square
  '''
  def __str__(self):
    print(f'sq: {self.sq}')
    if self.pc:
      print(f'piece: {self.pc.piece}')
      print(f'ID: {self.pc.id}')
    return ''

  def getTerrain(self, terrainType):
    if self.terrain:
      for i,t in enumerate(self.terrain):
        if terrainType in t:
          return i,t
    return None,None

  def getEffect(self, effectType):
    if self.pc:
      for i,e in enumerate(self.pc.effects):
        if effectType in e:
          return i,e
    return None,None

  def countDownTerrain(self, terrainType):
    ind,t = self.getTerrain(terrainType)
    if t:
      terrainTurns = int(t[-2:]) - 1
      if terrainTurns <= 0: #when terrain runs out
        del self.terrain[ind]
        self.terrainIm = ''
      else:
        t = t[:-2]+str(terrainTurns).zfill(2)
        self.terrain[ind] = t
        self.terrainIm = t[:-2]
      return terrainTurns
  
  '''
  Generic function simply reduces status by 1 each turn
  and removes if it is 0.  Simply don't add to effects that dont
  have numTurns
  '''
  def countDownEffect(self, effectType):
    ind,e = self.getEffect(effectType)
    if e:
      effectTurns = int(e[-2:]) - 1
      if effectTurns <= 0: #when effect runs out
        del self.pc.effects[ind]
      else:
        e = e[:-2]+str(effectTurns).zfill(2)
        self.pc.effects[ind] = e
      return effectTurns

  '''
  When terrain turns can be added on, use this
  '''
  def addTerrain(self, terrainType, extra, numTurns, sett = False):
    ind,t = self.getTerrain(terrainType)
    if not t:
      if numTurns and int(numTurns) != 0:
        tNew = terrainType+str(extra)+str(numTurns).zfill(2)
        self.terrain.append(tNew)
      else:
        tNew = terrainType+str(extra)
        self.terrain.append(tNew)
    else:
      totalTurns = ''
      if numTurns:
        currTurns = int(t[-2:])
        totalTurns = currTurns + int(numTurns)
        if sett:
          totalTurns = int(numTurns)
        #gets removed at end of turn
        if totalTurns <= 0:
          totalTurns = 1
        totalTurns = str(totalTurns).zfill(2)
      tNew = terrainType + str(extra)+totalTurns
      self.terrain[ind] = tNew
      return tNew[-2:]

  '''
  When effect turns can be added on, use this
  Don't add zeros when effect doesn't have numTurns??
  '''
  def addEffect(self, effectType, extra, numTurns, sett = False):
    ind,e = self.getEffect(effectType)
    if not e:
      if numTurns and int(numTurns) != 0:
        eNew = effectType+str(extra)+str(numTurns).zfill(2)
        self.pc.effects.append(eNew)
      else:
        eNew = effectType+str(extra)
        self.pc.effects.append(eNew)
        
    else:
      totalTurns = ''
      if numTurns:
        print(f'here and {numTurns}')
        currTurns = int(e[-2:])
        totalTurns = currTurns + int(numTurns)
        if sett:
          totalTurns = int(numTurns)
        #gets removed at end of turn
        #if totalTurns <= 0:
          #totalTurns = 1
        totalTurns = str(totalTurns).zfill(2)
      eNew = effectType + str(extra)+totalTurns
      self.pc.effects[ind] = eNew
      return eNew[-2:]
