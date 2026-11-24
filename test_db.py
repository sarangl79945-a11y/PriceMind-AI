
from database import get_db_connection

try:
    connection = get_db_connection()

    print("MySQL connection successful!")
    print("PriceMind AI database is connected.")

    connection.close()

except Exception as error:
    print("MySQL connection failed:")
    print(error)
