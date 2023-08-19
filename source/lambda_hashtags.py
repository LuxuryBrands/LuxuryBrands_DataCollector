import requests
import configparser
from datetime import datetime
import json
import utils


"""
def get_hashtag_id(tag_name: str) -> str
def get_hashtag_search(hashtag_id: str, limit: int, page_count: int) -> List[Dict]:
def fill_field_hashtag(data_list: List[Dict]) -> List[Dict]:
"""

ENV = "aws"


if ENV == "aws":
    SECRET = utils.get_secret()
elif ENV == "dev":
    secret = configparser.ConfigParser()
    secret.read("../secret/dev_secret.ini")
    SECRET = secret["SECRET"]

BUCKET = SECRET["bucket"]
CONFIG_FILE = SECRET["config_file"]

config = configparser.ConfigParser()
if ENV == "aws":
    config.read_string(utils.get_file_s3(bucket=BUCKET, object_key=CONFIG_FILE))
elif ENV == "dev":
    config.read(CONFIG_FILE)

WRITE_LOCATION_HASHTAGS = config[ENV]["hashtags_location"]
YMD = config["common"]["ymd"]
DATETIME = config["common"]["datetime"]

ERR_COUNT = {}






def get_hashtag_id(tag_name):
    if not tag_name:
        print("tag_name is empty!")
        return None

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    end_point += "/ig_hashtag_search"

    params = {
        "user_id": SECRET["ig_user_id"],
        "q": tag_name,
        "access_token": SECRET["access_token"],
    }

    res = requests.get(end_point, params=params)

    if res.status_code == 200:
        return res.json()["data"][0]["id"]

    print("get hashtag_id FAIL", res.status_code)
    print(res.text)
    raise AssertionError(res.json()["error"]["message"])


def get_hashtag_search(hashtag_id, limit=25, page_count=1):

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    # recent_media | top_media
    end_point += f"/{hashtag_id}/recent_media"

    hashtag_fields = ",".join([v.split()[0] for v in config["hashtag_media"].values()])

    params = {
        "user_id": SECRET["ig_user_id"],
        "fields": hashtag_fields,
        # not used fields
        # children, permalink, media_url
        "access_token": SECRET["access_token"],
        "limit": limit,
    }

    # print(f"request url : {end_point}")
    start_request = datetime.now()
    print(f"request time: {start_request.strftime('%y%m%d_%H%M_%S.%f')}", end="")
    res = requests.get(end_point, params=params)
    duration = datetime.now()-start_request
    print(f"\tDuration: {duration.total_seconds()}")

    if res.status_code == 200:
        print("REQUESTS SUCCESS")
        return res.json()["data"]

    print("REQUESTS FAIL", res.status_code)
    print(res.text)
    raise AssertionError(res.json()["error"]["message"])


def fill_field_hashtag(hashtag, data_list):
    hashtag_data = []

    for data in data_list:
        data["user_id"] = config["add_user_id"][hashtag]
        hashtag_record = utils.check_fields("hashtag_media", config["hashtag_media"], data, ERR_COUNT)
        hashtag_data.append(hashtag_record)

    return hashtag_data


def lambda_handler(event, context):
    hashtags = config["topic"]["hashtags"].split()

    line = "{time:14}\t{name:14}\t[{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", media="MEDI", error="")

    hashtag_results = []

    start_time = datetime.now()
    print(f"start: {datetime.now().strftime('%y%m%d_%H%M_%S.%f')}\n")
    for i, hashtag in enumerate(hashtags):
        print(f"API request processing.. TAG[{hashtag}]({i+1}/{len(hashtags)}) : ", end="")
        try:
            hashtag_id = get_hashtag_id(hashtag)
            print(hashtag_id)
            data = get_hashtag_search(hashtag_id)
            if data:
                # hashtag_data exist
                pass
        except Exception as e:
            print(e, "\n")
        else:
            hashtag_data = fill_field_hashtag(hashtag, data)
            hashtag_results.extend(hashtag_data)
            print()

    file_flag = True
    target_files = ""
    for file_name, data in [[
                                WRITE_LOCATION_HASHTAGS, hashtag_results
                            ]]:
        if data:
            file_name = file_name.format(ymd=start_time.strftime(YMD), date_time=start_time.strftime(DATETIME))
            f = utils.save_file(bucket=BUCKET, file_name=file_name, data=data)
            target_files += f"{BUCKET}/{file_name}\n"
        else:
            f = False
        file_flag &= f
        if f:
            print(f"WRITE TO [{BUCKET}/{file_name}] COMPLETE.")
        else:
            print("FAIL UPLOAD.")
    # write_log somewhere

    err_log = f"{' ERROR ':=^70}\n"
    for k,v in ERR_COUNT.items():
        err_log += f"{k:<45}{v:>5}\n"
    err_log += "="*70

    print(err_log)

    if file_flag:
        return {
            'statusCode': 200,
            'start_time': start_time.strftime("%y%m%d_%H%M_%S"),
            'end_time': datetime.now().strftime("%y%m%d_%H%M_%S"),
            'body': json.dumps('end processing\nupload success'),
            'error_log': json.dumps(err_log),
            'target_file': json.dumps(target_files)
        }
    else:
        return {
            'statusCode': 400,
            'start_time': start_time.strftime("%y%m%d_%H%M_%S"),
            'end_time': datetime.now().strftime("%y%m%d_%H%M_%S"),
            'body': json.dumps('end processing\nupload fail'),
            'error_log': json.dumps(err_log)
        }


if ENV == "dev":
    lambda_handler({}, {})