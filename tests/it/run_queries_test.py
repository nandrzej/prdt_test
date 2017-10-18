import subprocess
import sys

if sys.version_info[0] < 3:
    raise 'Python 3 required'


def test_fetching_and_saving_data():
    try:
        subprocess.check_call(
            'python src/run_queries.py --dry_run True', shell=True)
    except subprocess.CalledProcessError as e:
        assert False, str(e)
