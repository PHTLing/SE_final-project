from flask import jsonify, request

def initRoutes(app, mysql):

    @app.route('/admin/SignUp', methods=['POST'])
    def admin_SignUp():
        #Lấy dữ liệu từ database
        HoTen = request.form['HoTen']
        CCCD = request.form['CCCD']
        GioiTinh = request.form['GioiTinh']
        NgayGioSinh = request.form['NgayGioSinh']
        QueQuan = request.form['QueQuan']
        NgheNghiep = request.form['NgheNghiep']
        SDT = request.form['SDT']
        DiaChi = request.form['DiaChi']
        password = request.form['password']
        #Connect database
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO THANHVIEN (HoTen,CCCD,GioiTinh,NgayGioSinh,QueQuan,NgheNghiep,Sđt,DiaChi) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', HoTen,CCCD,GioiTinh,NgayGioSinh,QueQuan,NgheNghiep,SDT,DiaChi
        )
        cur.execute(
            'INSERT INTO  USERS (cccd,password) VALUES (%s,%s)', CCCD,password
            )
        #results = cur.fetchall()
        cur.close()
        
        # print(results[0]['email'])
        # #xử lý kết quả trước khi trả về
        # Trả về kết quả dưới dạng JSON
        return jsonify('Đăng ký thành công!')

    @app.route('/admin/SignIn', methods=['POST'])
    def admin_SignIn ():
        cccd = request.form['CCCD']
        password = request.form['password']

        if (cccd.size() !=12 ):
            return jsonify({'EC': '2', 'EM': 'CCCD không hợp lệ'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM USERS WHERE CCCD = %s ', cccd
        )
        results = cur.fetchall()
        if (password != results[0]['password']):
            return jsonify({'EC': '1', 'EM':'Mật khẩu không đúng'}),401
        cur.close()
        return jsonify({'EC': '0', 'EM':'Success'}),200
    
    @app.route('/admin/Account', methods=['GET'])
    def admin_Account():
        id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN WHERE id = %s', id
        )
        results = cur.fetchall()
        cur.close()
        return jsonify(results)
    
    @app.route('/admin/Home', methods=['POST'])
    def admin_Home():
        id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN ', 
        )
        results = cur.fetchall()
        cur.close()
        return jsonify(results)
    
    @app.route('/admin/SearchMember', methods=['GET','POST'])
    def admin_SearchMember():
        results = []
        HoTen = request.form['HoTen']
        NamSinh = request.form['NamSinh']
        QueQuan = request.form['QueQuan']
        DiaChi = request.form['DiaChi']
        query = "SELECT * FROM ThanhVien WHERE 1=1"
        params = []

        if HoTen:
            query += " AND HoTen LIKE ?"
            params.append(f"%{HoTen}%")
        if NamSinh:
            try:
                NamSinh = int(NamSinh)
                query += " AND NamSinh = ?"
                params.append(NamSinh)
            except ValueError:
                return jsonify({'EC': '3', 'EM': 'Năm sinh không hợp lệ'}), 400
        if QueQuan:
            query += " AND QueQuan LIKE ?"
            params.append(f"%{QueQuan}%")
        if DiaChi:
            query += " AND DiaChi LIKE ?"
            params.append(f"%{DiaChi}%")

        cur =  mysql.connection.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        if not rows:
            return jsonify({'EC': '2', 'EM': 'Không tìm thấy người dùng nào'}), 404

    results = []
    for row in rows:
        results.append({
            'name': row['name'],
            'birth_year': row['birth_year'],
            'hometown': row['hometown'],
            'address': row['address']
        })

    return jsonify({'EC': '0', 'EM': 'Thành công', 'data': results}), 200


    @app.route('/admin/UpdateMember', methods=['POST'])