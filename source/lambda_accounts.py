import requests
import configparser
from datetime import datetime

import json
import utils


"""
def get_account_media(user_name: str, page_count: int) -> Tuple[Dict, Dict]:
def fill_field_profile_media(data: Tuple[Dict, List]) -> Tuple[Dict, List]:
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

WRITE_LOCATION_PROFILES = config[ENV]["profiles_location"]
WRITE_LOCATION_MEDIA = config[ENV]["media_location"]

ERR_COUNT = {}






def get_account_media(user_name="", page_count=1):
    if not user_name:
        print("user_name is empty!")
        return None

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    end_point += f"/{SECRET['ig_user_id']}"

    profile_fields = ",".join([v.split()[0] for v in config["luxury_profile"].values()])
    media_fields = ",".join([v.split()[0] for v in config["luxury_media"].values()])

    params = {
        "fields": "business_discovery.username({username}){fields}" \
            .format(
                username=user_name,
                fields="{" + profile_fields + ",media{" + media_fields + "}}",
                # not used field
                # user - ig_id, follows_count, biography
                # media - owner
            ),
        "access_token": SECRET["access_token"],
    }

    # print(f"request url : {end_point}")
    start_request = datetime.now()
    print(f"request time: {start_request.strftime('%y%m%d_%H%M_%S.%f')}", end="")
    res = requests.get(end_point, params=params)
    duration = datetime.now()-start_request
    print(f"\tDuration: {duration.total_seconds()}")

    if res.status_code == 200:
        print("REQUESTS SUCCESS")
        # print(res.text)
        data = res.json().get("business_discovery",{})
        return data

    print("REQUESTS FAIL", res.status_code)
    print(res.text)

    if res.status_code == 403 and res.json()["error"]["code"]:
        # (#4) Application request limit reached
        raise AssertionError(res.json()["error"]["message"])
    raise AssertionError(res.json()["error"]["message"])


def fill_field_profile_media(account, data):
    profile_data = utils.check_fields(
        "luxury_profile", config["luxury_profile"], data, ERR_COUNT
    )

    media_list = data.get("media", {}).get("data", [{}])
    media_data = []
    for media in media_list:
        media["user_id"] = config["add_user_id"][account]
        media_record = utils.check_fields(
            "luxury_media", config["luxury_media"], media, ERR_COUNT
        )
        media_data.append(media_record)

    return profile_data, media_data


def lambda_handler(event, context):
    accounts = config["topic"]["accounts"].split()

    line = "{time:14}\t{name:14}\t[{profile}|{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", profile="PROF", media="MEDI", error="")

    profile_results = []
    media_results = []

    start_time = datetime.now()
    print(f"start: {datetime.now().strftime('%y%m%d_%H%M_%S.%f')}\n")
    for i, account in enumerate(accounts):
        print(f"API request processing.. ACCOUNT:[{account}].. ({i+1}/{len(accounts)})")
        try:
            data = get_account_media(account)
            if data:
                # profile_data exist
                pass
            if data.get("media", {}).get("data", False):
                # media_data exist
                pass

        except Exception as e:
            print(e, "\n")
        else:
            profile, media = fill_field_profile_media(account, data)
            profile_results.append(profile)
            media_results.extend(media)
            print()

    file_flag = True
    target_files = ""
    for file_name, data in [[
                                WRITE_LOCATION_PROFILES, profile_results
                            ], [
                                WRITE_LOCATION_MEDIA, media_results
                            ]]:
        if data:
            file_name = file_name.format(ymd=start_time.strftime("%y%m%d"), start_time=start_time.strftime("%y%m%d_%H%M_%S"))
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