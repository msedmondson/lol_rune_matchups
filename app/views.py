from flask import   render_template, Blueprint, render_template,\
                    jsonify, request, redirect, session
import os
from app import app
from app.scripts import dropUnicode, get_matchup_data_by_champion_ids
from app.db_queries import db_get_all_champions
from json import dumps
from app.logger import log

@app.route('/home', methods=["GET", "POST"])
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/rune_page_matchups', methods=['GET', 'POST'])
def rune_page_matchups():
    args = {"champion_list": "", "popup": False}
    args['champion_list'] = db_get_all_champions()
    
    return render_template("rune_page_matchups.html",
    champion_list = args['champion_list'],
    popup = args['popup'])

# Tis just a test page
@app.route('/test_page', methods=['GET', 'POST'])
def test_page():
    args = {"champion_list": "", "popup": False}
    args['champion_list'] = db_get_all_champions()
    
    return render_template("test_page.html",
    champion_list = args['champion_list'],
    popup = args['popup'])
    
@app.route('/todo/api/v1.0/matchup_data', methods=['GET'])
def get_matchup_data():
    if request.method == 'GET':
        allyId = request.args.get('allyId')
        enemyId = request.args.get('enemyId')
        winLoseTuple = get_matchup_data_by_champion_ids(allyId, enemyId)
        return jsonify(winLoseTuple)
    
@app.route("/about")
def about():
    return render_template("about.html")


# to debug in jinja {{ mdebug(query) }}
@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)
