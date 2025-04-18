from db_config import db  # app.py から db をインポート

# ユーザー情報設定
class User(db.Model):
    __tablename__ = "ユーザー情報"  # テーブル名
    __table_args__ = {"schema": "public"}  # スキーマ指定

    id = db.Column(db.Integer, primary_key=True, name="ユーザーcd")  # 主キー
    class_number = db.Column(db.String(50), nullable=False, name="クラス")
    number = db.Column(db.Integer, nullable=False, name="出席番号") 
    name = db.Column(db.String(100), nullable=False, name="名前") 
    label_number = db.Column(db.Integer, nullable=True, name="予測番号") 

    # 出席記録とのリレーション
    attendances = db.relationship(
        "Attendance", 
        lazy=True, 
        cascade="all, delete-orphan",
        primaryjoin="User.id == foreign(Attendance.user_id)"  # 外部キーの関係を明示
    )

# 出席記録設定
class Attendance(db.Model):
    __tablename__ = "出席記録"  # テーブル名
    __table_args__ = {"schema": "public"}  # スキーマ指定

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, name="出席cd")  # 主キー
    user_id = db.Column(db.Integer,nullable=False,name="ユーザーcd") # 外部キー

    check_day = db.Column(db.DateTime, nullable=False, name="日付") 
    check_in_time = db.Column(db.DateTime, nullable=False, name="出席時間") 
    check_out_time = db.Column(db.DateTime, nullable=True, name="退席時間") 
    check_in_time_2 = db.Column(db.DateTime, nullable=True, name="出席時間2") 
    check_out_time_2 = db.Column(db.DateTime, nullable=True, name="退席時間2") 
    status = db.Column(db.String(50), nullable=False, name="ステータス") 

