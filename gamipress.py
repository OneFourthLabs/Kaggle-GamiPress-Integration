import os
from kaggle import KaggleLeaderboard

class GamipressKaggleScorer:
    def __init__(self, config):
        self.kaggle_leaderboard = KaggleLeaderboard(config['kaggle']['competitions'])
        
        self.history_file = config['gamipress']['history_dump']
        if os.path.isfile(self.history_file):
            self.history = KaggleLeaderboard.from_json(self.history_file)
        else:
            self.history = None
        
        self.scores_to_points = config['gamipress']['scores_to_points']
    
    def award_points(self):
        for competition, competition_data in self.kaggle_leaderboard.competitions.items():
            if self.history and competition in self.history.competitions:
                self.award_points_for_progress(competition_data, self.history.competitions[competition])
            else:
                self.award_points_initial(competition_data)
        
        self.kaggle_leaderboard.dump_json(self.history_file)
        return
    
    def award_points_for_progress(self, current_data, prev_data):
        for user, user_data in current_data.items():
            score = user_data['score']
            prev_score = -1
            if user in prev_data:
                prev_score = prev_data[user]['score']
            
            for score_thresh, points in self.scores_to_points:
                if score_thresh > prev_score and score >= score_thresh:
                    print('Awarding %d points to %s' % (points, user))
        
        return
    
    def award_points_initial(self, current_data):
        for user, user_data in current_data.items():
            score = user_data['score']
            
            for score_thresh, points in self.scores_to_points:
                if score >= score_thresh:
                    print('Awarding %d points to %s' % (points, user))
        
        return
