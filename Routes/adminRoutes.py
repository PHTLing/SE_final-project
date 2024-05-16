from flask import jsonify, request

def initRoutes(app, mysql):

    @app.route('/admin/SignUp', methods=['POST'])
    def admin_SignUp():
        #Lấy dữ liệu từ database
        HoTen = request.form['HoTen']
        CCCD = request.form['CCCD']
        GioiTinh = request.form['GioiTinh']
        NgayGioSinh = request.form['NgayGioSinh']
        MaQueQuan = request.form['MaQueQuan']
        MaNgheNghiep = request.form['MaNgheNghiep']
        SDT = request.form['SDT']
        DiaChi = request.form['DiaChi']
        password = request.form['password']
        id_tvc = request.form['id_tvc'] or None
        MaQuanHe = request.form['MaQuanHe'] or None
        NgayPhatSinh = request.form['NgayPhatSinh'] or None
        #Connect database
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO THANHVIEN (HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh]
        )
        cur.execute(
            'INSERT INTO  USERS (CCCD,password,role) VALUES (%s,%s,user)', [CCCD,password]
            )
        #results = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify('Đăng ký thành công!')

    @app.route('/admin/SignIn', methods=['POST'])
    def admin_SignIn ():
        cccd = request.form['CCCD']
        password = request.form['password']

        if (len(cccd) !=12 ):
            return jsonify({'EC': '2', 'EM': 'CCCD không hợp lệ'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM USERS WHERE CCCD = %s ', [cccd]
        )
        results = cur.fetchall()
        if (password != results[0]['password']):
            return jsonify({'EC': '1', 'EM':'Mật khẩu không đúng'}),401
        cur.close()
        return jsonify({'EC': '0', 'EM':'Success'}),200
    
    @app.route('/admin/Account/<int:id>', methods=['GET'])
    def admin_Account(id):
        print(id)
        #id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN INNER JOIN USERS ON THANHVIEN.id_user = USERS.id WHERE id_user = %s', [id]
        )
        results = cur.fetchall()
        for item in results:
        # Sử dụng phương thức pop()
             item.pop("password" , None)
             item.pop("USERS.id" , None)
            #del results['password']
        cur.close()
        return jsonify(results)
    
    @app.route('/admin/Home/', methods=['GET'])
    def admin_Home():
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
        query = "SELECT * FROM THANHVIEN WHERE 1=1"
        params = []
        if HoTen  != 'null':
            query += " AND HoTen LIKE %s"
            params.append(f"%{HoTen}%")
        if NamSinh != 'null':
                NamSinh = int(NamSinh)
                query += " AND YEAR(NgayGioSinh) = %s"
                params.append(NamSinh)
        if QueQuan  != 'null':
            query += " AND QueQuan LIKE %s"
            params.append(f"%{QueQuan}%")
        if DiaChi != 'null':
            query += " AND DiaChi LIKE %s"
            params.append(f"%{DiaChi}%")

        cur =  mysql.connection.cursor()
        cur.execute(query, params)
        temp = cur.fetchall()
        print(temp)
        if not temp:
            return jsonify({'EC': '2', 'EM': 'Không tìm thấy người dùng nào'}), 404

        results = []
        for row in temp:
            results.append({
                'HoTen': row['HoTen'],
                'NamSinh': row['NamSinh'],
                'QueQuan': row['QueQuan'],
                'DiaChi': row['DiaChi']
            })

        return jsonify({'EC': '0', 'EM': 'Thành công', 'data': results}), 200


   