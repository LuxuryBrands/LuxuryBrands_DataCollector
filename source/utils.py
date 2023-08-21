import json
import re
import configparser

# aws
import boto3
from botocore.exceptions import ClientError


LOCAL_CONFIG = "../secret/dev_secret.ini"

"""
[prod only] (aws)
def clearing_lambda_tmp() -> None:
def get_secret(ENV: str) -> obj:
def get_config(ENV: str, SECRET: obj) -> obj:
def get_file_s3(bucket: str, object_key: str) -> obj:
def upload_file_s3(bucket: str, file_name: str, file: Dict) -> bool:

def save_file(bucket: str, file_name: str, data: Dict):

def write_to_json(file: str, data: Dict) -> None:
def read_to_json(file: str) -> Dict:
def saving_log(file: str, log: str) -> None:

def check_fields(topic: str, record: Dict) -> Dict:
"""

def clearing_lambda_tmp() -> None:
    import os
    tmp_file_path = "/tmp"
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
        return True
    return False

def get_secret(ENV):
    if ENV == "aws":
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
    elif ENV == "dev":
        secret = configparser.ConfigParser()
        secret.read(LOCAL_CONFIG)
        return secret["SECRET"]

def get_config(ENV, SECRET):
    BUCKET = SECRET["bucket"]
    CONFIG_FILE = SECRET["config_file"]

    config = configparser.ConfigParser()
    if ENV == "aws":
        config.read_string(get_file_s3(bucket=BUCKET, object_key=CONFIG_FILE))
    elif ENV == "dev":
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
        return write_to_json(file_name, data)
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

    for field, type in fields.items():
        res_field, res_type = type.split()

        var = record.get(res_field, None)
        if not isinstance(var, type_check[res_type]):
            # 리턴 타입 에러
            err_text = f"{topic}-[data type error] {field} is {var}"
            err_count[err_text] = err_count.get(err_text, 0) + 1
            print(f"{topic}-[data type error]\t{record['id']}\t{field} is {var}")

        if res_type == "url":
            url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            if var and not re.match(url_pattern, var):
                # url 형식 에러
                err_text = f"{topic}-[url format error] {field} is {var}"
                err_count[err_text] = err_count.get(err_text, 0) + 1
                print(f"{topic}-[url format error]\t{record['id']}\t{field}, {var}")

        if res_type == "timestamp":
            timestamp_pattern = "^(19|2[0-9])[0-9]{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])((\\+|-)[0-1][0-9]{3})?$"
            if var and not re.match(timestamp_pattern, var):
                # timestamp 형식 에러
                err_text = f"{topic}-[timestamp format error] {field} is {var}"
                err_count[err_text] = err_count.get(err_text, 0) + 1
                print(f"{topic}-[timestamp format error]\t{record['id']}\t{field}, {var}")

        ret[field] = (var if var else default_value[res_type])

    return ret


if __name__=="__main__":
    pass
    # print(get_list("../secret/asdf.txt"))
    # print(get_list("../secret/hashtags.txt"))

