from flask import Flask
from playhouse.flask_utils import FlaskDB
import settings

app = Flask(__name__)
app.config.from_object(settings)

flask_db = FlaskDB(app)
database = flask_db.database
