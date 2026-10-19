from waitress import serve
from social_site import create_app

if __name__ == '__main__':
    app = create_app()

    print("Starting production Waitress server on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000, threads=50)