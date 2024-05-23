from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from Routes.adminRoutes import initRoutes as routes 
app = Flask(__name__)
app.secret_key = 'SEProject' 

app.config['MYSQL_HOST'] = 'mysql_db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'se-backend'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["MYSQL_DATABASE_PASSWORD"] = 123456

mysql = MySQL(app)

routes(app, mysql)

app.debug = True
if __name__ == '__main__':
    app.run(debug=True)

