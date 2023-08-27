import json
import re
import configparser
from datetime import datetime
import logging

# aws
import boto3
from botocore.exceptions import ClientError

LOCAL_SECRET = "../secret/dev_secret.ini"

"""
[prod only] (aws)
def get_secret(env: str) -> obj:
def get_config(env: str, SECRET: obj) -> obj:
def get_file_s3(bucket: str, object_key: str) -> obj:
def upload_file_s3(bucket: str, file_name: str, file: Dict) -> bool:

def save_file(bucket: str, file_name: str, data: Dict):

def write_to_json(file: str, data: Dict) -> None:
def read_to_json(file: str) -> Dict:
def saving_log(file: str, log: str) -> None:

def check_fields(topic: str, record: Dict) -> Dict:
"""


def get_secret(env):
    # GET SECRET k-v
    if env == "local":
        secret = configparser.ConfigParser()
        secret.read(LOCAL_SECRET)
        return secret["SECRET"]
    elif env == "aws_lambda":
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

def get_config(env, SECRET):
    BUCKET = SECRET["bucket"]
    CONFIG_FILE = SECRET["config_file"]

    config = configparser.ConfigParser()
    if env == "local":
        config.read(CONFIG_FILE)
    elif env == "aws_lambda":
        # config.read_string(get_file_s3(bucket=BUCKET, object_key=CONFIG_FILE))
        # lambda cache issue -> s3 XXXXX
        config.read(CONFIG_FILE)

    return config


def get_file_s3(bucket, object_key):
    s3 = boto3.client('s3')
    return s3.get_object(Bucket=bucket, Key=object_key)["Body"].read().decode()


def upload_file_s3(bucket, file_name, data):
    encode_data = bytes(json.dumps(data).encode('UTF-8'))
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket, Key=file_name, Body=encode_data)
        return True
    except:
        return False


def save_file(bucket, file_name, data):
    print(f"saving_file.. {bucket}/{file_name}")
    if bucket == "local_env":
        return write_to_json("/"+file_name, data)
    else:
        return upload_file_s3(bucket, file_name, data)


def write_to_json(file, data):
    import os
    if not file or not data:
        print("No Params (file:str, data:Dict)")
        return False
    try:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            f.write(json.dumps(data))
        return True
    except:
        return False

def read_to_json(file):
    if not file:
        print("No Params (file:str)")
        return None

    with open(file, "r") as f:
        data = json.load(f)
    return data

def saving_log(file, log):
    if not file or not log:
        print("No Params (file:str, log:str)")
        return None

    try:
        with open(file, "w") as f:
            f.write(log)
        return True
    except:
        return False


def check_fields(topic, fields, record, err_count):
    """
    에러는 항상 수집필드(fields) 기준으로 발생.
    record의 데이터 수, 키값 불일치 는 문제 없음.
    
    fill the crawl field
    :param topic: "luxury_profile" | "luxury_media" | "hashtag_media"
    :param fields: config[topic] (Dict)
    :param record: data_record (Dict)
    :param err_count:
    :return: record to Dict
    """
    type_check = {"str": str, "int": int, "url": str, "timestamp": str}
    default_value = {"str": "", "int": 0, "url": "", "timestamp": "1970-01-01T00:00:00+0000"}

    ret = {}

    # 필수필드 (id) 누락
    if "id" not in record.keys():
        err_text = f"{topic}-[required field does not exist] id"
        err_count[err_text] = err_count.get(err_text, 0) + 1
        logging.error(f"{topic}-[required field does not exist] id")
        return {}

    # 필수필드 (id) 값 형식 체크
    id_pattern = "\d+"
    if not re.match(id_pattern, record["id"]):
        # id 형식 에러
        err_text = f"{topic}-[id format error] id is {record['id']}"
        err_count[err_text] = err_count.get(err_text, 0) + 1
        logging.error(f"{topic}-[id format error]\t{record['id']}\tid is {record['id']}")
        return {}

    # DEST FILE= {field}:data[{res_field}] .. type:(res_type)
    for field, type in fields.items():
        res_field, res_type = type.split()

        # 예상된 필드 유무 체크
        if res_field not in record.keys():
            # not found field
            err_text = f"{topic}-[not found field] {field}({res_field})"
            err_count[err_text] = err_count.get(err_text, 0) + 1
            logging.warning(f"{topic}-[not found field]\t{record['id']}\t{field}({res_field})")
            ret[field] = default_value[res_type]
            continue

        var = record.get(res_field)
        flag = True

        # 예상된 데이터 타입 체크
        if not isinstance(var, type_check[res_type]):
            # 리턴 타입 에러
            err_text = f"{topic}-[data type error] {field} is {var}"
            err_count[err_text] = err_count.get(err_text, 0) + 1
            logging.warning(f"{topic}-[data type error]\t{record['id']}\t{field}({res_type}) is {var}")
            flag = False

        else:
            if res_type == "url":
                url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
                if var and not re.match(url_pattern, var):
                    # url 형식 에러
                    err_text = f"{topic}-[url format error] {field} is {var}"
                    err_count[err_text] = err_count.get(err_text, 0) + 1
                    logging.warning(f"{topic}-[url format error]\t{record['id']}\t{field} is {var}")
                    flag = False

            elif res_type == "timestamp":
                # timestamp_pattern = "^(19|2[0-9])[0-9]{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])((\\+|-)[0-1][0-9]{3})?$"
                # if var and not re.match(timestamp_pattern, var):
                #     # timestamp 형식 에러
                #     err_text = f"{topic}-[timestamp format error] {field} is {var}"
                #     err_count[err_text] = err_count.get(err_text, 0) + 1
                #     print(f"{topic}-[timestamp format error]\t{record['id']}\t{field}, {var}")
                try:
                    datetime.strptime(var, "%Y-%m-%dT%H:%M:%S%z")
                except:
                    # timestamp 형식 에러
                    err_text = f"{topic}-[timestamp format error] {field} is {var}"
                    err_count[err_text] = err_count.get(err_text, 0) + 1
                    logging.warning(f"{topic}-[timestamp format error]\t{record['id']}\t{field} is {var}")
                    flag = False

            elif res_field == "media_product_type":
                if var not in ["AD", "FEED", "STORY", "REELS"]:
                    err_text = f"{topic}-[media_product_type domain not allowed] {field} is {var}"
                    err_count[err_text] = err_count.get(err_text, 0) + 1
                    logging.warning(f"{topic}-[media_product_type domain not allowed]\t{record['id']}\t{field} is {var}")
                    flag = False

            elif res_field == "media_type":
                if var not in ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"]:
                    err_text = f"{topic}-[media_type domain not allowed] {field} is {var}"
                    err_count[err_text] = err_count.get(err_text, 0) + 1
                    logging.warning(f"{topic}-[media_type domain not allowed]\t{record['id']}\t{field} is {var}")
                    flag = False


        ret[field] = (var if flag else default_value[res_type])

    return ret


if __name__=="__main__":
    pass
    # print(get_list("../secret/asdf.txt"))
    # print(get_list("../secret/hashtags.txt"))

