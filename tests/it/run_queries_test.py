import subprocess


def test_fetching_and_saving_data():
    try:
        subprocess.check_call(
            'python src/run_queries.py --dry_run True', shell=True)
    except subprocess.CalledProcessError as e:
        assert False, str(e)
