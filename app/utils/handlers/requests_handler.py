from http import HTTPStatus

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result, RetryCallState


def _return_last_value(retry_state: RetryCallState):
    return retry_state.outcome.result()


def _status_check(response_object: requests.Response) -> bool:
    return (
            response_object.status_code >= HTTPStatus.MULTIPLE_CHOICES
            and response_object.status_code != HTTPStatus.NOT_FOUND
    )


@retry(retry=(retry_if_result(_status_check)), stop=stop_after_attempt(3),
       retry_error_callback=_return_last_value,
       wait=wait_exponential(multiplier=1, min=4, max=10))
def get_with_retry(*args, **kwargs) -> requests.Response:
    """
    GET request.
    Trying to execute GET request. In case of any errors, re-trying 3 times, after it, returns result.
    :param args: any GET request's args
    :param kwargs: any GET request's kwargs

    :return: HTTP response
    """
    return requests.get(*args, **kwargs)
