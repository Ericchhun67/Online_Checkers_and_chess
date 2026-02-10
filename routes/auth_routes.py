from flask import Blueprint, request, redirect, jsonify, session, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db_handler import db, add_record
from models.user_model import User



auth_bp = Blueprint('auth', __name__)


# Register page (GET)
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# Register route
@auth_bp.route("/register", methods=["POST"])
def register_user():
    """" Register a new user with username, email, and password. """
    data = request.get_json(silent=True) or request.form
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    def render_form_error(message, status_code=400):
        return render_template("register.html", error=message), status_code
    
    # check if user with the same email or username already exists
    if not all([username, email, password]):
        if request.is_json:
            return jsonify({"Error": "all fields are required"}), 400
        return render_form_error("All fields are required.")

    if not request.is_json and not confirm_password:
        return render_form_error("Please confirm your password.")

    if confirm_password and confirm_password != password:
        if request.is_json:
            return jsonify({"Error": "Passwords do not match"}), 400
        return render_form_error("Passwords do not match.")
        
    if User.query.filter((User.email == email) | (User.username == username)).first():
        if request.is_json:
            return jsonify({"Error": "User with Email or username already registered"}), 409
        return render_form_error("Email or username is already registered.", 409)
    
    # create and hash the password 
    hashed_password = generate_password_hash(password)
    
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    # add to database
    if not add_record(new_user):
        if request.is_json:
            return jsonify({"Error": "Registration failed"}), 500
        return render_form_error("Registration failed. Please try again.", 500)

    session["user_id"] = new_user.id
    session["username"] = new_user.username

    if request.is_json:
        return jsonify({"message": "Registration successful"}), 201
    return redirect(url_for("lobby_bp.lobby_page"))
    
    
# Login route
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("index.html")


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or request.form
    email = data.get("email")
    password = data.get("password")

    def render_form_error(message, status_code=400):
        return render_template("index.html", error=message), status_code

    if not email or not password:
        if request.is_json:
            return jsonify({"error": "Email and password are required"}), 400
        return render_form_error("Email and password are required.")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        if request.is_json:
            return jsonify({"error": "Invalid email or password"}), 401
        return render_form_error("Invalid email or password.", 401)

    session["user_id"] = user.id
    session["username"] = user.username
    if request.is_json:
        return jsonify({"message": f"Welcome {user.username}!"}), 200
    return redirect(url_for("lobby_bp.lobby_page"))


# Logout route
@auth_bp.route("/logout", methods=["POST"])
def logout_user():
    session.clear()
    if request.is_json:
        return jsonify({"message": "Logged out successfully"}), 200
    return redirect(url_for("home"))
