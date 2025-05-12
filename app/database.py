import pyodbc

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=KMC\\SQLEXPRESS;'
        'DATABASE=HealthDB;'
        'UID=kmchealth;'
        'PWD=h34lth;'
        'Trusted_Connection=yes;'
    )
    print("Successfully connected to SQL Server!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
