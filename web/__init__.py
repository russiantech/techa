from flask import Flask
from web.extensions import config_app, init_ext, make_available

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=False)

    try:
        # Configure the app
        config_app(app, config_name)
        init_ext(app)
        app.context_processor(make_available) # make some-data available in the context through-out
        
        # Register Blueprints
        from web.main.routes import main
        from web.apis.errors.handlers import errors
        from web.showcase.routes import showcase_bp
        from web.apis.plans import plan_bp
        from web.apis.pays import pay
        from web.apis.user import user_bp
        
        # from web.apis.auth.routes import auth
        # app.register_blueprint(auth)
        
        app.register_blueprint(main)
        app.register_blueprint(errors)
        app.register_blueprint(showcase_bp)
        app.register_blueprint(plan_bp, url_prefix='/api')
        app.register_blueprint(pay, url_prefix='/api')
        app.register_blueprint(user_bp, url_prefix='/api')

        return app
    
    except Exception as e:
        print(f"Error initializing app: {e}")
        raise
