
from flask import Flask, render_template, request
from database import get_db_connection

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(debug=True)
