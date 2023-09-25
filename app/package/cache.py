import os
import json
import redis

redis_endpoint = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis_key = os.environ["REDIS_KEY"]

try:
    redis_conn = redis.StrictRedis(host=redis_endpoint, port=redis_port)
except Exception:
    redis_conn = None

try:
    redis_conn = redis.StrictRedis(host=redis_endpoint, port=redis_port)
except Exception:
    redis_conn = None


def dump_data(userId, data):
    try:
        redis_conn.hset(redis_key, f"user:{userId}", json.dumps(data))
        return True
    except redis.exceptions.ResponseError as e:
        print(f"Error: {e}")
        return False


def get_data(userId):
    try:
        data_json = redis_conn.hget(redis_key, f"user:{userId}")
        if data_json:
            return json.loads(data_json)
        else:
            print(f"Field 'user:{userId}' not found in the Redis Hash.")
            return None
    except redis.exceptions.ResponseError as e:
        print(f"Error: {e}")
        return None


def delete_data(userId):
    try:
        deleted_count = redis_conn.hdel(redis_key, f"user:{userId}")
        if deleted_count == 1:
            return True
        elif deleted_count == 0:
            print(f"Field 'user:{userId}' not found in the Redis Hash.")
            return False
    except redis.exceptions.ResponseError as e:
        print(f"Error: {e}")
        return False
