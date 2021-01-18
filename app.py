import json

from flask import Flask
from flask_restful import Api

from flask_jwt import JWT

from resources.image_resources import ImageResources
from resources.user_authentication import authenticate, identity

app = Flask(__name__)
app.secret_key = 'DyNotifyAuth'
api = Api(app)

jwt = JWT(app, authenticate, identity)

api.add_resource(ImageResources, '/images-similarity', endpoint='images-similarity')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
