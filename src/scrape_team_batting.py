from bs4 import BeautifulSoup, Comment
import requests
import pandas as pd

dfs_stats = []

def get_url(year):
    """
    Generate the URL for the given MLB season year.
    
    Parameters:
        year (int): The year for which the URL is generated.
        
    Returns:
        str: The URL of the Baseball Reference page for the specified year.
    """
    return f'https://www.baseball-reference.com/leagues/majors/{year}.shtml'

def get_soup(url):
    """
    Fetch and parse the HTML content of a webpage.
    
    Parameters:
        url (str): The URL of the webpage to parse.
    
    Returns:
        tuple: A tuple containing the parsed HTML content and HTML comments.
    """
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    comments = BeautifulSoup(''.join(soup.find_all(text=lambda text:isinstance(text, Comment))), 'html.parser')
    return soup, comments

def get_table_data(table, id):
    """
    Extracts data from a specific HTML table.
    
    Parameters:
        table (BeautifulSoup): The table to extract data from.
        id (str): The ID of the table to determine the extraction method ('teams_standard_batting', 'postseason').
    
    Returns:
        pandas.DataFrame or list: A DataFrame for batting statistics, or a list of postseason teams.
    """
    if id == 'teams_standard_batting':
        rows = table.find_all('tr')
        headers = [header.text.strip() for header in rows[0].find_all('th')]
        data = [[cell.text.strip() for cell in rows[r].find_all(['th', 'td'])] for r in range(1, len(rows) - 3)]
        return pd.DataFrame(data, columns=headers)
    
    elif id == 'postseason':
        rows = table.find('tbody').find_all('tr')
        postseason_teams = list({link.text.strip() for row in rows for link in row.find_all('td')[2].find_all('a')})
        return postseason_teams
    
def create_dataframes(year, soup, comments):
    """
    Create DataFrames for team batting statistics and postseason teams for a given year.
    
    Parameters:
        year (int): The season year.
        soup (BeautifulSoup): The parsed HTML of the webpage.
        comments (BeautifulSoup): The parsed HTML of the comments.
    """
    batting_table = soup.find('table', {'id': 'teams_standard_batting'})
    df = get_table_data(batting_table, 'teams_standard_batting')

    postseason_table = comments.find('table', {'id': 'postseason'})
    postseason_teams = get_table_data(postseason_table, 'postseason')

    df.insert(0, 'Year', year)
    df['Postseason'] = df['Tm'].isin(postseason_teams)

    dfs_stats.append(df)

def fetch_all_data(first_year, last_year):
    """
    Fetch and compile team batting statistics and postseason appearances for multiple seasons.
    
    Parameters:
        first_year (int): The starting season year.
        last_year (int): The final season year.
        
    Returns:
        pandas.DataFrame: A compiled DataFrame containing statistics across all requested seasons.
    """
    years = range(first_year, last_year + 1)

    for year in years:
        url = get_url(year)
        soup, comments = get_soup(url)
        create_dataframes(year, soup, comments)

    dfs_seasons = pd.concat(dfs_stats, ignore_index=True)
    return dfs_seasons