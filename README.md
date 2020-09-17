# Kaggle-GamiPress Integration

## Requirements

- Python 3.7+
- WordPress, with plugins:
  - [BuddyBoss](https://www.buddyboss.com/platform/)
  - [GamiPress](https://wordpress.org/plugins/gamipress/) and [Integration with BuddyBoss](https://wordpress.org/plugins/gamipress-buddyboss-integration/)
  - [GamiPress Extended Rest API](https://gamipress.com/add-ons/gamipress-rest-api-extended/)

- Ensure an extended user profile field called "Kaggle Username" is added:
  - Ensure your WordPress Register page is linked to BuddyBoss Register page.
  - Go to BuddyBoss->Profiles
  - In 'SignUp' Details, add a new field for "Kaggle ID" (as 4th field in that list)

## Setup & Running

- Setup all the required fields in `config.json`
- To run: `python main.py`

## Notes

- Works only for score types: Accuracy
- The `score_threshold` and correspoding reward points can be found as pairs in `scores_to_points` field of the config.
- Currently, the awarded points get added directly only to the user's balance.
  - To also register the awarded points as user earnings, [add this PHP hook](https://wordpress.org/support/topic/api-to-award-points-by-adding-to-user-earnings-and-balance/) to WordPress using the [Code Snippets](https://wordpress.org/plugins/code-snippets/) plugin.
