CREATE DATABASE vapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
mysql -u root -p vapi_db < vapi_db.sql;
mysql -u root -p -e "SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';"
mysql -u root -p -e "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"
SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
