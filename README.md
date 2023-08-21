# LuxuryBrands_DataCollector

```
instagram graph api docs
https://developers.facebook.com/docs/instagram-api
```


- 프로필데이터
  - `luxury_profiles_{"%y%m%d_%H%M_%S"}.json`
  - Fields
    - user_id : 
    - user_name : 
    - name : 
    - profile_picture_url : 
    - followers_count : 
    - media_count : 
  
- 프로필_미디어 최신 25건
  - `luxury_media_{"%y%m%d_%H%M_%S"}.json`
  - Fields
    - media_id : 
    - timestamp : 
    - caption : 
    - media_type :
    - media_product_type :
    - media_url : 
    - permalink : 
    - like_count : 
    - comments_count : 

- 해시태그 미디어 최신 25건
  - `hashtag_media_{"%y%m%d_%H%M_%S"}.json`
  - Fields
    - media_id : 
    - media_type : 
    - caption : 
    - comments_count : 
    - like_count : 
    - timestamp : 