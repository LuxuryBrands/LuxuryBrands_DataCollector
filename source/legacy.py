import requests
import json
from typing import *
from datetime import datetime

"""
instagram graph api docs
https://developers.facebook.com/docs/instagram-api

"""

ln = lambda:print("="*50)
class graph:

    base_url = f"https://graph.facebook.com/{VERSION}"
    CLIENT_ID = ""
    CLIENT_SECRET = ""
    FB_USER_ID = ""
    IG_USER_ID = ""
    # client_token = ""
    # access_token = ""
    access_token = ""





    def get_influencer(self, username: str) -> Dict:
        """
        Query basic information about influencer \n
        fields: [id, ig_id, username, name, followers_count, follows_count, media_count, biography]
        :return: Dict
        """
        url = self.base_url + f"/{self.IG_USER_ID}"
        # rozy = "17841439998241060"
        params = {
            "fields":"business_discovery.username({username}){fields}" \
                .format(
                username=username,
                fields="{id,ig_id,username,name,followers_count,follows_count,media_count,biography,profile_picture_url}",
                # fields="{id,ig_id,username,name}",
        ),
            "access_token":self.access_token,
        }
        res = requests.get(url, params=params)
        # print(res.json())
        data = res.json()["business_discovery"]
        return data

    def get_influencer_media(self, username, page_count=3):
        url = self.base_url + f"/{self.IG_USER_ID}"
        rozy = "17841439998241060"
        # discovery의 media탐색에서는 limit이 지원 안됨. =25
        fields = "business_discovery.username({username}){sub_fields}"
        sub_fields = "{username,media_count,media" \
            "{id,like_count,comments_count,media_product_type,media_type,caption,media_url,permalink,timestamp}}"
        # - media{username,owner}
        params = {
            "access_token":self.access_token,
        }

        id = ""
        after = "a"
        ret_data = []
        page_number = 1
        media_count_all = 0
        while after and page_number <= page_count:
            print(f"now load.. [{page_number}]", end="")
            params["fields"] = fields.format(username=username, sub_fields=sub_fields)
            res = requests.get(url, params=params)
            if res.status_code!=200:
                print(self.prettify(res.json()))
                exit(1)
            tmp = res.json()
            if not id:
                id = tmp["business_discovery"]["id"]
            try:
                # print(tmp)
                data = tmp["business_discovery"]["media"]["data"]
                ret_data.extend(data)
            except:
                print(self.prettify(tmp))

            media_count_page = len(data)
            print(f"  - DONE {media_count_page}")
            media_count_all += media_count_page

            after = None
            try:
                after = tmp["business_discovery"]["media"]["paging"]["cursors"]["after"]
            except:
                print("애프터 왜없냐")

            if not after:
                print(f"end of page.. [{page_number}]")
                break

            page_number += 1
            sub_fields = "{username,media_count,media.after("+ after +"){id,like_count,comments_count,media_product_type,media_type,caption,media_url,permalink,timestamp}}"

        print(f"complete media count {media_count_all}")
        return ret_data


    @staticmethod
    def hash_prettify(data_list):
        for data in data_list:
            print(graph.prettify(data))

    @staticmethod
    def prettify(text):
        if isinstance(text, str):
            print(json.dumps(json.loads(text), indent=4,))
        if isinstance(text, dict):
            print(json.dumps(text, indent=4,))

    def get_hashtag_id(self, keyword):
        end_point = "/ig_hashtag_search"
        params={
            "user_id":self.IG_USER_ID,
            "q":keyword,
            "access_token":self.access_token,
        }
        res = requests.get(self.base_url+end_point, params=params)
        return res.json()["data"][0]["id"]


    def get_hashtag_search(self, id, limit=25, page_count=3):
        """
        limit_max = 50
        default = 11개
        limit=3 page_count=10 -> 게시글 11개
        limit=5 page_count=5 -> 게시글 11개
        """
        # recent_media | top_media
        end_point = f"/{id}/top_media"
        params={
            "user_id":self.IG_USER_ID,
            "fields":"id,media_type,caption,comments_count,like_count,timestamp,children,permalink,media_url",
            # 가능한 필드들
            # id, media_type, caption, comments_count, like_count,
            # timestamp, children, permalink, media_url
            "access_token":self.access_token,
            "limit":limit,
        }

        next_url = self.base_url+end_point
        ret_data = []
        page_number = 1
        media_count_all = 0
        appended_count = 0
        prev_res = None
        tmp_point = 0
        try:
            while next_url and page_number <= page_count:
                tmp_point = 0
                print(f"now load.. [{page_number}]", end="")
                res = requests.get(next_url, params=params)
                tmp_point = 1
                tmp = res.json()

                tmp_point = 2
                data = tmp["data"]
                ### temp code
                appended_count += len(data)
                # write_to_json(data, "./data/pepsi", f"pepsi{page_number}")
                tmp_point = 3
                ret_data.extend(data)

                media_count_page = len(data)
                print(f"  - DONE {media_count_page}")
                media_count_all += media_count_page
                tmp_point = 4

                next_url = None
                if "paging" in tmp:
                    if "next" in tmp["paging"]:
                        next_url = tmp["paging"]["next"]
                    elif "after" in tmp["paging"]["cursors"]:
                        next_url = self.base_url + \
                                    f"{self.IG_USER_ID}/recent_media"
                        params["after"] = tmp["paging"]["cursors"]["after"]

                if not next_url:
                    print(f"end of page.. [{page_number}]")
                    break
                tmp_point = 5

                page_number += 1
                prev_res = res
        except Exception as e:
            print("""⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐
            ⭐⭐⭐⭐⭐⭐⭐망함⭐⭐⭐⭐⭐⭐⭐
            ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐""")
            print(e, f"point:{tmp_point}")
            ln()
            print("NEXT_URL and PARAMS")
            print(next_url, params)
            ln()
            print(res.status_code)
            print("💸res.header\n",res.headers)
            ln()
            print("🌙prev_res.json()\n",prev_res.json())
            ln()
            try:
                print("😊res.json()\n",res.json())
            except:
                print("res.json()망ㅎ마~~~~")
            try:
                print("😊res.text\n",res.text)
            except:
                print("res.text망함ㅁ~~~~")
            ln()
            print("💥appended_count\n",appended_count)

        print(f"complete media count {media_count_all}")
        return ret_data


def write_to_json(data, dir, file_name):
    if not file_name.endswith(".json"):
        file_name += ".json"
    with open(f"{dir}/{file_name}", "w") as f:
        f.write(json.dumps(data))
    print(f"wirte~~ {dir}/{file_name}")

def read_to_json(dir, file_name):
    if not file_name.endswith(".json"):
        file_name += ".json"
    with open(f"{dir}/{file_name}", "r") as f:
        data = json.load(f)
    return data

# 수집한 json파일 길이 분석
if 0:
    data = read_to_json("./data","tmp")
    media_url_max = 0
    permalink_max = 0
    for d in data:
        print(d["media_url"])
        ln()
        media_url_max = max(media_url_max, len(d["media_url"]))
        permalink_max = max(permalink_max, len(d["permalink"]))
    print(f"media_url_max:{media_url_max}")
    print(f"permalink_max:{permalink_max}")

g = graph()
influencer = [
    "selenagomez",
    "lechat.vv",
    "rozy.gram",
    "imapoki",
    "rina.8k",
    "ruuui_li",
    "here.me.lucy",
    "theo.rises",
    "sua_to_z",
    "_hanyua",
    "hogonheil",
]


if 0:
    for name in ["insta_conn_fb_ttt"]:#influencer:
        data = g.get_influencer(username=name)
        print(data)
        ln()
        print(g.prettify(data))
        ln()

# 인플루언서 요청 테스트용~
if 0:
    t = 0
    for name in influencer:
        data = g.get_influencer(username=name)
        print(data)
        ln()
        t = max(t, len(data["profile_picture_url"]))
    print(t)

# 인플루언서 그냥 검색 요령
if 0:
    for name in [influencer[1]]:
        print(f"now reading {name}..")
        data = g.get_influencer_media(username=name, page_count=1)
        print(data)
        save_to_json(data,"./data","tmp")

from collections import defaultdict
# 인플루언서 미디어 유형 카운트
if 0:
    all_data = []
    all_count = defaultdict(int)
    try:
        for name in influencer:
            print(f"now reading {name}..")
            data = g.get_influencer_media(username=name, page_count=8)
            t = defaultdict(int)
            all_data.extend(data)
            for d in data:
                # if d["media_type"]=="CAROUSEL_ALBUM":
                try:
                    t[d["media_product_type"]+"_"+d["media_type"]]+=1
                except:
                    print("엥 에러",d)
            print(t, sum(t.values()))
            ln()
            for k,v in t.items():
                all_count[k] += v
        ln();ln()
        print(all_count)
        print(sum(all_count.values()))
        write_to_json(all_data,"./data","test")

    except:
        print(all_count)
        print(sum(all_count.values()))
        write_to_json(all_data,"./data","test")
    print("END~~~~")
    # for i, d in enumerate(data):
    #     print(f"MEDIA NUMBER : {i+1}/{len(data)}")
    #     # print(d["caption"],"\n")
    #     for k,v in d.items():
    #         if k == "caption":
    #             v = "[ caption exist ]"
    #         if k == "media_url":
    #             v = "[ media_url ]"
    #         print(f"\t{k}: {v}")
    #     ln()


# 해시태그 미디어 수
if 0:
    # g.get_hashtag_count(g.get_hashtag_id("apoki"))
    g.get_hashtag_count("seouldessert")


# 해시태그 검색 요령
if 0:
    hashtags = ["",]
    for tag in hashtags:
        print(f"{tag}")
        hashtag = tag
        id = g.get_hashtag_id(hashtag)
        data = g.get_hashtag_search(id, limit=50, page_count=100)
        # print(data)
        # write_to_json(data, "./data/pepsi", f"{hashtag}")

        ln()
        # for i,d in enumerate(data):
        #     print(f"MEDIA NUMBER : {i+1}/{len(data)}")
        #     print(d["caption"],"\n")
        #     ln()
        print(tag,":",len(data))



