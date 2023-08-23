# LuxuryBrands_DataCollector

```
instagram graph api docs
https://developers.facebook.com/docs/instagram-api
```

### local test need
- `../secret/dev_secret.ini`
  ```
  [SECRET]
  ig_user_id = {123123}
  access_token = {aBcDE}
  bucket = local_env
  config_file = configure.ini
  ```

## collect data
- 프로필 기본 정보
- 프로필 미디어
- 해시태그 검색 미디어
  

- ### 프로필 기본 정보 - 1시간마다   
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
  
- ### 프로필 미디어 최신 25건 - 1시간마다   
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


- ### 해시태그 검색 미디어 최신 25건   
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
