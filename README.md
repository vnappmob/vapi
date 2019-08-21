## vAPI - API Tỉnh thành Việt Nam

Retrieve a list of province
```
[GET] /api/province
[GET] https://vapi.vnappmob.com/api/province
```

Retrieve a list of district in province_id
```
[GET] /api/province/{province_id}/
[GET] /api/province/{province_id}/district
[GET] https://vapi.vnappmob.com/api/province/{province_id}
[GET] https://vapi.vnappmob.com/api/province/{province_id}/district
```

Retrieve a list of ward in district_id
```
[GET] /api/province/{province_id}/{district_id}/
[GET] /api/province/{province_id}/district/{district_id}/
[GET] /api/province/{province_id}/district/{district_id}/ward
```

---
CREATE DATABASE vapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
mysql -u root -p vapi_db < vapi_db.sql;
mysql -u root -p -e "SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';"
mysql -u root -p -e "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"
SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
