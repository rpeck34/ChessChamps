import pygame as pg
import pygame_menu as pgm
import math #for correct distance between squares, need sqrt
import re #need for . and * wildcards

'''
TODO: Need a menu screen, achievements screen, talents screen, player screen info and 
settings and some more popup/drop down menus for main game UI.  The logic for which screen
will be dealt with in main loop.  On each screen there will be buttons to click
and keys to press that will navigate to another screen or drop down/ bring up a 
pop up menu
'''

'''
Graphics for playing game
'''
class GameGraphics:
  dirtyRects = []
  def __init__(self, bs):
    self.NUM_ROW = bs.numR
    self.NUM_COL = bs.numC
    self.SIZE = self.BOARD_WIDTH, self.BOARD_HEIGHT = 512, 512  # pixel dimensions of game screen
    self.SQ_SIZE = self.BOARD_WIDTH//self.NUM_ROW #pixel dimension of chess squares
    self.BOARD_WIDTH = self.BOARD_WIDTH
    self.BOARD_HEIGHT = self.BOARD_HEIGHT
    self.MOVE_LOG_WIDTH = self.BOARD_WIDTH//2
    self.MOVE_LOG_HEIGHT = self.BOARD_HEIGHT
    self.UI_WIDTH = self.BOARD_WIDTH//2
    self.UI_HEIGHT = self.BOARD_HEIGHT
    self.WIDTH = self.BOARD_WIDTH+self.UI_WIDTH+self.MOVE_LOG_WIDTH
    self.HEIGHT = self.BOARD_HEIGHT
    self.screen = pg.display.set_mode((self.WIDTH,self.HEIGHT)) #make pygames window
    COLOUR1 = pg.Color('white')  # first board square colour
    COLOUR2 = pg.Color('gray')  # second board square colour
    self.COLOURS = (COLOUR1, COLOUR2)
    self.PATH = "C:\\Users\\rpeck\\Documents\\Programming\\GitHub\\ChessProject\\PythonChess\\Art"
    self.imageDict = {'wP0': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'wP1': pg.image.load(self.PATH+"\\Pieces\\wPGold.PNG").convert_alpha(),
                     'wN0': pg.image.load(self.PATH+"\\Pieces\\wN.PNG").convert_alpha(),
                     'wN1': pg.image.load(self.PATH+"\\Pieces\\wNGold.PNG").convert_alpha(),
                     'wB0': pg.image.load(self.PATH+"\\Pieces\\wB.PNG").convert_alpha(),
                     'wB1': pg.image.load(self.PATH+"\\Pieces\\wBGold.PNG").convert_alpha(),
                     'wR0': pg.image.load(self.PATH+"\\Pieces\\wR.PNG").convert_alpha(),
                     'wR1': pg.image.load(self.PATH+"\\Pieces\\wRGold.PNG").convert_alpha(),
                     'wQ0': pg.image.load(self.PATH+"\\Pieces\\wQ.PNG").convert_alpha(),
                     'wQ1': pg.image.load(self.PATH+"\\Pieces\\wQGold.PNG").convert_alpha(),
                     'wK0': pg.image.load(self.PATH+"\\Pieces\\wK.PNG").convert_alpha(),
                     'wK1': pg.image.load(self.PATH+"\\Pieces\\wKGold.PNG").convert_alpha(),
                     'bP0': pg.image.load(self.PATH+"\\Pieces\\bP.PNG").convert_alpha(),
                     'bP1': pg.image.load(self.PATH+"\\Pieces\\bPGold.PNG").convert_alpha(),
                     'bN0': pg.image.load(self.PATH+"\\Pieces\\bN.PNG").convert_alpha(),
                     'bN1': pg.image.load(self.PATH+"\\Pieces\\bNGold.PNG").convert_alpha(),
                     'bB0': pg.image.load(self.PATH+"\\Pieces\\bB.PNG").convert_alpha(),
                     'bB1': pg.image.load(self.PATH+"\\Pieces\\bBGold.PNG").convert_alpha(),
                     'bR0': pg.image.load(self.PATH+"\\Pieces\\bR.PNG").convert_alpha(),
                     'bR1': pg.image.load(self.PATH+"\\Pieces\\bRGold.PNG").convert_alpha(),
                     'bQ0': pg.image.load(self.PATH+"\\Pieces\\bQ.PNG").convert_alpha(),
                     'bQ1': pg.image.load(self.PATH+"\\Pieces\\bQGold.PNG").convert_alpha(),
                     'bK0': pg.image.load(self.PATH+"\\Pieces\\bK.PNG").convert_alpha(),
                     'bK1': pg.image.load(self.PATH+"\\Pieces\\bKGold.PNG").convert_alpha(),
                     'blw': pg.image.load(self.PATH+"\\Pieces\\BlindSq.PNG").convert_alpha(),
                     'blb': pg.image.load(self.PATH+"\\Pieces\\BlindSq.PNG").convert_alpha(),
                     'wh1': pg.image.load(self.PATH+"\\Terrain\\wormholeWorm1.PNG").convert_alpha(),
                     'wh2': pg.image.load(self.PATH+"\\Terrain\\wormholeWorm2.PNG").convert_alpha(),
                     'wh3': pg.image.load(self.PATH+"\\Terrain\\wormholeWorm3.PNG").convert_alpha(),
                     'wh4': pg.image.load(self.PATH+"\\Terrain\\wormholeWorm4.PNG").convert_alpha(),
                     'Warlock': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Rogue': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Paladin': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Priest': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Marksman': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Mage': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha(),
                     'Warrior': pg.image.load(self.PATH+"\\Pieces\\wP.PNG").convert_alpha()}
    self.animate = True
    self.GAMENAME = "Chess Champs"  # name of game

    self.moveLogFont = pg.font.SysFont("Arial", 14, False, False)
    self.moveTexts = []
    self.UIRect = pg.Rect(self.BOARD_WIDTH, 0, self.UI_WIDTH, self.UI_HEIGHT)
    self.timerW = self.UI_WIDTH // 4
    self.timerH = self.UI_HEIGHT // 10
    timerPosX = self.BOARD_WIDTH + 3 * self.UI_WIDTH // 8
    offsetY = self.BOARD_HEIGHT // 8  # how much timers are offset from center vertically
    whiteTimerPosY = self.BOARD_HEIGHT // 2 + offsetY
    blackTimerPosY = self.BOARD_HEIGHT // 2 - offsetY - self.timerH
    whiteTimerRect = pg.Rect(timerPosX, whiteTimerPosY, self.timerW, self.timerH)
    blackTimerRect = pg.Rect(timerPosX, blackTimerPosY, self.timerW, self.timerH)
    self.timerRect = [whiteTimerRect, blackTimerRect]

    self.Button = Button #the actual class
    self.Button.counter = 0 #reset counter
    self.buttonsR = []
    self.buttonsC = []
    self.buttonsT = []
    self.buttonsI = []
    self.buttons = [] #starts empty then is added by instantiateButtons function

    self.Popup = Popup # actual popup class
    self.Popup.counter = 0 #reset counter
    self.popupsR = []
    self.popupsB = []
    self.popups = [] #start empty then is added by instantiatePopups function
    
    #update in main, give to buttons 17 and 18
    self.portraits = [None,None] #champion portrait images

    popupW = self.UI_WIDTH // 2
    popupH = self.UI_HEIGHT // 10
    popupX = self.BOARD_WIDTH+self.UI_WIDTH//2 - popupW//2
    popupY = self.BOARD_HEIGHT//2 - popupH//2
    rect1 = pg.Rect(self.BOARD_WIDTH,self.BOARD_HEIGHT-3*popupH//2,2*popupW,popupH)
    rect2 = pg.Rect(self.BOARD_WIDTH,popupH//2,2*popupW,popupH)
    expRect1 = pg.Rect(self.BOARD_WIDTH,self.BOARD_HEIGHT-3*popupH//2,
                       2*popupW,popupH//5)
    expRect2 = pg.Rect(self.BOARD_WIDTH,3*popupH//2-popupH//5,
                       2*popupW,popupH//5)
    #rating, class name, player name, etc.  Call update in main
    self.players=[PlayerUI(rect1,expRect1),PlayerUI(rect2,expRect2)]
    self.moveLogScrollbar = None
    self.highlightable = [[True for i in range(self.NUM_COL[i])] for i in range(self.NUM_ROW)]

  '''
  pygame doesn't support multi-line text rendering. Need this helper function 
  from stack overflow.  NOTE: max_width is not the width of the text box,
  but the lartest pixel position in the x axis that the text image can reach.
  CAN IMPROVE IN FUTURE BY ADDING A CENTERING OPTION.  TEXT IS ADDED FROM CENTER
  OF TEXT BOX REGION OUT IN BOTH HORIZONTAL AND VERTICAL DIRECTIONS
  '''
  @staticmethod
  def blit_text(screen, pos, maxwh, text, font, colour=pg.Color('black')):
    # 2D array where each row is a list of words.
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = maxwh
    x, y = pos
    for line in words:
      for word in line:
        word_surface = font.render(word, 0, colour)
        word_width, word_height = word_surface.get_size()
        if x + word_width >= max_width:
          x = pos[0]  # Reset the x.
          y += word_height  # Start on new row.
        screen.blit(word_surface, (x, y))
        x += word_width + space
      x = pos[0]  # Reset the x.
      y += word_height  # Start on new row.
      
  '''
  Change pygame icon and name of game
  '''
  def InitializeGameWindow(self):
    ICON = pg.image.load(self.PATH + "\\Pieces\\wK.PNG")  # saves image in icon var
    pg.display.set_icon(ICON)  # pygames snake replacement in pop-up window
    pg.display.set_caption(self.GAMENAME)  # title of pygames window

  '''
  draws board
  '''
  def drawBoard(self, bs, legalMoves, sqClicked, validSqs):
    board = bs.board
    for row in range(bs.numR):
      for col in range(bs.numC[row]):
        # create square on board
        rectObj = pg.Rect(self.SQ_SIZE * col, self.SQ_SIZE * row, self.SQ_SIZE, self.SQ_SIZE)
        #always update squares
        self.dirtyRects.append(rectObj)
        rectCol = self.COLOURS[(row + col) % 2]
        pg.draw.rect(self.screen, rectCol, rectObj)
        #draw terrain
        terrainIm = bs.sq[(row,col)].terrainIm
        if terrainIm != '':
          self.screen.blit(self.imageDict[terrainIm],rectObj)
    if len(validSqs) > 0: #if we are using an ability, highlight these squares
      for row in range(bs.numR):
        for col in range(bs.numC[row]):
          if (row,col) in validSqs:
            self.highlightSquare((row,col), pg.Color(0, 255, 0, a=100))
          else:
            self.highlightSquare((row,col), pg.Color(255, 0, 0, a=100))

    else: #look at piece moves
      # if the square clicked has a piece on it, highlight possible moves
      if not sqClicked == []:
        self.highlightSquare(sqClicked[-1], pg.Color(255, 255, 0, a=100))
        if board[sqClicked[-1][0]][sqClicked[-1][1]] != '--':
          for move in legalMoves:
            if move.startSq == sqClicked[-1]:  # if move started on clicked square
              endSq = move.endSq
              self.highlightSquare(endSq, pg.Color(255, 0, 0, a=100))

  '''
  highlights clicked square on board.
  '''
  def highlightSquare(self, pos, colour):
    row = pos[0]
    col = pos[1]
    if self.highlightable[row][col] == True:
      highlightSurf = pg.Surface((self.SQ_SIZE, self.SQ_SIZE))
      highlightSurf.fill(colour)
      highlightSurf.set_alpha(100)
      highlightObj = pg.Rect(self.SQ_SIZE * col, self.SQ_SIZE * row, self.SQ_SIZE, self.SQ_SIZE)
      self.screen.blit(highlightSurf, highlightObj)
      self.highlightable[row][col] = False

  '''
  Make cooler animations.
  '''
  def drawPieces(self, gs, moveMade, sqClicked):
    for row in range(gs.bs.numR):
      for col in range(gs.bs.numC[row]):
        #empty vision means dont draw piece
        if gs.bs.sq[(row,col)].pc:
          vision = gs.bs.sq[(row,col)].pc.vision[gs.bs.playerTurn]
          gold = gs.bs.sq[(row,col)].pc.gold
          if vision != '--':
            piece = self.imageDict[vision+str(gold)]
            self.screen.blit(piece, (self.SQ_SIZE * col, self.SQ_SIZE * row))

    if self.animate and moveMade:  # while we allow animations and a move was made
      move = gs.moveLog[-1]
      #don't animate power abilities, at least not yet
      #later on they will have their own specialMove animate function
      if not move.specialMoves[3]:
        if len(move.animateList) > 0: #multi-animation move
          if move.castle:
            self.animateMove(gs, move, sqClicked)
            self.animateMove(gs, move.rookMove, sqClicked)
            # changes board state for castle move appropriately
            gs.makeMove(move.rookMove, stealth = True)
          else: #not a castle move
            #each path is a separate move to animate
            for path in move.animateList: 
              #print(path.chessNotation())
              self.animateMove(gs, path, sqClicked, multiMove = True)
        else:
          self.animateMove(gs, move, sqClicked)

  '''
  animates moves
  '''
  def animateMove(self, gs, move, sqClicked, multiMove = False):
    #seperate paths making up a full move can be passed one at a time
    #to be animated consecutively using move.  However, each animation
    #needs to know full move beginning and final squares to properly
    #block the moving piece and the captured piece while animating
    #That is why this info is taken from the movelog and not the
    #individual moves passed in.
    board = gs.bs.board
    gs.clock[gs.bs.playerTurn].pause = True
    pieceMoved = move.pieceMoved
    pieceCaptured = move.pieceCaptured
    startCol = move.startCol
    startRow = move.startRow
    endCol = move.endCol
    endRow = move.endRow
    capCol = move.capCol
    capRow = move.capRow
    begCol = startCol
    begRow = startRow
    finCol = endCol
    finRow = endRow
    if multiMove:
      fullMove = gs.moveLog[-1]
      begCol = fullMove.startCol
      begRow = fullMove.startRow
      finCol = fullMove.endCol
      finRow = fullMove.endRow
      pieceCaptured = fullMove.pieceCaptured
    if pieceMoved != '--':
      gold = str(gs.bsLog[-1].gold[finRow][finCol])
      pieceMovedIm = self.imageDict[pieceMoved
                                  + gold]
    if pieceCaptured != '--':
      pieceCapturedIm = self.imageDict[pieceCaptured + gold]
      
    # animate the moving piece
    dR = endRow - startRow
    dC = endCol - startCol
    framesPerSquare = 10
    frameCount = min(math.sqrt(dR ** 2 + dC ** 2) * framesPerSquare, 20)
    for frame in range(int(frameCount) + 1):
      gs.clock[gs.bs.playerTurn].tick() #update time during animations
      # each frame redraw entire board
      self.drawBoard(gs.bs, gs.legalMoves,
                     sqClicked, gs.validSqs)  
      self.drawUI(gs)
      self.drawMoveLog(gs)  # draw each of these each frame of animation
      # each frame redraw all pieces
      for row in range(gs.bs.numR):
        for col in range(gs.bs.numC[row]):
          #empty vision means dont draw piece
          if gs.bs.sq[(row,col)].pc:
            vision = gs.bs.sq[(row,col)].pc.vision[gs.bs.playerTurn]
            if vision != '--':
              gold = gs.bs.sq[(row,col)].pc.gold
              piece = self.imageDict[vision+str(gold)]
              self.screen.blit(piece, (self.SQ_SIZE * col, self.SQ_SIZE * row))
      r, c = ((startRow + dR * frame / frameCount,
               startCol + dC * frame / frameCount))
      # draw empty square over where animated piece is
      rectObj = pg.Rect(self.SQ_SIZE * begCol, self.SQ_SIZE * begRow, self.SQ_SIZE, self.SQ_SIZE)
      rectCol = self.COLOURS[(begRow + begCol) % 2]
      pg.draw.rect(self.screen, rectCol, rectObj)
      # draw empty square over where move is ended
      rectObj = pg.Rect(self.SQ_SIZE * finCol, self.SQ_SIZE * finRow, self.SQ_SIZE, self.SQ_SIZE)
      rectCol = self.COLOURS[(finRow + finCol) % 2]
      pg.draw.rect(self.screen, rectCol, rectObj)
      # if ranged move, also draw square over captured piece
      if move.specialMoves[0]:
        rectObj = pg.Rect(self.SQ_SIZE * capCol, self.SQ_SIZE * capRow, self.SQ_SIZE, self.SQ_SIZE)
        rectCol = self.COLOURS[(capRow + capCol) % 2]
        pg.draw.rect(self.screen, rectCol, rectObj)
      if pieceCaptured != '--':
        # draw captured piece on captured square until animation finishes
        self.screen.blit(pieceCapturedIm, (self.SQ_SIZE * capCol, self.SQ_SIZE * capRow))
      # draw moving piece
      self.screen.blit(pieceMovedIm, (self.SQ_SIZE * c, self.SQ_SIZE * r))

      gs.clock[gs.bs.playerTurn].pause = False
      gs.clock[gs.bs.playerTurn].lastMoveStart = pg.time.get_ticks()
      pg.display.flip()  # update screen with minimal changes
      pg.time.Clock().tick(60)  # 60 fps or less

  '''
  Draws the UI and player timers.
  '''
  def drawUI(self, gs):
    font = self.moveLogFont
    #draw rectangle for UI space
    pg.draw.rect(self.screen, pg.Color('brown'), self.UIRect)
    
    #draw timer rectangles
    pg.draw.rect(self.screen, pg.Color('white'), self.timerRect[0])
    pg.draw.rect(self.screen, pg.Color('white'), self.timerRect[1])
    wCharges = gs.abilities[0].charges
    bCharges = gs.abilities[1].charges

    #draw timer text on timers
    #retrieve these from gs from clock/timer class
    whiteTime = str(gs.clock[0])
    blackTime = str(gs.clock[1])
    colourW = pg.Color('red') if gs.clock[0].timeRemaining <= 20 else pg.Color('black')
    colourB = pg.Color('red') if gs.clock[1].timeRemaining <= 20 else pg.Color('black')
    whiteTimerT = font.render(whiteTime, True, colourW)
    blackTimerT = font.render(blackTime, True, colourB)
    centerX = self.timerW // 2 - whiteTimerT.get_rect().width // 2
    centerY = self.timerH // 2 - whiteTimerT.get_rect().height // 2
    whiteTimerTLoc = self.timerRect[0].move(centerX, centerY)
    centerX = self.timerW // 2 - blackTimerT.get_rect().width // 2
    centerY = self.timerH // 2 - blackTimerT.get_rect().height // 2
    blackTimerTLoc = self.timerRect[1].move(centerX, centerY)
    self.screen.blit(whiteTimerT, whiteTimerTLoc)
    self.dirtyRects.append(whiteTimerTLoc)
    self.screen.blit(blackTimerT, blackTimerTLoc)
    self.dirtyRects.append(blackTimerTLoc)

    #draw playerUI
    self.players[0].draw(self.screen)
    self.dirtyRects.append(self.players[0].dirtyRects)
    self.players[1].draw(self.screen)
    self.dirtyRects.append(self.players[1].dirtyRects)
    
    #draw all active popups
    for popup, active in zip(self.popups, self.Popup.active):
      if active:
        popup.draw(self.screen)
        self.dirtyRects.append(popup.dirtyRects1)
        self.dirtyRects.append(popup.dirtyRects2)

    #draw all active buttons
    for button, active in zip(self.buttons, self.Button.active):
      #if button should be drawn
      if active:
        self.dirtyRects.append(button.dirtyRects1)
        if button.num in range(6,16):
          #if w power ability
          if button.num in range(6,11):
            charges = wCharges[button.func]
          elif button.num in range(11,16):
            charges = bCharges[button.func]
          button.draw(self.screen, flag = charges)
          self.dirtyRects.append(button.dirtyRects2)
        #buttons that aren't power abilities
        else:
          button.draw(self.screen)
          self.dirtyRects.append(button.dirtyRects2)

  '''
  Advance upon current move log
  '''
  def drawMoveLog(self, gs):
    font = self.moveLogFont
    moveLogRect = pg.Rect(self.BOARD_WIDTH + self.UI_WIDTH, 0,
                          self.MOVE_LOG_WIDTH, self.MOVE_LOG_HEIGHT)
    pg.draw.rect(self.screen, pg.Color('black'), moveLogRect)
    moveLog = gs.moveLog
                
    movesPerRow = 1
    padding = 5
    textY = padding
    lineSpacing = 2
    for i in range(0, len(self.moveTexts), movesPerRow):
      text = ""
      for j in range(movesPerRow):
        if i + j < len(self.moveTexts):
          text += self.moveTexts[i + j]
      textObject = font.render(text, True, pg.Color('white'))
      #if textY > self.UI_HEIGHT:
      self.moveLogScrollbar.active = True
      scrolled = self.moveLogScrollbar.scroll()
      #print(scrolled)
      textY += scrolled
      self.moveLogScrollbar.draw(self.screen)
      
      textLocation = moveLogRect.move(padding, textY)
      self.screen.blit(textObject, textLocation)
      self.dirtyRects.append(textLocation)
      textY += textObject.get_height() + lineSpacing

  '''
  Run in main after move to give name of move to moveLog
  '''
  def updateMoveTexts(self, gs):
    self.moveTexts.clear()
    moveNames = gs.moveNames
    clock = gs.clock
    #Instead of drawing all moves every frame
    if len(moveNames) > 0:
      lastMove = gs.moveLog[-1]
      #lots of power moves don't land on board, which causes error
      if lastMove.power == False:
        #stealth logic, only show move log if last move was not stealth piece move
        if gs.bs.sq[lastMove.endSq].pc:
          for e in gs.bs.sq[lastMove.endSq].pc.effects:
            if 'st' in e:
              return #no moveTexts to add to moveLog
            #if decoy piece moved
            if 'dc' in e:
              #get linked decoy piece
              for link in gs.bs.sq[lastMove.endSq].pc.link:
                if link[0] == 'dc':
                  #this is the decoy piece
                  piece = gs.bs.sq[link[1]].pc.piece
                  #permanently change the piece moved in the last move in the move log
                  lastMove.pieceMoved = piece
    for i in range(0, len(moveNames), 2):
      moveName = moveNames[i]
      moveString = (str(i // 2 + 1) + ". " +
                    moveName + " ")
      if i + 1 < len(moveNames):  # if black made a move after white, add it on
        moveName = moveNames[i + 1]
        moveString += moveName + "  "
        #add move times at end
        moveString += clock[0].timeStr(clock[0].moveTimes[i//2]) + " | "
        moveString += clock[1].timeStr(clock[1].moveTimes[i//2])
      self.moveTexts.append(moveString)    
  
  '''
  Draws text when game is over.
  TODO:
  Make end game text more interesting/make it a popup
  '''
  def endGameScreen(self, text):
    font = pg.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, pg.Color('Gray'))
    textLocation = pg.Rect(0, 0, self.BOARD_WIDTH, self.BOARD_HEIGHT).move(self.BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                 self.BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    self.screen.blit(textObject, textLocation)
    self.dirtyRects.append(textLocation)
    textObject = font.render(text, 0, pg.Color('Black'))
    textLocation.move(2, 2)
    self.screen.blit(textObject, textLocation)
    self.dirtyRects.append(textLocation)
    
  '''
  draws all graphics for chess game
  '''
  def drawAll(self, gs, moveMade, sqClicked):
    self.drawBoard(gs.bs, gs.legalMoves, sqClicked, gs.validSqs)
    self.drawPieces(gs, moveMade, sqClicked)
    self.drawUI(gs)
    self.drawMoveLog(gs)
    self.reset()

  '''
  Resets UI variables to prepare for next frame
  '''
  def reset(self):
    for i,row in enumerate(self.highlightable):
      for j,col in enumerate(row):
        self.highlightable[i][j] = True
    self.dirtyRects = []

  '''
  Initiates all Button classes in proper place on screen
  0) white draw
  1) white resign
  2) black draw
  3) black resign
  4) yes to draw proposal
  5) no to draw proposal
  6-10) white action bar buttons
  11-15) black action bar buttons
  16-17) white/black portraits
  18) moveLog scroll button
  '''
  def instantiateButtons(self):
    # Now draw draw and resign buttons for each player
    font = self.moveLogFont
    #wDraw, wRes, bDraw, bRes, Yes, No
    wDrawX = self.BOARD_WIDTH + self.UI_WIDTH // 8
    wDrawY = 4 * self.UI_HEIGHT // 5 - self.timerH // 2
    wDrawW = self.timerW
    wDrawH = self.timerH
    wDrawC = pg.Color('white')
    wDrawT = font.render("Draw", True, pg.Color('black'))
    wResX = self.BOARD_WIDTH + 5 * self.UI_WIDTH // 8
    wResT = font.render("Resign", True, pg.Color('black'))
    bDrawY = self.UI_HEIGHT // 5 - self.timerH // 2
    bDrawT = font.render("Draw", True, pg.Color('black'))
    bResX = wResX
    bResT = font.render("Resign", True, pg.Color('black'))
    popupW = self.UI_WIDTH // 2
    popupH = self.UI_HEIGHT // 10
    popupX = self.BOARD_WIDTH+self.UI_WIDTH//2 - popupW//2
    popupY = self.BOARD_HEIGHT//2 - popupH//2
    popupColour = pg.Color("White")
    popupFont = self.moveLogFont
    yesButtonT = popupFont.render("Yes", True, pg.Color("black"))
    noButtonT = popupFont.render("No", True, pg.Color("black"))
    yesButtonW =popupW//7
    yesButtonH = popupH//4
    yesButtonX = popupX+popupW//4 - yesButtonW//2
    yesButtonY = popupY+3*popupH//4
    noButtonX = popupX+3*popupW//4 - yesButtonW//2

    wActionH = self.UI_HEIGHT//20
    wActionW = self.UI_WIDTH//20
    wActionX = self.BOARD_WIDTH + self.UI_WIDTH//10
    delX = self.UI_WIDTH//5
    wActionY = self.UI_HEIGHT - wActionH
    bActionY = 0
    wActionC = pg.Color("green")
    wActionT = []
    for i in range(5):
      wActionT.append(font.render(str(i+1), True, pg.Color('black')))

    scrollH = wActionH
    scrollW = wActionW
    scrollX = self.WIDTH - wActionW
    scrollY = 0

    #0
    self.buttonsR.append(pg.Rect(wDrawX,wDrawY,wDrawW,wDrawH))
    self.buttonsC.append(wDrawC)
    self.buttonsT.append(wDrawT)
    self.buttonsI.append(None)
    #1
    self.buttonsR.append(pg.Rect(wResX,wDrawY,wDrawW,wDrawH))
    self.buttonsC.append(wDrawC)
    self.buttonsT.append(wResT)
    self.buttonsI.append(None)
    #2
    self.buttonsR.append(pg.Rect(wDrawX,bDrawY,wDrawW,wDrawH))
    self.buttonsC.append(wDrawC)
    self.buttonsT.append(bDrawT)
    self.buttonsI.append(None)
    #3
    self.buttonsR.append(pg.Rect(wResX,bDrawY,wDrawW,wDrawH))
    self.buttonsC.append(wDrawC)
    self.buttonsT.append(bResT)
    self.buttonsI.append(None)
    #4
    self.buttonsR.append(pg.Rect(yesButtonX,yesButtonY,yesButtonW,yesButtonH))
    self.buttonsC.append(pg.Color("green"))
    self.buttonsT.append(yesButtonT)
    self.buttonsI.append(None)
    #5
    self.buttonsR.append(pg.Rect(noButtonX,yesButtonY,yesButtonW,yesButtonH))
    self.buttonsC.append(pg.Color("red"))
    self.buttonsT.append(noButtonT)
    self.buttonsI.append(None)
    #6-10
    for i in range(5):
      self.buttonsR.append(pg.Rect(wActionX+i*delX,wActionY,wActionW,wActionH))
      self.buttonsC.append(wActionC)
      self.buttonsT.append(wActionT[i])
      self.buttonsI.append(None)
    #11-15
    for i in range(5):
      self.buttonsR.append(pg.Rect(wActionX+i*delX,bActionY,wActionW,wActionH))
      self.buttonsC.append(wActionC)
      self.buttonsT.append(wActionT[i])
      self.buttonsI.append(None)
    #16
    self.buttonsR.append(pg.Rect(self.BOARD_WIDTH,wActionY - 2*wActionH,
                                 4*wActionW,2*wActionH))
    self.buttonsC.append(None)
    self.buttonsT.append(None)
    self.buttonsI.append(self.portraits[0])
    #17
    self.buttonsR.append(pg.Rect(self.BOARD_WIDTH,bActionY + wActionH - popupH//5,
                                 4*wActionW,2*wActionH))
    self.buttonsC.append(None)
    self.buttonsT.append(None)
    self.buttonsI.append(self.portraits[1])
    #18
    self.buttonsR.append(pg.Rect(scrollX,scrollY,scrollW,scrollH))
    self.buttonsC.append(pg.Color("Gray"))
    self.buttonsT.append(None)
    self.buttonsI.append(None)

    #create the buttons
    for i in range(len(self.buttonsR)):
      self.buttons.append(self.Button(self.buttonsR[i],self.buttonsC[i],
                                      self.buttonsT[i],self.buttonsI[i]))
    self.Button.active = [True]*len(self.buttons)
    self.Button.clickable = [True]*len(self.buttons)
    self.Button.live = [False]*len(self.buttons) 

    #popup buttons for draw menu.  Don't draw or make interactable at first
    self.Button.active[4] = False
    self.Button.active[5] = False
    self.Button.clickable[4] = False
    self.Button.clickable[5] = False

    for i in range(10):
      self.Button.active[6+i] = False
      self.Button.clickable[6+i] = False
    #instantiate scrollBar
    scrollbarH = self.UI_HEIGHT
    scrollbarW = self.UI_WIDTH//20
    scrollbarX = self.WIDTH - scrollbarW
    scrollbarY = 0
    scrollRect = pg.Rect(scrollbarX,scrollbarY,scrollbarW,scrollbarH)
    self.moveLogScrollbar = Scrollbar(scrollRect,self.buttons[18])
    
  '''
  Instantiate popups
  0) draw proposal
  1) general message with no buttons
  2) white action bar
  3) black action bar
  4) talent hover info
  5) full talent info on portrait click
  '''
  def instantiatePopups(self):
    popupW = self.UI_WIDTH // 2
    popupH = self.UI_HEIGHT // 10
    popupX = self.BOARD_WIDTH+self.UI_WIDTH//2 - popupW//2
    popupY = self.BOARD_HEIGHT//2 - popupH//2

    #0
    self.popupsR.append(pg.Rect(popupX,popupY,popupW,popupH))
    #1
    self.popupsR.append(pg.Rect(popupX,popupY,popupW,popupH))
    #2
    self.popupsR.append(pg.Rect(self.BOARD_WIDTH,self.BOARD_HEIGHT - popupH//2,
                           2*popupW,popupH//2))
    #3
    self.popupsR.append(pg.Rect(self.BOARD_WIDTH,0,
                           2*popupW,popupH//2))
    #4
    self.popupsR.append(pg.Rect(self.BOARD_WIDTH,popupY - popupH//2,
                           2*popupW,2*popupH))
    #5
    self.popupsR.append(pg.Rect((self.BOARD_WIDTH - int(popupW*3.5))//2,
                                (self.BOARD_HEIGHT - popupH*10)//2,
                                 int(3.5*popupW),10*popupH))
    
    for i in range(len(self.popupsR)):
      self.popups.append(self.Popup(self.popupsR[i]))
      
    self.popups[5].clickToClose = True
    self.Popup.active = [False,False,True,True,False,False]
    
'''
Creates and draws a button with click functionality
In future, draw second darker rectangle underneath for depth?
Make highlight look nice when hovered
Use better cursors
'''
class Button():
  counter = 0
  active = [] #gets buttons that are drawn
  clickable = [] #gets buttons that are clickable
  live = [] #gets buttons currently performing their functions
  offColour = pg.Color(255, 0, 0)
  highlightColour = pg.Color(227, 174, 87, a=100) 
  pg.font.init()
  font = pg.font.SysFont("Arial", 14, False, False)
  
  def __init__(self,rect,colour,txt,image):
    self.num = self.__class__.counter
    self.__class__.counter += 1
    self.func = None
    self.args = None
    self.hFunc = None
    self.hArgs = None
    self.offHFunc = None
    self.hLive = False
    self.image = image
    self.click = False
    self.held = False
    self.hover = False
    self.clickTime = pg.time.get_ticks()
    self.hoverTime = pg.time.get_ticks()
    self.rect = rect
    self.w = rect.width
    self.h = rect.height
    self.colour1 = colour
    self.highlight = self.__class__.highlightColour
    self.txt = txt
    self.pos = None #last mouse position when clicked
    self.dirtyRects1 = self.rect
    self.dirtyRects2 = None
    if txt != None:
      centerX = self.w // 2 - self.txt.get_rect().width // 2
      centerY = self.h // 2 - self.txt.get_rect().height // 2
      self.txtLoc = self.rect.move(centerX, centerY)
      self.dirtyRects2 = self.txtLoc

  def getFunctions(self, func, args, hFunc, hArgs, offHFunc):
    self.func = func
    self.args = args
    self.hFunc = hFunc
    self.hArgs = hArgs
    self.offHFunc = offHFunc

  def draw(self, screen, flag = 1):
    if self.image == None:
      #colour when powers are out of charges
      if flag == 0:
        pg.draw.rect(screen, self.offColour, self.rect)
        #ability buttons
        if self.num in range(6,16):
          self.txt = self.font.render("0", True, pg.Color('black'))
      #default colour
      else:
        pg.draw.rect(screen, self.colour1, self.rect)
        #ability buttons
        if self.num in range(6,16):
          # if ability doesn't have charges
          if flag == -1:
            self.txt = self.font.render("", True, pg.Color('black'))
          else:
            self.txt = self.font.render(str(flag), True, pg.Color('black'))
      #highlighted rectangle if hovered over
      if self.hover:
        pg.draw.rect(screen, self.highlight, self.rect)
      #center and draw text on button
      if self.txt != None:
        screen.blit(self.txt, self.txtLoc)
    #button has image
    else:
      screen.blit(self.image, self.rect)
    
  #quicker method than clicked, runs every frame
  def checkHover(self, pos):
    self.pos = pos #mouse position
    #if hovering over button and button is clickable
    if self.__class__.clickable[self.num] and self.rect.collidepoint(pos): 
      if self.hover == False: #first frame of hovering
        self.hoverTime = pg.time.get_ticks()
      self.hover = True
      #pg.mouse.set_cursor(pg.cursors.broken_x)
      dt = (pg.time.get_ticks() - self.hoverTime)//1000
      if dt > 0 and self.hFunc != None: #after 1 sec of hovering, run hFunc
        #run only once
        if not self.hLive:
          self.hovered()
    else:
      if self.offHFunc != None:
        #run only when stopping hover
        if self.hover:
          self.offHFunc()
          self.hLive = False
      self.hover = False
    #continue running function while live
    if self.__class__.live[self.num] == True:
      self.performAction()
      
  # after button is clicked.
  def clicked(self):
    self.clickTime = pg.time.get_ticks()
    self.click = True
    self.held = True
    self.__class__.live[self.num] = not self.__class__.live[self.num]
    
  #run once upon hovering
  def hovered(self):
    if self.hArgs != None:
      self.hLive = True
      self.hFunc(*self.hArgs)
    else:
      self.hLive = True
      self.hFunc()

  def reset(self):
    self.__class__.active[self.num] = False
    self.__class__.clickable[self.num] = False
    self.__class__.live[self.num] = False

  # performs action based on function obtained from main initialization
  def performAction(self):
    #print(f'button num {self.num} live {self.live}')
    #print(f'live status {Button.live}')
    if self.func != None:
      if self.args != None:
        self.__class__.live[self.num] = self.func(*self.args)
      else:
        self.__class__.live[self.num] = self.func()
    
''' 
Makes message pop up in chat box with options to click on
'''
class Popup():
  counter = 0
  active = [] #gets popups that are drawn
  colour = pg.Color("White")
  highlightColour = pg.Color(227, 174, 87, a=100)
  pg.font.init()
  font = pg.font.SysFont("Arial", 14, False, False)

  def __init__(self,rect):
    self.num = self.__class__.counter
    self.__class__.counter += 1
    self.hover = False
    self.toClose = False #manually set to close in a delayed time
    self.clickToClose = False
    self.click = False
    self.openTime = pg.time.get_ticks()
    self.closeTime = pg.time.get_ticks()
    self.rect = rect
    self.x = rect.x
    self.y = rect.y
    self.w = rect.width
    self.h = rect.height
    self.colour = self.__class__.colour
    self.highlight = self.__class__.highlightColour
    self.font = self.__class__.font
    self.buttons = None #list of buttons that are part of popup
    self.txt = ''
    self.dirtyRects1 = self.rect
    self.dirtyRects2 = None

  def getButtons(self, buttons):
    self.buttons = buttons

  def draw(self, screen):
    #draw rectangle for popup outline
    pg.draw.rect(screen, self.colour, self.rect)
    #if self.hover:
      #pg.draw.rect(screen, self.highlight, self.rect)
    posx = self.x
    posy = self.y
    maxW = self.x + self.w
    maxH = self.h
    GameGraphics.blit_text(screen,(posx,posy),(maxW,maxH),self.txt,self.font)
    rectObj = pg.Rect(posx,posy,(maxW - posx),(maxH - posy))
    self.dirtyRects2 = rectObj

  def openPopup(self, txt):
    self.openTime = pg.time.get_ticks()
    self.txt = txt
    self.toClose = False
    self.dirtyRects1 = self.rect
    self.__class__.active[self.num] = True
    if self.buttons:
      for button in self.buttons:
        button.__class__.active[button.num] = True
        button.__class__.clickable[button.num] = True
        button.__class__.live[button.num] = False
      
  def closePopup(self):
    self.closeTime = pg.time.get_ticks()
    self.__class__.active[self.num] = False
    if self.buttons:
      for button in self.buttons:
        button.reset()
      
  #runs every frame
  def checkHover(self, pos):
    if self.rect.collidepoint(pos): #if hovering over popup
      self.hover = True
    else:
      self.hover = False

'''
Shows all useful player info in UI portion of game
'''
class PlayerUI():
  pg.font.init()
  font = pg.font.SysFont("Arial", 14, False, False)
  def __init__(self, rect, expRect):
    self.rating = 0  
    self.lvl = 0  
    self.exp = 0  # experience to next level
    self.name = "Anon"  
    self.portrait = None
    self.champion = None
    self.tree = None #player active talent info
    self.rect = rect #base area to draw playerUI on top of
    self.x = rect.x
    self.y = rect.y
    self.w = rect.width
    self.h = rect.height
    self.portraitRect = None
    self.expRect = expRect #full exp bar
    self.expBar = expRect
    self.expBarColour = pg.Color(255,0,0)
    self.colours = None
    self.txt1 = ''
    self.txt2 = ''
    self.dirtyRects = self.rect
    
  '''
  Takes a playerInfo class from Player module stored in gs and uses info
  to update playerUI
  '''
  def updatePlayerUI(self, player, button):
    self.rating = player.rating
    self.lvl = player.lvl
    self.exp = player.exp
    self.expScale = self.exp/200
    self.expBar.w = self.expScale*self.expRect.w
    self.name = player.name
    self.champion = player.champion
    self.portrait = button
    self.portraitRect = button.rect
    self.portraitW = button.rect.w
    #self.portraitW = self.portrait.image.get_rect().w
    self.tree = player.tree
    self.txt1 = '   '+str(self.name)+'   ' +str(self.rating)
    self.txt2 = '   Lvl ' + str(self.lvl)+'   '+str(self.champion)
    self.posx = self.x + self.portraitW
    self.posy1 = self.y + self.h//6
    self.posy2 = self.y + 3*self.h//6
    self.maxW = self.x + self.w
    self.maxH = self.h
    self.colours = player.colourDict[self.champion]

  '''
  portrait button is drawn separately, treated with other buttons.
  '''
  def draw(self, screen):
    #draw base rectangle for all info
    pg.draw.rect(screen, pg.Color("White"), self.rect)
    #draw background colour behind portrait
    if self.portrait != None:
      pg.draw.rect(screen, self.colours[0], self.portraitRect)
    #draw full exp bar
    pg.draw.rect(screen, pg.Color("Black"), self.expRect)
    #draw exp bar within full bar
    pg.draw.rect(screen, self.expBarColour, self.expBar)
    #draw player name and rating
    GameGraphics.blit_text(screen,(self.posx,self.posy1),
                           (self.maxW,self.maxH),self.txt1,self.font)
    #draw player level and champion name
    GameGraphics.blit_text(screen,(self.posx,self.posy2),
                           (self.maxW,self.maxH),self.txt2,self.font)

'''
Attaches to moveLog.  Becomes active once moveLog text is larger than
moveLog area.  One tricky part is that button rect has to move with
mouse once you click it.  get mouse position height and update button height
'''
class Scrollbar():
  def __init__(self, rect, button):
    self.rect = rect #empty bar for sliding bar to move within
    #button which when clicked and held moves moveLog txt up or down
    self.button = button
    self.scrollbarColour = pg.Color("White")
    self.active = False #is drawn and can be clicked if active
    self.scrollStart = None
    self.scrolled = 0
    self.delH = 0
    self.dirtyRects1 = self.rect
    
  def draw(self, screen):
    if self.active:
      pg.draw.rect(screen, self.scrollbarColour, self.rect)
      self.button.draw(screen)

  def scroll(self):
    if self.active and self.button.held:
      pos = self.button.pos
      if self.button.click:
        self.delH = pos[1] - self.button.rect.y
        self.scrollStart = self.scrolled +pos[1] - self.delH
      #tentative amount to scroll
      scroll = self.scrollStart - pos[1] + self.delH
      #button follows mouse in vertical direction
      buttonY = pos[1] - self.delH
      if buttonY < self.rect.top:
        buttonY = self.rect.top
      elif buttonY > self.rect.bottom - self.button.rect.h:
        buttonY = self.rect.bottom - self.button.rect.h
      rectY = self.button.rect.y - buttonY
      self.button.rect = pg.Rect.move(self.button.rect, 0, -rectY)
      #vertical pixel difference between scrollbar before frame
      #and current mouse position dragging scrollbar
      self.scrolled = scroll
    return self.scrolled

class SFX():
  def __init__(self):
    self.Lmusic = False
    self.vol = 0.7
    self.song1 = "song1.mp3"  # name of mp3 file of song to be played
