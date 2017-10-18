from google.cloud import bigquery
import uuid
from typing import Tuple

from sql import SAVE_FILTERED_USER_ID_QUERY
from sql import SAVE_FAVORITE_SHARES_IN_TIERS

PROJECT = 'candidate-evaluation'
DATASET = 'task_results'
FILTERED_USER_IDS_TABLE = 'a1_results'
FAVORITE_SHARES_IN_TIERS_TABLE = 'a2_results'

QUERY_TIMEOUT = 14 * 60_000  # 14 minutes


def create_table(dataset: bigquery.dataset.Dataset, table_name: str,
                 table_schema: Tuple[bigquery.SchemaField, ...]) -> None:

    table = dataset.table(table_name)

    if table.exists():
        # i'm deleting the table each time for simplicity,
        # in a real system it should probably archived or versioned
        table.delete()

    table.schema = table_schema
    table.create()


def submit_query_and_wait(
        client: bigquery.Client,
        label: str,
        query: str,
        timeout: int,
        params: Tuple[bigquery.ScalarQueryParameter, ...] = (),
        dry_run: bool = True) -> None:

    query_job = client.run_async_query(
        '{}_job_{}'.format(label, uuid.uuid4()),
        query,
        query_parameters=params)

    query_job.use_legacy_sql = False
    query_job.dry_run = dry_run

    query_job.begin()
    query_job.result(timeout=timeout)


def execute_queries() -> None:
    client = bigquery.Client(project=PROJECT)
    dataset = client.dataset(DATASET)

    if not dataset.exists():
        print('Dataset {} does not exist.'.format(DATASET))
        exit(1)

    create_table(dataset, FILTERED_USER_IDS_TABLE,
                 (bigquery.SchemaField('user_id', 'INTEGER'), ))

    create_table(dataset, FAVORITE_SHARES_IN_TIERS_TABLE, (
        bigquery.SchemaField('user_id', 'INTEGER'),
        bigquery.SchemaField('tier', 'STRING'),
        bigquery.SchemaField('share', 'FLOAT'),
    ))

    submit_query_and_wait(
        client,
        label='save_filtered_user_ids_query',
        query=SAVE_FILTERED_USER_ID_QUERY.format(PROJECT, DATASET,
                                                 FILTERED_USER_IDS_TABLE),
        timeout=QUERY_TIMEOUT,
        params=(bigquery.ScalarQueryParameter('tags_regexp', 'STRING',
                                              'java|python'),
                bigquery.ScalarQueryParameter('year', 'STRING', 2016)))

    # we only wait to show a message to the user
    submit_query_and_wait(
        client,
        label='save_favorite_shares_in_tiers_query',
        query=SAVE_FAVORITE_SHARES_IN_TIERS.format(
            PROJECT, DATASET, FAVORITE_SHARES_IN_TIERS_TABLE,
            FILTERED_USER_IDS_TABLE),
        timeout=QUERY_TIMEOUT)

    print('Done.')


if __name__ == "__main__":
    execute_queries()
