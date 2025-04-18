from flask import Flask
from db_config import db


app = Flask(__name__)
DATABASE_URI = "postgresql://postgres:gododb4600@localhost:5432/flask_app"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


from tables import *                            # テーブルをインポート
from utils import *                             # 関数をインポート
from routes.index import *                      # ルートをインポート
from routes.login import *                      # ルートをインポート
from routes.setting import *                    # ルートをインポート

if __name__ == '__main__':
    with app.app_context():
        create_database()  # データベース作成
        try:
            db.create_all()  # テーブル作成
            print("テーブルが正常に作成されました")
        except Exception as e:
            print(f"テーブル作成エラー: {e}")

        app.run(debug=True)
        