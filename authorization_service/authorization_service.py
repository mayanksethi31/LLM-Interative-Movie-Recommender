import os
from flask import Flask, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import requests
import jwt
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import text

# Initiating Flask App
app = Flask(__name__)
db = SQLAlchemy()
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@postgres_container:5432/entertainment"
db.init_app(app)

# Set a secret key for JWT token encryption
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# Create a database object
class employees(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name_person = db.Column(db.String(100), nullable=False)
    password_store = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "email": self.email,
            "name_person": self.name_person,
            "password_store": self.password_store,
        }


# Step 3: Registering and logging in users
# Create a route for registering new users
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    # Get user data from request body
    try:
        name_person = data["name"]
        email = data["email"]
        password_store = str(data["password"])
    except:
        return jsonify({"message": "Missing required fields"}), 400
    # Check if user already exists
    user = employees.query.filter_by(email=email).first()
    if user:
        return (
            jsonify(
                {"message": "User already exists. You may login with the password"}
            ),
            400,
        )

    # Insert new user into database
    person = employees(
        name_person=name_person,
        email=email,
        password_store=generate_password_hash(password_store),
    )
    db.session.add(person)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


# Create a route for logging in
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # Get user data from request body
    try:
        email = data["email"]
        password = str(data["password"])
    except:
        return jsonify({"message": "Missing required fields"}), 400
    # Check if user exists in database
    try:
        stmt = text(
            "SELECT name_person, email, password_store FROM employees WHERE email=:x;"
        )
        stmt = stmt.bindparams(x=email)
        data = db.session.execute(stmt).all()
    except:
        return jsonify({"message": "User not registered. Cannot login"}), 400
    try:
        retrieved_password = data[0][2]
    except:
        return jsonify({"message": "User not registered. Cannot login"}), 400
    # Check if password is correct
    if check_password_hash(retrieved_password, password):
        # Create JWT token
        token = jwt.encode(
            {
                "user_id": (str(data[0][1])),
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(hours=2),  # Setting expiry for token to 2 hours
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"token": token}), 200
    return make_response(
        "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


# Step 4: Securing routes and services with JWT token authentication
# Create a decorator function for verifying the JWT token - This will be the auth middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            token = str.replace(str(token), "Bearer ", "")
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            stmt = text("SELECT name_person, email FROM employees WHERE email=:x;")
            print(data["user_id"])
            stmt = stmt.bindparams(x=data["user_id"])
            data = db.session.execute(stmt).all()
            current_user = data[0][1]
        except:
            return jsonify({"message": "Unauthorized"}), 400
        return f(current_user, *args, **kwargs)

    return decorated


# Create a route for logging in
@app.route("/protected", methods=["GET", "POST"])
@token_required
def protected(current_user):
    return jsonify({"Mail Account": current_user, "message": "Verified"})


# Step 5: Running the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
