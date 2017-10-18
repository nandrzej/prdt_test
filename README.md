prdt_test
==============================

Command line tool invoking BigQuery queries.

Implementation notes
------------
* Tiers are calculated based on `favorite_count` ranking and the first one can contain 
up to 3 elements and seconds one up to 7. That means that if several questions have the same 
`favorite_count` they can land in different tiers. This behaviour can be easily changed by using `RANK()` 
function instead of `ROW_NUMBER()` in `SAVE_FAVORITE_SHARES_IN_TIERS`
* For simplicity tables are deleted and created again with each run. It means that in case of 
data corruption or other problems there wouldn't be a copy of the data to fall back on. 
In a real system I could use timestamp column or move the old data to different, archive table 
depending on requirements. 
* Since whole logic depends on Google APIs and mocks are not available only the integration test 
is provided. It just performs dry run of the query jobs to check for errors.
