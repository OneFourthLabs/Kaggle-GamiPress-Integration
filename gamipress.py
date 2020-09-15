import os
import requests
from kaggle import KaggleLeaderboard

class GamipressKaggleScorer:
    def __init__(self, config, kaggle2wp_id):
        self.kaggle_leaderboard = KaggleLeaderboard(config['kaggle']['competitions'])
        
        self.history_file = config['gamipress']['history_dump']
        if os.path.isfile(self.history_file):
            self.history = KaggleLeaderboard.from_json(self.history_file)
        else:
            self.history = None
        
        self.scores_to_points = config['gamipress']['scores_to_points']
        self.user2wp_id = kaggle2wp_id
        
        self.award_points_api = config['wordpress']['site'] + '/wp-json/wp/v2/gamipress/award-points'
        self.api_header = config['wordpress']['api']['header']
        self.points_type = config['gamipress']['points_type']
    
    def issue_rewards(self):
        for competition, competition_data in self.kaggle_leaderboard.competitions.items():
            if self.history and competition in self.history.competitions:
                self.award_points_for_progress(competition, competition_data, self.history.competitions[competition])
            else:
                self.award_points_initial(competition, competition_data)
        
        self.kaggle_leaderboard.dump_json(self.history_file)
        return
    
    def award_points_for_progress(self, competition_name, current_data, prev_data):
        for user, user_data in current_data.items():
            score = user_data['score']
            prev_score = -1
            if user in prev_data:
                prev_score = prev_data[user]['score']
            
            for score_thresh, points in self.scores_to_points:
                if score_thresh > prev_score and score >= score_thresh:
                    self.award_points_to_user(user, points, competition_name, score_thresh)
        
        return
    
    def award_points_initial(self, competition_name, current_data):
        for user, user_data in current_data.items():
            score = user_data['score']
            
            for score_thresh, points in self.scores_to_points:
                if score >= score_thresh:
                    self.award_points_to_user(user, points, competition_name, score_thresh)
        return

    def award_points_to_user(self, kaggle_username, points, competition_name, score_thresh):
        
        if kaggle_username not in self.user2wp_id:
            return False
        
        return_code = True
        # Award points for all culprits with that username
        for user_id in self.user2wp_id[kaggle_username]:
            params = {
                'user_id': user_id,
                'points': points,
                'points_type': self.points_type,
                'reason': 'Crossed score %.2f in competition: %s' % (score_thresh, competition_name)
            }
            r = requests.post(self.award_points_api, params=params, headers=self.api_header).json()
            return_code = return_code and r['success']
        
        return return_code
