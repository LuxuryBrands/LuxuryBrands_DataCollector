import unittest
import configparser
import os

from source.lambda_accounts import get_account_media
from source.lambda_hashtags import get_hashtag_id, get_hashtag_search



class api_request_test(unittest.TestCase):
    """
    API REQUESTS TEST
    """

    def setUp(self) -> None:
        self.ig_user_id = os.environ.get("ig_user_id")
        self.access_token = os.environ.get("access_token")
        self.SECRET = {"ig_user_id": self.ig_user_id, "access_token": self.access_token}

        self.config = configparser.ConfigParser()
        self.config.read("configure.ini")

    def test_account_requests(self):
        """
        account requests test
        """
        data = get_account_media("hermes", self.config, self.SECRET)

        self.assertIn("id" ,data.keys())
        self.assertIn("username" ,data.keys())
        self.assertIn("followers_count" ,data.keys())
        self.assertIn("media_count" ,data.keys())
        self.assertIn("media" ,data.keys())

        media_data = data["media"]["data"]

        exist_keys = {}
        for d in media_data:
            for k in d.keys():
                exist_keys[k] = ""

        self.assertIn("id", exist_keys)
        self.assertIn("timestamp", exist_keys)
        # self.assertIn("caption", exist_keys)  # nullable
        self.assertIn("media_type", exist_keys)
        self.assertIn("media_product_type", exist_keys)
        self.assertIn("media_url", exist_keys)
        self.assertIn("permalink", exist_keys)
        self.assertIn("like_count", exist_keys)
        self.assertIn("comments_count", exist_keys)

    def test_hashtag_requests(self):
        """
        hashtag requests test
        """
        hashtag_id = get_hashtag_id("hermes", self.config, self.SECRET)
        self.assertTrue(hashtag_id)
        self.assertRegex(hashtag_id, "\d+")

        data = get_hashtag_search(hashtag_id, self.config, self.SECRET)

        exist_keys = {}
        for d in data:
            for k in d.keys():
                exist_keys[k] = ""

        self.assertIn("id", exist_keys)
        self.assertIn("timestamp", exist_keys)
        # self.assertIn("caption", exist_keys)  # nullable
        self.assertIn("media_type", exist_keys)
        self.assertIn("like_count", exist_keys)
        self.assertIn("comments_count", exist_keys)

