#This is important to use in general
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
#this is for current datetime only (func.now)
#from sqlalchemy.sql import func

db = SQLAlchemy()
DB_NAME = "database.db"

'''
Add nullable = False to all appropriate columns next time db reset
'''
#we inheret some info from UserMixin class here which is useful
#in particular, UserMixin works with flask_login to add extra behind the
#scenes info and functionality to our User class like is_authenticated().
class User(db.Model, UserMixin):
    #id becomes the primary key here and it is an integer
    #primary key is automatically unique
    id = db.Column(db.Integer, primary_key=True)
    #string with max length 150
    #unique = true means all entries must have unique values for this column
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    num_champs = db.Column(db.Integer)
    #one user many champions
    #backref adds a column to child table.  In this case MMSettings
    champions = db.relationship('Champion', backref = 'User')
    #elo range for matchmaking
    #changed by slide bar or input on battle page
    elo_low = db.Column(db.Integer)
    elo_high = db.Column(db.Integer)
    #champion that will be used to battle (class name)
    #this is set in champion manager page under ready to battle
    selected_champ = db.Column(db.String(150))
    
    #magic method for classes in general.  Determines what print(class) does
    def __repr__(self):
        return (f'User({self.id}, {self.username}, {self.email}, '
                f'{self.num_champs})')

class Blocked(db.Model):
    #to block we use other user's user ids
    id = db.Column(db.Integer, primary_key=True)
    blockedid = db.Column(db.Integer, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#many user achievements to one user.  achievements table here.
#have to make default table manually somewhere...
class User_Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    achievement_name = db.Column(db.String(150), unique=True)
    completed = db.Column(db.Boolean)
    #the points gained from achievement... harder gives more
    value = db.Column(db.Integer)

#every player can have 1 of each champion
class Champion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    champ_class = db.Column(db.String(150), unique=True)
    elo = db.Column(db.Integer)
    lvl = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return (f'Champion({self.id}, {self.champ_class},'
                f'{self.elo}, {self.lvl}, {self.user_id})')

#many user achievements to one user.  achievements table here.
#have to make default table manually somewhere...
class Champion_Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    achievement_name = db.Column(db.String(150), unique=True)
    completed = db.Column(db.Boolean)
    #the points gained from achievement... harder gives more
    value = db.Column(db.Integer)
    #champ specific achievements gain exp and can unlock
    #secret abilities
    exp_gain = db.Column(db.Integer)

'''
talent logic not handled here, just recorded here in db.
Will be handled on talent page html and js.
One talent tree to every champion for now.
In future maybe can remember multiple for easy
interchange between talents
'''
class Talent_Tree(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), unique = True)
    desc = db.Column(db.String(500))
    #invested points
    inv = db.Column(db.Integer)
    #total points allowed to be allocated
    total = db.Column(db.Integer)
    champ_id = db.Column(db.Integer, db.ForeignKey('user.id'))
