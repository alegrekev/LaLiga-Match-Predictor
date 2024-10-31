from flask_restx import Resource, Namespace
from .models import *

ns = Namespace("api")

@ns.route("/standings")
class StandingsResource(Resource):
    def get(self):
        update_standings()
        standings = Standings.query.all()

        # Format the standings as a list of dictionaries
        standings_list = [
            {
                "Team": s.team,
                "GP": s.gp,
                "W": s.w,
                "D": s.d,
                "L": s.l,
                "F": s.f,
                "A": s.a,
                "GD": s.gd,
                "P": s.p
            } for s in standings
        ]

        return {"standings": standings_list}

@ns.route("/schedule")
class ScheduleResource(Resource):
    def get(self):
        update_schedule()
        schedule = Schedule.query.all()

        # Format the standings as a list of dictionaries
        schedule_list = [
            {
                "Team 1": s.team1,
                "Team 2": s.team2,
                "Location": s.location,
                "ODDS BY": s.odds,
                "Team 1 Win Probability": s.team1_prob,
                "Team 2 Win Probability": s.team2_prob,
                "Draw Probability": s.draw_prob
            } for s in schedule
        ]

        return {"schedule": schedule_list}
    
@ns.route("/next_game")
class nextgameResource(Resource):
    def get(self):
        update_next_game()
        next_game = NextGame.query.all()

        # Format the standings as a list of dictionaries
        next_game_list = [
            {
                "Team 1": s.team1,
                "Team 2": s.team2,
                "Location": s.location,
                "ODDS BY": s.odds,
                "Team 1 Win Probability": s.team1_prob,
                "Team 2 Win Probability": s.team2_prob,
                "Draw Probability": s.draw_prob
            } for s in next_game
        ]

        return {"next_game": next_game_list}