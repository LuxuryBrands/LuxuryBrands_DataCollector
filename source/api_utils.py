import requests
import json
import sys
import configparser
from datetime import datetime
now = lambda :datetime.now().strftime("%y%m%d_%H%M_%S")

CONFIG_FILE = "../configure.ini"

"""
사용 X 파일
유닛테스트 시 검증용으로 사용
"""

"""
access_token 기반으로
- fb_user_id, fb_page_id, ig_user_id
- [token_debug]
내용 갱신하는 코드
"""

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
        print("saved..")


def check_access_token(end_point, access_token):
    """
    only use update for config.ini
    :return: YYYY-MM-DD hh:mm:ss
            # 2023-10-06 18:40:50
    """
    params = {
        "input_token": access_token,
        "access_token": access_token,
    }

    res = requests.get(end_point + "/debug_token", params=params)
    config["ACCESS_TOKEN"] = res.json()["data"]
    config["ACCESS_TOKEN"]["access_token"] = access_token
    config["ACCESS_TOKEN"]["expires_at_date"] = str(datetime.fromtimestamp(res.json()["data"]["expires_at"]))
    config["ACCESS_TOKEN"]["data_access_expires_at_date"] = str(datetime.fromtimestamp(res.json()["data"]["data_access_expires_at"]))
    save_config(config)


def get_fb_user_id(end_point, access_token):
    res = requests.get(end_point + "/me", params={"access_token":access_token})
    if res.status_code==200:
        return res.json()["id"]
    else:
        return None

def get_fb_page_id(end_point, access_token):
    res = requests.get(end_point + "/me/accounts", params={"access_token":access_token})
    if res.status_code==200:
        return res.json()["data"][0]["id"]
    else:
        return None

def get_ig_user_id(end_point, fb_page_id ,access_token):
    res = requests.get(end_point + f"/{fb_page_id}",
                       params={
                           "fields": "instagram_business_account",
                           "access_token":access_token
                       })

    if res.status_code==200:
        return res.json()["instagram_business_account"]["id"]
    else:
        return None


# def token_exchange(token):
#     # call_only_once
#     """
#     장기토큰으로 전환.
#     앱 설정에서 클라이언트 ID, SECRET 확인 가능.
#     """
#     params = {
#         "grant_type": "fb_exchange_token",
#         "client_id": self.CLIENT_ID,
#         "client_secret": self.CLIENT_SECRET,
#         "fb_exchange_token": self.access_token,
#     }
#     res = requests.get(self.base_url + "/oauth/access_token", params=params)
#     token = res.json()["access_token"]
#     print(token)
#     return token

if __name__=="__main__":
    """
    [SECRET]access_token이 있는 상태에서 실행 시
    [SECRET]fb_user_id
    [SECRET]fb_page_id
    [SECRET]ig_user_id
    세가지 내용과 [ACCESS_TOKEN] 정보 업데이트.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    end_point = config["API"]["end_point"]
    end_point = end_point.format(VERSION=config["API"]["version"])
    access_token = config["SECRET"]["access_token"]

    check_access_token(end_point=end_point, access_token=access_token)

    fb_user_id = get_fb_user_id(end_point=end_point, access_token=access_token)
    config["SECRET"]["fb_user_id"] = fb_user_id

    fb_page_id = get_fb_page_id(end_point=end_point, access_token=access_token)
    config["SECRET"]["fb_page_id"] = fb_page_id

    ig_user_id = get_ig_user_id(end_point=end_point, fb_page_id=fb_page_id, access_token=access_token)
    config["SECRET"]["ig_user_id"] = ig_user_id

    save_config()