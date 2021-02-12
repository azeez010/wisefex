from models import User, db, app
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        model = User
        fields = ("id","username", "email", "is_admin", "phone", "is_paid")

user_schema = UserSchema(many=True)