import datetime as dt
from datetime import datetime
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from sqlalchemy import func
from .database import db 
from application.models import Deck, User, Card

@app.route("/", methods = ['GET','POST'])
def home():
    return redirect(url_for('login'))

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password == confirm_password:
            new_user = User(user_id=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return redirect(url_for('signup'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter(User.user_id == username).all()
        if len(user)==0:
            return redirect(url_for('login'))
        if user[0].password != password:
            return redirect(url_for('login'))
        else:
            return redirect('/dashboard/{}'.format(user[0].user_id))

@app.route("/dashboard/<user_id>" , methods= ["GET"])
def dashboard(user_id):
    # GET all decks for user_id
    decks = db.session.query(Deck).filter(Deck.user_id == user_id).all()
    return render_template("dashboard.html", decks = decks, user_id = user_id)

@app.route("/cards/<deck_id>" , methods= ["GET"])
def cards(deck_id):
    # For deck_id, return random card
    card = get_random_card(deck_id)
    deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
    return render_template("card.html", card = card, user_id = deck.user_id, deck_id = deck_id)

def get_random_card(deck_id):
    min_score = db.session.query(func.min(Card.card_score)).filter(Card.deck_id==deck_id).scalar()
    card = db.session.query(Card).filter(Card.card_score == min_score, Card.deck_id == deck_id).first()
    return card
    
@app.route("/cards/<card_id>/<difficulty>")
def next_card(card_id, difficulty):
    card = db.session.query(Card).filter(Card.card_id == card_id).first()
    deck_id = card.deck_id
    new_score = get_new_score(card.card_score, difficulty)
    old_score = card.card_score
    card.card_score = new_score
    dt_India = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S")
    card.card_last_review_time = dt_India
    deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
    deck.deck_score = deck.deck_score + new_score - old_score
    deck.deck_last_review_time = card.card_last_review_time
    db.session.commit()
    return redirect('/cards/{}'.format(deck_id))  
  
def get_new_score(card_score, difficulty):
    new_score = card_score
    if difficulty == 'EASY':
        new_score += 3
    elif difficulty == 'MEDIUM':
        new_score += 2
    else:
        new_score += 1
    return new_score
         
@app.route("/create_deck/<user_id>" , methods= ["GET", "POST"])
def create_deck(user_id):
    if request.method == 'GET':
        return render_template("create_deck.html", user_id = user_id)
    if request.method == 'POST':
        deck_name = request.form["deck_name"]
        deck_lrt = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S")
        new_deck = Deck(deck_name = deck_name, user_id = user_id, deck_last_review_time = deck_lrt)
        db.session.add(new_deck)
        db.session.commit()
        return redirect('/dashboard/{}'.format(user_id))

@app.route("/create_card/<deck_id>" , methods= ["GET", "POST"])
def create_card(deck_id):
    if request.method == 'GET':
        return render_template("create_card.html", deck_id = deck_id)
    if request.method == 'POST':
        card_front = request.form["card_front"]
        card_back = request.form["card_back"]
        card_lrt = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S")
        new_card = Card(deck_id = deck_id, card_front = card_front, card_back = card_back, card_last_review_time = card_lrt)
        db.session.add(new_card)
        db.session.commit()
        return redirect('/cards/{}'.format(deck_id))
    
@app.route("/decks/<deck_id>/update", methods=["GET", "POST"])
def update_deck(deck_id):
    if request.method == 'GET':
        return render_template("update_deck.html", deck_id=deck_id)
    if request.method == 'POST':
        deck_name = request.form["deck_name"]
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        deck.deck_name = deck_name
        db.session.commit()
        return redirect('/dashboard/{}'.format(deck.user_id))
    
@app.route("/cards/<card_id>/update", methods=["GET", "POST"])
def update_card(card_id):
    if request.method == 'GET':
        return render_template("update_card.html", card_id=card_id)
    if request.method == 'POST':
        card_front = request.form["card_front"]
        card_back = request.form["card_back"]
        card = db.session.query(Card).filter(Card.card_id == card_id).first()
        card.card_front = card_front
        card.card_back = card_back
        db.session.commit()
        return redirect('/cards/{}'.format(card.deck_id))

@app.route("/decks/<deck_id>/delete", methods = ['GET'])
def delete_deck(deck_id):
    deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
    cards = db.session.query(Card).filter(Card.deck_id == deck_id).all()
    for card in cards:
        db.session.delete(card)
        db.session.commit()
    db.session.delete(deck)
    db.session.commit()
    return redirect('/dashboard/{}'.format(deck.user_id))

@app.route("/cards/<card_id>/delete", methods = ['GET'])
def delete_card(card_id):
    card = db.session.query(Card).filter(Card.card_id == card_id).first()
    deck = db.session.query(Deck).filter(Deck.deck_id == card.deck_id).first()
    deck.deck_score -= card.card_score
    db.session.delete(card)
    db.session.commit()
    return redirect('/cards/{}'.format(card.deck_id))

@app.route("/decks/<deck_id>/reset", methods = ['GET', 'POST'])
def reset(deck_id):
    cards = db.session.query(Card).filter(Card.deck_id == deck_id).all()
    deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
    deck.deck_score = 0
    deck.deck_last_review_time = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S")
    db.session.commit()
    for card in cards:
        card.card_score = 0
        db.session.commit()
    return redirect('/dashboard/{}'.format(deck.user_id))