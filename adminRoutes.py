from flask import jsonify, request

def initRoutes(app, mysql):

    @app.route('/admin', methods=['POST'])
    def admin():
        #Lấy dữ liệu từ database
        id = request.form['id']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM users WHERE id = %s', (id,)  
            )
        results = cur.fetchall()
        cur.close()
        
        print(results[0]['email'])
        #xử lý kết quả trước khi trả về
        # Trả về kết quả dưới dạng JSON
        return jsonify(results[0])


    