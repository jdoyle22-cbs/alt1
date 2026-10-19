from flask import request, session
from flask_caching import Cache
from flask_compress import Compress
from flask_socketio import SocketIO

socketio = SocketIO()

cache = Cache()
def make_user_cache_key() -> str:
    user_id = session.get('user_id', 'guest')
    return f"{request.path}:{user_id}"

compress = Compress()
compress.cache = cache
compress.cache_key = make_user_cache_key