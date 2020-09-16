import os
import requests
from .kaggle import KaggleLeaderboard

class GamipressKaggleScorer:
    def __init__(self, config, kaggle2wp_id):
        self.kaggle_leaderboard = KaggleLeaderboard(config['kaggle']['competitions'])
        
        self.history_file = config['gamipress']['history_dump']
        if os.path.isfile(self.history_file):
            self.history = KaggleLeaderboard.from_json(self.history_file)
        else:
            self.history = None
        
        # Assumes score thresholds in ascending order
        self.scores_to_points = config['gamipress']['scores_to_points']
        self.user2wp_id = kaggle2wp_id
        
        self.award_points_api = config['wordpress']['site'] + '/wp-json/wp/v2/gamipress/award-points'
        self.api_header = config['wordpress']['api']['header']
        self.points_type = config['gamipress']['points_type']
    
    def issue_rewards(self):
        '''
        Issue award points for all users in all competitions,
        if any progress is made compared to the history.
        '''
        
        for competition, competition_data in self.kaggle_leaderboard.competitions.items():
            if self.history and competition in self.history.competitions:
                prev_competition_data = self.history.competitions[competition]
            else:
                prev_competition_data = None
            self.award_points_for_progress(competition, competition_data, prev_competition_data)
        self.kaggle_leaderboard.dump_json(self.history_file)
        return
    
    def award_points_for_progress(self, competition_name, current_data, prev_data=None):
        '''
        Compare the history and current Kaggle scores in the given competition,
        and award points accordingly as per the `scores_to_points` specification
        '''
        
        for user, user_data in current_data.items():
            score = user_data['score']
            prev_score = -1
            if prev_data and user in prev_data and 'last_awarded_score' in prev_data[user]:
                prev_score = prev_data[user]['last_awarded_score']
                user_data['last_awarded_score'] = prev_score # Save for persistence
            
            for score_thresh, points in self.scores_to_points:
                if score_thresh > prev_score and score >= score_thresh:
                    if self.award_points_to_user(user, points, competition_name, score_thresh):
                        user_data['last_awarded_score'] = score
        
        return

    def award_points_to_user(self, kaggle_username, points, competition_name, score_thresh):
        '''
        Calls the following API to award points to an user:
        https://gamipress.com/docs/gamipress-rest-api-extended/points-extended-controller
        '''
        
        if kaggle_username not in self.user2wp_id:
            return False
        
        # Do not award points for all culprits with that username
        users = self.user2wp_id[kaggle_username]
        if len(users) > 1:
            print('WARN: Forgery detected. The Kaggle username %s is set by the user_ids:' % kaggle_username)
            print(users)
            return False
        
        params = {
            'user_id': users[0],
            'points': points,
            'points_type': self.points_type,
            'reason': 'Crossed score %.2f in competition: %s' % (score_thresh, competition_name)
        }
        r = requests.post(self.award_points_api, params=params, headers=self.api_header).json()
        
        return r['success']
