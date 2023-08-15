import requests
import configparser
import inspect
from datetime import datetime
from utils import *


now = lambda :datetime.now().strftime("%y%m%d_%H%M_%S")

CONFIG_FILE = "../secret/configure.ini"


"""
def get_hashtag_id(tag_name: str) -> str
def get_account_media(user_name: str) -> Tuple(Dict, Dict) 
"""


def get_hashtag_id(tag_name):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    end_point += "/ig_hashtag_search"

    params = {
        "user_id": config['SECRET']['ig_user_id'],
        "q": tag_name,
        "access_token": config["SECRET"]["access_token"],
    }

    res = requests.get(end_point, params=params)

    if res.status_code == 200:
        return res.json()["data"][0]["id"]

    print(res.status_code)
    print(res.json())
    return None


def get_hashtag_search(hashtag_id, limit=25, page_count=1):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    # recent_media | top_media
    end_point += f"/{hashtag_id}/recent_media"

    params = {
        "user_id": config["SECRET"]["ig_user_id"],
        "fields": "id,media_type,caption,comments_count,like_count,timestamp",
        # not used fields
        # children, permalink, media_url
        "access_token": config["SECRET"]["access_token"],
        "limit": limit,
    }

    res = requests.get(end_point, params=params)

    if res.status_code == 200:
        print("REQUESTS SUCCESS")
        return res.json()["data"]

    print("REQUESTS FAIL")
    print(res.status_code)
    print(res.json())
    return None

def fill_field_hashtag(data_list):
    hashtag_data = []
    for data in data_list:
        hashtag_record = {
            "media_id": data.get("media_id", ""),
            "media_type": data.get("media_type", ""),
            "caption": data.get("caption", ""),
            "comments_count": data.get("comments_count", -1),
            "like_count": data.get("like_count", -1),
            "timestamp": data.get("timestamp", "")
        }
        hashtag_data.append(hashtag_record)
    return hashtag_data

if __name__ == "__main__":

    hashtags = get_list("../secret/hashtags.txt")

    line = "{time:14}\t{name:14}\t[{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", media="MEDI", error="")

    hashtag_results = {}

    start_time = now()
    print("start:", start_time)
    for i, hashtag in enumerate(hashtags):
        print(f"API request processing.. TAG[{hashtag}]({i+1}/{len(hashtags)}) : ", end="")
        data = {}
        request_time = now()
        media_log = ""
        error = ""
        try:
            hashtag_id = get_hashtag_id(hashtag)
            print(hashtag_id)
            data = get_hashtag_search(hashtag_id)

            media_log = ["FAIL", "DONE"][bool(data)]
        except Exception as e:
            error = str(e)

        log += line.format(
            time=request_time,
            name=hashtag,
            media=media_log,
            error=error
        )
        hashtag_results[hashtag] = fill_field_hashtag(data)
        print()

    write_to_json(f"../data/hashtag_media_{start_time}.json", hashtag_results)

    file_name = inspect.getfile(inspect.currentframe()).split("\\")[-1]
    saving_log(f"../logs/{file_name}_{now()}.txt", log)