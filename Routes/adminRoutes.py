from flask import jsonify, request

def initRoutes(app, mysql):

    @app.route('/admin/SignUp', methods=['POST'])
    def admin():
        #Lấy dữ liệu từ database
        HoTen = request.form['HoTen']
        CCCD = request.form['CCCD']
        GioiTinh = request.form['GioiTinh']
        NgayGioSinh = request.form['NgayGioSinh']
        QueQuan = request.form['QueQuan']
        NgheNghiep = request.form['NgheNghiep']
        Sđt = request.form['Sđt']
        DiaChi = request.form['DiaChi']
        password = request.form['password']
        #Connect database
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO THANHVIEN (HoTen,CCCD,GioiTinh,NgayGioSinh,QueQuan,NgheNghiep,Sđt,DiaChi) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', HoTen,CCCD,GioiTinh,NgayGioSinh,QueQuan,NgheNghiep,Sđt,DiaChi
            'INSERT INTO  USERS (cccd,password) VALUES (%s,%s)', CCCD,password
            )
        #results = cur.fetchall()
        cur.close()
        
        # print(results[0]['email'])
        # #xử lý kết quả trước khi trả về
        # Trả về kết quả dưới dạng JSON
        return jsonify('Đăng ký thành công!')


    