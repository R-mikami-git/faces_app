from app import app, db                 # app.py から必要なものをインポート
from tables import User,Attendance      # table.py からデータベースをインポート
from models import *                    # models.py　からモデルをインポート
from utils import *                     # utils.py からユーティリティ関数をインポート
from camera import *                    # camera.py からカメラと顔認証のクラスをインポート
from sqlalchemy import select
from flask import  request, jsonify


#ログインボタン
@app.route('/login', methods=['POST'])
def user_login():
    # リクエストデータを取得
    data = request.get_json()
    username = data.get("username", "").replace("　", "").replace(" ", "").replace("＿", "").replace("_", "").strip()
    password = data.get("password", "").strip()

    try:
        # データベースでクエリを実行して名前でユーザーを確認
        stmt = select(User).filter_by(name=username)
        existing_user = db.session.execute(stmt).scalar_one_or_none()
        
        # デバッグログ
        print("確認されたユーザー:", existing_user)
        print("入力されたパスワード:", password)
        
        if existing_user:
            if password == "000000":
                return jsonify({"success": True, "message": "ログイン成功"}), 200
            else:
                return jsonify({"success": False, "message": "パスワードが間違っています"}), 401
        else:
            return jsonify({"success": False, "message": "ユーザーが存在しません"}), 404

    except Exception as e:
        # エラー発生時の詳細をログに記録
        import traceback
        print("エラー詳細:", traceback.format_exc())
        return jsonify({"error": "サーバーエラーが発生しました", "details": str(e)}), 500
