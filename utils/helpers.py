import time
import functools

def retry(attempts=3, delay=1, exceptions=(Exception,)):
    """
    A decorator that retries a function execution a specified number of times before giving up.

    Parameters:
    attempts (int): The maximum number of attempts before giving up. Default is 3.
    delay (int): The delay in seconds between each attempt. Default is 1 second.
    exceptions (tuple): A tuple of exception classes that should trigger a retry. Default is (Exception,).

    Returns:
    function: The decorated function with retry logic.
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            """
            Wrapper function that implements the retry logic.

            Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

            Returns:
            Any: The return value of the decorated function if successful.

            Raises:
            Exception: The last exception caught if all attempts fail.
            """
            last_exception = None
            for attempt in range(attempts):
                try:
                    print(f"Attempt {attempt + 1} of {attempts}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Caught exception: {e}")
                    last_exception = e
                    time.sleep(delay)
            print("Reached the maximum number of failed attempts")
            if last_exception:
                raise last_exception
        return wrapper_retry
    return decorator_retry