import cv2
from models import *
from skimage.feature import hog
import psycopg2
from psycopg2 import sql
from scipy.special import softmax


#画像間のORB特徴量による類似度を計算
def calculate_feature_similarity(image1, image2):
    orb = cv2.ORB_create()
    
    key1, desc1 = orb.detectAndCompute(image1, None)
    key2, desc2 = orb.detectAndCompute(image2, None)

    if desc1 is None or desc2 is None:
        return 

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc1, desc2)
    return len(matches) / max(len(key1), len(key2))


# 画像からHOG特徴量を抽出
def extract_hog_features(image):
    return hog(image, orientations=9, pixels_per_cell=(8, 8),
               cells_per_block=(2, 2), transform_sqrt=True, block_norm="L2-Hys")

def create_label_confidence_list(new_faces_list):
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
    
    return label_list,confidence_list

# データベースとテーブルがない場合、新しくそれらを作成する
def create_database():
    conn = psycopg2.connect("postgresql://postgres:gododb4600@localhost:5432/postgres")
    conn.autocommit = True
    cursor = conn.cursor()
    db_name = "flask_app"
    cursor.execute("SELECT datname FROM pg_database WHERE datname = %s", (db_name,))
    if not cursor.fetchone():
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"データベース '{db_name}' が作成されました！")
    else:
        print(f"データベース '{db_name}' はすでに存在しています。")