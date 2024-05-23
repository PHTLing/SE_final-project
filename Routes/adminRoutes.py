from flask import jsonify, request, session
from datetime import datetime

def initRoutes(app, mysql):

    @app.route('/admin/SignUp', methods=['POST'])
    def admin_SignUp():
        #Lấy dữ liệu nhập
        HoTen = request.form['HoTen']
        CCCD = request.form['CCCD']
        GioiTinh = request.form['GioiTinh']
        NgayGioSinh = request.form['NgayGioSinh']
        MaQueQuan = request.form['MaQueQuan']
        MaNgheNghiep = request.form['MaNgheNghiep']
        SDT = request.form['SDT']
        DiaChi = request.form['DiaChi']
        password = request.form['password']
        #Connect database
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM USERS WHERE CCCD = %s', [CCCD]
        )
        temp= cur.fetchall()
        print(temp)
        if temp !=():
            return jsonify({'EC': '1', 'EM': 'CCCD đã tồn tại'}), 400 # Chưa có cây gia phả
        #Thêm thành viên + gia phả
        elif len(CCCD) != 12:
            return jsonify({'EC': '2', 'EM': 'CCCD không hợp lệ'}), 400
        elif len(SDT) != 10 or SDT[0] != '0':
            return jsonify({'EC': '3', 'EM': 'Số điện thoại không hợp lệ'}), 400
        elif len(password) < 4:
            return jsonify({'EC': '4', 'EM': 'Mật khẩu phải có ít nhất 4 ký tự'}), 400
        elif NgayGioSinh > datetime.now():
            return jsonify({'EC': '5', 'EM': 'Ngày sinh không hợp lệ'}), 400
        else:            
            cur.execute(
                'INSERT INTO THANHVIEN (HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi]
            )
            cur.execute(
                'INSERT INTO  USERS (CCCD,password,role) VALUES (%s,%s,user)', [CCCD,password]
                )
            #results = cur.fetchall()
            mysql.connection.commit()
            cur.execute(
                'SELECT FROM THANHVIEN tv JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s', [CCCD]
            )
            cur.execute(
                'SELECT tv.HoTen, tv.id, u.role FROM THANHVIEN tv JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s', [CCCD]
            )
            results = cur.fetchall()
            cur.close()
        return jsonify({'EC': '0', 'EM': 'Đăng ký thành công!', 'data': results}), 200

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
        #Tìm thành viên
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT tv.HoTen, tv.id, u.role FROM THANHVIEN tv JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s', [cccd]
        )
        results = cur.fetchall()
        session['cccd'] = cccd
        # Gửi id
        return jsonify({'EC': '0', 'EM':'Success', 'data': results}),200
    
    @app.route('/admin/SignOut/<int:id>', methods=['GET'])
    def admin_SignOut(id):
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT id_user FROM THANHVIEN WHERE id = %s', [id]
        )
        results = cur.fetchall()
        session.pop('result', None)
        return jsonify({'EC': '0', 'EM':'Đăng xuất thành công'}),200

    @app.route('/admin/Account/<int:id>', methods=['GET'])
    def admin_Account(id):
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
        return jsonify({'EC':0, 'EM':'Success', 'data':results})
    
    @app.route('/admin/ChangeAvt/<int:id>', methods=['POST'])
    def admin_ChangeAvt(id):
        url = request.form['url']
        cur = mysql.connection.cursor()
        cur.execute(
            'UPDATE THANHVIEN SET Avt = %s WHERE id = %s', [url,id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC':0, 'EM':'Change avatar successed!'}),200
    
    @app.route('/admin/ChangeSDT/<int:id>', methods=['POST'])
    def admin_ChangeSDT(id):
        SDT = request.form['SDT']
        cur = mysql.connection.cursor()
        cur.execute(
            'UPDATE THANHVIEN SET SDT = %s WHERE id = %s', [SDT,id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC':0, 'EM':'Change phone number successed!'}),200

    @app.route('/admin/Home/', methods=['GET'])
    def admin_Home():
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN ', 
        )
        results = cur.fetchall()
        cur.close()
        return jsonify(results)
    
    @app.route('/admin/SearchMember', methods=['POST'])
    def admin_SearchMember():
        results = []
        #Lấy dữ liệu nhập
        HoTen = request.form['HoTen'] 
        NamSinh = request.form['NamSinh'] 
        QueQuan = request.form['QueQuan'] # Frondend gửi kèm mã quê quán
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
            query += " AND MaQueQuan LIKE %s"
            params.append(f"%{QueQuan}%")
        if DiaChi != 'null':
            query += " AND DiaChi LIKE %s"
            params.append(f"%{DiaChi}%")

        cur =  mysql.connection.cursor()
        cur.execute(query, params)
        temp = cur.fetchall()
        print(temp)
        if not temp:
            return jsonify({'EC': '1', 'EM': 'Không tìm thấy người dùng nào'}), 404

        results = []
        for row in temp:
            #Tìm cha/ mẹ gốc
            if row['MaQuanHe'] == 1:
                cha['HoTen'] = ''
                me['HoTen'] = ''
            else:
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id = %s', [row['id_tvc']]
                )
                parent = cur.fetchall()
                print("check cha: ",parent)
                if parent is None:
                    cha = {'HoTen': ''}
                    me = {'HoTen': ''}
                else:
                    if parent[0]['GioiTinh'] == 'Nam':
                        cha = parent[0]
                    else: me = parent[0]
                    #Tìm cha/ mẹ còn lại
                    cur.execute(
                        'SELECT * FROM THANHVIEN WHERE id_tvc = %s AND MaQuanHe = 1', [row['id_tvc']]
                    )
                    parent = cur.fetchone()
                    if parent is None:
                        parent = ({'HoTen': ''},)
                    if cha is None:
                        cha = parent[0]
                    else: me = parent[0]
            results.append({
                'HoTen': row['HoTen'],
                'NgaySinh': row['NgayGioSinh'].strftime('%Y-%m-%d'),
                'Doi': row['Doi'],
                'Cha': cha['HoTen'],
                'Me': me['HoTen'],
            })

        return jsonify({'EC': '0', 'EM': 'Thành công', 'data': results}), 200

    @app.route('/admin/GetInfo', methods=['Get'])
    def admin_getinfo():
        results = []
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM QUEQUAN ',
        )
        results.append (cur.fetchall())
        cur.execute(
            'SELECT * FROM NGHENGHIEP ',
        )
        results.append(cur.fetchall())
        cur.execute(
            'SELECT * FROM QUANHE ',
        )
        results.append(cur.fetchall())
        cur.close()
        dic ={
            'QueQuan': results[0],
            'NgheNghiep': results[1],
            'QuanHe': results[2]
        }
        return jsonify(dic)
    
    @app.route('/admin/GetAward', methods=['Get'])
    def admin_getAward():
        results = []
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM LOAITHANHTICH' 
        )
        results.append(cur.fetchall())
        cur.close()
        return jsonify(results)

    @app.route('/admin/GetEnd', methods=['Get'])
    def admin_getEnd():
        results = []
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM NGUYENNHAN' 
        )
        results.append (cur.fetchall())
        cur.execute(
            'SELECT * FROM DIADIEMMAITANG' 
        )   
        results.append (cur.fetchall())
        cur.close()
        dict= {
            'NguyenNhan': results[0],
            'DiaDiemMaiTang': results[1]
        }
        return jsonify(dict)
    
    @app.route('/admin/ForgetPassword', methods=['POST'])
    def admin_ForgetPassword():
        results = []
        CCCD = request.form['CCCD']
        SDT = request.form['SDT']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT tv.HoTen, tv.id, u.role FROM THANHVIEN tv JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s AND tv.SDT = %s', [CCCD,SDT]
        )
        results = cur.fetchall()
        print(results)
        cur.close()
        if not results:
            return jsonify({'EC': '1', 'EM': 'Thông tin không chính xác'}), 404
        return jsonify({'EC': '0', 'EM': 'Success;', 'data': results}), 200

    @app.route('/admin/Add', methods=['POST'])
    def admin_Add(id):
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM QUEQUAN ', [id]
        )
        HoTen = request.form['HoTen']
        CCCD = request.form['CCCD']
        GioiTinh = request.form['GioiTinh'] or None
        NgayGioSinh = request.form['NgayGioSinh'] or None
        MaQueQuan = request.form['MaQueQuan'] or None #FE đính kèm
        MaNgheNghiep = request.form['MaNgheNghiep'] or None #FE đính kèm
        SDT = request.form['SDT'] 
        DiaChi = request.form['DiaChi'] or None
        id_tvc = request.form['id_tvc'] 
        MaQuanHe = request.form['MaQuanHe'] #FE đính kèm
        NgayPhatSinh = request.form['NgayPhatSinh'] or None
        ThanhVien = request.form['ThanhVienCu'] or None
        
        cur = mysql.connection.cursor()
        # cur.execute(
        #    'SELECT MaQueQuan FROM QUEQUAN WHERE TenQueQuan= %s', [QueQuan]
        # )
        # MaQueQuan = cur.fetchone()['MaQueQuan']
        # cur.execute(
        #     'SELECT MaNgheNghiep FROM NGHENGHIEP WHERE TenNgheNghiep= %s', [NgheNghiep]
        # )
        # MaNgheNghiep = cur.fetchone()['MaNgheNghiep']
        # cur.execute(
        cur.execute(
            'INSERT INTO THANHVIEN (HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh,id_user) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ HoTen,CCCD,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh,id_user]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify('Thêm thành viên thành công!')
    
    @app.route('/admin/SuggestName', methods=['POST'])
    def admin_SuggestName():
        results = []
        HoTen = request.form['HoTen']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT id, HoTen, NgayGioSinh, GioiTinh FROM THANHVIEN WHERE HoTen LIKE %s', [f"%{HoTen}%"]
        )
        results = cur.fetchall()
        results[0]['NgayGioSinh'] = results[0]['NgayGioSinh'].strftime('%Y-%m-%d')
        cur.close()
        return jsonify({'EC':'0','EM':'Found!','data':results})

    @app.route('/admin/RecordDeath', methods=['POST'])
    def admin_RecordDeath():
        MaDiaDiemMaiTang = request.form['MaDiaDiemMaiTang']
        MaNguyenNhan = request.form['MaNguyenNhan']
        id = request.form['id']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT id,HoTen,GioiTinh,NgayGioSinh FROM THANHVIEN WHERE id = %s', [id]
        )
        results = cur.fetchone()
        if results is None:
            return jsonify({'EC': '1', 'EM': 'Không tìm thấy thành viên'}), 404
        NgayGioMat = request.form['NgayGioMat']
        cur.execute(
            'UPDATE THANHVIEN SET Status = 1 WHERE id = %s', [id]
        )
        cur.execute(
            'INSERT INTO KETTHUC (MaThanhVien,NgayGioMat,MaNguyenNhan, MaDiaDiemMaiTang) VALUES (%s,%s,%s,%s)',[id,NgayGioMat,MaNguyenNhan,MaDiaDiemMaiTang]
        )
        mysql.connection.commit()
        return jsonify({'EC': '0', 'EM':'Ghi nhận thành công'}), 200