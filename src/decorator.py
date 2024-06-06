from json import JSONEncoder, dumps, loads
from functools import reduce
from datetime import datetime
from loki_logger import get_logger

import os

LOGGER = get_logger("price_scrapper")
EXTRA_TAGS = {"tags": {"process": "cache"}}


def cache_to_file(filename):
    class DateTimeEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)

    def decorator(func):
        def wrapper(*args, **kwargs):
            parsed_filename = reduce(
                lambda acc, args: acc.replace(f"[{args[0]}]", str(args[1])),
                kwargs.items(),
                filename,
            )

            for os.path.sep in filename:
                os.makedirs(os.path.dirname(parsed_filename), exist_ok=True)

            if os.path.exists(parsed_filename):
                LOGGER.info(
                    f"Fetched {parsed_filename} from cache",
                    extra=EXTRA_TAGS,
                )
                with open(parsed_filename, "r") as file:
                    cache_data = file.read()
                    return loads(cache_data)

            data = func(*args, **kwargs)

            LOGGER.info(
                f"Cached {parsed_filename} from internet",
                extra=EXTRA_TAGS,
            )
            with open(parsed_filename, "w") as file:
                file.write(dumps(data, cls=DateTimeEncoder))
                return data

        return wrapper

    return decorator
