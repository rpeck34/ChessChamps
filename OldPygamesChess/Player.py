'''Module which keeps important information about the player character
A player will have a rank, experience, and have a class array.  The effects
of the class array talents are dealt with in PieceLogic, but the information
is stored in the PlayerInfo class'''

#just used for colour theme info
import pygame as pg

class PlayerState():
  def __init__(self):
    #all this will be retrieved from database
    self.rating = 0  # elo
    self.lvl = 0  # start at 0
    self.exp = 0  # experience to next level
    self.k = 40 #default k-factor for beginner players (used for elo)
    self.name = "Anon"  # player name
    self.stats=(0,0,0,0) #wins, losses, draws, total games
    self.champion = None
    self.talents = []
    self.talentDict = {'Warlock': WarlockTree,
                       'Rogue': RogueTree,
                       'Paladin': PaladinTree,
                       'Priest': PriestTree,
                       'Marksman': MarksmanTree,
                       'Mage': MageTree,
                       'Warrior': WarriorTree}
    #each champion has a colour theme
    self.colourDict = {'Warlock': [pg.Color(255, 0, 255), pg.Color(0, 0, 0)],
                       'Rogue': [pg.Color(255, 255, 0), pg.Color(100, 0, 100)],
                       'Paladin': [pg.Color(0, 0, 255), pg.Color(100, 100, 100)],
                       'Priest': [pg.Color(255, 0, 255), pg.Color(255, 255, 255)],
                       'Marksman': [pg.Color(0, 255, 0), pg.Color(100, 100, 0)],
                       'Mage': [pg.Color(0, 255, 255), pg.Color(100, 100, 50)],
                       'Warrior': [pg.Color(255, 0, 0), pg.Color(0, 0, 0)]}
    self.tree = None
    self.me = None
    #updates during game, tracks which gold pieces player captured
    self.goldCap = [] 
    self.achievements = []
    self.wldata = [] #wins, losses, draws
    return

  '''
  adds info to player stats after game concludes, adjusts k-factor for elo
  calculation
  '''
  def statsUpdate(self, score):
    if score == 1: #win
      self.stats = (self.stats[0]+1, self.stats[1],
                    self.stats[2], self.stats[3]+1)
    elif score == 0: #loss
      self.stats = (self.stats[0], self.stats[1]+1,
                    self.stats[2], self.stats[3]+1)
    else: #draw
      self.stats = (self.stats[0], self.stats[1],
                    self.stats[2]+1, self.stats[3]+1)
    #update k-factor.  Kind of arbitrary parameter.
    #I adjusted definition of 800/num games to give more
    #reasonable k-factors for people playing 0 to 1000 games
    kFac = 10000/self.stats[3]
    #kFac suggested range between 10 and 40.
    if kFac > 40:
      kFac = 40
    elif kFac < 10:
      kFac = 10
    self.k = kFac
  '''
  Formula to update ELO rating of player.  Use this on each player after
  game.  Input player ratings and outcome of game
  '''
  def eloUpdate(self, oppRating, score):
    #score = 1 for win, 0.5 for draw, 0 for loss
    calc = 1+10**((self.rating - oppRating)/400)
    expectedScore = 1/calc
    self.rating = self.rating + self.k*(score - expectedScore)

  '''Update talents'''
  def updateInfo(self, champion, talents, player):
    self.rating = 1650
    self.lvl = self.rating // 200
    self.exp = self.rating - 200*self.lvl
    self.name = "Ryan"
    self.champion = champion
    self.talents = talents
    self.tree = self.talentDict[self.champion](self.talents)
    self.me = player

'''
holds name and description info for each talent for each champion.
Each talent needs a name, especially abilities, so can label them
on ability bars and players understand what they can do
'''
class TalentTree():
  def __init__(self, talents):
    self.talents = talents #talent point distribution input
    self.shape = [2,2,2,2,2] #number of choices at each level of tree
    self.depth = len(self.shape) # number of levels to tree
    #Actual ability functions.  This is passed in when gs is created
    self.abilities = None
    #Links above ability functions to corresponding talent
    self.getAb = {}
    #The abilities the player has based on their talents
    self.starterEnhancements = []
    self.starterAutos = []
    self.enhancements = []
    self.powers = []
    self.autos = []
    self.passives = []
    #input talent, outputs name of input talent
    self.talentName = {}
    #input talent, output talent description
    self.talentDesc = {}

  '''
  Different for each class.  Contains name of each talent and
  description of each talent
  '''
  def treeInfo(self):
    '''
    Fill in each dictionary entry manually
    '''
    self.talentName[(1, 1)] = ''
    self.talentDesc[(1, 1)] = '''.'''
    #Manually add which talents are abilities
    self.abilities.append([(1,1)]) #if an ability

  '''
  Returns list of available abilities of champion, based on
  champion talent tree and current invested talent points.
  Used in UI to create corresponding abilities on ability bar
  '''
  def getAbilityLists(self):
    playerStarterAutos = []
    playerStarterEnhancements = []
    playerEnhancements = []
    playerPowers = []
    playerAutos = []
    playerPassives = []
    for talent in self.talents:
      #tuples not mutable, have to remake them
      pureTalent = (talent[0],talent[1])
      if pureTalent in self.starterAutos:
        playerStarterAutos.append(talent)
      elif pureTalent in self.starterEnhancements:
        playerStarterEnhancements.append(talent)
      elif pureTalent in self.enhancements:
        playerEnhancements.append(talent)
      elif pureTalent in self.powers:
        playerPowers.append(talent)
      elif pureTalent in self.autos:
        playerAutos.append(talent)
      elif pureTalent in self.passives:
        playerPassives.append(talent)
    return playerStarterAutos, playerStarterEnhancements, playerEnhancements, \
           playerPowers, playerAutos, playerPassives 

'''
Ideas to be implemented... Far in future when core of program is a well oiled machine
Ritual (priest) once a certain configuration is reached, obtain permanent buff
/something cool happens.  Ritual shapes should be religious symbols, pentagram,
and gregorian choir songs: columns are quarter note divisions, pawn quarter note,
minor piece half note, major piece whole note.
for sheet music and rows of board represent pitch.

Another foundational class idea: board spatial manipulation... where warlock is
time based this class would be able to play around with board dimensions.
Could add extra sqs, remove sqs, change pawn movement direction?
rotate board, swap 2 files, swap 2 ranks.  reflect board, some other group theory
operations on board etc.  Make board repeat so that a move off board goes back on
on other side?

Foundational idea for a class.  Lots and lots of work but very cool.
May not do....
Easiest way to implement would be to allow multiple pieces on sq.  But then
everything dealing with pc would have to loop through all pieces.
Then also the problem of making a new piece art for each possible piece combo.
Transformers: One class and one talent but don't know which one.  Wild idea:
You can move your pieces on top of each other to combine them.  Combined pieces
cannot be uncombined.  Combined piece gains moveset of both pieces.  Cannot combine
same type of piece together.  If piece combined with king, king can be captured
and this results in checkmate

Enhancement to rewind?  Can choose a VALID piece to not be affected by the rewind.
Meaning after rewind, that piece stays where it is and does not revert back to previous
state.  Only pieces that wouldn't be on top of other pieces, and not attacking enemy
king after rewind will be valid.  Can only choose OWN pieces.  This would be best done
after implementing piece class, so it is easy to grab all piece information from the
piece object from current board state as a temp variable, then give the temp var to the
reverted boardstate and fake remove the piece with the same ID.  So need ID and
piece class before could do this.  Not even that big a deal don't worry about this yet.
What about add a list to sq class that records all the sqs the piece has been to
(could easily record in place function, store before place changes)
then, add all sqs in this list for each piece to moves,att,defended and then filter
them out in getlegalMOves.  So as long as move is legal, can move to any sq piece has
visited in past for all warlock pieces.  Could make it an ability that lasts a turn or two.
Would count as an attack too so returning to sq an enemy piece is on would cap piece.
Could be used on king to get out of check?
'''
class WarlockTree(TalentTree):
  def treeInfo(self):
    self.shape = [2,2,1,2,2]
    self.talentName[(1, 1)] = 'Rewind'
    self.talentDesc[(1, 1)] = ('If not in check, use half your remaining time '
                               'to revert to the board state before your last move.')
    self.powers.append((1, 1))
    self.getAb[(1,1)] = self.abilities.a1
    
    self.talentName[(1, 2)] = 'Wormhole'
    self.talentDesc[(1, 2)] = ('Use half your remaining time to create a wormhole '
                               'on the board.  Can be placed if your king moved last '
                               'turn.  Wormholes cannot be placed on pieces.  '
                               'Only two wormhole pairs can be active at a time.')
    self.enhancements.append((1, 2))
    self.getAb[(1,2)] = self.abilities.a2

    self.talentName[(2, 1)] = 'Rot'
    self.talentDesc[(2, 1)] = ('Use half your remaining time to rot an enemy piece.  '
                               'Can\'t be used on kings or queens.  After 1/2/3 turns '
                               'for pawns/minor/major pieces, the pieces are erased '
                               'from the board.')
    self.powers.append((2, 1))
    self.getAb[(2,1)] = self.abilities.a3

    self.talentName[(2, 2)] = 'Consume'
    self.talentDesc[(2, 2)] = ('Choose an enemy piece.  For the rest of the game '
                               'when that piece moves you steal 10 seconds of your '
                               'opponent\'s time.  Takes 1 minute of your time.  '
                               'Only one piece can be consumed at a time.')
    self.enhancements.append((2, 2))
    self.getAb[(2,2)] = self.abilities.a4

    self.talentName[(3, 1)] = 'Whither'
    self.talentDesc[(3, 1)] = ('Once your opponent\'s current move time exceeds your '
                               'last move time, their time loss becomes '
                               'doubled/tripled/quadrupled until they move.')
    self.passives.append((3,1))
    self.getAb[(3,1)] = self.abilities.a5

    self.talentName[(4, 1)] = 'Drain'
    self.talentDesc[(4, 1)] = ('If you capture a piece, steal 10 seconds '
                               'from your opponent.')
    self.autos.append((4, 1))
    self.getAb[(4,1)] = self.abilities.a6

    self.talentName[(4, 2)] = 'Decay'
    self.talentDesc[(4, 2)] = ('As long as you have moved faster than your opponent '
                               'for the last 3 turns in a row, your opponent\'s '
                               'time loss rate is doubled.')
    self.autos.append((4, 2))
    self.getAb[(4,2)] = self.abilities.a7
    
    self.talentName[(5, 1)] = 'Synchronization'
    self.talentDesc[(5, 1)] = ('You and your opponent set your clocks '
                               'to the average of your remaining times.')
    self.powers.append((5, 1))
    self.getAb[(5,1)] = self.abilities.a8

    self.talentName[(5, 2)] = 'Slow'
    self.talentDesc[(5, 2)] = ('If your opponent moves a pawn, it becomes frozen '
                               'in time and they can\'t move that same pawn '
                               'for one turn.')
    self.autos.append((5, 2))
    self.getAb[(5,2)] = self.abilities.a9

class RogueTree(TalentTree):
  def treeInfo(self):
    self.shape = [2,1,2,2,2]
    #good to choose between sneak and smokebomb because combination would be strong.
    self.talentName[(1, 1)] = 'Sneak'
    self.talentDesc[(1, 1)] = ('Pawns can move forward two squares if first square '
                               'is unoccupied.  Pawns are immune to en passant and'
                               'backstab.')
    self.talentName[(1, 2)] = 'Smoke Bomb'
    self.talentDesc[(1, 2)] = ('Your opponent can no longer see any squares near'
                               'your selected pawn.  Lasts 3 turns.')
    self.enhancements.append((1, 2))
    self.getAb[(1,2)] = self.abilities.a1

    self.talentName[(2, 1)] = 'Backstab'
    self.talentDesc[(2, 1)] = ('If your pawns moved two squares and past an adjacent enemy pawn,'
                               '(in en passant position) that pawn can be removed.')
    #touch up
    self.talentName[(3, 1)] = 'Decoy'
    self.talentDesc[(3, 1)] = ('At the beginning of the game, you may'
                               'swap your king position with any one'
                               'of your other pieces without your opponent'
                               'knowing.  The opponent will not see your swap.'
                               'The decoy is over when your king is in check.')
    self.starterEnhancements.append((3, 1))
    self.getAb[(3,1)] = self.abilities.a2

    self.talentName[(3, 2)] = 'Stealth'
    self.talentDesc[(3, 2)] = 'Grant invisibility to up to 3 of your pawns.'
    self.enhancements.append((3, 2))
    self.getAb[(3,2)] = self.abilities.a3
    #Pairs well with sneak
    self.talentName[(4, 1)] = 'Vicious Stab'
    self.talentDesc[(4, 1)] = 'Your pawns can attack forwards.'

    self.talentName[(4, 2)] = 'Assassination'
    self.talentDesc[(4, 2)] = ('If an enemy piece has 3 of your pawns 1 square from it'
                               'at the end of your turn, that piece is removed.  Enemy'
                               'king assassination results in checkmate.')
    self.autos.append((4, 2))
    self.getAb[(4,2)] = self.abilities.a4
    self.talentName[(5, 1)] = 'Long-live the King!'
    self.talentDesc[(5, 1)] = ('If there is an empty square in front of your king'
                               'your nearby pawns can move one square sideways'
                               'to this square.  Pieces cannot be captured with this move.')
    #this will probably be way too strong but we'll see
    self.talentName[(5, 2)] = 'Long-live the Queen!'
    self.talentDesc[(5, 2)] = 'Your pawns promote one rank sooner.'

#no manual abilities.  This tree looks good considering
#if only one talent from each tier can be chosen
class PaladinTree(TalentTree):
  def treeInfo(self):
    self.shape = [1, 2, 2, 2, 2]
    self.talentName[(1, 1)] = 'Welcome to the Brotherhood'
    self.talentDesc[(1, 1)] = ('Your bishops are replaced with knights.')

    self.talentName[(2, 1)] = 'Joust'
    self.talentDesc[(2, 1)] = ('Your knights can snipe forwards one square.')

    self.talentName[(2, 2)] = 'Nobility'
    self.talentDesc[(2, 2)] = ('You start with 1/2 extra knights at the cost of'
                               '2/4 of your pawns.')
    self.starterAutos.append((2, 2))

    #This will probably be too strong since you can
    #make a gay formation.  Try it out though.
    self.talentName[(3, 1)] = 'White Knight'
    self.talentDesc[(3, 1)] = ('Knights defending your queen are immune to capture.')
    #This is an interesting idea since the queen typically
    #can't take out a knight attacking it.  So then the queen
    #has to run far away from the knight in order for the knight to get
    #captured
    self.talentName[(3, 2)] = 'Dark Knight'
    self.talentDesc[(3, 2)] = ('Knights that attack your opponent\'s queen are'
                               'immune to capture.')
    #What if you turn a pawn into a knight?  Should it come in with
    #this ability... I think yes. Change createPiece to allow for
    #pieces to be created with statusEffects.
    self.talentName[(4, 1)] = 'Holy Aura'
    self.talentDesc[(4, 1)] = ('Your knights are enhanced with holy power.'
                               'The first time each of your knights land near an enemy'
                               'piece, it stuns all enemy pieces within one square'
                               'for one turn.')
    
    self.talentName[(4, 2)] = 'Atonement'
    self.talentDesc[(4, 2)] = ('If an enemy piece captures your knight, that'
                               'piece is stunned for a turn.')
    #can try it out but would rather find something
    #cooler for this one.
    self.talentName[(5, 1)] = 'Purge'
    self.talentDesc[(5, 1)] = ('Enemy pieces one square from your knights are'
                               'no longer empowered and lose any special abilities'
                               'they had.')

    self.talentName[(5, 2)] = 'Retribution'
    self.talentDesc[(5, 2)] = ('If you have less than 3 knights, each of your knights'
                               'can move two knight moves in one turn.  This only affects'
                               'piece movement.')

'''
Make use of ritual formations multiple times,
These are pretty cool and might be the basis for
priest play.  These rituals will be autos that
activate automatically at turn end based on board
state.
'''
class PriestTree(TalentTree):
  def treeInfo(self):
    self.shape = [2, 2, 2, 2, 1]
    #change wording and make sure ritual
    #cannot bring piece which attacks king on that turn.
    #or squares nearby king too.
    #Never want potential to auto into checkmate.
    self.talentName[(1, 1)] = 'Resurrection'
    self.talentDesc[(1, 1)] = ('If both your bishops and knights have'
                               'horizontal reflection symmetry across the'
                               'center of the board, the ritual begins.'
                               'Every turn the ritual is satisfied brings'
                               'another captured piece back onto the board.'
                               'The empty ritual summoning squares are the'
                               '2nd rank row of pawns and at least one space'
                               'must be open to bring a piece back.  The'
                               'player can choose which piece to resurrect.')
    #3 charges (1 for pawn, 2 for minor, 3 for major piece?) or only pawns because
    #too strong
    self.talentName[(1, 2)] = 'Conversion'
    self.talentDesc[(1, 2)] = ('Enemy pawn becomes yours for the rest of the game.')

    self.talentName[(2, 1)] = 'Sermon'
    self.talentDesc[(2, 1)] = ('If all your pawns are on the same rank ...'
                               'Requires 3 or more pawns.')
                               
    self.talentName[(2, 2)] = 'Lent'
    self.talentDesc[(2, 2)] = ('When used, bans both player\'s use of abilities'
                               'for 3 turns.  One charge.')

    self.talentName[(3, 1)] = 'Prayer'
    self.talentDesc[(3, 1)] = ('While bishops have horizontal symmetry,'
                               'bishops are immune to capture.')
    #Add debuff imunity logic to validSqs considerations
    #For things like rot and consume.  Don't allow ability
    #to be used and wasted if piece is immune to it.
    self.talentName[(3, 2)] = 'Cleanse'
    self.talentDesc[(3, 2)] = ('For any friendly pieces 2 squares from any of your'
                               'bishops, remove all debuffs and grant temporary'
                               'immunity to debuffs.')

    self.talentName[(4, 1)] = 'True Faith'
    self.talentDesc[(4, 1)] = ('Your bishops are immune to capture from'
                               'the opponent\'s bishops.')
    #changing what squares are being attacked on a button press
    #on your turn should only be allowed if it takes your full
    #turn to do so, or you can move, but is delayed.
    #One turn prep, second turn unleash?
    self.talentName[(4, 2)] = 'Rapture'
    self.talentDesc[(4, 2)] = ('Bishops attack in a spreading cone shape.'
                               'Each bishop can attack all squares in a'
                               'cone shape once per game.  Removes all enemy pieces in the line'
                               'of sight and your bishop.')
    #might be interesting?
    self.talentName[(5, 1)] = 'Worship'
    self.talentDesc[(5, 1)] = ('For the next 5 turns your king can move like a bishop.')
    
class MarksmanTree(TalentTree):
  def treeInfo(self):
    self.shape = [1, 2, 2, 2, 2]
    self.talentName[(1, 1)] = 'Trap'
    self.talentDesc[(1, 1)] = '''Each of your rooks can each leave traps
                                 behind them on square they have moved from.
                                 Can do this 1/2/3 times for each rook
                                 Opponent cannot see where the traps are
                                 or if you left a trap or not after moving your
                                 rook.
                                 If a trap is landed on, the opponent\'s piece
                                 is stunned for two turns.'''

    self.talentName[(2, 1)] = '360 No Scope'
    self.talentDesc[(2, 1)] = '''Your rooks can stay in place and
                                 shoot their targets from far away.'''

    self.talentName[(2, 2)] = 'Lie in wait'
    self.talentDesc[(2, 2)] = '''You can castle even after your rooks
                                 or king have moved.  You can castle multiple
                                 times in a game.  These special castle moves
                                 still otherwise obey regular castle rules.'''

                                 
    self.talentName[(3, 1)] = '360 Then Scope'
    self.talentDesc[(3, 1)] = '''Rook shots pierce through 1/2/3 pieces.
                                 Can also shoot through friendly pieces.
                                 Pierce shots cannot hit the king.'''
    
    self.talentName[(3, 2)] = 'Rook out!'
    self.talentDesc[(3, 2)] = '''While one of your rooks is defending
                                 your king, if a checkmate occurs, you
                                 can sacrifice one of your rooks to
                                 remove the opponent\'s attacking piece.'''

    self.talentName[(4, 1)] = 'Connected for Life'
    self.talentDesc[(4, 1)] = '''While your rooks are connected, if the opponent
                                 captures one of the rooks and the attacking piece
                                 ends on the captured rook\'s square, your
                                 remaining rook automatically snipes the
                                 attacking piece and removes it from the board.'''

    self.talentName[(4, 2)] = 'Thrill of the hunt'
    self.talentDesc[(4, 2)] = '''While queens are off the board, your rooks
                                 become even more dangerous.  They can now
                                 bulldoze through an entire row of pieces.
                                 Will also attack through your own pieces.
                                 Cannot attack through pieces that are immune
                                 to capture.  The enemy king can be placed
                                 into check but not checkmated in this way.
                                 If the king or an immune piece is reached,
                                 the rook must stop a square before it.'''

    self.talentName[(5, 1)] = 'Ambush'
    self.talentDesc[(5, 1)] = '''Your rooks treat the board like an infinite
                                 repeating plane.  Rook moves off the board
                                 on one end will continue on the other end.'''

    self.talentName[(5, 2)] = 'Alpha Predator'
    self.talentDesc[(5, 2)] = '''Your rooks move like queens.'''
    
class MageTree(TalentTree):
  def treeInfo(self):
    self.shape = [2, 2, 2, 2, 1]
    self.talentName[(1, 1)] = 'Frost Bolt'
    self.talentDesc[(1, 1)] = '''Your queen remains stationary while she
                                 fires a frost bolt at an enemy piece she is
                                 attacking.  This piece and all adjacent enemy
                                 pieces are frozen in place and cannot
                                 perform any actions next turn.'''

    self.talentName[(1, 2)] = 'Flame Bolt'
    self.talentDesc[(1, 2)] = '''Your queen remains stationary while she
                                 fires a fire bolt at an enemy piece she is
                                 attacking.  This piece is removed from the
                                 board.'''

    self.talentName[(2, 1)] = 'Teleport'
    self.talentDesc[(2, 1)] = '''If your opponent captured your queen last
                                 turn, you can place your queen back on the
                                 board on a space she was attacking when she
                                 was captured.  Can be done once per game.'''

    self.talentName[(2, 2)] = 'Thunder Bolt'
    self.talentDesc[(2, 2)] = '''Your queen conjures a great storm to reign
                                 down thunder on the enemy forces.  In two
                                 turns, any pieces in the center of the board
                                 are struck and remove from the board.'''
                                 
    self.talentName[(3, 1)] = 'Scorch'
    self.talentDesc[(3, 1)] = '''Your queen scorches two adjacents squares, making
                                 movement through the square impossible
                                 for two the rest of the game.  Can only
                                 be performed once per game.'''
    
    self.talentName[(3, 2)] = 'Qastle'
    self.talentDesc[(3, 2)] = '''Your king can castle with your queen.
                                 This immediately moves your king to
                                 your queenside rook, and your queenside
                                 rook to your king?'''

    self.talentName[(4, 1)] = 'Ice Wall'
    self.talentDesc[(4, 1)] = '''For two turns, a wall of ice blocks
                                 movement through a rank or file.
                                 Even knights cannot move through.
                                 Any pieces in the ice wall are frozen
                                 in place until the ice wall is melted.
                                 Can only be done one rank ahead of
                                 where the queen is.  Enemy kings can be
                                 frozen in the ice wall.'''

    self.talentName[(4, 2)] = 'Perfectionist'
    self.talentDesc[(4, 2)] = '''Your queen can move like a knight too.'''

    self.talentName[(5, 1)] = 'Queen\'s Gambit'
    self.talentDesc[(5, 1)] = '''If your queen is captured,
                                 your king can perform all the actions
                                 your queen could, except for movement.'''
    
class WarriorTree(TalentTree):
  def treeInfo(self):
    self.shape = [2, 2, 2, 1, 2]
    self.talentName[(1, 1)] = 'Axe Toss'
    self.talentDesc[(1, 1)] = '''If king is placed in check, throws
                                 axe at checking piece and removes it from
                                 board.  Cannot use again until axe is
                                 picked up from square piece was killed on.'''

    self.talentName[(1, 2)] = 'Deflect'
    self.talentDesc[(1, 2)] = '''King is immune to checkmate from close range
                                 pieces for 2 turns.  If distance from king
                                 is within 1 square than the check from that
                                 piece is ignored.  King cannot move while
                                 deflecting.  Can be used once a minute.'''

    self.talentName[(2, 1)] = 'Leap of Glory'
    self.talentDesc[(2, 1)] = '''Your king can now leap over both your and
                                 enemy pawns that are one square away.'''

    self.talentName[(2, 2)] = 'Battle Shout'
    self.talentDesc[(2, 2)] = '''Your king lets out a blood curdling roar.
                                 All enemy pieces within a radius of 3 squares
                                 are knocked back 1 square away from your king'''

    self.talentName[(3, 1)] = 'Rage Within'
    self.talentDesc[(3, 1)] = '''Your king can move two squares at a time.'''
    
    self.talentName[(3, 2)] = 'Rush'
    self.talentDesc[(3, 2)] = '''While your king is advanced further
                                 than the enemy king, your king can rush
                                 forwards and backwards, either stopping
                                 before the nearest friendly piece, or
                                 capturing the nearest enemy piece that is
                                 not their king.'''

    self.talentName[(4, 1)] = 'Berserk'
    self.talentDesc[(4, 1)] = '''For the next 1/2/3 turns,
                                 You cannot be checkmated and your king is
                                 immune to capture.  Can be used
                                 once per game.'''


    self.talentName[(5, 1)] = 'Cleave'
    self.talentDesc[(5, 1)] = '''Your king can attack all squares around him
                                 in the same turn, but cannot move if he attacks
                                 more than one piece.  Will cleave your own
                                 pawns (but not minor and major pieces)'''

    self.talentName[(5, 2)] = 'Thor\s Thunder'
    self.talentDesc[(5, 2)] = '''Remove all pieces in a circle of radius two
                                 squares from your king.  This includes
                                 friendly pieces.  If the enemy king is within
                                 this range, he is knocked back.'''
