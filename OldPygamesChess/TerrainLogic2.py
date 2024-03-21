'''
Used in GameState to handle terrain and status effect logic for each class
'''
import pygame as pg
from PieceLogic import Move
import copy
'''
Base class.  If there are some more universal status/terrain, add
them to base class, else keep them all specialized
'''
class TerrainLogic():
  def __init__(self, gs, me):
    self.gs = gs
    self.me = me
    self.notMe = 'w' if self.me == 'b' else 'b'
    self.bs = gs.bs
    self.board = gs.bs.board
    self.whiteTurn = gs.bs.whiteTurn
    self.player = gs.bs.player
    self.opp = gs.bs.opp
    self.playerTurn = gs.bs.playerTurn
    self.myTurn = 0 if self.me == 'w' else 1
    self.effects = gs.bs.effects
    self.champ = gs.pi[self.playerTurn].champion
    self.oppChamp = gs.pi[~self.playerTurn].champion
    self.talents = gs.pi[self.playerTurn].talents
    self.oppTalents = gs.pi[~self.playerTurn].talents
    self.updateEffectsDict['sn'] = self.updateStun
    self.applyEffectsDict['sn'] = self.applyStun
    self.updateTerrainDict = {}
    self.applyTerrainDict = {}
    self.moveable = gs.bs.moveable[self.playerTurn]
    self.blocked = gs.bs.blocked[self.playerTurn]

  #Do we need all these updates?  Why can't one ref to bs and gs work.
  def update(self, gs):
    self.gs = gs
    self.bs = gs.bs
    self.board = gs.bs.board
    self.whiteTurn = gs.bs.whiteTurn
    self.player = gs.bs.player
    self.opp = gs.bs.opp
    self.playerTurn = gs.bs.playerTurn
    self.moveable = gs.bs.moveable[self.playerTurn]
    self.blocked = gs.bs.blocked[self.playerTurn]
    self.effects = gs.bs.effects
    self.terrain = gs.bs.terrain

  '''
  Empty placeholder functions, dictionaries need to be filled
  '''
  @staticmethod
  def updateFoo(terrain, sq):
    pass
  
  @staticmethod
  def applyFoo():
    pass

  '''
  Generic updateStatus function simply reduces status by 1 each turn
  and removes if it is 0.  Simply don't add to terrain that dont
  have numTurns
  '''
  def countDownTerrain(self, terrainType, sq):
    ind,t = self.bs.sq[sq].getTerrain(terrainType)
    if t:
      terrainTurns = int(t[-2:]) - 1
      if terrainTurns <= 0: #when terrain runs out
        del self.bs.sq[sq].terrain[ind]
        self.bs.sq[sq].terrainIm = ''
      else:
        t = t[:-2]+str(terrainTurns).zfill(2)
        self.bs.sq[sq].terrain[ind] = t
        self.bs.sq[sq].terrainIm = t[:-2]
      return terrainTurns
  
  '''
  Generic function simply reduces status by 1 each turn
  and removes if it is 0.  Simply don't add to effects that dont
  have numTurns
  '''
  def countDownEffect(self, effectType, sq):
    ind,e = self.bs.sq[sq].getEffect(effectType)
    if e:
      effectTurns = int(e[-2:]) - 1
      if effectTurns <= 0: #when effect runs out
        del self.gs.bs.sq[sq].pc.effects[ind]
      else:
        e = e[:-2]+str(effectTurns).zfill(2)
        self.gs.bs.sq[sq].pc.effects[ind] = e
      return effectTurns
  
  '''
  Lots of classes use stun so it goes here
  '''
  def updateStun(self, sq):
    turnsLeft = self.countDownEffect('sn',sq)
    
  #a stunned piece cannot perform any actions, but an immobilized piece
  #could so long as it doesn't move (sniper pieces can still attack)
  def applyStun(self):
    for possibleMove in self.gs.bs.moves[self.playerTurn][:]:
      sq = possibleMove.startSq
      ind, e = self.gs.bs.sq[sq].getEffect('sn')
      if e:
        self.gs.bs.moves[self.playerTurn].remove(possibleMove)
        
'''
WARLOCK
'''
class WarlockTerrainLogic(TerrainLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.updateTerrainDict['wh'] = self.updateWormhole
    self.applyTerrainDict['wh'] = self.applyWormhole
    self.updateEffectsDict['wh'] = self.updateWormholeE
    self.applyEffectsDict['wh'] = self.applyFoo
    self.updateEffectsDict['rt'] = self.updateRot
    self.updateEffectsDict['cs'] = self.updateConsume
    self.applyEffectsDict['rt'] = self.applyFoo
    self.applyEffectsDict['cs'] = self.applyFoo
    self.bs.trueLinks.append('wh')
    self.bs.block.append('wh') #wormholes block
    
  '''
  Wormhole effect has to be used immediately, update sets to 0
  '''
  def updateWormholeE(self, sq):
    i,e = self.bs.sq[sq].getEffect('wh')
    #remove wormhole effect
    del self.bs.sq[sq].pc.effects[i]

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
      
  def updateRot(self, sq):
    turnsLeft = self.countDownEffect('rt',sq)
    if turnsLeft == 0:
      self.gs.removePiece(sq)

  #consume doesn't have turns
  def updateConsume(self, sq):
    if self.gs.moveLog[-1].endSq == sq: #if consumed piece moved
      self.gs.clock[self.playerTurn].timeRemaining -= 10
      self.gs.clock[~self.playerTurn].timeRemaining += 10

class RogueTerrainLogic(TerrainLogic):
  def __init__(self, gs, me):
    super().__init__(gs, me)
    self.updateTerrainDict['bl'] = self.updateBlind
    self.applyTerrainDict['bl'] = self.applyFoo
    self.updateEffectsDict['st'] = self.updateStealth
    self.applyEffectsDict['st'] = self.applyFoo
    self.updateEffectsDict['dc'] = self.updateDecoy
    self.applyEffectsDict['dc'] = self.applyFoo
    #all terrain that will break stealth and/or decoy
    self.breakStealthT = ['wh']
    #all effects that will break stealth and/or decoy
    self.breakStealthE = ['rt']

  '''
  Helper function for both stealth and decoy.  This function will check
  for any and all break stealth terrain and effects on stealth or decoy piece.
  If it spots any, it automatically removes them, and stealth and decoy are removed
  and vision is restored.  Runs in update, and only on stealth or decoy pieces
  Add list of lethal terrain similar to rest
  '''
  def checkBreakStealth(self, sq):
    #check lethal terrain
    flag = False
    for terrainType in self.breakStealthT:
      i,t = self.bs.sq[sq].getTerrain[terrainType]
      if t:
        flag = True
        #remove terrain 
        self.bs.addTerrain(terrainType, t[2:-2], 1, sett = True)
    for effectType in self.breakStealthE:
      i,e = self.bs.sq[sq].getEffect[effectType]
      if e:
        flag = True
        #remove effect
        self.bs.addEffect(effectType, e[2:-2], 1, sett = True)
    if flag:
      for effectType in ('dc','st'):
        i,e = self.bs.sq[sq].getEffect[effectType]
        if e:
          if 'st' in e:
            self.removeStealth(sq, noTurns = False)
          if 'dc' in e:
            self.removeDecoy(sq)

  #gives player piece stealth upon ending turn within blind area
  #if piece leaves blind p area (lastMove started in blind and
  #ended outside blind p area, and remove stealth turns by 2.
  #if stealth turns less than 0, remove stealth
  def updateBlind(self, sq):
    ind,t = self.bs.sq[sq].getTerrain('bl')
    bTurns = self.countDownTerrain('bl',sq)
    # blind gives stealth status effect only to player that caused blind
    player = t[2]
    if bTurns >= 0:
      lastMove = self.gs.moveLog[-1]
      if self.bs.sq[sq].pc:
        effects = self.bs.sq[sq].pc.effects
        if self.bs.sq[sq].pc.piece[0] == player:
          ind,e = self.bs.sq[sq].getEffect('st')
          #if piece not already stealth
          if not e:
            self.bs.sq[sq].addEffect('st','',2)
          #if only 1 turn of stealth left
          elif e and int(e[2]) == 1:
            self.bs.sq[sq].addEffect('st','',2, sett = True)
      #if player leaves blind area reduce stealth turns by 1
      if lastMove.pieceMoved[0] == player:
        #if piece started on blind square
        if lastMove.startSq == sq:
          ind2,t2 = self.bs.sq[lastMove.endSq].getTerrain('bl')
          #if left player blind area and didn't enter another one
          if not t2:
            self.removeStealth(lastMove.endSq, noTurns = False)
          elif t2 and 'bl'+player not in t2:
            self.removeStealth(lastMove.endSq, noTurns = False)
      
  def updateStealth(self, sq):
    stealthTurns = self.countDownEffect('st', sq)
    if stealthTurns == 0:
      self.removeStealth(sq, noTurns = True)
    else:
      #apply stealth to stealth unit
      self.bs.sq[sq].pc.vision[~self.myTurn] = '--'

  def removeStealth(self, sq, noTurns = True):
    #opponent regains vision
    self.bs.sq[sq].pc.vision[~self.myTurn] = self.bs.sq[sq].pc.piece
    if not noTurns:
      #set stealth to 0
      self.bs.sq[sq].addEffect('st','',1,sett=True)

  #no countdown
  def updateDecoy(self, sq):
    #make sure this is correct turn check.
    #Should be on your turn not opponent
    #if wrong switch
    if self.gs.bs.check and self.me == self.player:
      print('check in decoy update')
      #go through all of players decoys and remove them
      for row in range(self.bs.numR):
        for col in range(self.bs.numC[row]):
          ind,e = self.bs.sq[sq].getEffect('dc')
          if e and self.bs.sq[sq].pc.piece[0] == self.me:
            self.removeDecoy(sq)
                
  def removeDecoy(self, sq):
    #restore opponent vision
    self.bs.sq[sq].pc.vision[~self.playerTurn] = self.bs.sq[sq].pc.piece
    ind,e = self.bs.sq[sq].getEffect('dc')
    #remove dc effect
    del self.bs.sq[sq].pc.effects[ind]
    #get rid of decoy link
    for link in self.bs.sq[sq].pc.link:
      if link[0] == 'dc':
        self.bs.sq[sq].pc.link.remove(link)

class PaladinTerrainLogic(TerrainLogic):
  pass

class PriestTerrainLogic(TerrainLogic):
  pass

class MarksmanTerrainLogic(TerrainLogic):
  pass

class MageTerrainLogic(TerrainLogic):
  pass

class WarriorTerrainLogic(TerrainLogic):
  pass
