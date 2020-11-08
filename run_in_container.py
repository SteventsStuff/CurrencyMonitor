import os
import time

from .main import main


if __name__ == '__main__':
    is_container_run = int(os.environ.get('IS_CONTAINER_RUN'))
    if is_container_run:
        run_rate_sec = int(os.environ.get('RUN_RATE'))
        while True:
            main()
            time.sleep(run_rate_sec)
