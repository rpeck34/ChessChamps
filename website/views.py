from flask import Blueprint, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from .models import db
import json

views = Blueprint('views', __name__)

#this function will run on reaching root(home) page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        pass
    #img_file = url_for('static', filename='HotPotChess.png')
    return render_template("home.html", user=current_user)

@views.route('/battle', methods=['GET', 'POST'])
#can only use current_user from flask_login with login_required decorator
@login_required
def battle():
    #this is page where can play match
    #get last mmsettings from user mmsetings table
    return render_template("battle.html", user=current_user, elo=1000,
                           mmsettings=[200,1500], blocked = [])

@views.route('/champions', methods=['GET', 'POST'])
@login_required
def champions():
    #allowed champions
    champs = ['Warlock','Paladin','Rogue']
    return render_template("champions.html", champs=champs, user=current_user)

@views.route('/champion_manager', methods=['GET', 'POST'])
@login_required
def champion_manager():
    return render_template("champion_manager.html", user=current_user)
