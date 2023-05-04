from flask import Flask, request, jsonify
import json
import os
import requests
from itertools import groupby
import tmdbsimple as tmdb
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from collections import OrderedDict

# Initiating Flask App
app = Flask(__name__)
db = SQLAlchemy()
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@postgres_container:5432/entertainment"
db.init_app(app)

api_key = os.environ.get("TMDB_API_KEY")


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


def remove_duplicates(dict_list, key):
    dict_list = sorted(dict_list, key=lambda x: x[key])
    return [next(v) for k, v in groupby(dict_list, key=lambda x: x[key])]


genres = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}


def get_people(item_id, type):
    # construct the URL for the credits endpoint
    url = f"https://api.themoviedb.org/3/{type}/{item_id}/credits?api_key={api_key}"
    # send a GET request to the endpoint
    response = requests.get(url)
    # parse the response as JSON
    credits = response.json()
    casts_list = []
    for i in range(len(credits["cast"])):
        actor = {}
        actor["name"] = credits["cast"][i]["name"]
        actor["popularity"] = credits["cast"][i]["popularity"]
        casts_list.append(actor)
    sorted_response = sorted(casts_list, key=lambda x: (x["popularity"]), reverse=True)
    if len(sorted_response) >= 4:
        return sorted_response[:4]
    return sorted_response


def get_trailer(item_id, type):
    url = f"https://api.themoviedb.org/3/{type}/{item_id}/videos?api_key={api_key}&language=en-US"
    # Send request to TMDB API
    response = requests.get(url)
    # Parse JSON response and extract trailer data
    data = response.json()["results"]

    trailer_url = None
    for trailer in data:
        if trailer["type"] == "Trailer":
            key_value = trailer["key"]
            trailer_url = f"https://www.youtube.com/watch?v={key_value}"
            break
    return trailer_url


def get_movies(query):
    final_result = []
    tmdb.API_KEY = api_key
    tmdb.REQUESTS_SESSION = requests.Session()
    search = tmdb.Search()
    response = search.movie(query=query)
    movie_response = response["results"]
    for i in range(len(movie_response)):
        result = {}
        result["uid"] = movie_response[i]["id"]
        result["Title"] = movie_response[i]["title"]
        result["Release_date"] = movie_response[i]["release_date"]
        result["Popularity"] = movie_response[i]["popularity"]
        result["adult"] = movie_response[i]["adult"]
        result["Overview"] = movie_response[i]["overview"]
        trailer = get_trailer(movie_response[i]["id"], "movie")
        result["Trailer"] = trailer if trailer is not None else "No Trailer Available"
        result["Genres"] = []
        result["Entertainment_type"] = "movie"
        result["Casts"] = get_people(movie_response[i]["id"], "movie")
        for k in movie_response[i]["genre_ids"]:
            if k in genres:
                result["Genres"].append(genres[k])
            else:
                result["Genres"].append("Others")
        new_result = entertainment(
            item_id=str(result["uid"]).lower(),
            title=result["Title"],
            release_date=result["Release_date"],
            popularity=result["Popularity"],
            adult=result["adult"],
            overview=result["Overview"],
            trailer=result["Trailer"],
            casts=str(result["Casts"]),
            genre=str(result["Genres"]),
            data_type=result["Entertainment_type"],
            date_entry=str(date.today()),
        )
        db.session.add(new_result)
        try:
            db.session.commit()
        except:
            pass
        final_result.append(result)
    return final_result


def get_tv(query_check):
    tmdb.API_KEY = api_key
    tmdb.REQUESTS_SESSION = requests.Session()
    search = tmdb.Search()
    tv_response = search.tv(query=query_check)
    tv_response = tv_response["results"]
    final_result = []
    for i in range(len(tv_response)):
        result = {}
        result["uid"] = tv_response[i]["id"]
        result["Title"] = tv_response[i]["name"]
        result["Release_date"] = tv_response[i]["first_air_date"]
        result["Popularity"] = tv_response[i]["popularity"]
        result["adult"] = tv_response[i]["adult"]
        result["Overview"] = tv_response[i]["overview"]
        trailer = get_trailer(tv_response[i]["id"], "tv")
        result["Trailer"] = trailer if trailer is not None else "No Trailer Available"
        result["Entertainment_type"] = "tv"
        result["Casts"] = get_people(tv_response[i]["id"], "tv")
        result["Genres"] = []
        for k in tv_response[i]["genre_ids"]:
            if k in genres:
                result["Genres"].append(genres[k])
            else:
                result["Genres"].append("Others")
        new_result = entertainment(
            item_id=str(result["uid"]).lower(),
            title=result["Title"],
            release_date=result["Release_date"],
            popularity=result["Popularity"],
            adult=result["adult"],
            overview=result["Overview"],
            trailer=result["Trailer"],
            casts=str(result["Casts"]),
            genre=str(result["Genres"]),
            data_type=result["Entertainment_type"],
            date_entry=str(date.today()),
        )
        db.session.add(new_result)
        try:
            db.session.commit()
        except:
            pass
        final_result.append(result)
    return final_result


@app.route("/get_trending", methods=["GET", "POST"])
def get_trending_entertainment():
    data = request.get_json()
    media_type = data.get("entertainment_type")
    time_window = data.get("time_window")
    if media_type is None and time_window is not None:
        response = {"Message": "Media type is invalid"}
        response_code = 400
        return json.dumps(response), response_code
    elif media_type is not None and time_window is None:
        response = {"Message": "Time window is invalid"}
        response_code = 400
        return json.dumps(response), response_code
    else:
        if media_type.lower() not in [
            "all",
            "movie",
            "tv",
            "people",
        ] or time_window.lower() not in ["day", "week"]:
            response = {"Message": "Media or time slot is invalid"}
            response_code = 400
            return json.dumps(response), response_code
        else:
            try:
                media_type = media_type.lower()
                time_window = time_window.lower()
                url = f"https://api.themoviedb.org/3/trending/{media_type}/{time_window}?api_key={api_key}"
                # Send request to TMDB API
                response = json.loads(requests.get(url).text)
                response = response["results"]

                # Parse JSON response and extract trailer data
                if len(response) >= 10:
                    response = response[:10]
                final_result = []
                for i in range(len(response)):
                    result = {}
                    result["uid"] = response[i]["id"]
                    if response[i]["media_type"] == "movie":
                        result["Title"] = response[i]["title"]
                    elif response[i]["media_type"] == "tv":
                        result["Title"] = response[i]["name"]
                    if response[i]["media_type"] == "movie":
                        result["Release_date"] = response[i]["release_date"]
                    elif response[i]["media_type"] == "tv":
                        result["Release_date"] = response[i]["first_air_date"]
                    result["Popularity"] = response[i]["popularity"]
                    result["adult"] = response[i]["adult"]
                    result["Overview"] = response[i]["overview"]
                    if response[i]["media_type"] == "movie":
                        trailer = get_trailer(response[i]["id"], "movie")
                    elif response[i]["media_type"] == "tv":
                        trailer = get_trailer(response[i]["id"], "tv")
                    result["Trailer"] = (
                        trailer if trailer is not None else "No Trailer Available"
                    )
                    if response[i]["media_type"] == "movie":
                        result["Casts"] = get_people(response[i]["id"], "movie")
                    elif response[i]["media_type"] == "tv":
                        result["Casts"] = get_people(response[i]["id"], "tv")
                    result["Genres"] = []
                    for k in response[i]["genre_ids"]:
                        if k in genres:
                            result["Genres"].append(genres[k])
                        else:
                            result["Genres"].append("Others")
                    new_result = entertainment(
                        item_id=str(result["uid"]).lower(),
                        title=result["Title"],
                        release_date=result["Release_date"],
                        popularity=result["Popularity"],
                        adult=result["adult"],
                        overview=result["Overview"],
                        trailer=result["Trailer"],
                        casts=str(result["Casts"]),
                        genre=str(result["Genres"]),
                        data_type=response[i]["media_type"],
                        date_entry=str(date.today()),
                    )
                    final_result.append(result)
                    db.session.add(new_result)
                    try:
                        db.session.commit()
                    except:
                        print("Failed to add to Database")
                response = remove_duplicates(final_result, "uid")
                return json.dumps(response), 200
            except Exception as e:
                return str(e), 400


@app.route("/get_keywords", methods=["GET"])
def details_from_tmdb():
    try:
        if request.headers.get("Content-Type") == "application/json":
            data = request.get_json()
            query = data.get("entertainment")
            entertainment_type = data.get("entertainment_type")
        if query is None:
            response = {
                "Message": "Endpoint requires some valid TV/Movie name in input"
            }
            response_code = 400
        else:
            query = query.lower()
            if entertainment_type is None:
                movies = get_movies(query)
                tvs = get_tv(query)
                if tvs is None:
                    final_result = movies
                elif tvs is None:
                    final_result = tvs
                else:
                    final_result = tvs + movies
            elif entertainment_type.lower().strip() == "tv":
                final_result = get_tv(query)
            elif entertainment_type.lower().strip() == "movie":
                final_result = get_movies(query)
            else:
                response = {"Message": "Entertainment Type is invalid"}
                response_code = 400
                return json.dumps(response), response_code
            if len(final_result) == 0:
                response = {"Message": "No such TV/Movie found"}
                response_code = 400
                return json.dumps(response), response_code
            response = remove_duplicates(final_result, "uid")
            sorted_response = sorted(
                response,
                key=lambda x: (x["Release_date"], x["Popularity"]),
                reverse=True,
            )
            response = sorted_response[:10]
            response_code = 200
        return json.dumps(response), response_code
    except Exception as e:
        return str(e), 400


@app.route("/get_details", methods=["GET", "POST"])
def get_details():
    data = request.get_json()
    data = data.get("results")
    final_result = OrderedDict()
    try:
        for item in data:
            title = item["movie_name"]
            release_year = item["year"]
            media_type = item["media_type"].lower()
            try:
                stmt = text(
                    "SELECT item_id, title, release_date, cast(popularity as VARCHAR), adult, overview, trailer, casts, genre, data_type, date_entry FROM entertainment WHERE title = :x and CAST(EXTRACT(YEAR FROM CAST(release_date as DATE)) AS VARCHAR) = :y;"
                )
                stmt = stmt.bindparams(x=title, y=str(release_year))
                data = db.session.execute(stmt).all()
            except:
                print("Didn't read db")
            if data:
                result = OrderedDict(
                    [
                        ("uid", data[0][0]),
                        ("Title", data[0][1]),
                        ("Release_date", data[0][2]),
                        ("Popularity", data[0][3]),
                        ("adult", data[0][4]),
                        ("Overview", data[0][5]),
                        ("Trailer", data[0][6]),
                        ("Cast", data[0][7]),
                        ("Genre", data[0][8]),
                        ("data_type", data[0][9]),
                    ]
                )
            else:
                url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={api_key}&query={title}&year={release_year}"
                try:
                    response = json.loads(requests.get(url).text)
                    response = response["results"]
                    # Parse JSON response and extract trailer data
                    for i in range(len(response)):
                        if media_type == "movie":
                            res_title = response[i]["title"]
                            res_date = response[i]["release_date"]
                            trailer = get_trailer(response[i]["id"], "movie")
                            res_cast = get_people(response[i]["id"], "movie")
                        elif media_type == "tv":
                            res_title = response[i]["name"]
                            res_date = response[i]["first_air_date"]
                            trailer = get_trailer(response[i]["id"], "tv")
                            res_cast = get_people(response[i]["id"], "tv")
                        res_popularity = response[i]["popularity"]
                        res_adult = response[i]["adult"]
                        res_overview = response[i]["overview"]
                        res_trailer = (
                            trailer if trailer is not None else "No Trailer Available"
                        )
                        res_genre = []
                        for k in response[i]["genre_ids"]:
                            if k in genres:
                                res_genre.append(genres[k])
                            else:
                                res_genre.append("Others")
                        result = OrderedDict(
                            [
                                ("uid", response[i]["id"]),
                                ("Title", res_title),
                                ("Release_date", res_date),
                                ("Popularity", res_popularity),
                                ("adult", res_adult),
                                ("Overview", res_overview),
                                ("Trailer", res_trailer),
                                ("Cast", res_cast),
                                ("Genre", res_genre),
                                ("Entertainment_type", media_type),
                            ]
                        )
                        break
                    new_result = entertainment(
                        item_id=str(result["uid"]).lower(),
                        title=result["Title"],
                        release_date=result["Release_date"],
                        popularity=result["Popularity"],
                        adult=result["adult"],
                        overview=result["Overview"],
                        trailer=result["Trailer"],
                        casts=str(result["Casts"]),
                        genre=str(result["Genres"]),
                        data_type=result["Entertainment_type"],
                        date_entry=str(date.today()),
                    )
                    db.session.add(new_result)
                    try:
                        db.session.commit()
                    except:
                        print("Failed to save into database")
                except:
                    print("Failed to parse JSON response for the movie")
            try:
                final_result[f"{title}"] = result
            except:
                response = {"Message": "No such TV/Movie found"}
                response_code = 400
                return json.dumps(response), response_code
        return json.dumps(final_result, indent=4), 200
    except Exception as e:
        return str(e), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051, debug=True)
