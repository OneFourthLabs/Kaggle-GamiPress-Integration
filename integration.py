import base64
import json
import requests

class Integrator:
    def __init__(self, config_json):
        with open(config_json) as f:
            config = json.load(f)
        
        self.setup_wordpress(config)
        self.setup_kaggle2wp_map()
    
    def setup_wordpress(self, config):
        self.wp_domain = config['wordpress']['site']
        self.wp_credentials = config['wordpress']['api']['user'] + ':' + config['wordpress']['api']['password']
        self.wp_token = base64.b64encode(self.wp_credentials.encode())
        self.wp_header = {'Authorization': 'Basic ' + self.wp_token.decode('utf-8')}
        return
    
    def setup_kaggle2wp_map(self):
        '''Uses BuddyBoss API to get list of all users
        and extract the custom user field Kaggle ID'''
        
        ## Find number of pages to read
        bb_members_details_api = self.wp_domain + "/wp-json/buddyboss/v1/members/details"
        r = requests.get(url=bb_members_details_api, headers=self.wp_header).json()
        
        users_per_page = 100
        total_pages = (r['tabs']['all']['count'] // users_per_page) + 1
        
        
        ## Read user details from each available page
        bb_members_api = self.wp_domain + "/wp-json/buddyboss/v1/members?per_page=%d&page=%d"
        
        self.kaggle2wp_id = {}
        for page_num in range(total_pages):
            r = requests.get(url=bb_members_api % (users_per_page, page_num+1), headers=self.wp_header)
            for user in r.json():
                kaggle_username = user['xprofile']['groups']['1']['fields']['4']['value']['raw']
                if not kaggle_username:
                    continue
                # Assume multiple forgery boys will use same Kaggle username
                if kaggle_username not in self.kaggle2wp_id:
                    self.kaggle2wp_id[kaggle_username] = []
                self.kaggle2wp_id[kaggle_username].append(user['id'])
        
        return
    
if __name__ == '__main__':
    print(Integrator('config.json').kaggle2wp_id)
