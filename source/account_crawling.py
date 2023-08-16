import requests
import configparser
from datetime import datetime
from utils import *
import inspect

now = lambda:datetime.now().strftime("%y%m%d_%H%M_%S")

CONFIG_FILE = "../secret/configure.ini"

"""
def get_account_media(user_name: str) -> Tuple(Dict, Dict) 
"""


def get_account_media(user_name="", page_count=1):
    if not user_name:
        print("pls enter user_name")
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    end_point += f"/{config['SECRET']['ig_user_id']}"

    params = {
        "fields": "business_discovery.username({username}){fields}" \
            .format(
                username=user_name,
                fields="{id,username,name,profile_picture_url,followers_count,media_count,"
                       "media{id,timestamp,caption,media_type,media_product_type,media_url,permalink,like_count,comments_count}}",
                # not used field
                # user - ig_id, follows_count, biography
                # media - owner
            ),
        "access_token": config["SECRET"]["access_token"],
    }

    print(f"request url : {end_point}")
    res = requests.get(end_point, params=params)

    if res.status_code == 200:
        print("REQUESTS SUCCESS")
        # print(res.text)
        data = res.json().get("business_discovery",{})
        return data

    print("REQUESTS FAIL")
    print(res.status_code, res.json()["error"]["message"])

    if res.status_code == 403 and res.json()["error"]["code"]:
        # (#4) Application request limit reached
        raise AssertionError(res.json()["error"]["message"])
    raise AssertionError(res.json()["error"]["message"])


def fill_field_profile_media(data):
    profile_data = {
        "user_id": data.get("id", ""),
        "user_name": data.get("username", ""),
        "name": data.get("name", ""),
        "profile_picture_url": data.get("profile_picture_url", ""),
        "followers_count": data.get("followers_count", -1),
        "media_count": data.get("media_count", -1),
    }

    media_list = data.get("media", {}).get("data", [{}])
    media_data = []
    for media in media_list:
        media_record = {
            "media_id": media.get("id", ""),
            "timestamp": media.get("timestamp", ""),
            "caption": media.get("caption", ""),
            "media_type": media.get("media_type", ""),
            "media_product_type": media.get("media_product_type", ""),
            "media_url": media.get("media_url", ""),
            "permalink": media.get("permalink", ""),
            "like_count": media.get("like_count", -1),
            "comments_count": media.get("comments_count", -1)
        }
        media_data.append(media_record)

    return profile_data, media_data



if __name__ == "__main__":

    accounts = get_list("../secret/accounts.txt")

    line = "{time:14}\t{name:14}\t[{profile}|{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", profile="PROF", media="MEDI", error="")

    profile_results = {}
    media_results = {}

    start_time = now()
    print("start:", start_time)
    for i, account in enumerate(accounts):
        print(f"API request processing.. ACCOUNT:[{account}].. ({i+1}/{len(accounts)})")
        data = {}
        request_time = now()
        profile_log = "FAIL"
        media_log = "FAIL"
        error = ""
        try:
            data = get_account_media(account)
            if data:
                profile_log = "DONE"
            if data.get("media", {}).get("data", False):
                media_log = "DONE"
        except Exception as e:
            error = str(e)

        log += line.format(
            time=request_time,
            name=account,
            profile=profile_log,
            media=media_log,
            error=error
        )
        profile, media = fill_field_profile_media(data)
        profile_results[account] = profile
        media_results[account] = media
        print()

    write_to_json(f"../data/luxury_profiles_{start_time}.json", profile_results)
    write_to_json(f"../data/luxury_media_{start_time}.json", media_results)

    file_name = inspect.getfile(inspect.currentframe()).split("\\")[-1]
    saving_log(f"../logs/{file_name}_{now()}.txt", log)

