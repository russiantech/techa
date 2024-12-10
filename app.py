from web import create_app
# from dotenv import load_dotenv
# load_dotenv() # Load env variables from .env file

# app = create_app()
# app = create_app('testing')  # Set to 'development' if needed
# app = create_app('development')  # Set to 'production' if needed
app = create_app('production')  # Set to 'production'
from flask import jsonify
@app.route("/routes")
def site_map():
    links = []
    # for rule in app.url_map.iter_rules():
    for rule in app.url_map._rules:
        """ Filter out rules we can't navigate to in a browser, and rules that require parameters """
        links.append({'url': rule.rule, 'view': rule.endpoint})
    return jsonify(links), 200

if __name__ == '__main__':
    #app.run() 
    app.run(debug=True, port=8001)

