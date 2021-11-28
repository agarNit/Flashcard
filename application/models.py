from .database import db 
import datetime as dt

class User(db.Model):
	__tablename__ = 'users'
	user_id = db.Column(db.String, primary_key = True, nullable = False)
	password = db.Column(db.String, unique = True, nullable = False)
	
class Deck(db.Model):
    __tablename__ = 'decks'
    deck_id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
    user_id = db.Column(db.String, db.ForeignKey("users.user_id"), nullable = False)
    deck_name = db.Column(db.String, nullable = False)
    deck_score = db.Column(db.Float, nullable = False, default = 0)
    deck_last_review_time = db.Column(db.String, nullable = True, default = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S"))
 
class Card(db.Model):
	__tablename__ = 'cards'
	card_id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
	deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable = False)
	card_front = db.Column(db.String, nullable = True)
	card_back = db.Column(db.String, nullable = True)
	card_last_review_time = db.Column(db.String, nullable = True, default = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y AT %H:%M:%S"))
	card_score = db.Column(db.Float, nullable = True, default = 0)