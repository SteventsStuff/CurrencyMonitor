import os
import time
import datetime

from main import main


if __name__ == '__main__':
    is_container_run = int(os.environ.get('IS_CONTAINER_RUN'))
    print('is_container_run', is_container_run)
    if is_container_run:
        run_rate_sec = int(os.environ.get('RUN_RATE'))
        print('run_rate_sec', run_rate_sec)
        while True:
            print(f'Running script...\nTime: {datetime.datetime.utcnow()}')
            main()
            time.sleep(run_rate_sec)
