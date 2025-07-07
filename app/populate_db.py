import requests

# Script to fetch competition and team information from TheSportsDB API
# Used only to populate the database with initial data

def get_team_info(team_name, api_key="123", api_base_url="https://www.thesportsdb.com/api/v1/json"):    
    
    endpoint = f"{api_base_url}/{api_key}/searchteams.php"
    params   = {"t": team_name}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code}")
        
        
# Example: https://www.thesportsdb.com/api/v1/json/123/lookupleague.php?id=4328


def get_competition_info(league_id, api_key="123", api_base_url="https://www.thesportsdb.com/api/v1/json"):
    endpoint = f"{api_base_url}/{api_key}/lookupleague.php"
    params   = {"id": league_id}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code}")
        
        
team_name = "Ceara"
league_id = "4328"  # Example: Campeonato Brasileiro Série A
get_competition_info(league_id)
# get_team_info(team_name)