from time import time
import asyncio #for pygbag web assembly
'''
Pawns still stunned with 1 turn left, but can move still.
Current Project:
Get countdowns reaching 0 to go to 00 and result in effect/terrain being removed
cs -- good it seems... but probably not after changing back to just numTurns in addEffect
was working for numTurns + 1 but then doesn't work for everything else... find other sol.
rt -- Applying Rot, turns wont go below 01
sn -- Sn will go from 02 to just sn with no number, then won't leave ever
wh effect --
wh terrain --


After, do the special endTurn and undo(nextTurn for terrain effects) in getLegalMoves
Also:
Change legalMoves stuff to use sq and pc info rather than full Moves list etc.
Update bs.moves, attacked, defended, list only at very end with the filtered square info
by going through all sqaures and getting the info from the pieces on them.

Give sq, pc and bs more power:
add save piece, save sq functions to square which save and return all square and piece info
Add global save function, which saves full board state
Add nextTurn functions to squares, which progress turn by 1 (terrain and effects count down)
add lastTurn functions to squares, which undoes turn by 1 if there is a previous saved
sq to go back to

GET WH GOING SMOOTHLY. REJIGGER FULL WHLOGIC
Wormhole placement should count as a block, since it blocks sq left behind.
This should allow piece to get out of true pin (since it leaves wormhole, blocked sq, behind)
This info has to be input right away, in makeMoves is too late,
So this begs for a getAbilities, which generates all possible moves based off
valid sqs for each ability and enh.

Consider for Warlock:
wh enh literally doubles legalMoves just on its own.  For every move except
king there is another beefier move that also places wh down.
The rest are not so bad.
Rot and sync cannot be used if in check, (with expanded def of check below)
Rewind and consume can always be used, if validSqs

If checking piece will die next turn, don't count as check

If piece currently blocking a pin on king but will die next turn
add appropriate checkMove (the move attacking king without blocking piece there)

If check blocking piece will die next turn, don't count as block
(any blocks in legalMove should not consider pieces that will die next turn)

All abilities will have a getValidSqs function that runs
to check if there are any valid moves of that type to be made.  This info will be passed to
UI to change colour of buttons, and legalMoves.

bugs:
black pieces immediately eaten by wh, but white fine???
wh animation, gold fail, cap piece teleported to first wh.
BasePiece is likely not working for black.  I think black champ and talents will be whites
because black goes first, then white pieces go after and override class vars.  Check this.
Fix is either add this info to each individual piece, or find a way to instance the class,
then refer to this instance, one for white and one for black?
Make sure click anywhere but valid sq exits ability.  Right now can click other buttons
and won't exit active ability.

Implemented breakStealthE and T for this MAYBE FIXED
Stealth and wormhole placement don't play nice together.
Decoy and targetted abilities don't play nice together.
Lack of vision, knowledge of true piece allows for undesirable
ability moves, like rotting an enemy king because it appeared to be
a pawn, or placing a wormhole on an enemy piece in a blind sq.
Blind is easy -> blind goes from '--' to '??', if '??' can't place
wormhole.

Stealth and decoy are trickier.  Best sol I see is to allow ability
to be used in either case, however, if an impossible move is made, instead
of allowing that move (like wormhole on enemy king, or rot on enemy decoy king)
instead, the stealth/ decoy is removed from the piece.  This will be a feature
of stealth and decoy in general, as it should apply to non-warlock situations as well.

However, add attributes to Move/manualMove, so that stealth and decoy can easily know
if that move was illegal or not.  Example, add targetted bool so Move knows it can
work on an enemy piece.  makeMove deals in boardstate, not vision, so when move is attempted
to be made.  Can add terrainPlace bool, targetted, lethalMove, effectAdded... add
all bools necessary to give enough info for TerrainLogic and gs to react properly.

st can have no effects added to it.  If it does, break stealth.
similar for dc.
check still works like normal for a dc king that is stealth.
Now for decoy, moves that target an enemy piece like rot will also not work.
Ideal behaviour: can rot any piece when rogue in decoy.  If happen to rot king,
then instead of rot being applied, it breaks decoy.  Same for stealth.
Targetted terrain move like creating wormhole simply isn't allowed in blind
(already built in since wormhole can only work on empty terrain)
but blind can be used on top of wormhole after wormhole placed
targetted terrain move like wormhole CAN work on stealth sq, but just breaks stealth.
No wormhole made.
'''

import ChessEngine as ce
import PieceLogic as pl
import UI #my own user interface tools
import pygame as pg
import sys
from itertools import product as pr #powerset used for special moves

pg.init()
PATH = "C:\\Users\\rpeck\\Documents\\Programming\\GitHub\\ChessProject\\PythonChess"  # path

'''plays game when called'''
async def main():
  ms = MainState()
  #after init, unpause game clocks
  ms.gs.clock[0].pause = False
  #ms.gs.clock[1].pause = False
  playMusic(ms.mus.Lmusic, ms.mus.vol, ms.mus.song1)

  #Play game loop
  while 1:
    ms.gui.screen.fill((0,0,0)) #fill window with solid black
    pos = pg.mouse.get_pos() #mouse position
    live, hovered = getHovered(pos, ms.gui)
    ''' change cursors breaking game sometimes
    #if hovered == [False] * len(hovered):  # if no buttons hovered
      #ms.cursor = pg.cursors.arrow
    #else:
      #ms.cursor = pg.cursors.broken_x
    #pg.mouse.set_cursor(ms.cursor)
    '''
    #have separate logic for black and white?
    if ms.setup:
      manRun = ms.gs.runStarterEnhancements(0)
      timeRem = False if ms.gs.clock[0].timeRemaining <= 0 else True
      if not manRun or not timeRem:
        ms.setup = False
      if ms.setup == False:
        ms.gs.validSqs = []
        ms.gs.bs.update()
        ms.gs.getLegalMoves()
        #reset clocks
        wM, wS = ms.gs.timeControl[0][0], ms.gs.timeControl[0][1]
        bM, bS = ms.gs.timeControl[1][0], ms.gs.timeControl[1][1]
        ms.gs.clock[0].setTime(wM, wS)
        ms.gs.clock[1].setTime(bM, bS)
        #don't count time in setup as move time
        ms.gs.clock[0].lastmove = pg.time.get_ticks()
        ms.gs.clock[1].lastMove = pg.time.get_ticks()
    for event in pg.event.get():
      if event.type == pg.QUIT: #if x button pressed in window
        pg.quit() #stop pygames
        sys.exit() #close window
      #reset held buttons
      if event.type == pg.MOUSEBUTTONUP:
        resetHeld(ms.gui)
      #click on squares
      if event.type == pg.MOUSEBUTTONDOWN:
        if getClicked(live, ms.gui):
          ms.gs.validSqs = []
          ms.gs.abilities[ms.gs.bs.playerTurn].validSqs = []
        #make moves only if an ability is not live
        if not live:
          col = pos[0]//ms.gui.SQ_SIZE
          row = pos[1]//ms.gui.SQ_SIZE
          #use clicked squares to make moves
          clickLogic(ms, (row, col))
      if event.type == pg.KEYDOWN:
        #reset
        if event.key == ord('r'): #if r pressed
          if len(ms.gs.moveLog) > 0: #if there were moves made
            print('Move undone')
            ms.undo()
        #restart game
        if event.key == ord('z'): #if z pressed
          print('Game reset')
          ms = MainState()
          ms.gs.clock[0].pause = False
          ms.gs.clock[1].pause = True
          break
    #update ms after move made
    if ms.moveMade or ms.gs.powerUsed:
      ms.update()
    #do this after every frame
    ms.endFrame()
    await asyncio.sleep(0)

def playMusic(Lmusic, vol, song1):
  if Lmusic:
    pg.mixer.init()  # load mixer to play sounds in pygames
    pg.mixer.music.load(PATH + "\\BattleMusic\\" + song1)  # loads desired song.
    pg.mixer.music.set_volume(vol)  # sets desired volume
    # can make UI slider in menu that changes mixer volume.
    # right now starts playing as soon as playgame starts.
    # Can also make this conditional as well.
    # pg.mixer.music.play()
    # loops = -1 makes music loop forever
    pg.mixer.music.play(loops=-1)
    # can use pg.mixer.music.pause() and pg.mix.music.unpause() methods too
    # When finished game, use pg.mixer.music.stop() to stop song

def getHovered(pos, gui):
  hovered = []
  #check for live ability button
  if True in gui.Button.live[6:16]:
    live = True
  else:
    live = False
  for button in gui.buttons:
    #if there is a live ability
    #every other ability button that is not live does not get considered
    if live and (button in gui.buttons[6:16] and not button.live):
      button.hover = False
      hovered.append(False)
      button.click = False
      continue
    #if no live ability buttons, consider all buttons
    else:
      button.checkHover(pos)
      button.click = False #reset click status each frame
      hovered.append(button.hover)
      
  #check hovered for popups
  for popup,active in zip(gui.popups,gui.Popup.active):
    if active:
      popup.checkHover(pos)
      #if talent info popup, can't click board until closed
      if popup.num == 5:
        live = True
      #start delayed closes if any
      if popup.toClose:
        MainState.delayClosePopup(5, popup)
  return live, hovered

def resetHeld(gui):
  for button in gui.buttons:
    button.held = False

def getClicked(live, gui):
  for popup in gui.popups:
    if popup.hover and popup.clickToClose:
      popup.closePopup()
  for button,clickable in zip(gui.buttons, gui.Button.clickable):
    if button.hover and clickable:
      button.clicked()
      #if canceling a live button
      if live and button in gui.buttons[6:16]:
        return True

'''
After click registered in main loop, go here
'''
def clickLogic(ms, sqClicked):
  row = sqClicked[0]
  col = sqClicked[1]
  #if col and row are on chess board
  if (0 <= row < ms.gs.bs.numR) and (0 <= col < ms.gs.bs.numC[row]):
    if len(ms.possibleMoves) < 1:
      ms.sqClicked.append((row, col))
      #if more than one square has been clicked
      if (len(ms.sqClicked)>1):
        lastRow = ms.sqClicked[-2][0]
        lastCol = ms.sqClicked[-2][1]
        if (ms.sqClicked[-1] == ms.sqClicked[-2]): #if same square clicked
          ms.sqClicked.clear() #clear square clicked list
          ms.gs.validSqs.clear()
        else: #if another square clicked
          #if there was a piece on the last sq clicked and move has not already been made
          if ms.moveMade == False and ms.gs.bs.sq[(lastRow,lastCol)].pc:
            #if it was current players piece
            if ms.gs.bs.sq[(lastRow,lastCol)].pc.piece[0] == ms.gs.bs.player:
              #create desired instance of Move
              boolVals = [False, True]
              specialSet = (tuple(k) for k in pr(boolVals, repeat = 4))
              tryMove = []
              for specialMoves in specialSet:
                #making move with right mouse click prioritizes specials
                if pg.mouse.get_pressed()[2]:
                  specialMoves = (not specialMoves[0],not specialMoves[1],
                                 not specialMoves[2],not specialMoves[3])
                tryMove.append(pl.Move(ms.sqClicked[-2], ms.sqClicked[-1],
                           ms.gs.bs.board, specialMoves = specialMoves))
              #of the possible moves available by clicking two squares, find the legal ones
              possibleMoves = []
              if len(tryMove) >= 1:
                #the moves in legalMoves have more accurate information than
                #the moves generated above.  Work with these moves
                for move in ms.gs.legalMoves:
                  #print(move.chessNotation())
                  if move in tryMove:
                    possibleMoves.append(move)
                #if multiple possible moves
                if len(possibleMoves) > 1:
                  validSqs = []
                  for move in possibleMoves:
                    validSqs.append(move.capSq)
                  #show valid sqs
                  ms.gs.validSqs = validSqs
                  ms.possibleMoves = possibleMoves
                #if exactly one possible move
                elif len(possibleMoves) == 1:
                  moveToMake = possibleMoves[0]
                  #do this last after one move left
                  if ms.gs.enhanceName != '':
                    moveToMake.enhanceName = ms.gs.enhanceName
                  ms.gs.makeMove(moveToMake)
                  ms.moveMade = True
                #no possible moves
                else:
                  ms.sqClicked.clear()
    elif len(ms.possibleMoves) > 1:
      #look for another click. set to capClick
      capClick = (row, col) 
      if capClick in ms.gs.validSqs:
        for move in ms.possibleMoves:
          if move.capSq == capClick:
            moveToMake = move
            if ms.gs.enhanceName != '':
              moveToMake.enhanceName = ms.gs.enhanceName
            ms.gs.makeMove(moveToMake)
            ms.gs.validSqs.clear()
            ms.possibleMoves.clear()
            ms.moveMade = True
      else:
        ms.gs.validSqs.clear()
        ms.possibleMoves.clear()
                
class MainState():
  def __init__(self):
    # create instance of GameState class
    self.gs = ce.GameState()
    # create instance of GameGraphics class
    self.gui = UI.GameGraphics(self.gs.bs)
    for p in (0,1):
      self.gs.abilities[p].getSize(self.gui)
    self.funcsToButtons()
    self.passives = [[],[]]
    self.passivesArgs = [[],[]]
    for talent in self.gs.passives[0]:
      pureTalent = (talent[0],talent[1])
      self.passives[0].append(self.gs.pi[0].tree.getAb[pureTalent])
      self.passivesArgs[0].append(None)
    for talent in self.gs.passives[1]:
      pureTalent = (talent[0],talent[1])
      self.passives[1].append(self.gs.pi[1].tree.getAb[pureTalent])
      self.passivesArgs[1].append(None)
    self.mus = UI.SFX()
    self.gui.InitializeGameWindow()
    self.cursor = pg.cursors.arrow  # default cursor
    self.playerDrawOffer = None #player that last offered draw
    self.drawOffersLeft = [3, 3] #players only get 3 per game
    self.turnsSinceDrawOffer = [7, 7] #when larger than 6 can offer draw
    self.canDrawOffer = [True, True]
    self.sqClicked = []  # tracks what squares were clicked
    self.possibleMoves = [] #switches sqClicked logic function when not empty
    self.moveMade = False  # was a move made
    self.FPS = 30  # max frames per second set
    self.clock = pg.time.Clock()
    #still setting up initial board.
    self.setup = False
    if len(self.gs.starterEnhancements[0]) > 0:
      self.setup = True
      self.gs.clock[0].setTime(0,10)
    if len(self.gs.starterEnhancements[1]) > 0:
      self.setup = True
      self.gs.clock[1].setTime(0,10)
    if self.setup == False:
      self.gs.getLegalMoves()

  '''
  Instantiates buttons and popups.  Passes functions to buttons, and buttons to popups
  '''
  def funcsToButtons(self):
    #create incomplete button and popup instances
    self.gui.instantiateButtons()
    self.gui.instantiatePopups()
    self.numWAbs = 0
    self.numBAbs = 0
    #add appropriate functions to buttons
    #add appropriate buttons to popups
    func = []
    args = []
    hFunc = []
    hArgs = []
    offHFunc = []
    for i in range(len(self.gui.buttons)):
      func.append(None)
      args.append(None)
      hFunc.append(None)
      hArgs.append(None)
      offHFunc.append(None)
    func[0] = self.drawOffer
    args[0] = 'w'
    func[1] = self.resign
    args[1] = 'w'
    func[2] = self.drawOffer
    args[2] = 'b'
    func[3] = self.resign
    args[3] = 'b'
    func[4] = self.drawAccepted
    func[5] = self.drawDeclined
    #get white ability button functions
    j = 0
    if self.gs.powers[0]:
      for i,talent in enumerate(self.gs.powers[0]):
        pureTalent = (talent[0],talent[1])
        func[i+6] = self.gs.pi[0].tree.getAb[pureTalent]
        hFunc[i+6] = self.gui.popups[4].openPopup
        offHFunc[i+6] = self.gui.popups[4].closePopup
        txt = self.gs.pi[0].tree.talentName[pureTalent]
        txt += '\n' + self.gs.pi[0].tree.talentDesc[pureTalent]
        hArgs[i+6] = [txt]
        j = i+1
        self.gui.Button.active[i+6] = True
        self.gui.Button.clickable[i+6] = True
        self.numWAbs += 1
        #change self.gui.buttons[i+6] property here for powers
        #maybe shape, maybe add a second rectangle, maybe size?
        #can pygame draw circle in rectangular area?
    if self.gs.enhancements[0]:
      for i,talent in enumerate(self.gs.enhancements[0]):
        pureTalent = (talent[0],talent[1])
        func[j+i+6] = self.gs.pi[0].tree.getAb[pureTalent]
        hFunc[j+i+6] = self.gui.popups[4].openPopup
        offHFunc[j+i+6] = self.gui.popups[4].closePopup
        txt = self.gs.pi[0].tree.talentName[pureTalent]
        txt += '\n' + self.gs.pi[0].tree.talentDesc[pureTalent]
        hArgs[j+i+6] = [txt]
        self.gui.Button.active[j+i+6] = True
        self.gui.Button.clickable[j+i+6] = True
        self.numWAbs += 1
        
    #get black ability button functions
    j = 0
    if self.gs.powers[1]:
      for i,talent in enumerate(self.gs.powers[1]):
        pureTalent = (talent[0],talent[1])
        func[i+11] = self.gs.pi[1].tree.getAb[pureTalent]
        hFunc[i+11] = self.gui.popups[4].openPopup
        offHFunc[i+11] = self.gui.popups[4].closePopup
        txt = self.gs.pi[1].tree.talentName[pureTalent]
        txt += '\n' + self.gs.pi[1].tree.talentDesc[pureTalent]
        hArgs[i+11] = [txt]
        j = i+1
        self.gui.Button.active[i+11] = True
        self.numBAbs += 1
        #change self.gui.buttons[i+6] property here for powers
    if self.gs.enhancements[1]:
      for i,talent in enumerate(self.gs.enhancements[1]):
        pureTalent = (talent[0],talent[1])
        func[j+i+11] = self.gs.pi[1].tree.getAb[pureTalent]
        hFunc[j+i+11] = self.gui.popups[4].openPopup
        offHFunc[j+i+11] = self.gui.popups[4].closePopup
        txt = self.gs.pi[1].tree.talentName[pureTalent]
        txt += '\n' + self.gs.pi[1].tree.talentDesc[pureTalent]
        hArgs[j+i+11] = [txt]
        self.gui.Button.active[j+i+11] = True
        self.numBAbs +=1
    
    #white portrait click function
    func[16] = self.gui.popups[5].openPopup
    txt = ''
    for talent in self.gs.pi[0].talents:
      pureTalent = (talent[0],talent[1])
      txt += '\n' + self.gs.pi[0].tree.talentName[pureTalent]
      txt += '\n' + self.gs.pi[0].tree.talentDesc[pureTalent]
    args[16] = [txt]
    
    #black portrait click function
    func[17] = self.gui.popups[5].openPopup
    txt = ''
    for talent in self.gs.pi[1].talents:
      pureTalent = (talent[0],talent[1])
      txt += '\n' + self.gs.pi[1].tree.talentName[pureTalent]
      txt += '\n' + self.gs.pi[1].tree.talentDesc[pureTalent]
    args[17] = [txt]

    #give buttons functions
    for i in range(len(self.gui.buttons)):
      self.gui.buttons[i].getFunctions(func[i], args[i], hFunc[i], hArgs[i], offHFunc[i])
    #give popups buttons
    pButtons = [None]*len(self.gui.popups) #list of buttons for each popup
    #right now only draw offer popup has yes and no buttons
    pButtons[0] = [self.gui.buttons[4], self.gui.buttons[5]]
    for i in range(len(self.gui.popups)):
      self.gui.popups[i].getButtons(pButtons[i])
    self.gui.portraits[0] = self.gui.imageDict[self.gs.whiteChampion]
    self.gui.portraits[1] = self.gui.imageDict[self.gs.blackChampion]
    self.gui.buttons[16].image = self.gui.portraits[0]
    self.gui.buttons[17].image = self.gui.portraits[1]
    self.gui.players[0].updatePlayerUI(self.gs.pi[0],self.gui.buttons[16])
    self.gui.players[1].updatePlayerUI(self.gs.pi[1],self.gui.buttons[17])

  '''
  Run once per turn after gs.getlegalmoves()
  '''
  def updateClickable(self):
    clickable = self.gui.Button.clickable
    #update only abilities that each player has
    for i in range(self.numWAbs):
      clickable[6+i] = not clickable[6+i]
    for i in range(self.numBAbs):
      clickable[11+i] = not clickable[11+i]

  def undo(self):
    if len(self.gs.moveLog) > 0:
      if 1 < len(self.gs.bsLog) <= 4:
        self.gs.undoMove()
        self.gui.updateMoveTexts(self.gs)
        self.updateClickable()

  '''
  after move made do this
  '''
  def update(self):
    # get move times and store in moveTimes list
    pt = self.gs.bs.playerTurn
    self.gs.clock[0].update(0 == pt)
    self.gs.clock[1].update(0 != pt)
    #if opponent offered a draw and you moved a piece, reject offer
    if (self.playerDrawOffer == self.gs.bs.opp
        and self.gui.Popup.active[0]):
      self.drawDeclined()
    self.turnsSinceDrawOffer[pt] += 1
    self.drawOfferUpdate()
    self.updateClickable()
    self.gs.endTurn()
    self.gui.updateMoveTexts(self.gs)
    
  '''
  at end of every frame do this
  '''
  def endFrame(self):
    #stop updating time when gameover
    if not self.gs.gameOver:
      if self.gs.clock[0].tick() <= 0:
        if not self.setup:
          self.gs.gameOverCheck(noTime = [True, False])
      elif self.gs.clock[1].tick() <= 0:
        if not self.setup:
          self.gs.gameOverCheck(noTime = [False, True])
    # draw board, pieces, animate moves, etc
    self.gui.drawAll(self.gs, self.moveMade, self.sqClicked)
    if self.gs.gameOver:
      self.gui.endGameScreen(self.gs.gameOverText)
    dirtyRects = UI.GameGraphics.dirtyRects
    # reset variables each frame
    self.moveMade = False
    self.gs.powerUsed = False 
    if not self.setup:
      #runs player passives
      self.runPassives(self.gs.bs.playerTurn)
      #runs opp passives
      self.runPassives(~self.gs.bs.playerTurn)
    #print(len(UI.GameGraphics.dirtyRects))
    pg.display.update(dirtyRects)  # updates python window, must constantly update
    self.clock.tick(self.FPS)  # keeps display update rate at desired FPS

  # handles resignation button click
  def resign(self, player):
    if player == 'w':
      res = [True, False]
    else:
      res = [False, True]
    self.gs.gameOverCheck(resigns = res)
    print(self.gs.gameOverText)
    return False

  # handles draw offer button click
  def drawOffer(self, player):
    txt = "offers a draw. Do you accept?"
    if player == 'w':
      txt = "White " + txt
    elif player == 'b':
      txt = "Black " + txt
    self.playerDrawOffer = player
    canDraw = self.canDrawOffer[0] if player == 'w' else self.canDrawOffer[1]
    if canDraw:
      self.gui.popups[0].openPopup(txt)
      live = False #draw offer button has done its job and activated a popup
    else:
      txt = "Unable to offer draw."
      self.gui.popups[1].openPopup(txt)
      self.gui.popups[1].closeTime = pg.time.get_ticks()
      self.gui.popups[1].toClose = True
      live = False
    return live

  def drawAccepted(self):
    self.gs.draw[0] = True  # draw by agreement
    self.gs.gameOverCheck()
    self.gui.popups[0].closePopup()
    return False

  def drawDeclined(self):
    txt = "Draw offer declined."
    self.gui.popups[0].closePopup()
    self.gui.popups[1].openPopup(txt)
    self.gui.popups[1].closeTime = pg.time.get_ticks()
    self.gui.popups[1].toClose = True
    if self.playerDrawOffer == 'w':
      self.turnsSinceDrawOffer[0] = 0
      self.drawOffersLeft[0] -= 1
      self.canDrawOffer[0] = False
      live = False
    else:
      self.turnsSinceDrawOffer[1] = 0
      self.drawOffersLeft[1] -= 1
      self.canDrawOffer[1] = False
      live = False
    return live
      
  def drawOfferUpdate(self):
    if self.drawOffersLeft[0] > 0 and self.turnsSinceDrawOffer[0] > 6:
      self.canDrawOffer[0] = True
    else:
      self.canDrawOffer[0] = False
    if self.drawOffersLeft[1] > 0 and self.turnsSinceDrawOffer[1] > 6:
      self.canDrawOffer[1] = True
    else:
      self.canDrawOffer[1] = False

  @staticmethod
  def delayClosePopup(delay, popup):
    dt = (pg.time.get_ticks() - popup.closeTime) // 1000
    if dt >= int(delay): #after delay seconds
      popup.closePopup()
      popup.toClose = False

  def runPassives(self, player):
    for passive, args in zip(self.passives[player],
                             self.passivesArgs[player]):
      if args == None:
        passive()
      else:
        passive(*args)

#run game only if module is main5
if __name__ == "__main__":
  asyncio.run(main())
