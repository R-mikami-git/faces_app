from app import app, db                 # app.py から必要なものをインポート
from tables import User,Attendance      # table.py からデータベースをインポート
from models import *                    # models.py　からモデルをインポート
from utils import *                     # utils.py からユーティリティ関数をインポート
from camera import *                    # camera.py からカメラと顔認証のクラスをインポート
from scipy.special import softmax
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from flask import  request, render_template, Response
from collections import Counter


#アプリ起動時
@app.route('/')
def index():
    model.load_model()
    return render_template('index.html')

#カメラ起動
@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#送信ボタン押下
@app.route('/recordFace', methods=['POST'])
def recordFace():

    #javaで作った変数を受け取る
    data = request.get_json()
    Class = data.get("class")
    Number = data.get("studentNumber")
    Name = data.get("name").replace("　", "").replace(" ","").replace("＿", "").replace("_", "")

    if not Class.isalnum():
        return "ERROR: クラス名が無効です"

    try:
        # 新しい画像をリストに保存する
        new_faces_list = camera.capture_unique_photos()

        if len(new_faces_list) > 0:
            
            # ユーザー登録処理（データベース操作）
            stmt = select(User).filter_by(class_number=Class, number=Number)
            existing_user = db.session.execute(stmt).scalar_one_or_none()

            if existing_user:
                return f"{existing_user.name}さんはすでに登録されています"

            try:
                # ユーザーの登録
                user = User(class_number=Class, number=Number, name=Name, label_number=None)  # 初期値として label_number=None
                db.session.add(user)

                y_train = joblib.load(model.Y_train_path)
                
                unique_classes = np.unique(y_train)
                num_classes = len(unique_classes) 
                print("現在モデルのラベル数",num_classes)

                # 新しい画像でモデルを訓練
                label = num_classes
                new_labels = [label] * len(new_faces_list)
                model.new_data_retrain(new_faces_list, new_labels)
                
                print("訓練に成功しました")

                #モデルのテスト
                model.test_model_data()

                # label_number を更新
                user.label_number = num_classes  # 配列番号をラベル番号として設定
                db.session.commit()  # 変更を保存
                return f"{user.name}さんを登録しました"
            
            except Exception as e:
                db.session.rollback()
                return f"ERROR: データベース処理中にエラーが発生しました: {str(e)}"

        return "ERROR: 顔認証に失敗しました"

    except Exception as e:
        return f"ERROR: 処理中にエラーが発生しました: {str(e)}"
    
#出席ボタン
@app.route('/attendance', methods=['POST'])
def recordAttendance():

    now = datetime.now()
    today = now.date()

    try:
        new_faces_list = camera.capture_unique_photos()
        print("リスト化に成功しました")

        if model.clf is None:
            return "ERROR: 顔認識モデルが正しく初期化されていません"

        label_list = []
        confidence_list = []

        for resize_face in new_faces_list:

            # 顔認証でクラスラベルを取得
            resize_face_hog = model.extract_hog_features(resize_face)

            # スコアを取得し、確率に変換
            scores = model.clf.decision_function([resize_face_hog])  # スコアを取得
            confidence = softmax(scores, axis=1)  # ソフトマックスで確率に変換
            confidence_list.append(confidence.max())

            # 最も高い確率のクラスを取得
            label = int(confidence.argmax(axis=1)[0])  # 確率が最大のクラスを取得
            label_list.append(label)

        if min(confidence_list) >= camera.confidence_date:
            return "ERROR: 顔認証の信頼度が不足しています"

        # データベースからユーザー情報を取得
        with Session(db.engine) as session:
            try:
                counter = Counter(label_list)
                most_common_element, count = counter.most_common(1)[0]

                probability = count / len(label_list)
                print("{:.2%}".format(probability))
 
                # ユーザー情報を取得 (label_numberを基準に検索)
                stmt = select(User).filter_by(label_number=most_common_element)
                user = session.execute(stmt).scalar_one_or_none()

                if user is None:
                    return f"ERROR: label_number={label+1} に対応するユーザーが見つかりませんでした"

                # 出席記録を確認 (user_idと今日の日付を基準に検索)
                stmt = select(Attendance).filter_by(user_id=user.id, check_day=today)
                existing_attendance = session.execute(stmt).scalar_one_or_none()

                # 出席していて、退席２がある
                if existing_attendance is not None and existing_attendance.check_out_time_2 is not None:
                   return f"{user.name}さんは、二度以上退席しています"

                # 出席していて、退席がある
                elif existing_attendance is not None and existing_attendance.check_out_time is not None:
                    # 出席２に、新しい退席記録を追加
                    existing_attendance.check_in_time_2 = now
                    existing_attendance.status = "出席"

                # 出席していて、退席がない
                elif existing_attendance is not None and existing_attendance.check_out_time is None:
                    # 出席１に、新しい退席記録を追加
                    existing_attendance.check_in_time = now
                    existing_attendance.status = "出席"
                            
                else:
                    attendance = Attendance(user_id=user.id, check_day=today, check_in_time=now, status='出席')
                    session.add(attendance)

                # 変更を保存
                session.commit()
                return f"{user.name}さん、おはようございます"
            
            except Exception as e:
                session.rollback()
                return f"ERROR: データベースの更新中にエラーが発生しました: {str(e)}"

    except ValueError as ve:
        return f"ERROR: 値のエラーが発生しました: {str(ve)}"
    except Exception as e:
        return f"ERROR: 処理中に予期せぬエラーが発生しました: {str(e)}"

#退席ボタン押下
@app.route('/recordAway', methods=['POST'])
def recordAway():
    #カメラ設定

    now = datetime.now()
    today = now.date() 

    try:
        new_faces_list = camera.capture_unique_photos()
        print("リスト化に成功しました")

        if model.clf is None:
            return "ERROR: 顔認識モデルが正しく初期化されていません"
        
        #ラベルと信頼率を出す
        label_list,confidence_list = create_label_confidence_list(new_faces_list)

        if min(confidence_list) >= camera.confidence_date:
            return "ERROR: 顔認証の信頼度が不足しています"

        # データベースからユーザー情報を取得
        with Session(db.engine) as session:

            try:
                counter = Counter(label_list)
                most_common_element, count = counter.most_common(1)[0]

                probability = count / len(label_list)
                print("{:.2%}".format(probability))

                # ユーザー情報を取得 (label_numberを基準に検索)
                stmt = select(User).filter_by(label_number=most_common_element)
                user = session.execute(stmt).scalar_one_or_none()

                if user is None:
                    return "ERROR: ユーザーが見つかりませんでした"

                # 出席記録を確認
                stmt = select(Attendance).filter_by(user_id=user.id, check_day=today)
                existing_attendance = session.execute(stmt).scalar_one_or_none()

                # 出席２に記録があって、退席２に記録がある場合
                if existing_attendance.check_in_time_2 is not None and existing_attendance.check_out_time_2 is not None:
                    # 退席１に、新しい退席記録を追加
                    existing_attendance.check_out_time_2 = now
                    existing_attendance.status = "退席"
            
                # 出席２に記録があって、退席２に記録がない場合
                elif existing_attendance.check_in_time_2 is not None and existing_attendance.check_out_time_2 is None:
                    # 退席１に、新しい退席記録を追加
                    existing_attendance.check_out_time_2 = now
                    existing_attendance.status = "退席"
            
                # 出席していて、退席１の記録がある場合
                elif existing_attendance and existing_attendance.check_out_time is not None:
                    # 退席１に、新しい退席記録を追加
                    existing_attendance.check_out_time = now
                    existing_attendance.status = "退席"

                # 出席していて、退席１の記録がない場合
                elif existing_attendance and existing_attendance.check_out_time is None:
                    # 退席１に、新しい退席記録を追加
                    existing_attendance.check_out_time = now
                    existing_attendance.status = "退席"
            
                else:
                    return f"{user.name}さんの出席記録がありません"

                # 変更を保存
                session.commit()
                return f"{user.name}さん、おつかれさまでした"
            
            except Exception as e:
                session.rollback()
                return f"ERROR: データベースの更新中にエラーが発生しました: {str(e)}"

    except ValueError as ve:
        return f"ERROR: 値のエラーが発生しました: {str(ve)}"
    except Exception as e:
        return f"ERROR: 処理中に予期せぬエラーが発生しました: {str(e)}"
    
#設定ボタン押下、ログインページ読み込み
@app.route('/login', methods=["GET"])
def login():
    return render_template('login.html')




