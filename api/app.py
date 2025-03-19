from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse
from datetime import datetime
import os

app = Flask(__name__)
api = Api(app)

data_store = {
    "bike_status": None,
    "last_updated": None
}


class BikeData(Resource):
    def get(self):
        if data_store["bike_status"] is None:
            return {"error": "No bike data available."}, 404

        # Return the latest bike status
        response = {
            "bike_status": data_store["bike_status"],
            "last_updated": data_store["last_updated"]
        }
        return response, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sentry_mode', required=True, type=str, help='Sentry mode is required')
        parser.add_argument('latitude', required=True, type=float, help='Latitude is required')
        parser.add_argument('longitude', required=True, type=float, help='Longitude is required')
        args = parser.parse_args()

        # Update the data store with the new data
        data_store["bike_status"] = {
            "sentry_mode": args['sentry_mode'],
            "latitude": args['latitude'],
            "longitude": args['longitude']
        }
        data_store["last_updated"] = datetime.now().isoformat()

        return {"message": "Bike data updated successfully."}, 200


api.add_resource(BikeData, '/api/bike')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
