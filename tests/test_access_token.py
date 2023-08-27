import unittest
import configparser
import requests
from datetime import datetime, timedelta
import os

from source.config_update \
    import get_fb_user_id, get_fb_page_id, get_ig_user_id



class access_token_test(unittest.TestCase):
    """
    TOKEN VALIDATION TEST
    """

    def setUp(self) -> None:
        self.ig_user_id = os.environ.get("ig_user_id")
        self.access_token = os.environ.get("access_token")
        self.config = configparser.ConfigParser()
        self.config.read("configure.ini")

    def test_access_token_is_valid(self):
        """
        유효한 access_token 체크
        - api요청, 응답 여부 (response.status_code == 200)
        - 만료 여부 (response["is_valid"])
        - fb_user_id와 일치 여부  (response["user_id"])
        - 만료기간 일주일 이상인지 여부 (response["data_access_expires_at"])
        """
        end_point = self.config["API"]["end_point"]
        end_point = end_point.format(VERSION=self.config["API"]["version"])
        params = {
            "input_token": self.access_token,
            "access_token": self.access_token,
        }
        res = requests.get(end_point + "/debug_token", params=params)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["data"]["is_valid"])

        fb_user_id = get_fb_user_id(end_point, access_token=self.access_token)
        self.assertEqual(res.json()["data"]["user_id"], fb_user_id)

        expires_at = datetime.fromtimestamp(res.json()["data"]["data_access_expires_at"])
        today = datetime.now()
        token_remaining_time = expires_at-today

        self.assertGreater(token_remaining_time, timedelta(days=7))

    def test_auth_user_for_access_token(self):
        """
        access_token 기반 ig_user_id 동일 여부
        """
        end_point = self.config["API"]["end_point"]
        end_point = end_point.format(VERSION=self.config["API"]["version"])

        fb_page_id = get_fb_page_id(end_point=end_point, access_token=self.access_token)
        self.assertTrue(fb_page_id)

        ig_user_id = get_ig_user_id(end_point=end_point, fb_page_id=fb_page_id, access_token=self.access_token)
        self.assertTrue(ig_user_id)

        self.assertEqual(ig_user_id, self.ig_user_id)



if __name__ == "__main__":
    unittest.main()