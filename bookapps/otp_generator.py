import random
from redis_connection import redis_client


def generate_otp(length=6):
    otp = ""
    for _ in range(length):
        otp += str(random.randint(1, 7))
    return otp


def verify_otp(phone_number, otp):
    stored_otp = redis_client.get(phone_number)

    if stored_otp:
        stored_otp = stored_otp.decode('utf-8')

        if otp == stored_otp:
            redis_client.delete(phone_number)
            return True

    return False
