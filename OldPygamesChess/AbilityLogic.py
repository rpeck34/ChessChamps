'''
Deals with all the ability logic and functions for each champion
'''
import pygame as pg
from time import sleep
'''
Base class
'''
class AbilityLogic():
  def __init__(self, gs, me):
    #player and opp change with the turns, but me permanently
    #identifies which player, white or black, these abilities are for
    #similarly, notMe will always be the colour of the player without
    #the current abilities
    self.me = me
    self.notMe = 'w' if self.me == 'b' else 'b'
    self.myTurn = 0 if self.me == 'w' else 1
    self.gs = gs
    self.bs = gs.bs
    self.talents = gs.pi[self.myTurn].talents
    self.board = self.bs.board
    self.whiteTurn = self.bs.whiteTurn
    self.player = self.bs.player
    self.opp = self.bs.opp
    self.playerTurn = self.bs.playerTurn
    self.charges = {} #each class will have different number of charges for
    #each ability.  set -1 for abilities that don't have charges
    #bs sets dimensions of board and is given to gui
    #pixelSize is set by gui and is given to ability
    self.SIZE = None  # pixel dimensions of game screen
    self.SQ_SIZE = None #pixel dimension of chess squares

  def getSize(self, gui):
    self.SIZE = gui.SIZE  # pixel dimensions of game screen
    self.SQ_SIZE = gui.SQ_SIZE #pixel dimension of chess squares
    
  def update(self, gs):
    self.gs = gs
    self.bs = gs.bs
    self.board = self.bs.board
    self.whiteTurn = gs.bs.whiteTurn
    self.player = gs.bs.player
    self.opp = gs.bs.opp
    self.playerTurn = gs.bs.playerTurn

  '''
  gets valid squares for abilities
  *args are different filters to apply to each square
  args have form (function, (arguments)).  sq (row,col) is
  always first argument in filter functions.
  '''
  def getValidSqs(self, *args):
    for row in range(self.bs.numR):
      for col in range(self.bs.numC[row]):
        sq = (row,col)
        for f,arg in args:
          if arg:
            if not f(sq, arg):
              break
          else:
            if not f(sq):
              break
        #if passed all filters (no break)
        else:
          self.gs.validSqs.append((row,col))

  '''
  Some generally useful filters.  These must return bool.
  Effect filter checks if effect on sq
  '''
  def effectF(self, sq, effectType):
    if not self.bs.sq[sq].pc:
      return False
    else:
      if self.bs.sq[sq].pc.vision[self.myTurn] != '--':
        i,e = self.bs.sq[sq].getEffect(effectType)
        if e:
          return True
    return False

  def effectFN(self, sq, effectType):
    if not self.bs.sq[sq].pc:
      return False
    else:
      if self.bs.sq[sq].pc.vision[self.myTurn] != '--':
        i,e = self.bs.sq[sq].getEffect(effectType)
        if not e:
          return True
    return False

  '''
  Terrain filter checks if terrain on sq
  '''
  def terrainF(self, sq, terrainType):
    i,t = self.bs.sq[sq].getTerrain(terrainType)
    if t:
      return True
    return False

  def terrainFN(self, sq, terrainType):
    i,t = self.bs.sq[sq].getTerrain(terrainType)
    if not t:
      return True
    return False

  def enemyF(self, sq):
    if self.bs.sq[sq].pc:
      if self.bs.sq[sq].pc.vision[self.myTurn][0] == self.notMe:
        self.gs.validSqs.append(sq)

  def allyF(self, sq):
    if self.bs.sq[sq].pc:
      if self.bs.sq[sq].pc.vision[self.myTurn][0] == self.me:
        self.gs.validSqs.append(sq)
      
  '''
  Checks if piece on square matches list of accepted pieces
  '''
  def pieceF(self, sq, pieces):
    if not self.bs.sq[sq].pc:
      return False
    else:
      if self.bs.sq[sq].pc.vision[self.myTurn] in pieces:
        return True
    return False
  
  '''
  Gets next clicked square.  If click occurs, perform action
  Similar to getValidSqs, getClicked args have form (function, (args))
  '''
  def getClicked(self, *args, end = True):
    clicked = pg.mouse.get_pressed()
    if clicked[2]: #right click performs action
      #space out mouse clicks
      sleep(0.1)
      pos = pg.mouse.get_pos()
      col = pos[0]//self.SQ_SIZE
      row = pos[1]//self.SQ_SIZE
      sq = (row,col)
      if sq in self.gs.validSqs:
        for action,arg in args:
          if arg:
            action(sq, *arg)
          else:
            action(sq)
        if end:
          self.exitAbility()
          return False
      #not valid sq to use ability
      else:
        self.exitAbility()
        return False
    return True
  
  def exitAbility(self):
    self.gs.validSqs.clear()

'''
WARLOCK
'''
class WarlockAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.charges = {self.a1:1, self.a2:3, self.a3:4,
                    self.a4:-1, self.a8:1}
    self.numW = 0
    self.clock = gs.clock
    self.scale = 1
    self.wither = 1
    for x in range(1,4):
      if (3,1,x) in self.talents:
        self.wither = x + 1
  '''
  wormhole charges depends on number of wormholes, updated at endturn in gs
  '''
  def update(self, gs):
    super().update(gs)
    self.numW = gs.bs.terrainCount['wh']//2 #number of PAIRS of wormholes
    self.charges[self.a2] = 3 - self.numW
    
  '''
  Reverts time back two boardstates
  '''
  def a1(self):
    if self.charges[self.a1] > 0:
      if len(self.gs.bsLog) > 2:
        self.clock[self.myTurn].timeRemaining /= 2
        self.gs.undoMove(undoTime = False)
        self.gs.undoMove(undoTime = False)
        self.charges[self.a1] -= 1
    return False

  '''
  Wormhole generator.  Charges = 3 - num wormhole pairs
  '''
  def a2(self):
    if self.charges[self.a2] > 0:
      if not self.gs.validSqs:
        self.getValidSqs((self.canPlaceWormhole,()))
      return self.getClicked((self.whEnhance,()))
    else:
      return False #no charges

  '''
  Wormholes are placed on certain friendly pieces after they move
  if move allows them to place wormhole
  '''
  def canPlaceWormhole(self,sq):
    ind,t = self.bs.sq[sq].getTerrain('wh')
    if not t:
      if self.bs.sq[sq].pc:
        pieces = (self.me+'P',self.me+'N',self.me+'B',self.me+'R',self.me+'Q')
        if self.bs.sq[sq].pc.piece in pieces:
         return True
    return False

  '''
  Gives selected piece 'wh' effect, which makes its next move drop a wormhole
  where it started and where it ended, if possible
  '''
  def whEnhance(self,sq):
    self.gs.tes.applyEffect(self.bs.sq[sq], self.myTurn, 'wh'+str(self.numW+1))
    self.clock[self.myTurn].timeRemaining /= 2 #spend time
    self.gs.enhanceName = 'wh'
    self.exitAbility()
    
  def a3(self):
    if self.charges[self.a3]:
      if not self.gs.validSqs:
        oppPieces = (self.notMe+'P',self.notMe+'B',self.notMe+'N',self.notMe+'R')
        self.getValidSqs((self.effectFN, ('rt')), (self.pieceF, (oppPieces)))
      return self.getClicked((self.applyRT,())) 
    else:
      return False #no charges

  def applyRT(self, sq):
    self.gs.tes.applyEffect(self.bs.sq[sq], self.myTurn, 'rt')
    self.clock[self.myTurn].timeRemaining /= 2
    self.gs.usePower((-1,-1), (-1,-1), '--','--', 'ROT')
    self.charges[self.a3] -= 1

  def a4(self):
    if self.clock[self.myTurn].timeRemaining > 60:
      if not self.gs.validSqs:
        #check if enemy piece already consumed
        for row in range(self.bs.numR):
          for col in range(self.bs.numC[row]):
            sq = (row,col)
            i,e = self.bs.sq[sq].getEffect('cs')
            if e: #if consumed piece
              if self.bs.sq[sq].pc.vision[self.myTurn][0] == self.opp: #if enemy piece 
                return False #exit
        self.getValidSqs((self.enemyF, ()))
      else:
        self.getClicked((self.applyCS, ()))
    #not enough time for ability
    else:
      self.exitAbility()
      return False
    return True

  def applyCS(self, sq):
    self.gs.tes.applyEffect(self.bs.sq[sq], self.myTurn, 'cs')
    self.clock[self.myTurn].timeRemaining -= 60
    self.gs.enhanceName = 'CSM'

  '''
  As of now, any time lost from abilities in autos can spike
  time into the range where whither kick in.  Not sure if
  this will be more or less fun.  Could really insentivise
  aggro play from the Warlock, sacking pieces and making
  fast weird moves to burn time even quicker.  Or it might
  feel really bad to play against.  Have to play test it.
  '''
  def a5(self):
    #function executes constantly in main, but only does
    #something when it is the warlock's opponents turn
    if self.player == self.notMe:
      if len(self.gs.moveLog) > 1:
        #look at opponent last move time
        lastMoveTime = self.clock[~self.myTurn].moveTimes[-1]
        currMoveTime = (self.clock[self.myTurn].timeLog[-1] -
                        self.clock[self.myTurn].timeRemaining)
        if currMoveTime > lastMoveTime:
          self.clock[~self.myTurn].scale = self.scale * self.wither
        else:
          self.clock[~self.myTurn].scale = self.scale

  def a6(self):
    count = 0
    for piece in ['P','N','B','R','Q','K']:
      count += self.gs.bs.removed[self.notMe + piece]
      #take time from opp depending on number of pieces opp lost
    self.clock[self.myTurn].timeRemaining += count*10
    self.clock[~self.myTurn].timeRemaining -= count*10
  
  def a7(self):
    if self.notMe == self.me: #if opponent's turn
      if len(self.gs.moveLog)>=6:
        j = 0
        for i in range(2):
          if (self.clock[self.myTurn].moveTimes[-1-i] <
              self.clock[~self.myTurn].moveTimes[-1-i]):
            j+=1
        if j==3:
          self.scale = 2
          self.clock[~self.myTurn].scale = self.scale
        else:
          self.scale = 1
          self.clock[~self.myTurn].scale = self.scale

  def a8(self):
    if self.charges[self.a8] > 0:
      avg = (self.clock[0].timeRemaining + self.clock[1].timeRemaining)/2
      self.clock[0].timeRemaining = avg
      self.clock[1].timeRemaining = avg
      self.gs.usePower((-1,-1), (-1,-1), '--','--', 'SCH')
      self.charges[self.a8] -= 1
    return False

  def a9(self):
    if self.player == self.notMe: #if opponent made a move
      lastMove = self.gs.moveLog[-1]
      #if opponent moved a pawn last turn
      if lastMove.pieceMoved == self.notMe + 'P':
        sq = lastMove.endSq
        self.gs.tes.applyEffect(self.bs.sq[sq], self.myTurn, 'sn2')
  
'''
ROGUE
'''
class RogueAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.charges = {self.a1:3, self.a3:2}
    self.toAdd = []

  def exitAbility(self):
    self.gs.validSqs.clear()
    self.toAdd.clear()

  #smoke bomb
  #blind can be applied over existing terrain
  def a1(self):
    if self.charges:
      if not self.gs.validSqs:
        self.getValidSqs((self.pieceF,(self.player+'P')))  
      return self.getClicked((self.applyBL,()))
    else:
      return False

  def applyBL(self, sq):
    area = self.bs.area(sq,1,self.board)
    for row in range(self.bs.numR):
      for col in range(self.bs.numC[row]):
        sq = (row,col)
        if sq in area:
          #-bl for blind, player, numTurns
          self.bs.sq[sq].addTerrain('bl',str(self.me),'4',sett=True)
    self.charges[self.a1] -= 1
    self.gs.enhanceName = 'SMB'
    
  #rogue starter decoy
  def a2(self):
    if not self.gs.validSqs:
      #can make decoy with anything but another king
      targets = (self.me+'P',self.me+'N',self.me+'B',
                 self.me+'R',self.me+'Q')
      self.getValidSqs((self.pieceF,(targets)))

    return self.getClicked((self.applyDC,()))

  def applyDC(self, sq):
    king = self.bs.kingLoc[self.myTurn][0]
    self.bs.sq[king].addEffect('dc','','')
    self.bs.sq[sq].addEffect('dc','','')
    self.bs.sq[king].pc.link.append(('dc',sq))
    self.bs.sq[sq].pc.link.append(('dc',king))
    #switch locations
    self.bs.swapPieces(sq,king)
    #switch images for opponent
    self.bs.sq[king].pc.vision[~self.myTurn],self.bs.sq[sq].pc.vision[~self.myTurn] = \
    self.bs.sq[sq].pc.vision[~self.myTurn],self.bs.sq[king].pc.vision[~self.myTurn]

  #stealth pawns
  def a3(self):
    if self.charges[self.a3]:
      if not self.gs.validSqs:
        self.getValidSqs((self.pieceF,(self.me+'P')))
      #only run the following if
      clicked = pg.mouse.get_pressed()
      if len(self.toAdd) < 3:
        return self.getClicked((self.applySt,()), end = False)
      if len(self.toAdd) == 3:
        self.getClicked((self.applySt,()))
        self.charges[self.a3] -= 1
        self.gs.enhanceName = 'STL'
        for item in self.toAdd:
          print(item)
          self.bs.sq[item[0]].addEffect('st','',item[1])
        self.exitAbility()
        return False
      return True
    else:
      return False

  #add stealth helper
  def applySt(self, sq):
    i,e = self.bs.sq[sq].getEffect('st')
    if e:
      turns = e[-2:]
    else:
      turns = 0
    if turns < 6:
      self.toAdd.append((sq,'6'))
    elif (6 >= turns < 10):
      self.toAdd.append((sq,'4'))
    elif turns >= 10:
      self.toAdd.append((sq,'2'))
      
  #assassination auto
  def a4(self):
    if self.bs.pieces[self.me+'P'] > 2 and self.me == self.player:
      for row in range(self.bs.numR):
        for col in range(self.bs.numC[row]):
          sq = (row,col)
          if self.bs.sq[sq].pc:
            if self.bs.sq[sq].pc.piece[0] == self.opp:
              #check all adjacent squares for pawns
              pawnCount = 0
              for asq in self.bs.sq[sq].adjacent:
                if self.bs.sq[asq].pc:
                  if self.bs.sq[asq].pc.piece == self.player + 'P':
                    pawnCount += 1
              #assassination
              if pawnCount > 2:
                self.gs.removePiece(sq)
        
'''
PALADIN
'''
class PaladinAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    #self.charges = {self.a1:1, self.a2:4, self.a3:4,
                    #self.a4:-1, self.a8:1}
  pass

  #starter
  def a1(self):
    # Paladins can start with extra knights at the cost of some pawns
    if (champ == 'Paladin' and pureTalent == (2,1)):
      if self.me == 'b':
        row = 1
      else:
        row = len(self.board) - 2
      #remove 2*talent[2] number of pawns
      removedPawns = 0
      while removedPawns < 2*talent[2]:
        col = r.randint(0, len(self.board[row]) - 1)
        if self.bs.sq[(row,col)].piece[0] == self.me + 'P':
          self.gs.removePiece((row,col),fake = True)
          removedPawns += 1
      #add talent[2] number of knights
      knightsPlaced = 0
      while knightsPlaced < talent[2]:
        # pick a random unoccupied column and place a knight there
        col = r.randint(0, len(self.board[row]) - 1)
        if self.bs.sq[(row,col)].piece[0] == '--':
          piece = self.me + 'K'
          #gold pieces created below
          self.gs.createPiece((row,col),piece,fake = True, gold = False)
          knightsPlaced += 1

'''
PRIEST
'''
class PriestAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    #self.charges = {self.a1:1, self.a2:4, self.a3:4,
                    #self.a4:-1, self.a8:1}
  pass

'''
MARKSMAN
'''
class MarksmanAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    #self.charges = {self.a1:1, self.a2:4, self.a3:4,
                    #self.a4:-1, self.a8:1}
  pass

'''
MAGE
'''
class MageAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    #self.charges = {self.a1:1, self.a2:4, self.a3:4,
                    #self.a4:-1, self.a8:1}
  pass

'''
WARRIOR
'''
class WarriorAbilityLogic(AbilityLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    #self.charges = {self.a1:1, self.a2:4, self.a3:4,
                    #self.a4:-1, self.a8:1}
  pass
