#khởi động mtr
venv\Scripts\activate
Chạy dô file requirements.txt để copy trước nha, phòng hờ

#dùng lênh sau để tạo txt file chứa các thư viện cần cài đặt
```
pip freeze > requirements.txt  /// check thử coi trong ẻm có nội dung chưa
```
#dùng lệnh sau để cài đặt các thư viện trong file requirements.txt
```
pip install -r requirements.txt
```
#dùng lệnh sau để chạy chương trình
```
flask run --debug
```