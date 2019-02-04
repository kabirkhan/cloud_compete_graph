import hug
from src.app import api

hug_api = hug.API(__name__)
hug_api.http.add_middleware(hug.middleware.CORSMiddleware(hug_api, max_age=10))


@hug.extend_api()
def apis():
    return [api]
