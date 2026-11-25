
from database import get_db_connection


def add_sample_data():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Sample online stores
        sample_stores = [
            ("Amazon", "https://www.amazon.in"),
            ("Flipkart", "https://www.flipkart.com"),
            ("Croma", "https://www.croma.com")
        ]

        for store_name, website_url in sample_stores:
            cursor.execute(
                """
                SELECT store_id
                FROM stores
                WHERE store_name = %s
                """,
                (store_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO stores (store_name, website_url)
                    VALUES (%s, %s)
                    """,
                    (store_name, website_url)
                )

        # Sample products
        sample_products = [
            ("iPhone 15", "Apple", "Smartphone"),
            ("Galaxy S24", "Samsung", "Smartphone"),
            ("MacBook Air M2", "Apple", "Laptop")
        ]

        for product_name, brand, category in sample_products:
            cursor.execute(
                """
                SELECT product_id
                FROM products
                WHERE product_name = %s AND brand = %s
                """,
                (product_name, brand)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO products
                    (product_name, brand, category)
                    VALUES (%s, %s, %s)
                    """,
                    (product_name, brand, category)
                )

        connection.commit()

        # Get product names and their IDs
        cursor.execute(
            "SELECT product_id, product_name FROM products"
        )

        products = {
            product_name: product_id
            for product_id, product_name in cursor.fetchall()
        }

        # Get store names and their IDs
        cursor.execute(
            "SELECT store_id, store_name FROM stores"
        )

        stores = {
            store_name: store_id
            for store_id, store_name in cursor.fetchall()
        }

        # Sample prices
        sample_prices = [
            ("iPhone 15", "Amazon", 59999.00),
            ("iPhone 15", "Flipkart", 58999.00),
            ("iPhone 15", "Croma", 60999.00),

            ("Galaxy S24", "Amazon", 54999.00),
            ("Galaxy S24", "Flipkart", 53999.00),
            ("Galaxy S24", "Croma", 55999.00),

            ("MacBook Air M2", "Amazon", 89999.00),
            ("MacBook Air M2", "Flipkart", 87999.00),
            ("MacBook Air M2", "Croma", 90999.00)
        ]

        for product_name, store_name, price in sample_prices:
            product_id = products.get(product_name)
            store_id = stores.get(store_name)

            if product_id is None or store_id is None:
                continue

            cursor.execute(
                """
                SELECT price_id
                FROM product_prices
                WHERE product_id = %s AND store_id = %s
                """,
                (product_id, store_id)
            )

            existing_price = cursor.fetchone()

            if existing_price:
                cursor.execute(
                    """
                    UPDATE product_prices
                    SET price = %s
                    WHERE price_id = %s
                    """,
                    (price, existing_price[0])
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO product_prices
                    (product_id, store_id, price)
                    VALUES (%s, %s, %s)
                    """,
                    (product_id, store_id, price)
                )

            # Save sample price history
            cursor.execute(
                """
                INSERT INTO price_history
                (product_id, store_id, price)
                VALUES (%s, %s, %s)
                """,
                (product_id, store_id, price)
            )

        connection.commit()

        print("Sample products and prices added successfully!")

    except Exception as error:
        connection.rollback()
        print("Error adding sample data:", error)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    add_sample_data()
