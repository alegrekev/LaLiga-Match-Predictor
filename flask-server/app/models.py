from .extensions import db
from .scraper import *

class Standings(db.Model):
    __tablename__ = 'standings'
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String(100), nullable=False)
    gp = db.Column(db.Integer, nullable=False)  # Games Played
    w = db.Column(db.Integer, nullable=False)   # Wins
    d = db.Column(db.Integer, nullable=False)   # Draws
    l = db.Column(db.Integer, nullable=False)   # Losses
    f = db.Column(db.Integer, nullable=False)   # Goals For
    a = db.Column(db.Integer, nullable=False)   # Goals Against
    gd = db.Column(db.Integer, nullable=False)  # Goal Difference
    p = db.Column(db.Integer, nullable=False)   # Points

def update_standings():
    standings_df = get_standings()
    
    # Delete existing records in the standings table
    Standings.query.delete()

    # Insert the new standings into the database
    for _, row in standings_df.iterrows():
        standing = Standings(
            team=row['Team'],
            gp=row['GP'],
            w=row['W'],
            d=row['D'],
            l=row['L'],
            f=row['F'],
            a=row['A'],
            gd=row['GD'],
            p=row['P']
        )
        db.session.add(standing)
    
    db.session.commit()

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    odds = db.Column(db.String(100), nullable=False)
    team1_prob = db.Column(db.String(100), nullable=False)
    team2_prob = db.Column(db.String(100), nullable=False)
    draw_prob = db.Column(db.String(100), nullable=False)

def update_schedule():
    schedule_df = get_schedule()
    schedule_odds_df = get_schedule_odds(schedule_df)
    
    # Delete existing records in the schedule table
    Schedule.query.delete()

    # Insert the new schedule into the database
    for _, row in schedule_odds_df.iterrows():
        schedule = Schedule(
            team1=row['Team 1'],
            team2=row['Team 2'],
            location=row['Location'],
            odds=row['ODDS BY'],
            team1_prob=row['Team 1 Win Probability'],
            team2_prob=row['Team 2 Win Probability'],
            draw_prob=row['Draw Probability']
        )
        db.session.add(schedule)
    
    db.session.commit()

class NextGame(db.Model):
    __tablename__ = 'next_game'
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    odds = db.Column(db.String(100), nullable=False)
    team1_prob = db.Column(db.String(100), nullable=False)
    team2_prob = db.Column(db.String(100), nullable=False)
    draw_prob = db.Column(db.String(100), nullable=False)

def update_next_game():
    schedule_df = get_schedule()
    next_game_df = get_next_game_odds(schedule_df)
    
    # Delete existing records in the schedule table
    NextGame.query.delete()

    # Insert the new schedule into the database
    for _, row in next_game_df.iterrows():
        next_game = NextGame(
            team1=row['Team 1'],
            team2=row['Team 2'],
            location=row['Location'],
            odds=row['ODDS BY'],
            team1_prob=row['Team 1 Win Probability'],
            team2_prob=row['Team 2 Win Probability'],
            draw_prob=row['Draw Probability']
        )
        db.session.add(next_game)
    
    db.session.commit()