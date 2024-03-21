from .extensions import socketio
from flask import redirect, url_for
from flask_socketio import emit
from flask_login import current_user
from .models import db, User, Champion

#socket io
@socketio.on('connect')
def handle_connect():
    socketio.emit('connectedSuccess')
    print('USER CONNECTED')

#clear queue on server startup
mmqueue = []
#eventually matchid for the last match played will be saved somewhere.
#import that info here matchid = db.matchid+1
matchid = 0
user = current_user

'''
Change so only created champs appear in select champ,
everything not made yet is in create new champion
'''
'''champion events'''
@socketio.event
def selectChampion(champClass):
    print('selecting' + champClass)
    user.selected_champ = champClass
    db.session.commit()

@socketio.event
def deleteChampion():
    print('here')
    deleted = False
    #deletes currently selected champion, in future
    #put up prompt and ask them to verify
    for champ in user.champions:
        if champ.champ_class == user.selected_champ:
            db.session.delete(champ)
            db.session.commit()
            deleted = True
            #user will have to select another champ if they want to battle
            user.selected_champ = ''
    [print(champ) for champ in user.champions]
    return

@socketio.event
#with current_user might not need to pass userid
def createChampion(champClass):
    print(champClass)
    print('creating '+ champClass)
    #check if the clicked champion can be created, if in db can't
    for champ in user.champions:
        if champ.champ_class == champClass:
            #would have to flash this message
            print(("champion already exists.  You must delete it first "
                  "to make a new one"))
            return
    #get num champs and increment by 1 now
    numChamps = user.num_champs + 1

    #starting elo is 500
    champion = Champion(id = numChamps, champ_class = champClass,
                        elo = 500, lvl = 0, user_id = user.id)
    db.session.add(champion)
    user.num_champs = numChamps
    #immediately set current champ to created one
    user.selected_champ = champClass
    db.session.commit()
    socketio.emit("championCreated")
    #why is redirect not working?
    #return redirect(url_for('views.champion_manager'))
    
@socketio.event
def playRandom(userid, elo, rng, blocked):
    print(userid, elo, rng, blocked)
    #newest users are added at back so always search from front
    #of queue as that is where people have been in queue longest
    mmqueue.append([userid, elo, rng, blocked])
    print(mmqueue)
    #everytime user adds queue, check if queue larger than 1, if
    #so try to match users
    if len(mmqueue) > 1:
        #keep matchid up to date
        matchid = tryMatch(mmqueue, True)

#match function for matchmaking.  Goes through entire! list
#looking for possible matches.  
def tryMatch(mmqueue, matchid):
    for i,p1 in enumerate(mmqueue):
        for p2 in mmqueue[i:]:
            if i != j:
                #players don't block each other
                if p1 not in p2[3] and p2 not in p1[3]:
                    #players are in each others rating range
                    if p1[1] in p2[2] and p2[1] in p1[2]:
                        startMatch(p1[0],p2[0],matchid)
                        matchid += 1
                        #up to here we would have encoutered users that
                        #didn't match.  Knowing this should we arrange
                        #queue in a better way?  Might need to think about
                        #this in future.
    return matchid

def startMatch(userid1, userid2, matchid):
    print('match starting')
    #connect both users into same chess board, start white clock etc.

#Want all moves, times, and other data
#to be stored in separate db eventually automatically after each match.
def endMatch():
    pass

'''champion_manager events'''
@socketio.event
def SubmitTalents():
    pass

@socketio.event
def UndoTalents():
    pass

@socketio.event
def SelectChampion():
    pass

'''battle events'''
#this will be when a user stops searching for random game
@socketio.event
def stopSearching(username, rng, blocked):
    mmqueue.remove([username, rng, blocked])
