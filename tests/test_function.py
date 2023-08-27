import unittest

from source.utils import check_fields


class check_fields_function_test(unittest.TestCase):

    def setUp(self) -> None:
        pass
    def test_valid_field(self):
        """
        valid field test
        """
        topic = "valid_test"

        dest_key, target_key, target_type, target_data = "d_str", "t_str", "str", "tesT_Data"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_int", "t_int", "int", 1230
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"2", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_int", "t_int", "int", 0
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"2", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_int", "t_int", "int", 73163157
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"2", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_int", "t_int", "int", 650000000
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"2", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_url", "t_url", "url", "https://www.instagram.com/p/CwXgrzuM2tY/"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"3", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_ts", "t_ts", "timestamp", "2023-08-25T12:20:31+0000"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"4", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        brand_profile_picture_url = "https://scontent-sea1-1.xx.fbcdn.net/v/t51.2885-15/46728774_524937071335491_5735839144890859520_n.jpg?_nc_cat=1&ccb=1-7&_nc_sid=86c713&_nc_ohc=4cyqR-XCFPMAX_1uhty&_nc_ht=scontent-sea1-1.xx&edm=AL-3X8kEAAAA&oh=00_AfCsR_Oae4TmFuBqdZd0DPYwmAJhMH53Revv1i8EwnpgBQ&oe=64ED6C9A"
        dest_key, target_key, target_type, target_data = "d_url", "t_url", "str", brand_profile_picture_url
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id": "17841400681603877", target_key: target_data},
                           err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        brand_name = "Herm\u00e8s"
        dest_key, target_key, target_type, target_data = "d_url", "t_url", "str", brand_name
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id": "18035763970539659", target_key: target_data},
                           err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        dest_key, target_key, target_type, target_data = "d_ts", "t_ts", "timestamp", "2023-08-16T00:00:10+0000"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"351244", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        caption = "Soaring silk \ud83e\ude81 Colorful, versatile and poetic: it is all about silk. \u200b\n\n#SilkInTheClouds\u200b\n#DriveMeCrazyCarr\u00e9\u200b\n#HermesSilk\u200b\n#Hermes"
        dest_key, target_key, target_type, target_data = "d_str", "t_str", "str", caption
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"74544563", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_type = "IMAGE"
        dest_key, target_key, target_type, target_data = "d_str", "media_type", "str", media_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"11", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_type = "VIDEO"
        dest_key, target_key, target_type, target_data = "d_str", "media_type", "str", media_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"11", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_type = "CAROUSEL_ALBUM"
        dest_key, target_key, target_type, target_data = "d_str", "media_type", "str", media_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"11", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_product_type = "AD"
        dest_key, target_key, target_type, target_data = "d_str", "media_product_type", "str", media_product_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"12", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_product_type = "FEED"
        dest_key, target_key, target_type, target_data = "d_str", "media_product_type", "str", media_product_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"12", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_product_type = "STORY"
        dest_key, target_key, target_type, target_data = "d_str", "media_product_type", "str", media_product_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"12", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_product_type = "REELS"
        dest_key, target_key, target_type, target_data = "d_str", "media_product_type", "str", media_product_type
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"12", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

        media_url = "https://scontent-sea1-1.cdninstagram.com/o1/v/t16/f1/m82/1D4C38B107EE5B501F2FCFE3FF35B295_video_dashinit.mp4?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLjcyMC5jbGlwcyJ9&_nc_ht=scontent-sea1-1.cdninstagram.com&_nc_cat=110&vs=1760624701045490_3044809697&_nc_vs=HBksFQIYT2lnX3hwdl9yZWVsc19wZXJtYW5lbnRfcHJvZC8xRDRDMzhCMTA3RUU1QjUwMUYyRkNGRTNGRjM1QjI5NV92aWRlb19kYXNoaW5pdC5tcDQVAALIAQAVABgkR0VFWUN4WlVDQlJodm1zQ0FFMm9hc2VoMjc0OWJxX0VBQUFGFQICyAEAKAAYABsBiAd1c2Vfb2lsATEVAAAmvPPU5oKf%2FT8VAigCQzMsF0AbqfvnbItEGBJkYXNoX2Jhc2VsaW5lXzFfdjERAHUAAA%3D%3D&ccb=9-4&oh=00_AfC2DmkHEB29qL832UUCnxNmLYA9oYVbNKHAN7xmg8KpOA&oe=64EA9B70&_nc_sid=1d576d&_nc_rid=9b22d6f490"
        dest_key, target_key, target_type, target_data = "d_url", "t_url", "url", media_url
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"3", target_key:target_data}, err_count)
        self.assertEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 0)

    def test_invalid_field(self):
        """
        invalid field test
        """
        topic = "invalid_test"

        # data type err
        dest_key, target_key, target_type, target_data = "d_str", "t_int", "str", 2000
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # data type err
        dest_key, target_key, target_type, target_data = "d_int", "t_str", "int", "159084352"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # url format err
        dest_key, target_key, target_type, target_data = "d_url", "t_url", "url", "isNotURL"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # ts format err
        dest_key, target_key, target_type, target_data = "d_timestamp", "t_timestamp", "timestamp", "2023-08-23 13:59:34+0000"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # ts format err
        dest_key, target_key, target_type, target_data = "d_timestamp", "t_timestamp", "timestamp", "20230823T13:59:34+0000"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # no id
        dest_key, target_key, target_type, target_data = "d_str", "t_str", "str", "str_data"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {target_key: target_data}, err_count)
        self.assertFalse(ret)
        self.assertEqual(sum(err_count.values()), 1)

        # id format err
        dest_key, target_key, target_type, target_data = "d_str", "t_str", "str", "str_data"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"zxzzxxz", target_key: target_data}, err_count)
        self.assertFalse(ret)
        self.assertEqual(sum(err_count.values()), 1)

        # media_product_type domain err
        dest_key, target_key, target_type, target_data = "d_str", "media_product_type", "str", "VIDEO"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # media_type domain err
        dest_key, target_key, target_type, target_data = "d_str", "media_type", "str", "FEED"
        err_count = {}
        ret = check_fields(topic, {dest_key: f"{target_key} {target_type}"}, {"id":"1", target_key:target_data}, err_count)
        self.assertNotEqual(ret[dest_key], target_data)
        self.assertEqual(sum(err_count.values()), 1)

        # field not match
        fields = {
            "a": "b int",
        }
        record = {
            "id": "112",
            "zz": 123123,
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertEqual(ret["a"], 0)
        self.assertEqual(sum(err_count.values()), 1)

    def test_record(self):
        """
        record test
        """
        topic = "record_test"

        fields = {
            "A": "aa int",
            "B": "bb url",
            "C": "cc timestamp",
        }
        record = {
            "id": "11121212",
            "ab": "abab",
            "bc": 123123,
            "cd": "https://www.naver.com",
            "dd": "2023-08-25T23:46:00+0000",
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertEqual(len(ret.keys()), 3)
        self.assertEqual(ret["A"], 0)
        self.assertEqual(ret["B"], "")
        self.assertEqual(ret["C"], "1970-01-01T00:00:00+0000")
        # self.assertEqual(len(ret.keys()), len(fields.keys()))
        self.assertEqual(sum(err_count.values()), 3)

        # no id
        fields = {
            "A": "aa int",
            "B": "bb url",
            "C": "cc timestamp",
        }
        record = {
            "ab": "abab",
            "bc": 123123,
            "cd": "https://www.naver.com",
            "dd": "2023-08-25T23:46:00+0000",
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertFalse(ret)
        self.assertEqual(sum(err_count.values()), 1)

        # id format err
        fields = {
            "ID": "id str",
            "A": "aa int",
            "B": "bb url",
            "C": "cc timestamp",
            "D": "dd str",
        }
        record = {
            "id": "axcvb",
            "ab": "abab",
            "bc": 123123,
            "cd": "https://www.naver.com",
            "dd": "2023-08-25T23:46:00+0000",
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertFalse(ret)
        self.assertEqual(sum(err_count.values()), 1)

        # field matched, data type err
        fields = {
            "ID": "id str",
            "A": "ab int",
            "B": "bc url",
            "C": "cd timestamp",
            "D": "dd str",
            "E": "media_product_type str",
        }
        record = {
            "id": "123010242148921",
            "ab": "abab",
            "bc": 123123,
            "cd": "https://www.naver.com",
            "dd": "2023-08-25T23:46:00+0000",
            "media_product_type": "IMAGE",
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertEqual(len(ret.keys()), 6)
        self.assertEqual(sum(err_count.values()), 4)

        # all fine
        fields = {
            "ID": "id str",
            "A": "ab int",
            "B": "bc url",
            "C": "cd timestamp",
            "D": "dd str",
            "E": "media_product_type str",
            "F": "media_type str",
        }
        record = {
            "id": "123010242148921",
            "ab": 123123,
            "bc": "https://www.naver.com",
            "cd": "2023-08-25T23:46:00+0000",
            "dd": "abab",
            "media_product_type": "REELS",
            "media_type": "CAROUSEL_ALBUM"
        }
        err_count = {}
        ret = check_fields(topic, fields, record, err_count)
        self.assertEqual(len(ret.keys()), 7)
        self.assertTrue(ret)
        self.assertEqual(sum(err_count.values()), 0)



if __name__ == "__main__":
    unittest.main()