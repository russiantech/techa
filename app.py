from os import getenv
from web import create_app

# app = create_app()
# app = create_app('development')  # Set to 'production' if needed
app = create_app('production')  # Set to 'production' if needed

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(getenv("PORT", 5000)))
