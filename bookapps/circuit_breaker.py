import random
from redis_connection import redis_client
from sms_service import send_otp_with_signal, send_otp_with_kavenegar


def is_provider_blocked(provider):
    provider_key = f"{provider}_circuit_state"
    return redis_client.get(provider_key) == b'blocked'


def block_provider(provider):
    provider_key = f"{provider}_circuit_state"
    redis_client.setex(provider_key, 1800, 'blocked')


def unblock_provider(provider):
    provider_key = f"{provider}_circuit_state"
    redis_client.delete(provider_key)


def send_otp_with_circuit_breaker(phone_number, otp):
    provider = random.choice(['kavenegar', 'signal'])

    consecutive_failures = 0

    while consecutive_failures < 3:
        if is_provider_blocked(provider):
            provider = 'signal' if provider == 'kavenegar' else 'kavenegar'
            continue

        try:
            if provider == 'kavenegar':
                send_otp_with_kavenegar(phone_number, otp)
            elif provider == 'signal':
                send_otp_with_signal(phone_number, otp)
            return True
        except Exception as e:
            print(f"Failed to send OTP via {provider}: {str(e)}")
            consecutive_failures += 1
            redis_client.incr(f"{provider}_circuit_failures")

        if consecutive_failures >= 3:
            # If three consecutive failures occurred, block the provider for 30 minutes
            block_provider(provider)
            return False

    # If the loop exits, it means the provider is blocked, so switch to the other one
    unblock_provider(provider)
    return False