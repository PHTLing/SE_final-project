from flask import jsonify, request, session
from datetime import datetime

def initRoutes(app, mysql):

    @app.route('/admin/SignUp', methods=['POST'])
    def admin_SignUp():
        #Lấy dữ liệu nhập
        HoTen = request.json.get('HoTen')
        CCCD = request.json.get('CCCD')
        GioiTinh = request.json.get('GioiTinh')
        NgayGioSinh = request.json.get('NgayGioSinh')
        MaQueQuan = request.json.get('MaQueQuan')
        MaNgheNghiep = request.json.get('MaNgheNghiep')
        SDT = request.json.get('SDT')
        DiaChi = request.json.get('DiaChi')
        password = request.json.get('password')
        #Connect database
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM USERS WHERE CCCD = %s', [CCCD]
        )
        temp= cur.fetchall()
        print(temp)
        if temp !=():
            return jsonify({'EC': 1, 'EM': 'CCCD đã tồn tại'}), 400 # Chưa có cây gia phả
        #Thêm thành viên + gia phả
        elif len(CCCD) != 12:
            return jsonify({'EC': 2, 'EM': 'CCCD không hợp lệ'}), 400
        elif len(SDT) != 10 or SDT[0] != 0:
            return jsonify({'EC': 3, 'EM': 'Số điện thoại không hợp lệ'}), 400
        elif len(password) < 4:
            return jsonify({'EC': 4, 'EM': 'Mật khẩu phải có ít nhất 4 ký tự'}), 400
        elif NgayGioSinh > datetime.now():
            return jsonify({'EC': 5, 'EM': 'Ngày sinh không hợp lệ'}), 400
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
        return jsonify({'EC': 0, 'EM': 'Đăng ký thành công!', 'data': results}), 200

    @app.route('/admin/SignIn', methods=['POST'])
    def admin_SignIn ():
        cccd = request.json.get('CCCD')
        password = request.json.get('password')
        #print(password)
        if (len(cccd) !=12 ):
            return jsonify({'EC': 2, 'EM': 'CCCD không hợp lệ'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM USERS WHERE CCCD = %s ', [cccd]
        )
        results = cur.fetchall()
        #print(results[0]['password'])
        if (password != results[0]['password']):
            return jsonify({'EC': 1, 'EM':'Mật khẩu không đúng'}),401
        
        #Tìm thành viên
        cur.execute(
            'SELECT tv.HoTen, tv.id, u.role FROM THANHVIEN tv INNER JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s', [cccd]
        )
        results = cur.fetchall()
        session['cccd'] = cccd
        # Gửi id
        print(results[0])
        return jsonify({'EC': 0, 'EM':'Success', 'data': results[0]}),200
    
    @app.route('/admin/SignOut/<int:id>', methods=['GET'])
    def admin_SignOut(id):
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT id_user FROM THANHVIEN WHERE id = %s', [id]
        )
        results = cur.fetchall()
        session.pop('result', None)
        return jsonify({'EC': 0, 'EM':'Đăng xuất thành công'}),200

    @app.route('/admin/Account/<int:id>', methods=['GET'])
    def admin_Account(id):
        #id = request.args.get('id')
        print("id: ",id)
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN JOIN USERS ON THANHVIEN.id_user = USERS.id WHERE THANHVIEN.id = %s', [id]
        )
        results = cur.fetchall()
        for item in results:
            if isinstance(item['NgayGioSinh'], datetime):
                formattedNGS = item['NgayGioSinh'].strftime('%d/%m/%Y %H:%M')
            else:
                formattedNGS = None
            item['NgayGioSinh'] = formattedNGS
            cur.execute(
                'SELECT TenQueQuan FROM QUEQUAN WHERE MaQueQuan = %s', [item['MaQueQuan']]
            )
            item['QueQuan'] = cur.fetchone()['TenQueQuan']
            cur.execute(
                'SELECT TenNgheNghiep FROM NGHENGHIEP WHERE MaNgheNghiep = %s', [item['MaNgheNghiep']]
            )
            item['NgheNghiep'] = cur.fetchone()['TenNgheNghiep']
            item.pop("password" , None)
            item.pop("USERS.id" , None)
            if item['TrangThai'] == 1:
                item['TrangThai'] = 'Đã mất'
                cur.execute(
                    'SELECT * FROM KETTHUC WHERE MaThanhVien = %s', [id]
                )
                item['NgayGioMat'] = cur.fetchone()['NgayGioMat']
                cur.execute(
                    'SELECT TenNguyenNhan FROM NGUYENNHAN WHERE MaNguyenNhan = %s', [item['MaNguyenNhan']]
                )
                item['NguyenNhan'] = cur.fetchone()['TenNguyenNhan']
                cur.execute(
                    'SELECT TenDiaDiemMaiTang FROM DIADIEMMAITANG WHERE MaDiaDiemMaiTang = %s', [item['MaDiaDiemMaiTang']]
                )
                item['DiaDiemMaiTang'] = cur.fetchone()['TenDiaDiemMaiTang']
        print(results)   
        cur.close()
        
        return jsonify({'EC':0, 'EM':'Success', 'data':results[0]})
    
    @app.route('/admin/ChangeAvt/<int:id>', methods=['POST'])
    def admin_ChangeAvt(id):
        url = request.json.get('url')
        cur = mysql.connection.cursor()
        cur.execute(
            'UPDATE THANHVIEN SET Avt = %s WHERE id = %s', [url,id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC':0, 'EM':'Change avatar successed!'}),200
    
    @app.route('/admin/ChangeSDT/<int:id>', methods=['POST'])
    def admin_ChangeSDT(id):
        SDT = request.json.get('SDT')
        cur = mysql.connection.cursor()
        cur.execute(
            'UPDATE THANHVIEN SET SDT = %s WHERE id = %s', [SDT,id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC':0, 'EM':'Change phone number successed!'}),200
    
    @app.route('/admin/SearchMember', methods=['POST'])
    def admin_SearchMember():
        results = []
        #Lấy dữ liệu nhập
        HoTen = request.json.get('HoTen') 
        NamSinh = request.json.get('NamSinh') 
        MaQueQuan = request.json.get('MaQueQuan') # Frondend gửi kèm mã quê quán
        DiaChi = request.json.get('DiaChi') 
        print ("Tên: ",HoTen,"Năm: " ,NamSinh,"Quê: ", MaQueQuan,"DC: ", DiaChi)
        if HoTen == '' and NamSinh == '' and MaQueQuan == '' and DiaChi == '':
            return jsonify({'EC': 1, 'EM': 'Vui lòng nhập ít nhất một trường', 'data': []}), 400
        query = "SELECT HoTen,id,id_tvc,MaQuanHe, NgayGioSinh,Doi FROM THANHVIEN WHERE 1=1"
        params = []
        if HoTen  != '':
            query += " AND HoTen LIKE %s"
            params.append(f"%{HoTen}%")
        if NamSinh != '':
            NamSinh = int(NamSinh)
            query += " AND YEAR(NgayGioSinh) = %s"
            params.append(NamSinh)
        if MaQueQuan  != '':
            query += " AND MaQueQuan LIKE %s"
            params.append(f"%{MaQueQuan}%")
        if DiaChi != '':
            query += " AND DiaChi LIKE %s"
            params.append(f"%{DiaChi}%")

        cur =  mysql.connection.cursor()
        cur.execute(query, params)
        temp = cur.fetchall()
        print (temp)
        final_results = []
        if not temp:
            return jsonify({'EC': 1, 'EM': 'Không tìm thấy người dùng nào', 'data': final_results}), 404
        for i in range(len(temp)):
            print(temp[i]['NgayGioSinh'])
            if isinstance(temp[i]['NgayGioSinh'], datetime):
                formattedNGS = temp[i]['NgayGioSinh'].strftime('%d/%m/%Y')
            else:
                formattedNGS = None
            temp[i]['NgayGioSinh'] = formattedNGS
            if temp[i]['id_tvc'] is None:
                temp[i]['id_tvc'] = ''
                final_results.append(
                    {
                        'HoTen': temp[i]['HoTen'],
                        'id': temp[i]['id'],
                        'NgaySinh': temp[i]['NgayGioSinh'],
                        'Doi': temp[i]['Doi'],
                        'Cha': {'HoTen': '', 'id': ''},
                        'Me': {'HoTen': '', 'id': ''}
                    }
                )
            elif temp[i]['MaQuanHe'] == 1:
                final_results.append(
                    {
                        'HoTen': temp[i]['HoTen'],
                        'id': temp[i]['id'],
                        'NgaySinh': temp[i]['NgayGioSinh'],
                        'Doi': temp[i]['Doi'],
                        'Cha': {'HoTen': '', 'id': ''},
                        'Me': {'HoTen': '', 'id': ''}
                    }
                )
            else:
                cur.execute(
                    'SELECT HoTen,id, GioiTinh FROM THANHVIEN WHERE id = %s', [temp[i]['id_tvc']]
                )
                parent = cur.fetchall()
                print("P1: ",parent)
                if parent is None:
                    cha = {'HoTen': '', 'id': ''}
                    me = {'HoTen': '', 'id': ''}
                else:
                    if parent[0]['GioiTinh'] == 'Nam':
                        cha = {'HoTen': parent[0]['HoTen'], 'id': parent[0]['id']}
                    else: me = {'HoTen': parent[0]['HoTen'], 'id': parent[0]['id']}
                    cur.execute(
                        'SELECT HoTen,id, GioiTinh FROM THANHVIEN WHERE id_tvc = %s and MaQuanHe=1', [temp[i]['id_tvc']]
                    )
                    parent_2 = cur.fetchall()
                    print("P2: ",parent_2)
                    if parent_2[0]['GioiTinh'] == 'Nam':
                        cha = {'HoTen': parent_2[0]['HoTen'], 'id': parent_2[0]['id']}
                    else: me = {'HoTen': parent_2[0]['HoTen'], 'id': parent_2[0]['id']}
                    final_results.append(
                        {
                            'HoTen': temp[i]['HoTen'],
                            'id': temp[i]['id'],
                            'NgaySinh': temp[i]['NgayGioSinh'],
                            'Doi': temp[i]['Doi'],
                            'Cha': {'HoTen': cha['HoTen'], 'id': cha['id']},
                            'Me': {'HoTen': me['HoTen'], 'id': me['id']}
                        }
                    )
            print(final_results)
        return jsonify({'EC': 0, 'EM': 'Thành công', 'data': final_results}), 200
        
    @app.route('/admin/GetInfo', methods=['Get'])
    def admin_GetInfo():
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
        print(dic)
        return jsonify({'EC':0,'EM': 'success','data':dic})
    
    @app.route('/admin/GetAward', methods=['Get'])
    def admin_getAward():
        results = []
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM LOAITHANHTICH' 
        )
        results=cur.fetchall()
        cur.close()
        return jsonify({'data':results})

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
        return jsonify({'data':dict})
    
    @app.route('/admin/ForgetPassword', methods=['POST'])
    def admin_ForgetPassword():
        results = []
        CCCD = request.json.get('CCCD')
        SDT = request.json.get('SDT')
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT tv.HoTen, tv.id, u.role FROM THANHVIEN tv JOIN USERS u ON tv.id_user=u.id WHERE tv.CCCD = %s AND tv.SDT = %s', [CCCD,SDT]
        )
        results = cur.fetchall()
        print(results)
        cur.close()
        if not results:
            return jsonify({'EC': 1, 'EM': 'Thông tin không chính xác'}), 404
        return jsonify({'EC': 0, 'EM': 'Success;', 'data': results}), 200
    
# Các chức năng    
    @app.route('/admin/Search', methods=['POST'])
    def admin_Search():
        results = []
        HoTen = request.json.get('HoTen')
        print(HoTen)
        cur = mysql.connection.cursor()
        if HoTen != '':
            cur.execute(
                'SELECT id, HoTen,CCCD FROM THANHVIEN WHERE HoTen LIKE %s', [f"%{HoTen}%"]
            )
            results = cur.fetchall()
        if results is None:
            print("Rỗng: ",results)
            return jsonify({'EC': 1, 'EM': 'Không tìm thấy thành viên', 'data': []}), 404
        print("Có: ",results)
        return jsonify({'EC':0,'EM':'Found!','data':results})

    @app.route('/admin/RecordEnd', methods=['POST'])
    def admin_RecordEnd():
        MaDiaDiemMaiTang = request.json.get('MaDiaDiemMaiTang')
        MaNguyenNhan = request.json.get('MaNguyenNhan')
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT id,HoTen,GioiTinh,NgayGioSinh FROM THANHVIEN WHERE id = %s', [id]
        )
        results = cur.fetchone()
        if results is None:
            return jsonify({'EC': 1, 'EM': 'Không tìm thấy thành viên'}), 404
        NgayGioMat = request.json.get('NgayGioMat')
        cur.execute(
            'UPDATE THANHVIEN SET Status = 1 WHERE id = %s', [id]
        )
        cur.execute(
            'INSERT INTO KETTHUC (MaThanhVien,NgayGioMat,MaNguyenNhan, MaDiaDiemMaiTang) VALUES (%s,%s,%s,%s)',[id,NgayGioMat,MaNguyenNhan,MaDiaDiemMaiTang]
        )
        mysql.connection.commit()
        return jsonify({'EC': 0, 'EM':'Ghi nhận thành công'}), 200
    
    @app.route('/admin/AddAward', methods=['POST'])
    def admin_AddAward():
        id = request.json.get('id')
        MaLoaiThanhTich = request.json.get('MaLoaiThanhTich')
        NgayPhatSinh = request.json.get('NgayPhatSinh')
        print(id, MaLoaiThanhTich, NgayPhatSinh)
        cur = mysql.connection.cursor()
        if id == '':
            return jsonify({'EC': 1, 'EM': 'Không tìm thấy thành viên'}), 404
        else:
            cur.execute(
                'SELECT * FROM THANHVIEN WHERE id = %s', [id]
            )
            results = cur.fetchall()
         
            if results is None:
                return jsonify({'EC': 1, 'EM': 'Không tìm thấy thành viên'}), 404
            else:
                cur.execute(
                    'INSERT INTO THANHTICH (MaThanhVien,MaLoaiThanhTich,NgayPhatSinh) VALUES (%s,%s,%s)',[id,MaLoaiThanhTich,NgayPhatSinh]
                )
                mysql.connection.commit()
        return jsonify({'EC': 0, 'EM':'Thêm thành tích thành công!'}),200


# Chỉnh sửa bảng phụ (thêm)
    @app.route('/admin/AddQueQuan', methods=['POST'])
    def admin_AddQueQuan():
        TenQueQuan = request.json.get('TenQueQuan')
        cur = mysql.connection.cursor()
        #Kiểm tra tên quê quán đã tồn tại chưa
        cur.execute(
            'SELECT * FROM que_quan WHERE LOWER(TenQueQuan) = LOWER(%s)', [TenQueQuan])
        result = cur.fetchone()
        
        if result:
            return jsonify({'EC': 1, 'EM': 'Tên quê quán đã tồn tại'}), 400
        #Thêm quê quán
        cur.execute(
            'INSERT INTO QUEQUAN (TenQueQuan) VALUES (%s)', [TenQueQuan]
        )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM QUEQUAN WHERE TenQueQuan = %s', [TenQueQuan]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thêm quê quán thành công!', 'data':results}),200

    @app.route('/admin/AddNgheNghiep', methods=['POST'])
    def admin_AddNgheNghiep():
        TenNgheNghiep = request.json.get('TenNgheNghiep')
        cur = mysql.connection.cursor()
        #Kiểm tra tên nghề nghiệp đã tồn tại chưa
        cur.execute(
            'SELECT * FROM NGHENGHIEP WHERE LOWER(TenNgheNghiep) = LOWER(%s)', [TenNgheNghiep])
        result = cur.fetchone()
        if result:
            return jsonify({'EC': 1, 'EM': 'Tên nghề nghiệp đã tồn tại'}), 400
        cur.execute(
            'INSERT INTO NGHENGHIEP (TenNgheNghiep) VALUES (%s)', [TenNgheNghiep]
        )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM NGHENGHIEP WHERE TenNgheNghiep = %s', [TenNgheNghiep]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thêm nghề nghiệp thành công!', 'data':results}),200
    
    @app.route('/admin/AddNguyenNhan', methods=['POST'])
    def admin_AddNguyenNhan():
        TenNguyenNhan = request.json.get('TenNguyenNhan')
        cur = mysql.connection.cursor()
        #Kiểm tra tên nguyên nhân đã tồn tại chưa
        cur.execute(
            'SELECT * FROM NGUYENNHAN WHERE LOWER(TenNguyenNhan) = LOWER(%s)', [TenNguyenNhan])
        result = cur.fetchone()
        if result:
            return jsonify({'EC': 1, 'EM': 'Tên nguyên nhân đã tồn tại'}), 400
        cur.execute(
            'INSERT INTO NGUYENNHAN (TenNguyenNhan) VALUES (%s)', [TenNguyenNhan]
        )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM NGUYENNHAN WHERE TenNguyenNhan = %s', [TenNguyenNhan]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thêm nguyên nhân thành công!', 'data': results}),200
    
    @app.route('/admin/AddDiaDiemMaiTang', methods=['POST'])
    def admin_AddDiaDiemMaiTang():
        TenDiaDiemMaiTang = request.json.get('TenDiaDiemMaiTang')
        cur = mysql.connection.cursor()
        #Kiểm tra tên địa điểm mai táng đã tồn tại chưa
        cur.execute(
            'SELECT * FROM DIADIEMMAITANG WHERE LOWER(TenDiaDiemMaiTang) = LOWER(%s)', [TenDiaDiemMaiTang])
        result = cur.fetchone()
        if result:
            return jsonify({'EC': 1, 'EM': 'Tên địa điểm mai táng đã tồn tại'}), 400
        cur.execute(
            'INSERT INTO DIADIEMMAITANG (TenDiaDiemMaiTang) VALUES (%s)', [TenDiaDiemMaiTang]
        )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM DIADIEMMAITANG  WHERE TenDiaDiemMaiTang = %s', [TenDiaDiemMaiTang]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thêm địa điểm mai táng thành công!','data': results}),200
    
    @app.route('/admin/AddLoaiThanhTich', methods=['POST'])
    def admin_AddLoaiThanhTich():
        TenLoaiThanhTich = request.json.get('TenLoaiThanhTich')
        print(TenLoaiThanhTich)
        cur = mysql.connection.cursor()
        #Kiểm tra tên loại thành tích đã tồn tại chưa
        cur.execute(
            'SELECT * FROM LOAITHANHTICH WHERE LOWER(TenLoaiThanhTich) = LOWER(%s)', [TenLoaiThanhTich])
        result = cur.fetchone()
        if result:
            return jsonify({'EC': 1, 'EM': 'Tên loại thành tích đã tồn tại'}), 400
        cur.execute(
            'INSERT INTO LOAITHANHTICH (TenLoaiThanhTich) VALUES (%s)', [TenLoaiThanhTich]
        )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM LOAITHANHTICH WHERE TenLoaiThanhTich = %s', [TenLoaiThanhTich]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thêm loại thành tích thành công!','data':results}),200
    
#Home  
    @app.route('/admin/Home', methods=['GET'])
    def admin_Home():
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM THANHVIEN', 
        )
        results = cur.fetchall()
        data=[]
        for i,item in enumerate(results):
            #print ("=====================",i,"=====================")
            temp = {}
            temp['name'] = item['HoTen']
            #print(item['HoTen'])
            temp['id'] = item['id']
            if item['GioiTinh'] == 'Nam':
                temp['gender'] = 'male'
            else:
                temp['gender'] = 'female'
            temp['pids'] = []
            temp['fid'] =[]
            temp['mid'] = []
            cur.execute(
                'SELECT * FROM THANHVIEN WHERE id_tvc = %s and MaQuanHe=1', [item['id']]
            )
            #Tìm vợ/chồng
            partner_1 = cur.fetchall()
            #print("P1: ",partner_1 )
            if partner_1 is ():
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id = %s AND (MaQuanHe = 2 OR MaQuanHe IS NULL)', [item['id_tvc']]
                )
                partner_2 = cur.fetchall()
                #print(partner_2)
                if partner_2 is not (): 
                    temp['pids'].append(partner_2[0]['id'])   
            else:
                temp['pids'].append(partner_1[0]['id'])
            
            #Tìm cha 
            if item['MaQuanHe'] == 1:
                temp['fid'] = ''
                temp['mid'] = ''
            else:
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id = %s', [item['id_tvc']]
                )
                parent = cur.fetchall() 
                #print("Pa: ",parent)
                if parent is ():
                    temp['fid'] = ''
                else:
                    temp['fid'] = parent[0]['id']
            #Tìm mẹ
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id_tvc= %s and MaQuanHe=1', [item['id_tvc']]
                )
                parent_2 = cur.fetchall()
                #print("Ma: ",parent_2)
                if parent_2 is ():
                    temp['mid'] = ''
                else:
                    temp['mid'] = parent_2[0]['id']
            data.append(temp)
        print(data)
        return jsonify({'data':data}),200
        
    @app.route('/admin/UpdateInfor', methods=['POST']) #Sửa thông tin thành viên (admin)
    def admin_Update():
        id = request.json.get('id')
        HoTen = request.json.get('HoTen')
        GioiTinh = request.json.get('GioiTinh')
        SDT = request.json.get('SDT')
        NgayGioSinh = request.json.get('NgayGioSinh')
        MaQueQuan = request.json.get('MaQueQuan')
        MaNgheNghiep = request.json.get('MaNgheNghiep')
        CCCD = request.json.get('CCCD')
        DiaChi = request.json.get('DiaChi')
        print('id', id, 'Tên: ', HoTen, 'Giới tính:', GioiTinh, 'SDT:', SDT, 'Sinh:', NgayGioSinh, 'Quê:', MaQueQuan, 'Nghề:', MaNgheNghiep, 'CCCD:', CCCD, 'Địa chỉ:',DiaChi)
        cur = mysql.connection.cursor()
        if HoTen != '':
            cur.execute(
            'UPDATE THANHVIEN SET HoTen = %s WHERE  id= %s' , [HoTen,id]
            )
        if GioiTinh != '':
            cur.execute(
            'UPDATE THANHVIEN SET GioiTinh = %s WHERE  id= %s' , [GioiTinh,id]
            )
        if SDT != '':
            cur.execute(
            'UPDATE THANHVIEN SET SDT = %s WHERE  id= %s' , [SDT,id]
            )
        if NgayGioSinh != '':
            cur.execute(
            'UPDATE THANHVIEN SET NgayGioSinh = %s WHERE  id= %s' , [NgayGioSinh,id]
            )
        if MaQueQuan != '':
            cur.execute(
            'UPDATE THANHVIEN SET MaQueQuan = %s WHERE  id= %s' , [MaQueQuan,id]
            )
        if MaNgheNghiep != '':
            cur.execute(
            'UPDATE THANHVIEN SET MaNgheNghiep = %s WHERE id = %s', [MaNgheNghiep, id]
            )
        if CCCD != '':
            cur.execute(
            'UPDATE THANHVIEN SET CCCD = %s WHERE id = %s', [CCCD, id]
            )
        if SDT != '':
            cur.execute(
            'UPDATE THANHVIEN SET SDT = %s WHERE id = %s', [SDT, id]
            )
        if DiaChi != '':
            cur.execute(
            'UPDATE THANHVIEN SET DiaChi = %s WHERE id = %s', [DiaChi, id]
            )
        mysql.connection.commit()
        cur.execute(
            'SELECT * FROM THANHVIEN WHERE id = %s', [id]
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Update successed!', 'data':results}),200
    
    @app.route('/admin/ChangePassword', methods=['POST'])
    def admin_ChangePassword():
        id = request.json.get('id')
        password = request.json.get('password')
        newpassword = request.json.get('newpassword')
        print(id, password, newpassword)
        cur = mysql.connection.cursor()
        #Kiểm tra mật khẩu cũ
        cur.execute(
            'SELECT USERS.password, USERS.CCCD FROM USERS INNER JOIN THANHVIEN tv ON USERS.CCCD = tv.CCCD WHERE tv.id = %s', [id]
        )
        results = cur.fetchall()
        print(results)
        if results[0]['password'] != password:
            return jsonify({'EC': 1, 'EM': 'Mật khẩu cũ không đúng'}), 400
        else:
            cur.execute(
                'UPDATE USERS SET password = %s WHERE CCCD = %s', [newpassword, results[0]['CCCD']]
            )
            mysql.connection.commit()
        cur.close()
        return jsonify({'EC':0, 'EM':'Thay đổi mật khẩu thành công'}),200

    @app.route('/admin/AddMember', methods=['POST'])
    def admin_AddMember():
        id = request.json.get('id')
        HoTen = request.json.get('HoTen')
        CCCD = request.json.get('CCCD')
        GioiTinh = request.json.get('GioiTinh') 
        NgayGioSinh = request.json.get('NgayGioSinh') 
        MaQueQuan = request.json.get('MaQueQuan')
        MaNgheNghiep = request.json.get('MaNgheNghiep') 
        SDT = request.json.get('SDT') 
        DiaChi = request.json.get('DiaChi') 
        id_tvc = request.json.get('id_tvc') 
        MaQuanHe = request.json.get('MaQuanHe')
        NgayPhatSinh = request.json.get('NgayPhatSinh') 
        password = request.json.get('password')
        #Kiểm tra CCCD đã tồn tại chưa
        cur = mysql.connection.cursor()
        if len(CCCD) != 12:
            return jsonify({'EC': 2, 'EM': 'CCCD không hợp lệ'}), 400
        else:
            cur.execute(
                'SELECT * FROM USERS WHERE CCCD = %s', [CCCD]
            )
            temp= cur.fetchall()
            if temp !=():
                return jsonify({'EC': 1, 'EM': 'CCCD đã tồn tại'}), 400 #Đã tồn tại tài khoản
            else:
                #Tạo tài khoản
                cur.execute(
                    'INSERT INTO USERS (CCCD,password,role) VALUES (%s,%s,user)', [CCCD,'1234']
                )
                cur.connection.commit()
                #Lấy id tài khoản
                cur.execute(
                    'SELECT id FROM USERS WHERE CCCD = %s', [CCCD]
                )
                id_user = cur.fetchone()['id']
                #Lấy thông tin đời trước
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id = %s', [id_tvc]
                )
                temp = cur.fetchall()
                if temp is ():
                    return jsonify({'EC': 3, 'EM': 'Không tìm thấy đời trước'}), 404
                elif (temp[0]['NgayGioSinh'] < NgayGioSinh and MaQuanHe == 2): # con nhỏ hơn cha/mẹ
                    return jsonify({'EC': 4, 'EM': 'Ngày sinh không hợp lệ'}), 400
                elif (MaQuanHe == 1 and temp[0]['GioiTinh'] == GioiTinh): # Cha/Mẹ phải khác giới
                    return jsonify({'EC': 5, 'EM': 'Giới tính không hợp lệ'}), 400
                elif (MaQuanHe == 1): 
                    Doi = temp[0]['Doi']
                elif (MaQuanHe == 2):
                    Doi= temp[0]['Doi'] + 1
                #Thêm thành viên
                cur.execute(
                    'INSERT INTO THANHVIEN (HoTen,CCCD,Doi,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh,id_user) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ HoTen,CCCD,Doi,GioiTinh,NgayGioSinh,MaQueQuan,MaNgheNghiep,SDT,DiaChi,id_tvc,MaQuanHe,NgayPhatSinh,id_user]
                )
                mysql.connection.commit()
                cur.execute(
                    'SELECT * FROM THANHVIEN WHERE id = %s', [id]
                )
                results = cur.fetchall()
        return jsonify({'EC':0,'EM':'Thêm thành viên thành công!', 'data':results}),200
    
# Xóa thành tích, xóa ghi nhận kết thúc 
    @app.route('/admin/DeleteAward', methods=['POST'])
    def admin_DeleteAward():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM THANHTICH WHERE MaThanhVien = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/DeleteEnd', methods=['POST'])
    def admin_DeleteEnd():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM KETTHUC WHERE MaThanhVien = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
# Điều chỉnh các bảng phụ
    @app.route('/admin/DeleteQueQuan', methods=['POST'])
    def admin_DeleteQueQuan():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM QUEQUAN WHERE MaQueQuan = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/DeleteNgheNghiep', methods=['POST'])
    def admin_DeleteNgheNghiep():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM NGHENGHIEP WHERE MaNgheNghiep = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/DeleteNguyenNhan', methods=['POST'])
    def admin_DeleteNguyenNhan():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM NGUYENNHAN WHERE MaNguyenNhan = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/DeleteDiaDiemMaiTang', methods=['POST'])
    def admin_DeleteDiaDiemMaiTang():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM DIADIEMMAITANG WHERE MaDiaDiemMaiTang = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/DeleteLoaiThanhTich', methods=['POST'])
    def admin_DeleteLoaiThanhTich():
        id = request.json.get('id')
        cur = mysql.connection.cursor()
        cur.execute(
            'DELETE FROM LOAITHANHTICH WHERE MaLoaiThanhTich = %s', [id]
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'EC': 0, 'EM':'Xóa thành công!'}),200
    
    @app.route('/admin/BaoCaoTangGiam', methods=['POST'])
    def admin_BaoCaoTangGiam():
        start_year= request.json.get('NamBatDau')
        end_year = request.json.get('NamKetThuc')
        start_year = int(start_year)
        end_year = int(end_year)
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Year(tv.NgayGioSinh) as Nam, COUNT(*) AS SoLuongSinh FROM THANHVIEN tv WHERE Year(tv.NgayGioSinh) BETWEEN %s AND %s AND MaQuanHe=2 GROUP BY Year(tv.NgayGioSinh) ', [start_year, end_year]
        )
        Birth = cur.fetchall()
        
        cur.execute(
            'SELECT Year(NgayPhatSinh) as Nam, COUNT(*) AS SoLuongKetHon FROM THANHVIEN WHERE Year(NgayPhatSinh) BETWEEN %s AND %s AND MaQuanHe=1 GROUP BY Year(NgayPhatSinh)', [start_year, end_year]
        )
        Marriage = cur.fetchall()
        cur.execute(
            'SELECT Year(NgayPhatSinh) as Nam, COUNT(*) AS SoLuongMat FROM THANHVIEN WHERE Year(NgayPhatSinh) BETWEEN %s AND %s AND TrangThai = 1 GROUP BY Year(NgayPhatSinh)', [start_year, end_year]
        )
        Death = cur.fetchall()
        
        result = {year: {'Nam': year, 'SoLuongSinh': 0, 'SoLuongKetHon': 0, 'SoLuongMat': 0} for year in range(start_year, end_year + 1)}

        for row in Birth:
            year = row['Nam']
            if year in result:
                result[year]['SoLuongSinh'] = row['SoLuongSinh']

        for row in Marriage:
            year = row['Nam']
            if year in result:
                result[year]['SoLuongKetHon'] = row['SoLuongKetHon']

        for row in Death:
            year = row['Nam']
            if year in result:
                result[year]['SoLuongMat'] = row['SoLuongMat']
            # Chuyển kết quả từ dictionary sang list
        final_result = list(result.values())

        return jsonify({'EC': 0, 'EM': 'Success', 'data': final_result}), 200
    
    @app.route('/admin/BaoCaoThanhTich', methods=['POST'])
    def admin_BaoCaoThanhTich():
        start_year= request.json.get('NamBatDau')
        end_year = request.json.get('NamKetThuc')
        
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT tt.MaLoaiThanhTich, ltt.TenLoaiThanhTich, COUNT(*) AS SoLuongThanhTich FROM THANHTICH tt INNER JOIN LOAITHANHTICH ltt ON tt.MaLoaiThanhTich = ltt.MaLoaiThanhTich WHERE Year(tt.NgayPhatSinh) BETWEEN %s AND %s GROUP BY tt.MaLoaiThanhTich', [start_year, end_year] 
        )
        results = cur.fetchall()
        cur.close()
        return jsonify({'EC':0, 'EM':'Success', 'data': results}),200