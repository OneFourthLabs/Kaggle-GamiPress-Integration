import base64
import json
import requests

from .gamipress import GamipressKaggleScorer

class Integrator:
    def __init__(self, config_json):
        with open(config_json) as f:
            self.config = json.load(f)
        
        self.setup_wordpress()
        self.setup_kaggle2wp_map()
    
    def setup_wordpress(self):
        wp_credentials = self.config['wordpress']['api']['user'] + ':' + self.config['wordpress']['api']['password']
        wp_token = base64.b64encode(wp_credentials.encode())
        self.config['wordpress']['api']['header'] = {'Authorization': 'Basic ' + wp_token.decode('utf-8')}
        return
    
    def setup_kaggle2wp_map(self):
        '''Uses BuddyBoss API to get list of all users
        and extract the custom user field "Kaggle Username".
        
        Ref: https://www.buddyboss.com/resources/api/#api-Members-GetBBMembers'''
        
        ## Find number of pages to read
        bb_members_details_api = self.config['wordpress']['site'] + "/wp-json/buddyboss/v1/members/details"
        r = requests.get(url=bb_members_details_api, headers=self.config['wordpress']['api']['header']).json()
        
        users_per_page = 100
        total_pages = (r['tabs']['all']['count'] // users_per_page) + 1
        
        ## Read user details from each available page
        bb_members_api = self.config['wordpress']['site'] + "/wp-json/buddyboss/v1/members?per_page=%d&page=%d"
        
        self.kaggle2wp_id = {}
        for page_num in range(total_pages):
            r = requests.get(url=bb_members_api % (users_per_page, page_num+1), headers=self.config['wordpress']['api']['header'])
            for user in r.json():
                kaggle_username = user['xprofile']['groups']['1']['fields']['4']['value']['raw']
                if not kaggle_username:
                    continue
                # Assume multiple forgery boys will use same Kaggle username
                if kaggle_username not in self.kaggle2wp_id:
                    self.kaggle2wp_id[kaggle_username] = []
                self.kaggle2wp_id[kaggle_username].append(user['id'])
        
        return
    
    def run_rewarder(self):
        GamipressKaggleScorer(self.config, self.kaggle2wp_id).issue_rewards()
