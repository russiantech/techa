from flask_migrate import Migrate
from flask_mail import Mail
from flask_moment import Moment
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from flask_wtf.csrf import CSRFProtect
from web.models import db, bcrypt, s_manager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
from os import getenv

# Initialize extensions
f_session = Session()
mail = Mail()
migrate = Migrate()
moment = Moment()
oauth = OAuth()
csrf = CSRFProtect()

def config_app(app, config_name):
    """Configure app settings based on environment."""
    from web.config import app_config
    app.config.from_object(app_config[config_name])

def init_ext(app):
    """Initialize all extensions."""
    db.init_app(app)
    f_session.init_app(app)
    bcrypt.init_app(app)
    s_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    oauth.init_app(app)
    csrf.init_app(app)

def make_available():
    """Provide application metadata."""
    products_links = {
        'salesnet_link': 'salenset.techa.tech',
        'barman_link': 'barman.techa.tech',
        'paysafe_link': 'paysafe.techa.tech',
        'intellect_link': 'intellect.techa.tech',
        'workforce_link': 'workforce.techa.tech'
    }
    app_data = {
        'app_name': 'Techa',
        'hype': 'Your Digital Learning Companion.',
        'app_desc': 'Elite software engr team with special interest in artificial intelligence, data and hacking..',
        'app_desc_long': 'Elite software engr team with special interest in artificial intelligence, data and hacking..\n\
            Techa m-powers people & powers businesses to stay relevant with technologies and advancements.',
        'app_location': 'Graceland Estate, Lekki, Lagos, Nigeria.',
        'app_email': 'hi@techa.tech',
        'app_logo': getenv('LOGO_URL'),
        'site_logo': getenv('LOGO_URL'),
        'site_link': 'https://www.techa.tech',
        'whatsapp_link': 'https://www.techa.tech',
        'terms_link': 'https://www.techa.tech/terms',
        'policy_link': 'https://www.techa.tech/policy',
        'cookie_link': 'https://www.techa.tech/cookie',
        'github_link': 'https://github.com/russiantech',
        'fb_link': 'https://www.facebook.com/RussianTechs',
        'x_link': 'https://twitter.com/chris_jsmes',
        'instagram_link': 'https://www.instagram.com/chrisjsmz/',
        'linkedin_link': 'https://www.linkedin.com/in/chrisjsm',
        'youtube_link': 'https://www.youtube.com/@russian_developer',
    }

    # Combine app_data and products_links
    datas = {**app_data, **products_links}
    return datas
