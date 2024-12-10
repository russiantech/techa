
class SequentialGenerator:
    def __init__(self, start=1):
        self.counter = start

    def next(self):
        current_value = self.counter
        self.counter += 1
        return current_value

# Create an instance of the SequentialGenerator
generator = SequentialGenerator(start=10)
# version=generator.next()

# Utility functions for responses
from flask import jsonify
def success_response(message, data=None, status_code=200):
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data.to_dict() if hasattr(data, 'to_dict') else data
    return jsonify(response), status_code

def error_response(message,status_code=400):
    """
    Helper function to generate an error response.
    """
    return jsonify({'success': False, 'error': message})

# Making slug
from slugify import slugify
def slugifie(title, id=0):
    combined = f"{title}-{id}"
    return slugify(combined.lower())

import random
import string

def generate_random_id(k=8):
    """Generate a random alphanumeric ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k)).lower()

def make_slug(text):
    """Generate a slug from the given text with a random ID."""
    # Generate a random ID
    id = generate_random_id()

    # Extract the first 50 characters of the text
    text_prefix = text[:50]
    
    # Remove any non-alphanumeric characters and replace spaces with hyphens
    cleaned_text = ''.join(c if c.isalnum() else '-' for c in text_prefix.strip()).strip('-')
    
    # Combine the cleaned text and the ID to create the slug
    slug = f"{cleaned_text}-{id}"
    
    return slug.lower()

""" usage-example:
text = "This is a long text with some characters."
slug = make_slug(text)
print(slug)  # Output example: 'This-is-a-long-text-q7ZwF9Xv'
 """
 
from flask import request
def user_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip =  request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    return ip


def strtobool_custom(value):
    value = value.lower()
    if value in ('y', 'yes', 'true', 't', '1'):
        return True
    elif value in ('n', 'no', 'false', 'f', '0'):
        return False
    else:
        raise ValueError(f"Invalid boolean string: {value}")
