import pandas as pd
import numpy as np
import re

def get_standings():
    STANDINGS_LINK = "https://www.espn.com/soccer/standings/_/league/esp.1"
    espn_standings = pd.read_html(STANDINGS_LINK)

    # Extract the two DataFrames
    teams_df = espn_standings[0]
    stats_df = espn_standings[1]

    # Combine them into a single DataFrame by concatenating along the columns (axis=1)
    standings = pd.concat([teams_df, stats_df], axis=1)

    # Remove the position numbers and team abbreviations, drop the original Team column
    standings['Team'] = standings[standings.columns[0]].str.extract(r'\d{1}[A-Z]{3}(\D+)', expand=False).str.strip()
    standings.drop(standings.columns[0], axis=1, inplace=True)

    # Reset the index, reorder the columns
    standings.reset_index(drop=True, inplace=True)
    standings = standings[["Team","GP","W","D","L","F","A","GD","P"]]
    standings.index = np.arange(1, len(standings)+1)

    return standings


def get_la_liga_historical():
    LA_LIGA_HISTORICAL_LINK = "https://fbref.com/en/comps/12/2023-2024/2023-2024-La-Liga-Stats"
    fbref_la_liga = pd.read_html(LA_LIGA_HISTORICAL_LINK)

    # Extract only the first table containing historical data on La Liga, filter out teams that moved to Segunda Division
    la_liga_historical = fbref_la_liga[0]
    la_liga_historical = la_liga_historical[~la_liga_historical['Notes'].str.contains("Relegated", na=False)]
    la_liga_historical.index = np.arange(1, len(la_liga_historical)+1)

    return la_liga_historical


def get_segunda_division_historical():
    SEGUNDA_DIV_HISTORICAL_LINK = "https://fbref.com/en/comps/17/2023-2024/2023-2024-Segunda-Division-Stats"
    fbref_segunda_div = pd.read_html(SEGUNDA_DIV_HISTORICAL_LINK)

    # Extract only the first table containing historical data on Segunda Division, filter for teams that moved to La Liga
    segunda_div_historical = fbref_segunda_div[0]
    segunda_div_historical = segunda_div_historical[segunda_div_historical['Notes'].str.contains("Promoted", na=False)]
    segunda_div_historical.index = np.arange(1, len(segunda_div_historical)+1)

    return segunda_div_historical


def get_schedule():
    SCHEDULE_LINK = "https://www.espn.com/soccer/schedule/_/league/esp.1"
    espn_schedule = pd.read_html(SCHEDULE_LINK)

    schedule = pd.concat([match for match in espn_schedule], axis=0)

    # Split the 'MATCH.1' column into 'Team 2' and 'Score' columns
    schedule[["Score", "Team 2"]] = schedule["MATCH.1"].str.split(" ", n=1, expand=True)
    schedule['Team 1'] = schedule["MATCH"]
    schedule['Location'] = schedule["location"]

    # Reorder columns
    schedule = schedule[['Team 1', 'Team 2', 'Location', 'ODDS BY']]
    schedule = schedule[schedule["ODDS BY"].notnull()]
    schedule.index = np.arange(1, len(schedule)+1)

    return schedule


def calculate_odds(standings, la_liga_historical, segunda_div_historical, team1, team2, market_odds):
    # Function to extract odds from the string
    def extract_odds(odds_str):
        # Use regex to find a number with optional + or - sign
        match = re.search(r'[+-]?\d+', odds_str)
        if match:
            odds = float(match.group())
            
            # Flip the sign: + becomes - and - becomes +, reflecting chance of winning
            if odds > 0:
                return -odds  # + becomes negative for lower chance
            else:
                return abs(odds)  # - becomes positive for higher chance
        return None

    # Example betting odds string
    market_odds = market_odds[6:].split('/')[0]  # Extract odds substring
    market_odds = extract_odds(market_odds)  # Apply extraction and flipping logic

    # Convert betting odds to probability (fractional odds assumed)
    if market_odds < 0:  # Negative odds
        team1_odds_prob = abs(market_odds) / (abs(market_odds) + 100)
        team2_odds_prob = 1 - team1_odds_prob
    else:  # Positive odds
        team1_odds_prob = 100 / (market_odds + 100)
        team2_odds_prob = 1 - team1_odds_prob


    # Get standings data
    team1_standing = standings[standings["Team"] == team1]
    team2_standing = standings[standings["Team"] == team2]
    team1_points = team1_standing["P"].values[0]
    team2_points = team2_standing["P"].values[0]

    # Win probability based on standings
    team1_standing_prob = team1_points / (team1_points + team2_points)
    team2_standing_prob = team2_points / (team1_points + team2_points)

    def get_team_history(team_name):
        team_name_cleaned = team_name.replace("Real ", "").replace("Rayo ", "").strip()

        # Search in La Liga historical data for team name containment
        team_hist = la_liga_historical[la_liga_historical["Squad"].str.contains(team_name_cleaned, case=False, na=False)]
        
        # If not found, search in Segunda Division historical data
        if team_hist.empty:
            team_hist = segunda_div_historical[segunda_div_historical["Squad"].str.contains(team_name_cleaned, case=False, na=False)]
        
        # Return the DataFrame if found, otherwise return None
        return team_hist if not team_hist.empty else None


    # Retrieve historical data for both teams
    team1_hist = get_team_history(team1)
    team2_hist = get_team_history(team2)

    # Ensure both teams' historical data is found before proceeding
    if team1_hist is not None and team2_hist is not None:
        team1_hist_points = team1_hist["Pts"].values[0]
        team2_hist_points = team2_hist["Pts"].values[0]
    else:
        print(f"Historical data not found for {team1} or {team2}")

    # Win probability based on historical data
    team1_hist_prob = team1_hist_points / (team1_hist_points + team2_hist_points)
    team2_hist_prob = team2_hist_points / (team1_hist_points + team2_hist_points)

    # Convert betting odds to probability (fractional odds assumed)
    market_odds_frac = float(market_odds)  
    team1_odds_prob = 1 / (market_odds_frac + 1)
    team2_odds_prob = 1 - team1_odds_prob


    # Draw probability from current standings (based on number of draws)
    team1_draw_rate = team1_standing["D"].values[0] / team1_standing["GP"].values[0]
    team2_draw_rate = team2_standing["D"].values[0] / team2_standing["GP"].values[0]
    draw_standing_prob = (team1_draw_rate + team2_draw_rate) / 2  # Average draw rate


    # Draw probability from historical data
    team1_hist_draw_rate = team1_hist["D"].values[0] / team1_hist["MP"].values[0]
    team2_hist_draw_rate = team2_hist["D"].values[0] / team2_hist["MP"].values[0]
    draw_hist_prob = (team1_hist_draw_rate + team2_hist_draw_rate) / 2  # Average historical draw rate

    # Adjusted weights for the new probabilities
    w_standings = 0.35
    w_historical = 0.25
    w_odds = 0.2
    w_draw = 0.2  # Adding weight for draw probability

    # Win probabilities
    team1_combined_prob = (team1_standing_prob * w_standings) + (team1_hist_prob * w_historical) + (team1_odds_prob * w_odds)
    team2_combined_prob = (team2_standing_prob * w_standings) + (team2_hist_prob * w_historical) + (team2_odds_prob * w_odds)

    def calculate_draw_prob(team1_prob, team2_prob, w_draw):
        # Scaling factor for the draw based on the closeness of the teams
        closeness_factor = 1 - abs(team1_prob - team2_prob)  # Higher closeness means higher chance of draw
        w_draw = 0.2  # Base probability of a draw (can be adjusted)
        
        # Final draw probability increases when teams are closer in strength
        draw_prob = w_draw * closeness_factor
        
        # Ensure draw probability doesn't exceed the remaining total probability
        return min(draw_prob, 1 - (team1_prob + team2_prob))

    # Use this function to calculate draw probability
    draw_odds_prob = calculate_draw_prob(team1_combined_prob, team2_combined_prob, w_draw)

    # Draw probability (weighted)
    combined_draw_prob = (draw_standing_prob * w_standings) + (draw_hist_prob * w_historical) + (draw_odds_prob * w_odds)

    # Ensure probabilities sum to 1
    total_prob = team1_combined_prob + team2_combined_prob + combined_draw_prob
    team1_combined_prob /= total_prob
    team2_combined_prob /= total_prob
    combined_draw_prob /= total_prob

    # Round to two decimal places, multiply by 100, convert to strings, and add percent sign
    team1_combined_prob = f"{round(team1_combined_prob * 100, 2)}%"
    team2_combined_prob = f"{round(team2_combined_prob * 100, 2)}%"
    combined_draw_prob = f"{round(combined_draw_prob * 100, 2)}%"

    # Return probabilities as strings with percent signs
    return [team1_combined_prob, team2_combined_prob, combined_draw_prob]



def get_next_game_odds(schedule):
    standings = get_standings()
    la_liga_historical = get_la_liga_historical()
    segunda_div_historical = get_segunda_division_historical()

    # Get the next game (first row) from the schedule dataframe
    next_game = schedule.iloc[0].copy()

    next_game["Team 1 Win Probability"] = 0
    next_game["Team 2 Win Probability"] = 0
    next_game["Draw Probability"] = 0

    # Extract relevant data
    team1 = next_game["Team 1"]
    team2 = next_game["Team 2"]
    espn_odds = next_game["ODDS BY"]

    if pd.isna(espn_odds):
        print(f"Skipping calculation for {team1} vs {team2} due to missing odds.")
    else:
        # Calculate win probabilities
        [t1_win, t2_win, draw] = calculate_odds(standings, la_liga_historical, segunda_div_historical, team1, team2, espn_odds)

        # Assign the calculated probabilities back to the 'schedule' dataframe
        next_game["Team 1 Win Probability"] = t1_win
        next_game["Team 2 Win Probability"] = t2_win
        next_game["Draw Probability"] = draw

    next_game = pd.DataFrame([next_game])

    # Display the updated next game with probabilities
    return next_game


def get_schedule_odds(schedule):
    standings = get_standings()
    la_liga_historical = get_la_liga_historical()
    segunda_div_historical = get_segunda_division_historical()

    # Define new columns for win and draw probabilities
    schedule["Team 1 Win Probability"] = 0.0
    schedule["Team 2 Win Probability"] = 0.0
    schedule["Draw Probability"] = 0.0    

    # Loop through each row of the schedule dataframe
    for index, row in schedule.iterrows():
        # Extract the necessary information from the row
        team1 = row['Team 1']
        team2 = row['Team 2']
        espn_odds = row['ODDS BY']

        # Check if espn_odds is NaN before proceeding
        if pd.isna(espn_odds):
            continue  # Skip to the next iteration if odds are missing

        # Call the calculate_odds function with the relevant data
        [t1_win, t2_win, draw] = calculate_odds(standings, la_liga_historical, segunda_div_historical, team1, team2, espn_odds)

        # Add the returned probabilities to the schedule dataframe
        schedule.at[index, 'Team 1 Win Probability'] = t1_win
        schedule.at[index, 'Team 2 Win Probability'] = t2_win
        schedule.at[index, 'Draw Probability'] = draw

    schedule.dropna(inplace=True)

    # Display the updated schedule dataframe
    return schedule
