from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from db_connection import db_connection
from mysql.connector import Error
app = Flask(__name__)
ma = Marshmallow(app)

class UsersSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)

    class Meta:
        fields = ("name", "email")

users_schema = UsersSchema()
user_schema = UsersSchema()

@app.route('/')
def home():
    return "Welcome to the Flask Party"

@app.route('/users', methods=['GET'])
def get_users():
    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            return users_schema.jsonify(users)
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    return jsonify({"Error": "Database Connection failed"}), 500

@app.route('/users', methods=['POST'])
def add_customer():
    try:
        customer_data = users_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": "Invalid Data"}), 400

    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            new_customer = (customer_data['name'], customer_data['email'])
            query = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(query, new_customer)
            conn.commit()
            return jsonify({'Message': "New User Added Successfully!"}), 201
        except Error:
            return jsonify({"Error": "Internal Server Error"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database Connection Failed!"}), 500

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": "Invalid Data"}), 400

    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(check_query, (id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"Error": "User not found"}), 404
            updated_user = (user_data['name'], user_data['email'], id)
            query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
            cursor.execute(query, updated_user)
            conn.commit()
            return jsonify({"Message": f"Successfully updated User {id}"}), 200
        except Error:
            return jsonify({"Error": "Internal Server Error"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database Connection Failed!"}), 500

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(check_query, (id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"Error": "User not found"}), 404
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()
            return jsonify({"Message": f"User {id} was Destroyed!"})
        except Error:
            return jsonify({"Error": "Internal Server Error"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database Connection Failed!"}), 500