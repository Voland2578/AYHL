from flask import Blueprint
# so, if we define an endpoint in the "routes", the page will be /clientapp/ENDPOINT
clientapp = Blueprint('clientapp',
                      __name__,
                      static_folder='/home/yfurman/hockey_stats/static/public/clientapp',
                      template_folder='templates_dir',
                      url_prefix="/stats",
                      static_url_path="/clientapp/static"
                      )
from . import routes
