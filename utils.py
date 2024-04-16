import time


def calculate_time_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"PARSER IS WORKING! Please wait...")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"CHECKING TIME ==>> Process finished in: {end_time - start_time} seconds")
        return result
    return wrapper


def async_calculate_time_decorator(func):
    async def wrapper(*args, **kwargs):
        print(f"PARSER IS WORKING! Please wait...")
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"CHECKING TIME ==>> Process finished in: {end_time - start_time} seconds")
        return result
    return wrapper