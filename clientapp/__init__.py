from flask import Blueprint
# so, if we define an endpoint in the "routes", the page will be /clientapp/ENDPOINT
clientapp = Blueprint('clientapp', __name__,template_folder='templates_dir',
                      url_prefix="/stats")
from . import routes
