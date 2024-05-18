from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from Routes.adminRoutes import initRoutes as routes 
app = Flask(__name__)
app.secret_key = 'SEProject' 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'se_backend'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

routes(app, mysql)

app.debug = True
if __name__ == '__main__':
    app.run(debug=True)

