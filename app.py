
import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")


def login_required(view):
    """Redirect unauthenticated users to the login page."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/test-db")
def test_db():
    connection = get_db_connection()
    connection.close()

    return "PriceMind AI database connection successful!"


@app.route("/search", methods=["POST"])
def search_products():
    search_query = request.form.get("query", "").strip()

    if not search_query:
        return render_template(
            "search_results.html",
            products=[],
            search_query="",
            message="Please enter a product name."
        )

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT
            p.product_id,
            p.product_name,
            p.brand,
            p.category,
            s.store_name,
            pp.price,
            pp.product_url
        FROM products p
        LEFT JOIN product_prices pp
            ON p.product_id = pp.product_id
        LEFT JOIN stores s
            ON pp.store_id = s.store_id
        WHERE p.product_name LIKE %s
        ORDER BY pp.price ASC
    """

    cursor.execute(sql, ("%" + search_query + "%",))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    if products:
        message = f"Found {len(products)} matching result(s)."
    else:
        message = "No matching products found in the database."

    return render_template(
        "search_results.html",
        products=products,
        search_query=search_query,
        message=message
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", username=username, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", username=username, email=email)

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s OR username = %s",
                (email, username),
            )
            if cursor.fetchone() is not None:
                flash("An account with that username or email already exists.", "danger")
                return render_template("register.html", username=username, email=email)

            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT user_id, username, email, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=True)
