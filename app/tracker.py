import requests

from messages import TRIALS_REPORT_FAILURE, TRIALS_REPORT_TEMPLATE
from settings import d2_api_root, d2_app_api_key

d2_app_header = {'X-API-Key': d2_app_api_key}


def get_player_by_query(query):
    api_url = d2_api_root + '/User/SearchUsers/'

    resp = requests.get(api_url, params={'q': query}, headers=d2_app_header)
    return resp.json()


def get_membership_info(membership_id, membership_type):
    api_url = d2_api_root + '/User/GetMembershipsById/{}/{}/'.format(membership_id, membership_type)

    resp = requests.get(api_url, headers=d2_app_header)
    return resp.json()


def get_destiny_profile(membership_type, destiny_membership_id):
    api_url = d2_api_root + '/Destiny2/{}/Profile/{}/'.format(membership_type, destiny_membership_id)

    components = {'components': '100,102'}
    resp = requests.get(api_url, headers=d2_app_header, params=components)
    return resp.json()


def get_stats_osiris(membership_type, destiny_membership_id, character_id):
    api_url = d2_api_root + '/Destiny2/{}/Account/{}/Character/{}/Stats/Activities/'.format(membership_type,
                                                                                            destiny_membership_id,
                                                                                            character_id)

    components = {'mode': 84, 'count': 250}
    resp = requests.get(api_url, headers=d2_app_header, params=components)
    return resp.json()


def calculate_mean_kda(osiris_response):
    activities = osiris_response['Response']['activities']

    kda_sum = 0

    for game in activities:
        kda_sum = kda_sum + game['values']['killsDeathsAssists']['basic']['value']

    return kda_sum / len(activities)


def calculate_win_streaks(osiris_response):
    flawless_count = 0

    activities = osiris_response['Response']['activities']

    last_result = 0
    streak = 0
    for game in activities:
        game_result = game['values']['standing']['basic']['value']  # victory = 0, defeat = 1

        if (last_result == game_result) & (game_result == 0):
            streak = streak + 1
        if last_result != game_result:
            streak = 0

        if streak == 7:
            streak = 0
            flawless_count = flawless_count + 1

        last_result = game_result

    return flawless_count


def find_actual_membership_id_account(username, search_results):
    response = search_results['Response']

    for player in response:
        if username.lower() == player['displayName'].lower():
            return player['membershipId']

    return -1


def find_in_game_membership_id(player_profile, platform):
    memberships = player_profile['Response']['destinyMemberships']

    for membership in memberships:
        if membership['membershipType'] == platform:
            return membership['membershipId']

    return -1


def create_report(username, platform):
    players = get_player_by_query(username)
    actual_membership_id = find_actual_membership_id_account(username, players)
    player_profile = get_membership_info(actual_membership_id, platform)
    in_game_membership_id = find_in_game_membership_id(player_profile, platform)
    destiny_profile = get_destiny_profile(1, in_game_membership_id)
    character_ids = destiny_profile['Response']['profile']['data']['characterIds']

    common_mean_kda = 0
    flawless_count = 0
    for character_id in character_ids:
        try:
            stat = get_stats_osiris(1, in_game_membership_id, character_id)
            common_mean_kda = common_mean_kda + calculate_mean_kda(stat)
            flawless_count = flawless_count + calculate_win_streaks(stat)
        except Exception:
            print("Some exception occurred: privacy setting or Bungie API is shit")

    common_mean_kda = common_mean_kda / len(character_ids)

    return round(common_mean_kda, 2), flawless_count, in_game_membership_id


def render_report(username, platform):
    try:
        kda, flawless, mem_id = create_report(username, platform)
        if kda == 0:
            return TRIALS_REPORT_FAILURE
        return TRIALS_REPORT_TEMPLATE.format(kda, flawless, mem_id)
    except Exception:
        return TRIALS_REPORT_FAILURE
