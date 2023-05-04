from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import json

# Initiating Flask App
app = Flask(__name__)
db = SQLAlchemy()
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@postgres_container:5432/entertainment"
db.init_app(app)


class entertainment(db.Model):
    item_id = db.Column(db.String(200), primary_key=True)
    title = db.Column(db.String(2000), nullable=False)
    release_date = db.Column(db.String(20))
    popularity = db.Column(db.Numeric(precision=10, scale=2))
    adult = db.Column(db.Boolean)
    overview = db.Column(db.Text)
    trailer = db.Column(db.String(2000))
    casts = db.Column(db.Text)
    genre = db.Column(db.String(2000))
    data_type = db.Column(db.String(10))
    date_entry = db.Column(db.String(20))

    def to_dict(self):
        return {
            "item_id": self.command,
            "title": self.server_url,
            "release_date": self.release_date,
            "popularity": self.popularity,
            "adult": self.adult,
            "overview": self.overview,
            "trailer": self.trailer,
            "casts": self.casts,
            "genre": self.genre,
            "data_type": self.data_type,
            "date_entry": self.date_entry,
        }


@app.route("/check_data", methods=["GET", "POST"])
def see_data():
    try:
        stmt = text(
            "SELECT item_id, title, release_date, cast(popularity as VARCHAR), adult, overview, trailer, casts, genre, data_type, date_entry FROM entertainment;"
        )
        stmt = stmt.bindparams()
        response = db.session.execute(stmt).all()
        if len(response) == 0:
            response = {"Message": "No data found"}
            return json.dumps(response), 400
        else:
            full_result = []
            for row in response:
                result = {}
                result["item_id"] = row[0]
                result["title"] = row[1]
                result["release_date"] = row[2]
                result["popularity"] = row[3]
                result["adult"] = row[4]
                result["overview"] = row[5]
                result["trailer"] = row[6]
                result["casts"] = row[7]
                result["genre"] = row[8]
                result["data_type"] = row[9]
                result["date_entry"] = row[10]
                full_result.append(result)
            # Convert the list of dictionaries to JSON format
            return json.dumps(full_result), 200
    except:
        response = {"Message": "Data not added properly"}
        return json.dumps(response), 400


@app.route("/filter_data", methods=["GET", "POST"])
def filter_data():
    data = request.get_json()
    title = data["title"]
    data_type = data["data_type"]
    genre = data["genre"]

    try:
        stmt = text(
            """
                    SELECT item_id, title, release_date, cast(popularity as VARCHAR), adult, overview, trailer, casts, genre, data_type, date_entry 
                    FROM entertainment
                    WHERE title = :a AND CAST(genre as VARCHAR) like :b
                    AND data_type like :c
                    """
        )
        stmt = stmt.bindparams(a=title, b=str(genre), c=data_type)
        response = db.session.execute(stmt).all()
        if len(response) == 0:
            response = {"Message": "No data found. Try changing Filters."}
            return json.dumps(response), 400
        else:
            full_result = []
            for row in response:
                result = {}
                result["item_id"] = row[0]
                result["title"] = row[1]
                result["release_date"] = row[2]
                result["popularity"] = row[3]
                result["adult"] = row[4]
                result["overview"] = row[5]
                result["trailer"] = row[6]
                result["casts"] = row[7]
                result["genre"] = row[8]
                result["data_type"] = row[9]
                result["date_entry"] = row[10]
                full_result.append(result)
            # Convert the list of dictionaries to JSON format
            return json.dumps(full_result), 200
    except:
        response = {"Message": "Filters not added properly"}
        response_code = 400
        return json.dumps(response), response_code


# Step 5: Running the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=True)
