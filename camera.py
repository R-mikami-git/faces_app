import cv2
import time
from utils import *

#アプリケーションのカメラや顔検出を管理するクラス
class AppContext:
    
    shared_frame = None
    face_cascade = None
    camera = None
    confidence_date = None

    def __init__(self):

        self.shared_frame = None
        self.camera = cv2.VideoCapture(0)
        self.confidence_date = 60
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        if not self.camera.isOpened():
            raise RuntimeError("カメラがオープンできませんでした")
        
    #カメラからフレームを取得し、HTTPストリーム形式で返す
    def generate_frames(self):
        while True:

            #frameをnumpy配列で保存
            success, frame = self.camera.read()
            if not success:
                break

            resized_frame = cv2.resize(frame, (400, 300))
            self.shared_frame = resized_frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
    
    #フレームをグレースケール化する
    def create_gray_frame(self):
        if self.shared_frame is None:
            raise ValueError("ERROR: カメラからフレームを取得できませんでした")
        
        gray_frame = cv2.cvtColor(self.shared_frame, cv2.COLOR_BGR2GRAY)
        return gray_frame
    
    #グレーフレームを顔認証して、真ん中にある顔を受け取る
    def create_resize_face(self, gray_frame):

        try:
            # 顔認証を行う
            faces = self.face_cascade.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            # 顔が検出されているか確認
            if len(faces) > 0:

                # 中心に最も近い顔を選択するためのロジック
                frame_center_x = gray_frame.shape[1] // 2  # フレームの中心 X座標
                frame_center_y = gray_frame.shape[0] // 2  # フレームの中心 Y座標

                # 中心からの距離を計算
                distances = [
                    ((x + w // 2 - frame_center_x) ** 2  + 
                     (y + h // 2 - frame_center_y) ** 2, (x, y, w, h))
                    for (x, y, w, h) in faces
                ]
        
                # 最も中心に近い顔を選択
                _, (x, y, w, h) = min(distances, key=lambda d: d[0])

                # 顔部分を抽出しリサイズ
                face = gray_frame[y:y + h, x:x + w]
                resize_face = cv2.resize(face, (128, 128))

                # 保存処理（例として画像ファイルに保存）
        
                return resize_face
            else:
                return f"顔が検出されませんでした: {str(e)}"

        except cv2.error as e:
            return f"OpenCVエラーが発生しました: {str(e)}"
        except Exception as e:
            return f"予期しないエラーが発生しました: {str(e)}"
        
    
        
    #顔画像をリサイズして返す
    def create_resize_img(self, gray_frame,faces):

        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            img = gray_frame[y:y + h, x:x + w]
            resized_img = cv2.resize(img, (128, 128))

            return resized_img
        return None

    # ユニークな写真を撮影して保存
    def capture_unique_photos(self, duration=3, threshold=0.7):

        start_time = time.time()
        new_faces_list = []
        previous_frame = None

        while time.time() - start_time < duration:

            # グレースケール化と顔検出
            gray_frame = camera.create_gray_frame()
            resize_faces = camera.create_resize_face(gray_frame)

            if previous_frame is not None:

                similarity = calculate_feature_similarity(previous_frame, resize_faces)

                if similarity <= threshold:
                    new_faces_list.append(resize_faces)
                    
            previous_frame = resize_faces
            
        print(f"{len(new_faces_list)}枚を保存しました")

        return new_faces_list
    
#メソッド化
camera = AppContext() 