import os
import joblib
import numpy as np
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from skimage.feature import hog
from skimage.transform import resize


class FaceRecognitionModel:

    clf = None
    test_accuracy = None
    models_path = None
    X_train_hog_path = None
    Y_train_path = None
    
    def __init__(self):
        self.clf = None
        self.test_accuracy = None
        self.models_path = os.path.join("models", "face_recognition_model.pkl")
        self.X_train_hog_path = os.path.join("models", "X_train_hog.pkl")
        self.Y_train_path = os.path.join("models", "y_train.pkl")

    # HOG特徴量を抽出
    def extract_hog_features(self,image):
        features = hog(image, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), transform_sqrt=True, block_norm="L2-Hys")
        return features

    #モデルの作成と保存
    def create_models(self):
        
        lfw_people = fetch_lfw_people(min_faces_per_person=70, resize=0.4)
        lfw_people.images = [resize(img, (128, 128)) for img in lfw_people.images]
        faces = lfw_people.images
        labels = lfw_people.target

        # トレーニングデータとテストデータに分割
        X_train, X_test, y_train, y_test = train_test_split(
            faces, labels, test_size=0.2, random_state=0
        )

        # 特徴量抽出
        X_train_hog = np.array([self.extract_hog_features(img) for img in X_train])
        X_test_hog = np.array([self.extract_hog_features(img) for img in X_test])

        # モデル作成と学習
        self.clf = SGDClassifier(loss="hinge", penalty="l2")
        self.clf.fit(X_train_hog, y_train)

        # 精度計算
        y_test_pred = self.clf.predict(X_test_hog)
        self.test_accuracy = accuracy_score(y_test, y_test_pred)
        print(f"テストデータに対する精度: {self.test_accuracy}")

        joblib.dump(self.clf, self.models_path)
        joblib.dump(X_train_hog, self.X_train_hog_path)
        joblib.dump(y_train, self.Y_train_path)
        print("モデルが保存されました")

    #保存されたモデルをロード
    def load_model(self):

        if not os.path.exists(self.models_path):  # モデルファイルが存在するか確認
            print("モデルファイルが存在しません。")
            return
        self.clf = joblib.load(self.models_path)
        print("モデルがロードされました")

    #新しいデータを追加しモデルを再学習
    def new_data_retrain(self, new_faces_list, new_labels):  # ラベルを引数で指定  

        if not new_faces_list or not new_labels:  # データとラベルが提供されているか確認
            print("新しいデータとラベルを提供してください。")
            return

        # 特徴量抽出
        new_faces_hog = np.array([self.extract_hog_features(img) for img in new_faces_list])
        
        X_train_hog = joblib.load(self.X_train_hog_path)
        y_train = joblib.load(self.Y_train_path)
        
        # 新しいデータの統合
        X_train_combined = np.concatenate([X_train_hog, new_faces_hog])  
        y_train_combined = np.concatenate([y_train, new_labels])

        # モデルの再学習
        self.clf.fit(X_train_combined, y_train_combined)
        joblib.dump(self.clf, self.models_path)               # モデルを保存
        joblib.dump(X_train_combined, self.X_train_hog_path)  # 統合データを保存
        joblib.dump(y_train_combined, self.Y_train_path)      # 統合ラベルを保存

        print("モデルが再度保存されました")

    # テストデータ生成と評価を行うメソッド
    def test_model_data(self):
        if self.clf is None:
            print("モデルがロードされていません。まず 'load_model()' を呼び出してください")
            return
    
        # テストデータ生成（コードで作成）
        lfw_people = fetch_lfw_people(min_faces_per_person=70, resize=0.4)
        lfw_people.images = [resize(img, (128, 128)) for img in lfw_people.images]
        faces = lfw_people.images
        labels = lfw_people.target

        # テスト用データを作成
        _, X_test, _, y_test = train_test_split(faces, labels, test_size=0.2, random_state=0)

        # 特徴量抽出
        X_test_hog = np.array([self.extract_hog_features(img) for img in X_test])

        # 予測実行
        y_test_pred = self.clf.predict(X_test_hog)

        # 精度計算
        accuracy = accuracy_score(y_test, y_test_pred)
        print(f"生成されたテストデータでのモデル精度: {accuracy}")

    

model = FaceRecognitionModel()
model.load_model()