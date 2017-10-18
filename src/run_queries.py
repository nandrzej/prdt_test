import argparse
import uuid
import sys
from typing import Tuple
from google.api.core.exceptions import GoogleAPIError
from google.cloud import bigquery

from sql import SAVE_FILTERED_USER_ID_QUERY
from sql import SAVE_FAVORITE_SHARES_IN_TIERS
"""
This script runs the two queries described in the task requirements
(repo/prdt_test/references/Data Engineer FT 2017 - test task.pdf).

First query fetches a list of filtered user ids, second one
uses the list, calculates favorite questions share and saves them.
"""

PROJECT = 'candidate-evaluation'
DATASET = 'task_results'
FILTERED_USER_IDS_TABLE = 'a1_results'
FAVORITE_SHARES_IN_TIERS_TABLE = 'a2_results'

QUERY_TIMEOUT = 14 * 60000  # 14 minutes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run scripts for tasks a1 and a2.')
    parser.add_argument(
        '--dry_run',
        type=bool,
        required=False,
        default=False,
        help='Connect to Google Cloud and test the queries.')
    return parser.parse_args()


def create_table(dataset: bigquery.dataset.Dataset, table_name: str,
                 table_schema: Tuple[bigquery.SchemaField, ...]) -> None:
    """
    Creates a table for given dataset with given name.
    Deletes the old one if exists.
    """

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
        dry_run: bool = False) -> None:
    """
    Submits a standard SQL,  asynchronous query job using given client
    with given label (unique id is added to it) and timeout. Accepts query
    parameters. Can be run in dry_run mode (queries are validated,
    nothing is fetched)
    """
    try:
        query_job = client.run_async_query(
            '{}_job_{}'.format(label, uuid.uuid4()),
            query,
            query_parameters=params)

        query_job.use_legacy_sql = False
        query_job.dry_run = dry_run

        query_job.begin()
        query_job.result(timeout=timeout)
    except GoogleAPIError as e:
        print('Error occurred while trying to run the {} query: {}'
              .format(label, e))
        exit(1)


def execute_queries(dry_run: bool = False) -> None:
    """
    Executes the two queries defined in sql.py.
    :param dry_run: if True queries are validated but
    nothing is fetched
    """
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

    print('Running first query:',
          'fetching and saving filtered user ids in table {}.{}...'
          .format(DATASET, FILTERED_USER_IDS_TABLE))

    submit_query_and_wait(
        client,
        label='save_filtered_user_ids_query',
        query=SAVE_FILTERED_USER_ID_QUERY.format(PROJECT, DATASET,
                                                 FILTERED_USER_IDS_TABLE),
        timeout=QUERY_TIMEOUT,
        params=(bigquery.ScalarQueryParameter('tags_regexp', 'STRING',
                                              'java|python'),
                bigquery.ScalarQueryParameter('year', 'STRING', 2016),
                bigquery.ScalarQueryParameter('reputation', 'INT64', 400000)),
        dry_run=dry_run)

    print('Fetched and saved filtered user ids.')

    print('Running second query:',
          'fetching and saving favorite question shares in table {}.{}...'
          .format(DATASET, FAVORITE_SHARES_IN_TIERS_TABLE))

    # we only wait to show a message to the user
    submit_query_and_wait(
        client,
        label='save_favorite_shares_in_tiers_query',
        query=SAVE_FAVORITE_SHARES_IN_TIERS.format(
            PROJECT, DATASET, FAVORITE_SHARES_IN_TIERS_TABLE,
            FILTERED_USER_IDS_TABLE),
        timeout=QUERY_TIMEOUT,
        dry_run=dry_run)

    print('Fetched and saved favorite question shares in tiers.')
    print('Done.')


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise 'Python 3 required'

    args = parse_args()
    execute_queries(args.dry_run)
