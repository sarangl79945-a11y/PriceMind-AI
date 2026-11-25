
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Connect to the PriceMind AI MySQL database."""

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection


def create_tables():
    """Create the required PriceMind AI database tables."""

    connection = get_db_connection()
    cursor = connection.cursor()

    tables = [

        # 1. User accounts
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # 2. Online stores
        """
        CREATE TABLE IF NOT EXISTS stores (
            store_id INT AUTO_INCREMENT PRIMARY KEY,
            store_name VARCHAR(100) NOT NULL UNIQUE,
            website_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # 3. Products
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            brand VARCHAR(100),
            category VARCHAR(100),
            image_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # 4. Current product prices
        """
        CREATE TABLE IF NOT EXISTS product_prices (
            price_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            store_id INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            product_url VARCHAR(500),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
                REFERENCES products(product_id),

            FOREIGN KEY (store_id)
                REFERENCES stores(store_id)
        )
        """,

        # 5. Historical prices
        """
        CREATE TABLE IF NOT EXISTS price_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            store_id INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
                REFERENCES products(product_id),

            FOREIGN KEY (store_id)
                REFERENCES stores(store_id)
        )
        """,

        # 6. Machine Learning price predictions
        """
        CREATE TABLE IF NOT EXISTS price_predictions (
            prediction_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            predicted_price DECIMAL(10, 2) NOT NULL,
            prediction_date DATE NOT NULL,
            model_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
        """,

        # 7. Product reviews
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            store_id INT,
            review_text TEXT,
            sentiment VARCHAR(30),
            rating DECIMAL(3, 1),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
                REFERENCES products(product_id),

            FOREIGN KEY (store_id)
                REFERENCES stores(store_id)
        )
        """,

        # 8. Price alerts
        """
        CREATE TABLE IF NOT EXISTS price_alerts (
            alert_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            target_price DECIMAL(10, 2) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
        """
    ]

    try:
        for table_query in tables:
            cursor.execute(table_query)

        connection.commit()
        print("All PriceMind AI tables created successfully!")

    except mysql.connector.Error as error:
        connection.rollback()
        print("Error creating tables:", error)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()
