import requests
import configparser
from datetime import datetime
from utils import *
import re

now = lambda: datetime.now().strftime("%y%m%d_%H%M_%S")
now_ms = lambda: datetime.now().strftime("%y%m%d_%H%M_%S.%f")


"""
def get_account_media(user_name: str, page_count: int) -> Tuple[Dict, Dict]:
def check_fields(topic: str, record: Dict) -> Dict:
def err_check(error_text: str) -> None:
def fill_field_profile_media(data: Tuple[Dict, List]) -> Tuple[Dict, List]:
"""


CONFIG_FILE = "../secret/configure.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

WRITE_LOCATION_PROFILES = config["dev"]["profiles_location"]
WRITE_LOCATION_MEDIA = config["dev"]["media_location"]

ERR_COUNT = {}



def get_account_media(user_name="1", page_count=1):
    if not user_name:
        print("pls enter user_name")
        return None

    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    end_point += f"/{config['SECRET']['ig_user_id']}"

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
        "access_token": config["SECRET"]["access_token"],
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


def check_fields(topic, record):
    """
    fill the crawl field
    :param topic: "luxury_profile" | "luxury_media" | "hashtag_media"
    :param record: data_record (Dict)
    :return: record to Dict
    """
    type_check = {"str":str, "int":int, "url":str, "timestamp":str}
    default_value = {"str":"", "int":-1, "url":"", "timestamp":"1970-01-01T00:00:00+0000"}

    fields = config[topic]
    ret = {}

    for field, type in fields.items():
        res_field, res_type = type.split()

        var = record.get(res_field, None)
        if not isinstance(var, type_check[res_type]):
            # 리턴 타입 에러
            err_check(f"[data type error] {field} is {var}")
            print(f"[data type error]\t{('p' if topic=='luxury_profile' else '')+record['id']}\t{field} is {var}")

        if res_type == "url":
            url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            if var and not re.match(url_pattern, var):
                # url 형식 에러
                err_check(f"[url format error] {field} is {var}")
                print(f"[url format error]\t{('p' if topic=='luxury_profile' else '')+record['id']}\t{field}, {var}")

        if res_type == "timestamp":
            timestamp_pattern = "^(19|2[0-9])[0-9]{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])((\\+|-)[0-1][0-9]{3})?$"
            if var and not re.match(timestamp_pattern, var):
                # timestamp 형식 에러
                err_check(f"[timestamp format error] {field} is {var}")
                print(f"[timestamp format error]\t{('p' if topic=='luxury_profile' else '')+record['id']}\t{field}, {var}")

        ret[field] = (var if var else default_value[res_type])

    return ret


def err_check(error_text):
    ERR_COUNT[error_text] = ERR_COUNT.get(error_text, 0) + 1


def fill_field_profile_media(data):
    profile_data = check_fields("luxury_profile", data)

    media_list = data.get("media", {}).get("data", [{}])
    media_data = []
    for media in media_list:
        media_record = check_fields("luxury_media", media)
        media_data.append(media_record)

    return profile_data, media_data



if __name__ == "__main__":
    accounts = config["topic"]["accounts"].split()

    line = "{time:14}\t{name:14}\t[{profile}|{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", profile="PROF", media="MEDI", error="")

    profile_results = {}
    media_results = {}

    start_time = now()
    print(f"start: {now_ms()}\n")
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
            print(e)

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

    write_to_json(WRITE_LOCATION_PROFILES.format(start_time=start_time), profile_results)
    write_to_json(WRITE_LOCATION_MEDIA.format(start_time=start_time), media_results)

    # saving_log(f"../logs/account_{now()}.txt", log)

    err_log = f"{' ERROR ':=^50}\n"
    for k,v in ERR_COUNT.items():
        err_log += f"{k:<45}{v:>5}\n"
    err_log += "="*50

    print(err_log)