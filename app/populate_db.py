import requests

# Script to fetch competition and team information from TheSportsDB API
# Used only to populate the database with initial data

def get_team_info(team_name, api_key="123", api_base_url="https://www.thesportsdb.com/api/v1/json"):    
    
    endpoint = f"{api_base_url}/{api_key}/searchteams.php"
    params   = {"t": team_name}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()        
        team_info = data.get("teams", [])
        
        if team_info:
            team = team_info[0]
            
            leagues = []
            for i in range(1, 8):
                league_key = "strLeague" if i == 1 else f"strLeague{i}"
                id_key     = "idLeague"  if i == 1 else f"idLeague{i}"
                league_name = team.get(league_key)
                league_id   = team.get(id_key)
                
                if league_name and league_id:
                    leagues.append(f"{league_id} - {league_name}")

            team_obj = {
                "id"           : team.get("idTeam               "),
                "idAPI"        : team.get("idAPIfootball        "),
                "name"         : team.get("strTeam              "),
                "abreviation"  : team.get("strTeamShort         "),
                "full_name"    : team.get("strTeamAlternate     "),
                "creation_year": team.get("intFormedYear        "),
                "competitions" : leagues,
                "stadium"      : team.get("strStadium           "),
                "location"     : team.get("strStadiumLocation   "),
                "website"      : team.get("strWebsite           "),
                "facebook"     : team.get("strFacebook          "),
                "twitter"      : team.get("strTwitter           "),
                "instagram"    : team.get("strInstagram         "),
                "youtube"      : team.get("strYoutube           "),
                "badge"        : team.get("strTeamBadge         "),
                "shirt"        : team.get("strEquipment         "),
            }
            
            print(team_obj)
            
        else:
            print("No team found.")
        
    else:
        print(f"Error: {response.status_code}")
        
        
# Example: https://www.thesportsdb.com/api/v1/json/123/lookupleague.php?id=4328


def get_competition_info(league_id, api_key="123", api_base_url="https://www.thesportsdb.com/api/v1/json"):
    endpoint = f"{api_base_url}/{api_key}/lookupleague.php"
    params   = {"id": league_id}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        league_info = data.get("leagues", [])
        
        if league_info:
            league = league_info[0]
            league_obj = {
            "id"          : league.get("idLeague            "),
            "idAPI"       : league.get("idAPIfootball       "),
            "sport"       : league.get("strSport            "),
            "name"        : league.get("strLeague           "),
            "full_name"   : league.get("strLeagueAlternate  "),
            "country"     : league.get("strCountry          "),
            "website"     : league.get("strWebsite          "),
            "facebook"    : league.get("strFacebook         "),
            "instagram"   : league.get("strInstagram        "),
            "twitter"     : league.get("strTwitter          "),
            "youtube"     : league.get("strYoutube          "),
            "description" : league.get("strDescriptionPT    "),
            "banner"      : league.get("strBanner           "),
            "badge"       : league.get("strBadge            "),
            "logo"        : league.get("strLogo             "),
            "poster"      : league.get("strPoster           "),
            "trophy"      : league.get("strTrophy           "),
            "naming"      : league.get("strNaming           "),
            }
            print(league_obj)
            
        else:
            print("No league found.")
        
        
    else:
        print(f"Error: {response.status_code}")
        
        
team_name = "Ceara"
league_id = "4351"  
get_competition_info(league_id)
# get_team_info(team_name)