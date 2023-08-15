# LuxuryBrands_DataCollector

```
instagram graph api docs
https://developers.facebook.com/docs/instagram-api
curl -i -X GET \
 "https://graph.facebook.com/v3.2/17841405309211844?fields=business_discovery.username(bluebottle){followers_count,media_count,media}&access_token={access-token}"
```

`*`가 붙은 필드는 append용으로 복제하여 수집.

- 프로필데이터
  - `luxury_profile_{account}_{"%y%m%d_%H%M_%S"}.json`
  - Fields
    - user_id : 
    - user_name : 
    - name : 
    - profile_picture_url : 
    - followers_count : 
    - media_count : 
    - *followers_count :
    - *media_count : 
  
- 프로필_미디어 최신 25건
  - `luxury_media_{account}_{"%y%m%d_%H%M_%S"}.json`
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
    - *like_count : 
    - *comments_count : 

- 해시태그 미디어 최신 25건
  - `luxury_hashtag_media_{account}_{"%y%m%d_%H%M_%S"}.json`
  - Fields
    - media_id : 
    - media_type : 
    - caption : 
    - comments_count : 
    - like_count : 
    - timestamp : 