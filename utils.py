import asyncio
from functools import wraps


def async_retry(tries=6, delay=1, backoff=2, logger=None):

    def deco_retry(f):
        @wraps(f)
        async def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    msg = f'[Error] {f.__name__} raises {e}, Retrying in {mdelay} seconds...'
                    if logger:
                        logger.debug(msg)
                    else:
                        print(msg)
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await f(*args, **kwargs)
        return f_retry

    return deco_retry
