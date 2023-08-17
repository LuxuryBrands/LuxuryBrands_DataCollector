import boto3
import requests
import configparser
from datetime import datetime
import json
import re
from botocore.exceptions import ClientError


now = lambda: datetime.now().strftime("%y%m%d_%H%M_%S")
now_ms = lambda: datetime.now().strftime("%y%m%d_%H%M_%S.%f")


"""
[prod only] (aws)
def get_secret() -> obj:
def get_file_s3(bucket: str, object_key: str) -> obj:
def upload_file_s3(bucket: str, file_name: str, file: str) -> bool:

def get_hashtag_id(tag_name: str) -> str
def get_hashtag_search(hashtag_id: str, limit: int, page_count: int) -> List[Dict]:
def check_fields(topic: str, record: Dict) -> Dict:
def err_check(error_text: str) -> None:
def fill_field_hashtag(data_list: List[Dict]) -> List[Dict]:
"""


s3 = boto3.client('s3')


def get_secret():
    secret_name = "DE-2-1-SECRET"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        raise e


def get_file_s3(bucket, object_key):
    return s3.get_object(Bucket=bucket, Key=object_key)["Body"].read().decode()


def upload_file_s3(bucket, file_name, file):
    encode_file = bytes(json.dumps(file).encode('UTF-8'))
    try:
        s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
        return True
    except:
        return False



SECRET = get_secret()

BUCKET = SECRET["bucket"]
CONFIG_FILE = SECRET["config_file"]

config = configparser.ConfigParser()
config.read_string(get_file_s3(bucket=BUCKET, object_key=CONFIG_FILE))

WRITE_LOCATION_HASHTAGS = config["aws"]["hashtags_location"]

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
            print(f"[data type error]\t{record['id']}\t{field} is {var}")

        if res_type == "url":
            url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            if var and not re.match(url_pattern, var):
                # url 형식 에러
                err_check(f"[url format error] {field} is {var}")
                print(f"[url format error]\t{record['id']}\t{field}, {var}")

        if res_type == "timestamp":
            timestamp_pattern = "^(19|2[0-9])[0-9]{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])((\\+|-)[0-1][0-9]{3})?$"
            if var and not re.match(timestamp_pattern, var):
                # timestamp 형식 에러
                err_check(f"[timestamp format error] {field} is {var}")
                print(f"[timestamp format error]\t{record['id']}\t{field}, {var}")

        ret[field] = (var if var else default_value[res_type])

    return ret


def err_check(error_text):
    ERR_COUNT[error_text] = ERR_COUNT.get(error_text, 0) + 1


def fill_field_hashtag(data_list):
    hashtag_data = []

    for data in data_list:
        hashtag_record = check_fields("hashtag_media", data)
        hashtag_data.append(hashtag_record)

    return hashtag_data


def lambda_handler(event, context):
    hashtags = config["topic"]["hashtags"].split()

    line = "{time:14}\t{name:14}\t[{media}] {error}\n"
    log = ""
    log += line.format(time="time", name="brand_name", media="MEDI", error="")

    hashtag_results = {}

    start_time = now()
    print(f"start: {now_ms()}\n")
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
            print(e)

        log += line.format(
            time=request_time,
            name=hashtag,
            media=media_log,
            error=error
        )

        hashtag_results[hashtag] = fill_field_hashtag(data)
        print()

    f = upload_file_s3(bucket=BUCKET, file_name=WRITE_LOCATION_HASHTAGS.format(start_time=start_time), file=hashtag_results)
    if f:
        print(f"WRITE TO [{WRITE_LOCATION_HASHTAGS.format(start_time=start_time)}] COMPLETE.")
    else:
        print("FAIL UPLOAD.")
    # upload_file_s3(bucket=BUCKET, file_name=f"logs/hashtag_media_{start_time}.txt", file=log)

    err_log = f"{' ERROR ':=^50}\n"
    for k,v in ERR_COUNT.items():
        err_log += f"{k:<45}{v:>5}\n"
    err_log += "="*50

    print(err_log)

    if f:
        return {
            'statusCode': 200,
            'start_time': start_time,
            'end_time': now(),
            'body': json.dumps('end processing\nupload success'),
            'error_log': json.dumps(err_log),
            'target_file': json.dumps(BUCKET+"/"+WRITE_LOCATION_HASHTAGS.format(start_time=start_time))
        }
    else:
        return {
            'statusCode': 400,
            'start_time': start_time,
            'end_time': now(),
            'body': json.dumps('end processing\nupload fail'),
            'error_log': json.dumps(err_log)
        }