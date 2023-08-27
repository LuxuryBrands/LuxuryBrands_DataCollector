import requests
import json
import logging
from datetime import datetime

from source import utils

# lambda 로거와 연결
logger = logging.getLogger(__name__)
# INFO이상의 로그만 기록.
logger.setLevel(logging.INFO)

"""
def get_hashtag_id(
    tag_name: str,
    config: obj,
    SECRET: obj
) -> str

def get_hashtag_search(
    hashtag_id: str,
    config: obj,
    SECRET: obj,
    limit: int,
    page_count: int
) -> List[Dict]:

def fill_field_hashtag(
    data_list: List[Dict],
    config: obj,
    err_count: Dict
) -> List[Dict]:
"""

# local | aws_lambda
ENV = "aws_lambda"


def get_hashtag_id(tag_name, config, SECRET):
    if not tag_name:
        raise AssertionError("tag_name is empty!")

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

    logger.error("get hashtag_id FAIL", res.status_code)
    logger.error(res.text)
    raise AssertionError(res.json()["error"]["message"])


def get_hashtag_search(hashtag_id, config, SECRET, limit=25, page_count=1):
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
    logger.info(f"request time: {start_request.strftime('%y%m%d_%H%M_%S.%f')}", end="")
    res = requests.get(end_point, params=params)
    duration = datetime.now()-start_request
    logger.info(f"\tDuration: {duration.total_seconds()}")

    if res.status_code == 200:
        logger.info("REQUESTS SUCCESS")
        return res.json()["data"]

    logger.error("REQUESTS FAIL", res.status_code)
    logger.error(res.text)
    raise AssertionError(res.json()["error"]["message"])


def fill_field_hashtag(hashtag, data_list, config, err_count):
    hashtag_data = []

    for data in data_list:
        data["user_id"] = config["add_user_id"][hashtag]
        hashtag_record = utils.check_fields("hashtag_media", config["hashtag_media"], data, err_count)
        hashtag_data.append(hashtag_record)

    return hashtag_data


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
    WRITE_LOCATION_HASHTAGS = config["common"]["hashtags_location"]
    YMD = config["common"]["ymd"]
    DATETIME = config["common"]["datetime"]

    ERR_COUNT = {}

    # RUN
    hashtags = config["topic"]["hashtags"].split()

    line = "{time:14}\t{name:14}\t[{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", media="MEDI", error="")

    hashtag_results = []

    start_time = datetime.now()
    logger.info(f"start: {datetime.now().strftime('%y%m%d_%H%M_%S.%f')}\n")
    # START REQUESTS
    for i, hashtag in enumerate(hashtags):
        logger.info(f"API request processing.. TAG[{hashtag}]({i+1}/{len(hashtags)}) : ", end="")
        try:
            hashtag_id = get_hashtag_id(hashtag, config=config, SECRET=secret)
            logger.info(hashtag_id)
            data = get_hashtag_search(hashtag_id, config=config, SECRET=secret)
            if data:
                # hashtag_data exist
                pass
        except Exception as e:
            logger.warning(e, "\n")
        else:
            hashtag_data = fill_field_hashtag(hashtag, data, config=config, err_count=ERR_COUNT)
            hashtag_results.extend(hashtag_data)
            #
    # END REQUESTS

    # FILE SAVING
    file_flag = True
    target_files = ""
    for file_name, data in [[
                                WRITE_LOCATION_HASHTAGS, hashtag_results
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