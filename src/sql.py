SAVE_FILTERED_USER_ID_QUERY = """
    INSERT INTO
      `{0}.{1}.{2}` (user_id)
    SELECT
      DISTINCT p.owner_user_id
    FROM
      `bigquery-public-data.stackoverflow.stackoverflow_posts` AS p
    JOIN
      `bigquery-public-data.stackoverflow.users` AS u
    ON
      (u.id=p.owner_user_id)
    WHERE
      REGEXP_CONTAINS(p.tags, @tags_regexp)
      AND FORMAT_DATETIME('%Y',
        CAST(p.last_activity_date AS DATETIME)) = @year
      AND p.owner_user_id IS NOT NULL
      AND u.reputation >= @reputation
"""

SAVE_FAVORITE_SHARES_IN_TIERS = """
    INSERT INTO
      `{0}.{1}.{2}` (user_id, tier, share)
    WITH
      favorites_sum_per_tiers AS (
      SELECT
        w.owner_user_id,
        SUM(w.favorite_count) AS sum_per_tier,
        CASE
          WHEN row_no BETWEEN 1 AND 3 THEN 'Tier 1'
          WHEN row_no BETWEEN 4 AND 10 THEN 'Tier 2'
          ELSE 'Tier 3'
        END AS tier
      FROM (
        SELECT
          owner_user_id,
          favorite_count,
          ROW_NUMBER() OVER (
            PARTITION BY owner_user_id
            ORDER BY favorite_count DESC) AS row_no
        FROM
          `bigquery-public-data.stackoverflow.stackoverflow_posts`
        WHERE
            owner_user_id IN (SELECT user_id FROM `{0}.{1}.{3}`)
        ) w
      GROUP BY
        owner_user_id,
        tier),
      favorites_sum_per_user AS (
      SELECT
        owner_user_id,
        SUM(favorite_count) AS sum_per_user
      FROM
        `bigquery-public-data.stackoverflow.stackoverflow_posts`
      WHERE
        owner_user_id IN (SELECT user_id FROM `{0}.{1}.{3}`)
      GROUP BY
        owner_user_id)
    SELECT
      favorites_sum_per_user.owner_user_id AS userId,
      favorites_sum_per_tiers.tier AS tier,
      CASE
        WHEN favorites_sum_per_user.sum_per_user != 0
        THEN
            favorites_sum_per_tiers.sum_per_tier
            / favorites_sum_per_user.sum_per_user
        ELSE 0
      END AS share
    FROM
      favorites_sum_per_tiers
    JOIN
      favorites_sum_per_user
    ON
      (favorites_sum_per_tiers.owner_user_id=favorites_sum_per_user.owner_user_id)
"""
# ^ no ORDER BY because result are inserted into a table
