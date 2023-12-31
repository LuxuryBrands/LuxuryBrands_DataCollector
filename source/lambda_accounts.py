import requests
import json
import logging
from datetime import datetime

import utils

# lambda 로거와 연결
logger = logging.getLogger(__name__)
# INFO이상의 로그만 기록.
logger.setLevel(logging.INFO)

"""
def get_account_media(
    user_name: str,
    config: obj,
    SECRET: obj,
    page_count: int
) -> Tuple[Dict, Dict]:

def fill_field_profile_media(
    data: Tuple[Dict, List],
    config: obj,
    err_count: Dict
) -> Tuple[Dict, List]:
"""

# local | aws_lambda
ENV = "aws_lambda"


def get_account_media(user_name, config, SECRET, page_count=1):
    if not user_name:
        logger.error("user_name is empty!")
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
    logger.info(f"request time: {start_request.strftime('%y%m%d_%H%M_%S.%f')}")
    res = requests.get(end_point, params=params)
    duration = datetime.now()-start_request
    logger.info(f"\tDuration: {duration.total_seconds()}")

    if res.status_code == 200:
        logger.info("REQUESTS SUCCESS")
        # print(res.text)
        data = res.json().get("business_discovery",{})
        return data

    logger.error("REQUESTS FAIL", res.status_code)
    logger.error(res.text)

    if res.status_code == 403 and res.json()["error"]["code"]:
        # (#4) Application request limit reached
        logger.error("(#4) Application request limit reached")
        raise AssertionError(res.json()["error"]["message"])

    raise AssertionError(res.json()["error"]["message"])


def fill_field_profile_media(account, data, config, err_count):
    profile_data = utils.check_fields(
        "luxury_profile", config["luxury_profile"], data, err_count
    )

    media_list = data.get("media", {}).get("data", [{}])
    media_data = []
    for media in media_list:
        media["user_id"] = config["add_user_id"][account]
        media_record = utils.check_fields(
            "luxury_media", config["luxury_media"], media, err_count
        )
        media_data.append(media_record)

    return profile_data, media_data


def lambda_handler(event, context):
    # GET SECRET/CONFIG
    secret = utils.get_secret(env=ENV)
    config = utils.get_config(env=ENV, SECRET=secret)

    if not config or not secret:
        raise AssertionError(
            ("NO PARAMS CONFIG " if not config else "") + \
            ("NO PARAMS SECRET " if not secret else "")
        )

    # SET VARIABLES
    BUCKET = secret["bucket"]
    WRITE_LOCATION_PROFILES = config["common"]["profiles_location"]
    WRITE_LOCATION_MEDIA = config["common"]["media_location"]
    YMD = config["common"]["ymd"]
    DATETIME = config["common"]["datetime"]

    ERR_COUNT = {}

    # RUN
    accounts = config["topic"]["accounts"].split()

    line = "{time:14}\t{name:14}\t[{profile}|{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", profile="PROF", media="MEDI", error="")

    profile_results = []
    media_results = []

    start_time = datetime.now()
    logger.info(f"start: {datetime.now().strftime('%y%m%d_%H%M_%S.%f')}\n")
    # START REQUESTS
    for i, account in enumerate(accounts):
        logger.info(f"API request processing.. ACCOUNT[{account}].. ({i+1}/{len(accounts)})")
        try:
            data = get_account_media(account, config=config, SECRET=secret)
            if not data:
                # profile_data not exist
                raise AssertionError("profile_data not exist")
            if not data.get("media", {}).get("data", False):
                # media_data not exist
                raise AssertionError("media_data not exist")

        except Exception as e:
            logger.warning(e, "\n")
        else:
            profile, media = fill_field_profile_media(account, data, config=config, err_count=ERR_COUNT)
            profile_results.append(profile)
            media_results.extend(media)
            #
    # END REQUESTS

    # FILE SAVING
    file_flag = True
    target_files = ""
    for file_name, data in [[
                                WRITE_LOCATION_PROFILES, profile_results
                            ], [
                                WRITE_LOCATION_MEDIA, media_results
                            ]]:
        if data:
            file_name = file_name.format(ymd=start_time.strftime(YMD), datetime=start_time.strftime(DATETIME))
            f = utils.save_file(bucket=BUCKET, file_name=file_name, data=data)
            target_files += f"{BUCKET}/{file_name}\n"
        else:
            f = False
        file_flag &= f
        if f:
            logger.info(f"WRITE TO [{BUCKET}/{file_name}] COMPLETE.")
        else:
            logger.error("FAIL UPLOAD.")
    # write_log somewhere

    # PRINT ERROR LOG
    err_log = f"{' ERROR ':=^70}\n"
    for k,v in ERR_COUNT.items():
        err_log += f"{k:<45}{v:>5}\n"
    err_log += "="*70

    logger.info(err_log)

    # END FUNCTION
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


if __name__ == "__main__":
    lambda_handler({}, {})