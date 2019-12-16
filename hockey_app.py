# Nice documentation:
# http://exploreflask.com/en/latest/configuration.html  -  what I am reading to get the configs right.
# https://babeljs.io/docs/en has a better list of babel packages than in the page above.
# A very simple Flask Hello World app for you to get started with...
# http://www.valentinog.com/blog/babel -- this got me through babel setup
from flask import Flask, render_template, url_for, jsonify, Blueprint
from admin import admin as admin_bp
from clientapp import clientapp as clientapp


#app = Flask(__name__,
#        static_folder="./public",
#        template_folder ="./static") # are blueprints relative to "template folder"?

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

# this is really cool as it explains what gets loaded
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.register_blueprint(admin_bp)
app.register_blueprint(clientapp)

@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return render_template("all_links.html", links=links)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


# this generally goes into the __init__.py or views.py of the blueprint directory
# admin = Blueprint('admin', __name__,
#                     template_folder='templates',
#                     static_folder='static')

# clientapp = Blueprint('clientapp', __name__,
#                     template_folder='templates',
#                     template_url_path='/clientapp/static',
#                     static_folder='static')

# app.register_blueprint(admin)
# app.register_blueprint(clientapp)

# #@admin_bp.route('/admin')
# @app.route('/adminmain')
# def adminmain():
#     return render_template('index.html')
# @admin_bp.route('/admin')
# def admin():
#     return render_template('index.html')
# @clientapp.route('/clientapp')
# def clientapp():
#     return render_template('index.html')

# import the one view that I have currently created
#from static.hockeyhome import hockey_blueprint
#pp.register_blueprint(hockey_blueprint)

# app = Flask(__name__)
# # allows viewing messages
# app.debug = True


# # allows loading configurations from the config file defined on the same level as the app itself. This config will be in the repository
# app.config.from_object('config')


# tasks = [
#     {
#         'id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
#         'done': False
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web',
#         'done': False
#     }
# ]
# @app.route('/config')
# def print_config():
#     # Flask looks for Jinja2 templates in the templates directory
#     result = ""
#     for k,v in app.config.items():
#         result += "{}--{}<br>".format(k,v)
#     return result

# @app.route('/')
# def hello_world():
#     # Flask looks for Jinja2 templates in the templates directory
#     return render_template('hello.html')

# @app.route('/test_endpoint', methods=['GET'])
# def get_tasks():
#     return jsonify({'tasks': tasks})
