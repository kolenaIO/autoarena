import argparse
from argparse import Namespace


def get_command_line_args() -> Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("battles_parquet", nargs="?", help="Path to parquet file containing battles to seed project")
    ap.add_argument("-d", "--dev", action="store_true", help="Run in development mode")
    return ap.parse_args()
