#Thank you to Eddie Sharick for his extremely helpful chess youtube series
#which provided this project a strong foundation to build off of

import BoardLogic as bl
import PieceLogic as pl
import AbilityLogic as al
import TerrainLogic as tl
import pygame as pg
import Player as player 
import copy #for deep copying for boardstate
from time import time #for profiling

'''
Keeps track of the general game state
'''
class GameState:
  def __init__(self):
    self.bs = None
    self.bsLog = [] #keeps track of full board state for each turn
    #implement!: only keeps up to last 4 turns before cutting
    #normally would have a server to dump info to so don't have to store
    #list of player legal moves
    self.legalMoves = []
    #w,b fix rest of program to follow suit here
    self.legalMovesLog = [[],[]]
    #tracks moves made throughout game
    self.moveLog = []
    #names of moves to give to the UI movelog
    self.moveNames = []
    self.stalemate = False
    #agreement, 50 move rule, three-fold repition, insufficient material
    self.draw = [False]*4
    self.gameOver = False
    self.gameOverText = ''
    #(wmin, wsec, wInc),(bmin, bsec, bInc)
    self.timeControl = [(5,0,0),(5,0,0)]
    #one clock class for each player
    self.clock = [Clock(self.timeControl[0]),Clock(self.timeControl[1])]
    self.pieceDict = {'Warlock': pl.WarlockPieceState,
                     'Rogue': pl.RoguePieceState,
                     'Paladin': pl.PaladinPieceState,
                     'Priest': pl.PriestPieceState,
                     'Marksman': pl.MarksmanPieceState,
                     'Mage': pl.MagePieceState,
                     'Warrior': pl.WarriorPieceState}
    self.abilityDict = {'Warlock': al.WarlockAbilityLogic,
                        'Rogue': al.RogueAbilityLogic,
                        'Paladin': al.PaladinAbilityLogic,
                        'Priest': al.PriestAbilityLogic,
                        'Marksman': al.MarksmanAbilityLogic,
                        'Mage': al.MageAbilityLogic,
                        'Warrior': al.WarriorAbilityLogic}
    self.terrainDict = {'Warlock': tl.WarlockTerrainLogic,
                        'Rogue': tl.RogueTerrainLogic,
                        'Paladin': tl.PaladinTerrainLogic,
                        'Priest': tl.PriestTerrainLogic,
                        'Marksman': tl.MarksmanTerrainLogic,
                        'Mage': tl.MageTerrainLogic,
                        'Warrior': tl.WarriorTerrainLogic}
    # create this attribute before self.logic.  PieceLogic uses this
    self.pi = [player.PlayerState(), player.PlayerState()]
    # Need to update PlayerInfo class with champion and talent info
    '''
    self.pi[0].updateInfo('Rogue',[(1,1),(1,2),(2,1),
                                            (3,1),(3,2),(4,1),(4,2),
                                            (5,1),(5,2)], 'w')
    '''

    self.pi[0].updateInfo('Warlock',[(1,1),(1,2),(2,1),(2,2),
                                     (3,1,0),(4,1),(4,2),
                                     (5,1),(5,2)], 'w')

    self.pi[1].updateInfo('Warlock',[(1,1),(1,2),(2,1),(2,2),
                                     (3,1,0),(4,1),(4,2),
                                     (5,1),(5,2)], 'b')
    #if pi contains ref to gs, can it modify gs vars there?
    #so in updateInfo, add gs.whiteChampion = ...
    self.whiteChampion = self.pi[0].champion
    self.blackChampion = self.pi[1].champion
    self.ps = [None,None]
    self.abilities = [None,None]
    self.validSqs = []
    #keeps track of if ability was used
    self.powerUsed = False
    self.enhanceName = '' #name of enhancement used. Enhancements allow move after
    #lists of talents each player currently has access to by type
    self.starterAutos = [[],[]]
    self.starterEnhancements = [[],[]]
    self.enhancements = [[],[]]
    self.powers = [[],[]]
    self.autos = [[],[]]
    self.passives = [[],[]]
    self.starterAutosFunc = [[],[]]
    self.starterAutosArgs = [[],[]]
    self.starterEnhancementsFunc = [[],[]]
    self.starterEnhancementsArgs = [[],[]]
    self.autosFunc = [[],[]]
    self.autosArgs = [[],[]]
    self.chargeLog = [[],[]]
    self.boardSetup()

  '''
  updates initial board state based on champion talents and abilities
  '''
  def boardSetup(self):
    #Create initial board, terrain, and effects states

    board =    [["bR", "--", "--", "--", "bK", "bB", "bN", "bR"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["wR", "wN", "wB", "wQ", "wK", "--", "--", "wR"]]
    '''
    board =    [["--", "--", "--", "--", "bK", "--", "--", "--"],
                ["--", "--", "--", "bB", "--", "bN", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "wB", "--", "wN", "--", "--"],
                ["--", "--", "--", "--", "wK", "--", "--", "--"]]
    '''
    terrain =  [[[] for i in range(len(board))] for j in range(len(board))]
    effects =  [[[] for i in range(len(board))] for j in range(len(board))]
    #create base BoardState class
    self.bs = bl.BoardState(board,terrain,effects)
    self.ps = [self.pieceDict[self.whiteChampion](self),
                       self.pieceDict[self.blackChampion](self)]
    #create pieces on board.  This overrides effects, so do before changing effects
    for row in range(self.bs.numR):
      for col in range(self.bs.numC[row]):
        sq = (row,col)
        piece = self.bs.board[row][col]
        if piece != '--':
          pt = 0 if piece[0] == 'w' else 1
          self.createPiece(sq, piece, fake = True)
    #update each sq info with correct bs as given above
    self.bs.updateSqs()
    #update each class with updated bs
    self.abilities = [self.abilityDict[self.whiteChampion](self, 'w'),
                      self.abilityDict[self.blackChampion](self, 'b')]
    self.tes = tl.TerrainLogic(self, self.terrainDict[self.whiteChampion](self, 'w'),
                          self.terrainDict[self.blackChampion](self, 'b'))
    self.pi[0].tree.abilities = self.abilities[0]
    self.pi[1].tree.abilities = self.abilities[1]
    #this completes initialization of talent tree, ideally baked in, change later
    self.pi[0].tree.treeInfo()
    self.pi[1].tree.treeInfo()
    
    #for each player
    for p in [0,1]:
      champ = self.pi[p].champion
      talents = self.pi[p].talents
      player = self.pi[p].me
      charges = list(self.abilities[p].charges.values())
      #can we give getAbility list reference to gs (self) and add these
      #lines in directly in that function?
      #SHOULD I MAKE ABILITY LOGIC BEHAVE LIKE OTHER LOGIC MODULES
      #->MAKE AN ATTACH AN ABILITY STATE OBJECT TO GS WITH THE REQUIRED INFO
      #FOR EACH PLAYER AND CHAMPION INVOLVED... YES WHY NOT
      l1,l2,l3,l4,l5,l6 = self.pi[p].tree.getAbilityLists()
      self.starterAutos[p] = l1
      self.starterEnhancements[p] = l2
      self.enhancements[p] = l3
      self.powers[p] = l4
      self.autos[p] = l5
      self.passives[p] = l6
      self.chargeLog[p].append(charges)
      #go through all of each players talents
      for talent in talents:
        pureTalent = (talent[0], talent[1])
        #get starters and auto abilities for player based on auto talents they have
        if pureTalent in self.starterAutos[p]:
          self.starterAutosFunc[p].append(self.pi[p].tree.getAb[pureTalent])
          self.starterAutosArgs[p].append(None)
        elif pureTalent in self.starterEnhancements[p]:
          self.starterEnhancementsFunc[p].append(self.pi[p].tree.getAb[pureTalent])
          self.starterEnhancementsArgs[p].append(None)
        elif pureTalent in self.autos[p]:
          self.autosFunc[p].append(self.pi[p].tree.getAb[pureTalent])
          self.autosArgs[p].append(None)

    #Auto starters
    for p in [0,1]:
      self.runStarterAutos(p)
    self.bs.update()
    self.bsLog.append(copy.deepcopy(self.bs))

  '''
  Inserts substring into existing string
  '''
  @staticmethod
  def strInsert(string,sub,ind1,ind2):
    string = string[:ind1] + sub + string[ind2:]
    return string
    
  '''
  For debugging purposes, print out useful info
  '''
  def debug(self):
    print('xxxxxx')

  def getMoves(self):
    #get player piece moves
    self.bs.getMoves()
    #get player power and enhancement moves
    #self.abs.getMoves()
    
  '''
  get all legal moves for current board state.
  '''
  def getLegalMoves(self):
    #generate all possible moves with minimal filters
    self.getMoves() #player moves
    #get player terrain and effects moves
    self.tes.alterMoves()
    #after terrain filters moves,attacks etc by square
    self.bs.sumMoves()
    self.bs.getPinsAndChecks() #player checks and pins on opp
    #endTurn to go to opp turn with updated board state
    #will probably have to make a special end turn for this case
    #self.bs.endTurn(specialCond)
    self.bs.switchTurns()
    self.getMoves() #opp moves
    #get player terrain and effects moves
    self.tes.alterMoves()
    self.bs.getPinsAndChecks() #opp checks and pins on player
    self.bs.sumMoves()
    #filter and store opponent legal moves
    self.bs.findLegalMoves()
    self.legalMovesLog[self.bs.playerTurn].append(self.bs.moves[self.bs.playerTurn])
    #switch back, undo terrain and effects from endTurn,
    #need to make sure moves are kept though so player findLegalMoves has them
    #self.undoMove(specialCond)
    self.bs.switchTurns()
    #filter and store player legal moves
    self.bs.findLegalMoves() #removes player illegal moves
    self.legalMovesLog[self.bs.playerTurn].append(self.bs.moves[self.bs.playerTurn])
    self.legalMoves = self.bs.moves[self.bs.playerTurn]#stores current player legal moves

  '''
  makes a move using the input move class data, updates GameState board.
  '''
  def makeMove(self, move, stealth = False):
    board = self.bs.board  # current board position
    sq1 = move.startSq
    sq2 = move.endSq
    sq3 = move.capSq
    pieceMoved = move.pieceMoved 
    pieceCaptured = move.pieceCaptured
    # captured piece logic
    if pieceCaptured != '--':
      self.removePiece(sq3)
    # piece moves to new square logic
    self.bs.movePiece(sq1, sq2)
    if move.pawnPromotion:
      self.bs.pawnPromotion(pieceMoved, sq2, self.removePiece, self.createPiece)
    '''Extra stuff to check for, enhancements, adding terrain etc'''
    self.tes.alterMove(move)
    #always good to do this after any move made
    self.bs.findMoveable()
    #NOT effect stealth, changes whether move is added to movelog
    if not stealth:
      self.moveLog.append(move)

  '''
  If enhancement ADD these as extra properties to existing Move/pass in to future Move
  somehow.
  If power, create a Move class with power flag raised and adjust the appropriate
  variables.  Power variables are attached to move but only used when power is True
  '''
  def usePower(self, startSq, endSq, pieceMoved,
                pieceCaptured, powerName, stealth = False):
    #if no attacking piece involved, input startSq as (-1,-1)
    #if no piece capture involved, input endSq as (-1,-1)
    #if no attacking piece, pieceMoved = '--'
    #if no pieceCaptured, pieceCaptured = '--'
    special = (False, False, False, True)
    #create special move signaling ability used
    #eventually can pass name of ability?
    powerMove = pl.Move(startSq,endSq, self.bs.board,
                         specialMoves = special)
    powerMove.pieceMoved = pieceMoved
    powerMove.pieceCaptured = pieceCaptured
    #ADD CAPROW CAPCOL CAPSQ TO POWER MOVES
    powerMove.enhanceName = powerName
    #move made logic
    startRow = powerMove.startRow
    startCol = powerMove.startCol
    endRow = powerMove.endRow
    endCol = powerMove.endCol
    endSq = (powerMove.endRow,powerMove.endCol)
    #if piece captured by power move
    if powerMove.pieceCaptured != '--':
      self.removePiece(endSq)
    if not stealth:
      self.moveLog.append(powerMove) # keep track of movesmade
    self.powerUsed = True

  #Deals with playerstate for gold cap. fake doesn't count captures
  #erase does link logic for removed piece
  def removePiece(self, sq, fake = False, erase = True):
    #if piece exists, try to remove it
    if self.bs.sq[sq].pc:
      piece = self.bs.sq[sq].pc.piece
      #terrain and effect link remove piece logic     
      if erase:
        #if piece being removed has true terrain link, remove partner too
        if len(self.bs.sq[sq].link) > 1:
          for terrainType in self.bs.trueLinks:
            for link in reversed(self.bs.sq[sq].link):
              if link[0] == terrainType:
                #erase = False prevents infinite calling
                self.removePiece(link[1], fake = True, erase = False)
        #if piece being removed has true effect link, remove partner too
        if len(self.bs.sq[sq].pc.link) > 1:
          for effectType in self.bs.truePcLinks:
            for link in reversed(self.bs.sq[sq].pc.link):
              if link[0] == effectType:
                #so far all link removals are fake and do not double count
                #may change in future...
                #del link first to prevent infinite looping from links
                cLink = link
                #remove link to linked piece
                del self.bs.sq[sq].pc.link[link]
                #remove linked piece
                self.removePiece(cLink[1], fake = True)
            #delete link to removed piece
            del self.bs.sq[link[1]].pc.link[(link[0],sq)]
            #delete link from removed piece
            del self.bs.sq[sq].pc.link[link]
      #should count as a true removal
      if not fake:
        self.bs.removed[piece] += 1
        if self.bs.sq[sq].pc.gold == 1:
          if piece[0] == 'w':
            self.pi[1].goldCap.append(piece[1])
          elif piece[0] == 'b':
            self.pi[0].goldCap.append(piece[1])
      #remove piece
      self.bs.sq[sq].pc = None

  def createPiece(self, sq, piece, fake = False, gold = True, effects = ()):
    pt = 0 if piece[0] == 'w' else 1
    #might need list(effects)
    self.bs.sq[sq].pc = self.ps[pt].pieceDict[piece[1]](
    sq, piece, gold = gold, effects = effects)
    if not fake:
      self.bs.created[piece] += 1
    
  '''
  Copies piece and all properties from sq1 to sq2.  Leaves original piece unaltered
  '''
  def copyPiece(self, sq1, sq2):
    self.bs.sq[sq2].pc = copy.deepcopy(self.bs.sq[sq1].pc)
    self.bs.sq[sq2].pc.place(sq2)
    
  '''
  Undoes moves using gamestate info stored in various logs
  '''
  def undoMove(self, undoTime = True):
    # reset game over conditions
    self.draw = [False] * len(self.draw)  
    self.stalemate = False  
    self.gameOver = False
    self.bsLog.pop()
    self.bs = copy.deepcopy(self.bsLog[-1])
    #clear last turn info from logs
    self.moveLog.pop()
    self.moveNames.pop()
    self.legalMovesLog[0].pop()
    self.legalMovesLog[1].pop() 
    self.chargeLog[0].pop() 
    self.chargeLog[1].pop() 
    #get past and set current gs variables using logs
    self.legalMoves = self.legalMovesLog[self.bs.playerTurn][-1]
    #reset charges dictionary for each player
    for p in [0,1]:
      values = list(self.chargeLog[p][-1])
      for key,value in self.abilities[p].charges.items():
        self.abilities[p].charges[key] = value
    # change clocks back to what they were at beginning of previous move
    if undoTime:
      self.clock[0].undoTime(self.bs.playerTurn == 0)
      self.clock[1].undoTime(self.bs.playerTurn != 0)
    self.endTurn(undo=True)

  '''
  update PieceLogic classes with current gamestate (importantly gs.board)
  '''
  def endTurn(self, undo = False):
    start = time()
    self.enhanceName = '' #reset
    for p in [0,1]:
      self.runAutos(p)
    self.bs.update(reset = True)
    if not undo:
      self.bs.switchTurns()
      self.tes.nextTurn()
      for p in [0,1]:
        charge = list(self.abilities[p].charges.values())
        self.chargeLog[p].append(charge)
        #do I need this???  Can't ref to gs.bs one time be enough,
        #just like it is enough for pieceState?  Test refs with id()
        self.abilities[p].update(self)
      start2 = time()
      self.bsLog.append(copy.deepcopy(self.bs))
      end2 = time()
      print(f'copying took {end2 - start2} seconds')
      #only keep up to 4 bs in bsLog
      if len(self.bsLog) > 4:
        del self.bsLog[0]
      self.getLegalMoves()
      # check for end game conditions and end game
      self.gameOverCheck()
      # modify last move to know if it was checkmate
      # might have to switch
      if self.bs.checks[~self.bs.playerTurn]:
        self.moveLog[-1].check = True
      if self.bs.checkmate[self.bs.playerTurn]:
        self.moveLog[-1].checkmate = True
      self.moveNames.append(
      self.moveLog[-1].chessNotation(legalMoves = self.legalMovesLog[~self.bs.playerTurn][-2]))
      end = time()
      print(f'full EndTurn took {end - start} seconds')

  '''
  Runs player starter auto abilities in board setup
  '''
  def runStarterAutos(self, pLogic):
    for starter, args in zip(self.starterAutosFunc[pLogic], self.starterAutosArgs[pLogic]):
      if args == None:
        result = starter()
      else:
        result = starter(*args)
      return result
    
  '''
  Runs player starter enhancement abilities in main game loop.  Each player
  should only have one starter enhancement to keep game and code simplified.
  '''
  def runStarterEnhancements(self, pLogic):
    for starter, args in zip(self.starterEnhancementsFunc[pLogic],
                             self.starterEnhancementsArgs[pLogic]):
      if args == None:
        result = starter()
      else:
        result = starter(*args)
      return result

  '''
  Runs player auto abilities (if any) in endTurn
  '''
  def runAutos(self, pLogic):
    for auto, args in zip(self.autosFunc[pLogic], self.autosArgs[pLogic]):
      if args == None:
        auto()
      else:
        auto(*args)

  '''
  checks if game is over and gives proper end game message to write
  to gameOverScreen in UI
  '''
  def gameOverCheck(self, noTime = [False,False], resigns = [False,False]):
    #gameOver = True stops game and triggers gameOverScreen popup
    if noTime[0]:
      self.gameOverText = "Black wins on time"
      self.gameOver = True
    elif noTime[1]:
      self.gameOverText = "White wins on time"
      self.gameOver = True
    self.drawCheck()
    # check for stalemate and checkmate
    if len(self.legalMoves) == 0:
      if self.bs.checks[~self.bs.playerTurn]:
        self.bs.checkmate[self.bs.playerTurn] = True
      else:
        self.stalemate = True
    if self.stalemate:
      self.gameOverText = "Stalemate"
      self.gameOver = True
    elif self.bs.checkmate[0]:
      self.gameOverText = "Checkmate, black wins"
      self.gameOver = True
    elif self.bs.checkmate[1]:
      self.gameOverText = "Checkmate, white wins"
      self.gameOver = True
    elif resigns[0]:
      self.gameOverText = "White resigns, black wins"
      self.gameOver = True
    elif resigns[1]:
      self.gameOverText = "Black resigns, white wins"
      self.gameOver = True
    # if at least one draw condition is true
    elif self.draw != [False] * len(self.draw):
      self.gameOver = True
      if self.draw[0] == True:
        self.gameOverText = "Draw by agreement"
      elif self.draw[1] == True:
        self.gameOverText = "Draw by 50 move rule"
      elif self.draw[2] == True:
        self.gameOverText = "Draw by three-fold repition"
      elif self.draw[3] == True:
        self.gameOverText = "Draw by insufficient material"

  '''checks for draws.  Changes gs.draw directly when run.
  in future can have dedicated variable for counting moves made
  without pawn moves or captures and if it reaches 100 (50 full moves)
  then a draw is reached.
  '''
  def drawCheck(self):
    # 50 moves no captures or pawn moves
    if len(self.moveLog) >= 100:  # 50 'moves' is 100 individual player turns
      chk = 0
      for move in self.moveLog[-100:-1]:  # check last 50 full moves
        if move.pieceMoved[1] == 'P' or move.pieceCaptured != '--':
          chk += 1
      if chk == 0:
        self.draw[1] = True

    '''
    three-fold repition
    if same board state reached 2 times, draw.
    Officially, the moves do not need to be consecutive but it is
    most commonly the case.  This function does not require
    consecutive moves.
    Lastly board state defined by both the player and
    opponents available legal moves, and current turn
    '''
    legalMovesLog = self.legalMovesLog[self.bs.playerTurn]
    oppLegalMovesLog = self.legalMovesLog[~self.bs.playerTurn]
    #min number of half gamestates for 3-fold repition to occur
    #(the initial board state with no moves counts as 1)
    if len(legalMovesLog) >= 7:
      #create boardstate consisting of both players' legal moves
      state=[] #remake state each time
      for i in range(len(legalMovesLog)):
        #assumes turns alternate
        if i%2 == 0:
          player = 'w'
        else:
          player = 'b'
        state.append((legalMovesLog[i],oppLegalMovesLog[i],player))
      #count number of times each state appears
      for i in range(2, len(state)):
        k = 0
        for j in range(3+i, len(state)):
          if (state[i-2] == state[j-2]
              and state[i-1] == state[j-1]
              and state[i] == state[j]):
            k+=1
            if k>= 1:
              self.draw[2] = True
    '''
    Insufficient material
    Implemented for most basic logic.  Did not change considering complications.
    When no mate is POSSIBLE (so even when players blunder, there is no mate)
    then we have insufficient material.  The cases are: if BOTH players has
    any one of the three combos below, then insufficient material
    lone K
    K and bishop
    K and knight
    special case: if lone king vs king and two knights, also a draw
    '''
    has = [[],[]]
    cond = [False,False]
    #get white and black pieces left
    for k,v in self.bs.pieces.items():
      if v > 0:
        if k[0] == 'w':
          has[0].extend(k[1]*v)
        elif k[0] == 'b':
          has[1].extend(k[1]*v)
    #check insufficient materials conditions
    for i,h in enumerate(has):
      if len(h) == 1 and 'K' in h:
        cond[i] = True
        #check special case of lone king versus king and two knights
        if len(has[~i]) == 3:
          if has[~i].count('K') == 1 and has[~i].count('N') == 2:
            cond[~i] = True
      elif len(h) == 2:
        if h.count('K') == 1 and h.count('B') == 1:
          cond[i] = True
        elif h.count('K') == 1 and h.count('N') == 1:
          cond[i] = True
    if cond == [True,True]:
      self.draw[3] = True
    
'''
Clock class keeps track of time between moves for a player
and counts down from a set amount of time.  returns time
as a string in format m : ss
'''
class Clock():
  def __init__(self, timeControl):
    self.timeControl = timeControl
    self.timeRemaining = self.timeControl[0]*60 + self.timeControl[1]
    self.moveTimes = [] #actual time taken for last move
    self.timeLog = [self.timeRemaining]  # time remaining when player makes a move
    self.lastCall = pg.time.get_ticks()
    self.lastMove = pg.time.get_ticks() #in game time when player made last move
    self.lastMoveStart = pg.time.get_ticks() #time when turn began
    self.scale = 1  # scale can be modified by warlock class
    self.pause = True #start paused, then unpause after loading successfully

  '''
  Updates with info after each turn is made
  '''
  def update(self, turn):
    #switch clocks
    self.pause = not self.pause
    #if it was your turn
    if turn:
      self.increment()
      self.lastMove = pg.time.get_ticks()
      moveTime = (self.lastMove - self.lastMoveStart)/1000
      self.moveTimes.append(moveTime)
      self.timeLog.append(self.timeRemaining)

  def undoTime(self, turn):
    #switch clocks
    self.pause = not self.pause
    if len(self.timeLog) > 1:
      if turn:
        self.timeRemaining = self.timeLog[-1]
        self.timeLog.pop()
        self.moveTimes.pop()
        self.lastMoveStart = pg.time.get_ticks()
      else:
        self.timeRemaining = self.timeLog[-1]
        #take away increment from last move
        self.decrement()
    
  def tick(self):
    if self.pause:
      dt = 0
      self.lastCall = pg.time.get_ticks()
    else:
      currTime = pg.time.get_ticks()
      dt = currTime - self.lastCall
      self.lastCall = currTime
    timePassed = dt * self.scale/1000 # in seconds, scaled
    # time left in seconds
    self.timeRemaining -= timePassed
    return self.timeRemaining

  def increment(self):
    self.timeRemaining += self.timeControl[2]

  def decrement(self):
    self.timeRemaining -= self.timeControl[2]
    
  def setTime(self, m ,s):
    self.timeRemaining = m*60 + s

  def __str__(self):
    # convert timeRemaining into desired format
    minutes = int(self.timeRemaining) // 60
    seconds = int(self.timeRemaining) % 60
    if seconds >= 10:
      time = str(minutes) + " : " + str(seconds)
    elif seconds < 10:
      time = str(minutes) + " : 0" + str(seconds)
    if minutes <= 0 and seconds <= 0:
      time = "0 :00"
    return time

  "similar to __str__ but takes a time in seconds as input"
  @staticmethod
  def timeStr(time):
  # convert time into desired format
    minutes = int(time // 60)
    seconds = time % 60
    seconds = int(seconds) #make integer
    if minutes > 0:
      if seconds >= 10:
        timeStr = str(minutes) + " : " + str(seconds)
      elif seconds < 10:
        timeStr = str(minutes) + " : 0" + str(seconds)
    elif minutes == 0:
      timeStr = str(seconds)
    return timeStr
