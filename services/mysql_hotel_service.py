import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

class MySQLHotelService:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def get_hotels(self, city=None):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM hotels WHERE status='APPROVED'"
        params = ()
        if city:
            query += " AND city=%s"
            params = (city,)
        cursor.execute(query, params)
        hotels = cursor.fetchall()
        cursor.close()
        return hotels

    def get_room_types(self, hotel_id=None):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM room_types WHERE status='APPROVED'"
        params = ()
        if hotel_id:
            query += " AND hotel_id=%s"
            params = (hotel_id,)
        cursor.execute(query, params)
        room_types = cursor.fetchall()
        cursor.close()
        return room_types

    def get_bookings(self, user_email=None):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT b.*, u.email FROM bookings b JOIN users u ON b.user_id = u.id"
        params = ()
        if user_email:
            query += " WHERE u.email=%s"
            params = (user_email,)
        cursor.execute(query, params)
        bookings = cursor.fetchall()
        cursor.close()
        return bookings

    def close(self):
        if self.connection:
            self.connection.close()
