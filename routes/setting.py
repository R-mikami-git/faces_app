from app import app, db                 # app.py から必要なものをインポート
from tables import User,Attendance      # table.py からデータベースをインポート
from models import *                    # models.py　からモデルをインポート
from utils import *                     # utils.py からユーティリティ関数をインポート
from camera import *                    # camera.py からカメラと顔認証のクラスをインポート
from datetime import date, time
from sqlalchemy import and_
from flask import  request, render_template, jsonify


#設定画面
@app.route('/setting', methods=["GET"])
def show_setting_table():
     # JOINクエリを実行
    result = db.session.query(
        User.id,
        User.class_number,
        User.number,
        User.name,
        Attendance.check_day,
        Attendance.check_in_time,
        Attendance.check_out_time,
        Attendance.check_in_time_2,
        Attendance.check_out_time_2,
        Attendance.status,
    ).join(
        Attendance, User.id == Attendance.user_id
    ).all()

    # 結果を表示用に整形
    setting_data = [
        {
            "ユーザーcd": row[0],
            "クラス": row[1],
            "出席番号": row[2],
            "名前": row[3],
            "日付": row[4].strftime("%Y-%m-%d") if isinstance(row[4], date) else row[4],
            "出席時間": row[5].strftime("%H:%M:%S") if isinstance(row[5], time) else row[5],
            "退席時間": row[6].strftime("%H:%M:%S") if isinstance(row[6], time) else row[6],
            "出席時間": row[7].strftime("%H:%M:%S") if isinstance(row[7], time) else row[7],
            "退席時間": row[8].strftime("%H:%M:%S") if isinstance(row[8], time) else row[8],
            "ステータス": row[9].strip()  # スペースを削除
        }
        for row in result
    ]
    # HTMLテンプレートにデータを渡す
    return render_template('setting.html', data = setting_data)

#送信ボタン
@app.route('/data_transmission', methods=['POST'])
def data_transmission():
    try:
        # クライアントから受け取ったデータを取得
        data = request.get_json()
        print("受信データ:", data)

        # 受信データから変数を抽出
        Class = data.get("class")
        Name = data.get("name").replace("　", "").replace(" ", "").replace("＿", "").replace("_", "")
        Check_day = data.get("checkDay")

        # クエリ条件の作成
        conditions = []
        if Class:
            conditions.append(User.class_number == Class)
        if Name:
            conditions.append(User.name == Name)
        if Check_day:
            conditions.append(Attendance.check_day == Check_day)

        # データベースクエリの実行
        result_query = db.session.query(
            User.id,
            User.class_number,
            User.number,
            User.name,
            Attendance.check_day,
            Attendance.check_in_time,
            Attendance.check_out_time,
            Attendance.check_in_time_2,
            Attendance.check_out_time_2,
            Attendance.status,
        ).join(
            Attendance, User.id == Attendance.user_id
        )

        if conditions:
            result = result_query.filter(and_(*conditions)).all()
        else:
            print("検索結果が見つかりませんでした。")
            result = []

        if not result:
            # データが見つからなかった場合のログ出力や処理
            return jsonify([])  # 空のリストを返す

            # クエリ結果を整形
        setting_data = [
            {
                "ユーザーcd": row[0],
                "クラス": row[1],
                "出席番号": row[2],
                "名前": row[3],
                "日付": row[4].strftime("%Y-%m-%d") if isinstance(row[4], date) else row[4],
                "出席時間": row[5].strftime("%H:%M:%S") if isinstance(row[5], time) else row[5],
                "退席時間": row[6].strftime("%H:%M:%S") if isinstance(row[6], time) else row[6],
                "出席時間": row[7].strftime("%H:%M:%S") if isinstance(row[7], time) else row[7],
                "退席時間": row[8].strftime("%H:%M:%S") if isinstance(row[8], time) else row[8],
                "ステータス": row[9].strip()  # スペースを削除
            }
            for row in result
        ]   

        # 整形されたデータをレスポンスとして返却
        return jsonify(setting_data), 200

    except Exception as e:
        import traceback
        print("エラー詳細:", traceback.format_exc())
        return jsonify({"error": f"サーバーエラー: {str(e)}"}), 500
    
#更新ボタン
@app.route('/update_confidence', methods=['POST'])
def update_confidence():

    try:
        # クライアントから受け取ったデータを取得
        data = request.get_json()
        print("受信データ:", data)

        # 受信データから変数を抽出し、数値型に変換
        confidence = data.get("confidence")
        if confidence is None:
            return jsonify({"message": "ERROR: 信頼度が提供されていません"}), 400
        try:
            confidence = int(confidence)  # 数値型に変換
        except ValueError:
            return jsonify({"message": "ERROR: 信頼度は数値でなければなりません"}), 400

        #global変数を更新
        camera.confidence_date = confidence

        # 成功レスポンスを返却
        return jsonify({"message": "更新しました", "confidence_date": data}), 200

    except Exception as e:
        # エラー処理
        print(f"エラー: {e}")
        return jsonify({"error": "サーバー内部でエラーが発生しました"}), 500

#初期化ボタン
@app.route('/clear_confidenc', methods=['POST'])
def clear_confidenc():#

    #global変数を初期値(60)に変更
    camera.confidence_date = 60

    # 成功レスポンスを返却
    return jsonify({"message": "初期化しました"}), 200
