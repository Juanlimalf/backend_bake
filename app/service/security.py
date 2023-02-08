import jwt
from datetime import datetime, timedelta
from decouple import config


JWT_SECRET = config('secret')
JWT_ALGORITHM = config('alghorithm')


def encode_jwt():
    payload = {
        "date": str(datetime.now()+timedelta(hours=1))
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt(token: str):

    try:
        decode_token = datetime.strptime(jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)['date'],
                                         "%Y-%m-%d %H:%M:%S.%f")

        if decode_token > datetime.now():
            return True
        else:
            return False
    except:
        return False