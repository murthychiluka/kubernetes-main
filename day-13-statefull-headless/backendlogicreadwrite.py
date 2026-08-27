from flask import Flask, request, jsonify
import mysql.connector
import time

app = Flask(__name__)

# -------------------------------
# Database Configuration
# -------------------------------
DB_CONFIG = {
    "user": "root",
    "password": "rootpassword",
    "database": "testdb",
    "port": 3306
}

# Writer (mysql-0) and Reader (mysql-1)
WRITER_HOST = "mysql-0.mysql.default.svc.cluster.local"
READER_HOST = "mysql-1.mysql.default.svc.cluster.local"


# -------------------------------
# Database Helpers
# -------------------------------
def query_db(host, sql, params=None, write=False):
    try:
        conn = mysql.connector.connect(host=host, **DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        if write:
            conn.commit()
        else:
            result = cursor.fetchall()
            return result
    finally:
        cursor.close()
        conn.close()


# -------------------------------
# Routes
# -------------------------------

@app.route("/read", methods=["GET"])
def read_data():
    """GET endpoint → routes to mysql-1 (reader)"""
    try:
        rows = query_db(READER_HOST, "SELECT @@hostname, NOW();")
        return jsonify({
            "target": READER_HOST,
            "pod_hostname": rows[0][0],
            "timestamp": str(rows[0][1])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/write", methods=["POST"])
def write_data():
    """POST endpoint → routes to mysql-0 (writer)"""
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        query_db(WRITER_HOST, "INSERT INTO test_table (data, created_at) VALUES (%s, %s)", ("test-write", timestamp), write=True)
        rows = query_db(WRITER_HOST, "SELECT @@hostname, NOW();")
        return jsonify({
            "target": WRITER_HOST,
            "pod_hostname": rows[0][0],
            "timestamp": str(rows[0][1]),
            "message": "Write successful"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "MySQL routing test service",
        "endpoints": {
            "GET /read": "Read from mysql-1 (reader)",
            "POST /write": "Write to mysql-0 (writer)"
        }
    })


# -------------------------------
# Start Flask Server
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
