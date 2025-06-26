
from waitress import serve
import ginstech.wsgi


if __name__ == "__main__":
    serve(ginstech.wsgi.application, host='127.0.0.1', port=8000)