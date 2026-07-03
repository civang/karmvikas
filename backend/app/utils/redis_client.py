import redis


class RedisClient:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        self.client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)


redis_client = RedisClient()
