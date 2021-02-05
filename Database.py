import mysql.connector
from datetime import datetime

class Database:
    def __init__(self):
        self.user = "rudar"
        self.password = "kovajenasa123"
        self.host = "localhost"
        self.port = 3306
        self.database = "rudnik"
        
        
    def storeValue(self, table, value):
        try:
            conn = mysql.connector.connect(user = self.user,
                                   password = self.password,
                                   host = self.host,
                                   port = self.port,
                                   database = self.database)
            cursor = conn.cursor()
            
            now = datetime.now()
            sql = "INSERT INTO "+table+" (value, created_at) VALUES (%s, %s)"
            val = (value, now)
            
            cursor.execute(sql, val)
            conn.commit()
            conn.close()
        except KeyboardInterrupt:
            conn.close()
        