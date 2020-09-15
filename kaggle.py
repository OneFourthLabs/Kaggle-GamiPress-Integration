import json
import requests

LEADERBOARD_API = 'https://www.kaggle.com/c/%s/leaderboard.json?includeBeforeUser=true&includeAfterUser=false'

class KaggleLeaderboard:
    def __init__(self, competitions_list, call_api=True):
        if call_api:
            # For each competition, retrieve data from API
            self.competitions = {}
            for competition in competitions_list:
                user_data = self.get_users_in_leaderboards(competition)
                self.competitions[competition] = user_data
        else:
            # Just use the dump which is passed
            self.competitions = competitions_list
    
    def dump_json(self, write_to):
        with open(write_to, 'w', encoding='utf-8') as f:
            json.dump(self.competitions, f, ensure_ascii=False, indent=2)
        return
    
    @classmethod
    def from_json(cls, read_from):
        with open(read_from, 'r', encoding='utf-8') as f:
            competitions = json.load(f)
        return cls(competitions, False)
    
    def get_users_in_leaderboards(self, competition_id):
        r = requests.get(LEADERBOARD_API % competition_id).json()
        total_teams = r['totalRankings']
        teams = r['beforeUser'] + r['nearUser'] + r['afterUser']
        assert len(teams) == total_teams
        
        user_details = {}
        for team in teams:
            team_data = {
                'rank': team['rank'],
                'score': team['score'],
                'entries': team['entries']
            }
            # Extract users
            for member in team['teamMembers']:
                username = member['profileUrl'].replace('/', '')
                if username in user_details:
                    # Allow only one user to be present in only 1 team
                    continue
                user_details[username] = team_data
        
        return user_details

if __name__ == '__main__':
    # Testing
    print(KaggleLeaderboard(["padhai-mp-neuron-like-unlike-classification"]).competitions)
