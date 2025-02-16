# import functions from scrape_team_batting.py
from scrape_team_batting import fetch_all_data

# get data from the 2000 to 2024 MLB seasons
df = fetch_all_data(2000, 2024)

# save DataFrame to csv in data folder
df.to_csv('data/mlb_batting_statistics.csv')