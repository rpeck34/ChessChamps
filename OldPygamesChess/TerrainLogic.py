'''
Used in GameState to handle terrain and status effect logic for each class
'''
import pygame as pg
from PieceLogic import Move
import copy
'''
Aggregates info from both separate champion terrain logic classes to easily
and efficiently handle all terrain and effect logic at once.
'''
class TerrainLogic():
  def __init__(self, gs, class1, class2):
    self.gs = gs
    self.bs = gs.bs
    self.board = gs.bs.board
    self.effects = gs.bs.effects

    #rename
    self.champ = (class1, class2)

    #from bs.  keep in bs or no?
    self.terrainCount = {}
    self.effectsCount = {}
    for champ in self.champ:
      for terrainType in champ.terrain:
        self.terrainCount[terrainType] = 0
      for effectType in champ.effects:
        self.effectsCount[effectType] = 0

  '''
  apply terrain to sq. pt gives who is applying terrain t
  Typically, t/e are given as full terrain/effect strings, but could
  pass only the type and handle the logic for numTurns etc in apply function too.
  This is done in the case of rot for example.  Might be better to be as consistent
  as possile and pick one way to do it.
  '''
  def applyTerrain(self, sq, pt, t):
    print(f'applied {t} on: ')
    print(str(sq))
    self.champ[pt].applyTerrain(sq, t)

  '''
  apply effect to pc
  '''
  def applyEffect(self, sq, pt, e):
    print(f'applied {e} on: ')
    print(str(sq))
    self.champ[pt].applyEffect(sq, e)

  '''
  While terrain is still there, do this at end of turn
  '''
  def nextTerrain(self, sq, terrainType):
    print(f'next {terrainType} from: ')
    print(str(sq))
    if terrainType in self.champ[0].terrain:
      self.champ[0].nextTerrain(sq, terrainType)
    elif terrainType in self.champ[1].terrain:
      self.champ[1].nextTerrain(sq, terrainType)

  '''
  While effect is still there, do this at end of turn
  '''
  def nextEffect(self, sq, effectType):
    print(f'next {effectType} from: ')
    print(str(sq))
    if effectType in self.champ[0].effects:
      self.champ[0].nextEffect(sq, effectType)
    elif effectType in self.champ[1].effects:
      self.champ[1].nextEffect(sq, effectType)

  '''
  When numTurns reaches 0, or terrain is removed somehow, do this
  '''
  def removeTerrain(self, sq, terrainType):
    print(f'removed {terrainType} from: ')
    print(str(sq))
    if terrainType in self.champ[0].terrain:
      self.champ[0].removeTerrain(sq, terrainType)
    elif terrainType in self.champ[1].terrain:
      self.champ[1].removeTerrain(sq, terrainType)

  '''
  Proper removal of effectType
  '''
  def removeEffect(self, sq, effectType):
    print(f'removed {effectType} from: ')
    print(str(sq))
    if effectType in self.champ[0].effects:
      self.champ[0].removeEffect(sq, effectType)
    elif effectType in self.champ[1].effects:
      self.champ[1].removeEffect(sq, effectType)

  '''
  Do something in gs.makeMove
  '''
  def alterMove(self, move):
    if self.bs.sq[move.endSq].pc:
      for e in self.bs.sq[move.endSq].pc.effects:
        if e[:2] in self.champ[0].effects:
          print(f'move altered by e')
          self.champ[0].alterMove(move)
        elif e[:2] in self.champ[1].effects:
          print(f'move altered by e')
          self.champ[1].alterMove(move)

  '''
  change (both add and remove) moves, attacked, defended etc based on terrain
  and effects on board.  Change moves by square rather than by full moves list
  '''
  def alterMoves(self):
    print('altering both champions moves')
    self.champ[0].alterMoves(self.bs)
    #moves already altered should not be altered again.
    #no double wormhole moves added type stuff.
    #don't prevent running twice since logic for that is tricky...
    #let run second time if champs are same, but moves should not get altered??
    self.champ[1].alterMoves(self.bs)

  '''
  count down all terrain and status effects on each sq/pc.
  This must go through both players effect
  '''
  def nextTurn(self):
    print('next turn for effects and terrain')
    #reset and recount terrain and effects
    #is default keys or values? might have to .keys()
    for k in self.terrainCount:
      self.terrainCount[k] = 0
    for k in self.effectsCount:
      self.effectsCount[k] = 0
    for row in range(self.bs.numR):
      for col in range(self.bs.numC[row]):
        sq = (row,col)
        #move get/add terrain/effects here??
        for t in self.bs.sq[sq].terrain:
          if t[:2] in self.champ[0].terrain:
            numTurns = self.champ[0].nextTerrain(self.bs.sq[sq], t)
          elif t[:2] in self.champ[1].terrain:
            numTurns = self.champ[1].nextTerrain(self.bs.sq[sq], t)
          if numTurns:
            self.terrainCount[t[:2]] += 1
        if self.bs.sq[sq].pc:
          for e in self.bs.sq[sq].pc.effects:
            if e[:2] in self.champ[0].effects:
              numTurns = self.champ[0].nextEffect(self.bs.sq[sq], e)
            elif e[:2] in self.champ[1].effects:
              numTurns = self.champ[1].nextEffect(self.bs.sq[sq], e)
            if numTurns:
              self.effectsCount[e[:2]] += 1

'''
Base terrain and effects logic to be inhereted by champions.  Contains all
functions possible.  Simply override in champion class to fill out class
'''
class BaseTerrainLogic():
  def __init__(self, gs, me):
    self.gs = gs
    self.bs = gs.bs
    self.me = me
    self.opp = 'b' if self.me == 'w' else 'w'
    self.myTurn = 0 if self.me == 'w' else 1
    self.terrain = ()
    self.effects = ()
    #want to handle links better trueLinks and truePcLinks is dumb
    #gs.bs.trueLinks
    #gs.bs.truePcLinks
    #gs.bs.block
    #gs.bs.impass

  #apply terrain and effect is typically done through abilities.
  #validSqs is handled there so if this function is run it is assumed to be
  #applied to a validSq
  def applyTerrain(self, sq, t):
    pass

  def applyEffect(self, sq, e):
    pass

  #next terrain and effect is run once in getLegalMoves at beginning of next turn
  #but then bs is reverted after, and once for real in endTurn.  Progresses the
  #effect/terrain countdowns on every sq and changes bs accordingly.
  def nextTerrain(self, sq, terrainType):
    pass

  def nextEffect(self, sq, effectType):
    pass

  #handles proper removal of terrain/effect.  Usually run when counter runs out
  #or if piece is captured/removed somehow
  def removeTerrain(self, sq, terrainType):
    pass

  def removeEffect(self, sq, effectType):
    pass

  #alters a single move, the move being made this turn.  For example, if a piece with the
  #wh effect makes a move, this is checked for in alterMove and causes a wh to be placed
  def alterMove(self, move, bs):
    pass

  #runs once for each player? in getLegalMoves.  Adjusts moves based solely on terrain and
  #effects.  Example, stunned pieces have all attacked squares and legal moves removed.
  #ranged, linear pieces attacking wormholes have moves added (moves going out of wh).
  def alterMoves(self, bs):
    pass
      
'''
WARLOCK
Break up wh stuff into new bite sized functions
'''
class WarlockTerrainLogic(BaseTerrainLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.gs = gs
    self.terrain = ('wh',)
    self.effects = ('wh','cs','rt','sn')
    #maybe this will be handled automatically with new layout,
    #can explicitly write this in?  maybe not true links but block perhaps?
    gs.bs.trueLinks.append('wh')
    gs.bs.block.append('wh') #wormholes block

  def applyTerrain(self, sq, t):
    if t[:2] == 'wh':
      pass

  def applyEffect(self, sq, e):
    if e[:2] == 'wh':
      sq.addEffect(e[:2],e[2:3],'10')

    elif e[:2] == 'cs':
      sq.addEffect('cs','','')

    elif e[:2] == 'rt':
      if sq.pc.vision[self.myTurn][1] == 'P':
        turns = '3'
      elif sq.pc.vision[self.myTurn][1] in ('B','N'):
        turns = '5'
      elif sq.pc.vision[self.myTurn][1] == 'R':
        turns = '7'
      sq.addEffect('rt','',turns)
      print(f'applying {e}')

    elif e[:2] == 'sn':
      sq.addEffect('sn','',e[2:])

  def nextTerrain(self, sq, t):
    numTurns = self.bs.sq[sq].addTerrain(t[:2],t[2:-2],-1)
    if numTurns:
      self.nextTerrain(self.bs.sq[sq], t[:2])
    #if no turns left
    else:
      self.removeTerrain(self.bs.sq[sq], t[:2])

  #fix this up?  OR put back in main nextTurn?
  def nextEffect(self, sq, e):
    if e[:2] == 'wh':
      i,e = sq.getEffect('wh')
      del sq.pc.effects[i]

    elif e[:2] == 'rt':
      pass
    
    elif e[:2] == 'sn':
      numTurns = int(sq.addEffect(e[:2],e[2:-2],-1))
      if not numTurns: #no turns left
        self.removeEffect(sq,e[:2])
      print(f'number turns left, {numTurns}')

  def removeTerrain(self, sq, terrainType):
    if terrainType == 'wh':
      pass

  def removeEffect(self, sq, effectType):
    #remove wh effect handled directly in nextTurn... always removed
    if effectType == 'wh':
      pass

    elif effectType == 'cs':
      pass

    elif effectType == 'rt':
      self.gs.removePiece(sq.sq)

    elif effectType == 'sn':
      i,e = sq.getEffect('sn')
      del sq.pc.effects[i]
      
  def alterMove(self, move):
    sq1 = move.startSq
    sq2 = move.endSq
    sq3 = move.capSq
    #consume
    ind,e = self.bs.sq[sq2].getEffect('cs')
    if e:
      self.gs.clock[self.bs.playerTurn].timeRemaining -= 10
      self.gs.clock[~self.bs.playerTurn].timeRemaining += 10
    #wormhole placement
    if sq2 != sq1:
      ind,e = self.bs.sq[sq2].getEffect('wh')
      if e:
        #only place wh if no terrain on end sq
        if not self.bs.sq[sq2].terrain:
          #add wh to end sq
          self.bs.sq[sq2].addTerrain('wh',e[2],e[-2:])
          #add wh to start sq
          self.bs.sq[sq1].addTerrain('wh',e[2],e[-2:])
          #add link to both sqs
          self.bs.sq[sq2].link.append(('wh',sq1))
          self.bs.sq[sq1].link.append(('wh',sq2))

  def alterMoves(self, bs):
    moves = copy.deepcopy(bs.moves[bs.playerTurn])
    for possibleMove in moves:
      sq = possibleMove.startSq
      ind,e = bs.sq[sq].getEffect('sn')
      if e:
        #stunned pieces do not even attack squares
        bs.moves[bs.playerTurn].remove(possibleMove)
        bs.sq[sq].pc.moves.clear()
        bs.sq[sq].pc.attacked.clear()
        bs.sq[sq].pc.defended.clear()
      ind,e = bs.sq[sq].getEffect('wh')
      if e:
        pass

  def updateWormhole(self, sq):
    #whij: wh - wormhole, i - wormhole pair number, j - num turns left for pair
    wTurns = self.countDownTerrain('wh', sq)
    for link in self.bs.sq[sq].link:
      if 'wh' == link[0]:
        whSq = link[1] 
    if wTurns <= 0:
      #full remove first piece on closing wormhole
      if self.bs.sq[sq].pc:
        self.gs.removePiece(sq)
    else:
      lastMove = self.gs.moveLog[-1]
      #if piece on wormhole or paired wh at turn end
      if self.bs.sq[sq].pc:
        #if moved on to wormhole last turn
        if lastMove.endSq == sq:
          self.gs.copyPiece(sq,whSq)
      #if piece on wormhole moved off wormhole this turn
      else:
        if lastMove.startSq == sq:
          #remove copy of piece
          self.gs.removePiece(whSq, fake = True)

  '''
  Logic to manipulate moves based on wormhole terrain
  '''
  def applyWormhole(self):
    whs = []
    turns = []
    whMoves = []
    #find wh squares
    for row in range(self.bs.numR):
      for col in range(self.bs.numC[row]):
        sq = (row,col)
        ind,t = self.bs.sq[sq].getTerrain('wh')
        if t:
          whs.append(sq)
          turns.append(t[3])
    for w, wTurns in zip(whs, turns): #all wormhole squares
      for king in self.gs.bs.kingLoc[self.playerTurn]: #all kings
        #if king on wormhole about to close
        if king == w and wTurns <= 2:
          self.bs.check = True
          #force a king move off of the wormhole
          #might need deep copy here...
          for move in self.gs.bs.moves[self.playerTurn][:]:
            if (move.pieceMoved[1] != 'K' or
                move.pieceMoved[1] == 'K' and move.endSq == w):
              self.bs.moves[self.playerTurn].remove(move)
    for move in self.bs.moves[self.playerTurn]: 
      #if ending on wormhole
      if move.endSq in whs:
        whMoves.append(move)
    self.whGen(whMoves, whs, 0)

  '''
  Recursive helper function to whLogic.
  calls itself with extra whMoves if there are any.
  Does this until there are no extra whMoves or
  the piece has gone through a number of wormholes equal
  to the amount on the board
  '''
  def whGen(self, whMoves, whs, depth):
    whNext = []
    numWhs = len(whs)
    pt = self.playerTurn
    mv = self.bs.moveable[pt]
    bl = self.bs.blocked[pt]
    while depth < numWhs:
      for move in whMoves:
        print(move.chessNotation())
        whMovedTo = move.endSq
        for link in self.bs.sq[move.endSq].link:
          print(link)
          if link[0] == 'wh':
            sq = link[1]
          row = sq[0]
          col = sq[1]
        #some moves will already have animate list and path from previous iteration
        animate = move.animateList
        path = move.path
        whPiece = move.pieceMoved[1]
        ind,t = self.bs.sq[(move.endRow,move.endCol)].getTerrain('wh')
        if t:
          wTurns = int(t[3])
        #if wh attacked, pair wh is also attacked
        if sq not in self.gs.bs.attacked[pt]:
          self.gs.bs.attacked[pt].append(sq)
        #can't suicide king into wormhole
        if move.pieceMoved[1] == 'K':
          if wTurns <= 2:
            if move in self.gs.bs.moves[pt]:
              self.gs.bs.moves[pt].remove(move)
              continue
        if self.board[row][col]!='--': #paired wormhole occupied
          if self.board[row][col]==self.opp:
            self.gs.bs.moves[pt].append(Move(move.startSq,sq,self.board))
          if self.board[row][col]==self.player:
            self.gs.bs.defended[pt].append(Move(move.startSq,sq,self.board))
            #piece cannot defend itself in wormhole
            if move.startSq == self.bs.link[('wh',sq)][1]:
              self.gs.bs.defended[pt].remove(Move(move.startSq,sq,self.board))
        else: #both wormholes are open
          #consider tracking number of moves from path and comparing to rng or
          #something for non-infinite range pieces
          #if piece can move more than 1 sq
          if self.bs.sq[move.startSq].pc.canPin:
            #move piece to wormhole and generate moves
            self.bs.movePiece(move.startSq,sq)
            #gen moves
            moos,dees,atts = self.bs.sq[sq].pc.getMoves(gen = True)
            #move piece back to start sq
            self.bs.movePiece(sq, move.startSq)
            for m in moos:
              if m.moveDir == move.moveDir: 
                if m not in self.gs.bs.moves[pt]:#if need to take wormhole
                  whMove = Move(move.startSq,m.endSq,self.board)
                  #set move dir to be movedir of last move
                  whMove.moveDir = move.moveDir
                  #for UI to animate move properly
                  #if move already had a list of animations
                  if animate != []:
                    whMove.animateList.extend(animate)
                    whMove.animateList.append(m)
                    path.extend(whMove.path)
                    whMove.path = path
                  else:
                    whMove.animateList.append(move)
                    whMove.animateList.append(m)
                  self.gs.bs.moves[pt].append(whMove)
                  #if one of the generated moves attacks another wormhole
                  if whMove.endSq in whs:
                    #add to new list of whMoves
                    whNext.append(whMove)
                if m.endSq not in self.gs.bs.attacked[pt]:
                  self.gs.bs.attacked[pt].append(m.endSq)
            for d in dees:
              if d.moveDir == move.moveDir:
                if d not in self.gs.bs.defended[pt]:
                  self.gs.bs.defended[pt].append(
                    Move(move.startSq,d.endSq,self.board))
                  #set proper move dir
                  self.gs.bs.moves[pt][-1].moveDir = move.moveDir
      #run through logic for next depth of wormhole moves
      depth += 1
      if len(whNext) > 0:
        self.whGen(whNext,whs,depth)
      else:
        depth = numWhs
        break

#rework from terrainLogic 2 
class RogueTerrainLogic(BaseTerrainLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.terrain = ('bl')
    self.effects = ('st')

  def alterMove(self, move, bs):
    sq1 = move.startSq
    sq2 = move.endSq
    sq3 = move.capSq
    #stealth effect logic, changes move notation to ???
    ind,e = self.bs.sq[sq2].getEffect('st')
    if e:
      move.stealth = True
    return move

class PaladinTerrainLogic(BaseTerrainLogic):
  pass

class PriestTerrainLogic(BaseTerrainLogic):
  pass

class MarksmanTerrainLogic(BaseTerrainLogic):
  pass

class MageTerrainLogic(BaseTerrainLogic):
  pass

class WarriorTerrainLogic(BaseTerrainLogic):
  pass
