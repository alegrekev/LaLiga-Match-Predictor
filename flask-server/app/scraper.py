import pandas as pd
import numpy as np

def get_standings():
    espn_standings = pd.read_html("https://www.espn.com/soccer/standings/_/league/esp.1")

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

def get_schedule():
    # get schedule in tabular format
    espn_schedule = pd.read_html("https://www.espn.com/soccer/schedule/_/league/esp.1")

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