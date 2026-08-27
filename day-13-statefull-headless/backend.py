import mysql.connector

# -------------------------------
# Connect via ClusterIP Service
# -------------------------------
clusterip_db = mysql.connector.connect(
    host="mysqll.default.svc.cluster.local",  # ClusterIP service
    user="root",
    password="rootpassword",
    database="testdb",
    port=3306
)

cursor = clusterip_db.cursor()
cursor.execute("SELECT @@hostname;")
print("ClusterIP service hits Pod:", cursor.fetchone()[0])
clusterip_db.close()

# -------------------------------
# Connect via Headless Service
# -------------------------------
# For StatefulSet Pod 1
headless_db_1 = mysql.connector.connect(
    host="mysql-1.mysql.default.svc.cluster.local",  # Headless service
    user="root",
    password="rootpassword",
    database="testdb",
    port=3306
)

cursor = headless_db_1.cursor()
cursor.execute("SELECT @@hostname;")
print("Headless service Pod 1:", cursor.fetchone()[0])
headless_db_1.close()

# For StatefulSet Pod 0
headless_db_0 = mysql.connector.connect(
    host="mysql-0.mysql.default.svc.cluster.local",  # Headless service
    user="root",
    password="rootpassword",
    database="testdb",
    port=3306
)

cursor = headless_db_0.cursor()
cursor.execute("SELECT @@hostname;")
print("Headless service Pod 0:", cursor.fetchone()[0])
headless_db_0.close()
