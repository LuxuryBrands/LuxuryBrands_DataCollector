# LuxuryBrands_DataCollector

<img src="https://img.shields.io/badge/python-3776AB?style=flat&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/awslambda-FF9900?style=flat&logo=awslambda&logoColor=white"/>

aws Lambda에서 [인스타그램 그래프 API](https://developers.facebook.com/docs/instagram-api)
를 이용하여 계정 데이터를 수집하여 s3에 적재합니다.

```
end_point = https://graph.facebook.com/{VERSION}
version = v17.0
```

**요청 시 필요한 user_id는 ig_user_id임*

![collector_flow.png](dev_logs/collector_flow.png)

데이터 수집이 우선이므로 일부 데이터 에러에 대해서는 느슨한 처리를 하였음. (일부 데이터로 인한 전체 데이터 수집 오류 방지)   
    -> 크리티컬한 실패를 제외하고는 오류가 있는 데이터만을 제외하고, 정상 동작으로 정의 함.   
다만 데이터 실패/품질에 대한 여부 로깅을 확실히 함으로써 이후 파악 가능하도록 함.

- 레코드 단위, 필드 단위 오류 구분
    - 필수 필드 존재 유무 여부
        - id
    - 필수 필드 포맷 일치 여부
        - id
    - 필드값 존재 유무 여부
    - 데이터 타입 일치 여부
    - 데이터 포맷 일치 여부
        - url
        - timestamp
    - 데이터 도메인 일치 여부
        - media_product_type
        - media_type

- 오류 데이터는 default값으로 채워 저장.
    - 문자형 `""`
    - 정수형 `0`

- - -

## local test need
- `../secret/dev_secret.ini`
  
  ```
  [SECRET]
  ig_user_id = {123123}
  access_token = {aBcDE}
  bucket = local_env
  config_file = configure.ini
  ```

- - -

## 수집 개요 및 수집 요구사항

- API 제한사항
    - API요청 개인 사용자 앱 1당 시간 당 200회   
    `Calls within one hour = 200 * Number of Users`
        - business_discovery
        - hashtag_id search
    - 해시태그 검색 7일간 30종류, 1일 당 4800회
        - hashtag search

다음 11개 명품 브랜드 계정에 대해서 인스타그램 내 계정 프로필 정보와, 미디어 그리고 해시태그로 검색된 미디어를 수집한다.

사전에 정의된 ERD모델링 네이밍과 동일한 필드 명으로 매핑

brand, media, media_hashtag 세 모델로 데이터를 저장

brand, media는 1시간마다 계정정보, 25개 미디어 수집

media_hashtag는 5분마다 25개 미디어 수집

nested 데이터를 모두 flatten 데이터로 저장. -> `List[Dict]` 형태

### 수집 계정 및 해시태그

    #hermes #chanel #dior   #louisvuitton   #gucci  #prada  #ysl    #celine #valentino  #miumiu #fendi

### API 요청에 따른 응답 / 수집 필드

- **/business_discovery.username(`USER_NAME`)**

    *request time :* `1request per 1hours`   
    *data rows :*   
        *- brand(account_profile) :* `1row per 1request`   
        *- media(account_medias) :* `25rows per 1request`   
    *response field :* 
        ```
        id, username, name, profile_picture_url, followers_count, media_count, media{ id, timestamp, caption, media_type, media_product_type, media_url, permalink, like_count, comments_count }
        ```

- **/`HASHTAG_ID`/recent_media**

    *request time :* `1request per 5minutes`   
    *data rows :* `25rows per 1request`   
    *response field :*
        ```
        id, timestamp, caption, media_type, like_count, comments_count
        ```

- - -

### 수집 데이터

ymd = `%Y-%m-%d`   
datetime = `%Y-%m-%d_%H%M%S`

API응답 필드에서 JSON저장 파일 필드 매핑은 `configure.ini` 파일 참조.

*user_id는 모두 바뀌지 않는다는 가정하게 configure.ini에서 메타로 추가해서 사용 

- #### brand (프로필 기본 정보)   
  `BUCKET` / `raw/brand_{ymd}` / `brand_{datetime}.json`
    ```
    [
        {
            "user_id":             str  ('17841400681603877')
            "user_name":           str  ('hermes')
            "name":                str  ('Hermès')
            "profile_picture_url": url  ('https://scontent-*.*.*.net/v/*')
            "followers_count":     int
            "media_count":         int
        },
        {
            "fields": ...
        },
        {}, {}, {}, ...
    ]
    ```
  
- #### media (프로필 미디어 최신)
  `BUCKET` / `raw/media_{ymd}` / `media_{datetime}.json`
    ```
    [
        {
            "user_id":            str        ('17841400681603877')
            "media_id":           str        ('17872654964957867')
            "timestamp":          timestamp  ('2023-08-16T09:30:00+0000')
            "caption":            str        ('hello\ninsta')
            "media_type":         str        ('IMAGE'|'VIDEO'|'CAROUSEL_ALBUM')
            "media_product_type": str        ('AD'|'FEED'|'STORY'|'REELS')
            "media_url":          url        ('https://*.*instagram.com/*')
            "permalink":          url        ('https://www.instagram.com/(type)/*/')
            "like_count":         int
            "comments_count":     int
        },
        {
            "fields": ...
        },
        {}, {}, {}, ...
    ]
    ```


- #### media_hashtag (해시태그 검색 미디어 최신)   
  `BUCKET` / `raw/media_hashtag_{ymd}` / `media_hashtag_{datetime}.json`
    ```
    [
        {
            "user_id":        str        ('17841401770520874')
            "media_id":       str        ('18006172678923441')
            "timestamp":      timestamp  ('2023-08-16T09:30:00+0000')
            "caption":        str        ('hello\ninsta')
            "media_type":     str        ('IMAGE'|'VIDEO'|'CAROUSEL_ALBUM')
            "like_count":     int
            "comments_count": int
        },
        {
            "fields": ...
        },
        {}, {}, {}, ...
    ]
    ```

## 로깅
![log_alert.png](dev_logs/log_alert.png)

# 이후 개선 사항
- AWS Cloudwatch에서 로그 그룹화하여 출력
- 에러 등급 별 구분   
  `DEBUG|INFO|WARNING|ERROR|CRITICAL`