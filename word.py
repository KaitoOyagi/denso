# word.py

import requests
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
import random
from collections import Counter
import boto3
from botocore.exceptions import NoCredentialsError
from flask import redirect, url_for


matplotlib.use("Agg")


def create_cloud(data):
    # Google Apps ScriptのWebアプリケーションのURLを指定
    web_app_url = "https://script.google.com/macros/s/AKfycbyGI_JTsJ_-Lo4tdmWSi3iXbw3CrxUvq2cKPZnGxHIbpKD_xZA5gNYxWuYA3iZHD9gjxQ/exec"

    # GETリクエストを送信してJSONデータを取得
    response = requests.get(web_app_url)

    # 応答をJSON形式として読み込む
    if response.status_code == 200:
        # JSONデータを取得
        values = response.json()

        # valuesからテキストデータを抽出
        text_data = ""
        for row in values:
            text_data += " ".join(row) + "\n"  # 各セルのテキストをスペース区切りで結合し、改行で区切る

        # テキストデータをトークナイズ
        t = Tokenizer()
        tokens = t.tokenize(text_data)

        word_list = []
        # 単語の出現回数をカウント
        word_count = Counter()

        for token in tokens:
            word = token.surface
            partOfSpeech = token.part_of_speech.split(",")[0]
            partOfSpeech2 = token.part_of_speech.split(",")[1]

            if partOfSpeech in ["名詞", "動詞", "形容詞", "形容動詞"]:
                if partOfSpeech != "記号":
                    if (
                        (partOfSpeech2 != "非自立")
                        and (partOfSpeech2 != "代名詞")
                        and (partOfSpeech2 != "数")
                    ):
                        word_list.append(word)
                        word_count[word] += 1  # 単語の出現回数をカウント

        # 単語の出現回数が1回のものを削除
        word_list = [word for word in word_list if word_count[word] > 1]

        words = " ".join(word_list)
        print(words)
        stop_words = [
            "デンソー",
            "ある",
            "有る",
            "高い",
            "問う",
            "含む",
            "同様な",
            "幅広い",
            "重んずる",
            "クルマ",
            "「",
            "」",
            "思います",
            "です",
            "ます",
            "できる",
            "こと",
            "、",
            "・",
            "/",
            "／",
            '"',
            "！",
            "こと",
            "し",
            "あり",
            "する",
            "(",
            ")",
        ]
        fpath = "./姫明朝しらゆきmini.otf"

        def random_color(
            word, font_size, position, orientation, font_path, random_state
        ):
            return f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"

        wordcloud = WordCloud(
            font_path=fpath,  # フォントを指定しない
            width=900,
            height=600,
            background_color="white",
            stopwords=set(stop_words),
            max_words=30,
            min_font_size=4,
            collocations=False,
            color_func=random_color,
        ).generate(words)

        # ファイルに保存
        local_output_image_path = "./static/image/wordcloud.png"
        wordcloud.to_file(local_output_image_path)

        # S3に画像をアップロード
        s3_bucket_name = "wordcloud--bucket"  # Replace with your S3 bucket name
        s3_object_key = "result/wordcloud.png"  # Specify the S3 object key after upload
        try:
            upload_to_s3(local_output_image_path, s3_bucket_name, s3_object_key)

            # S3上の画像のURLを返す
            s3_image_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_object_key}"
            print(f"S3 Image URL: {s3_image_url}")  # 追加: S3上の画像のURLをログに出力
            return s3_image_url

        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")  # 追加: S3へのアップロード時のエラーをログに出力
            raise e


def upload_to_s3(local_file, bucket, s3_key, content_type="image/png"):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id="AKIARCEU2H6H42THUXEV",
            aws_secret_access_key="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",
        )

        # ExtraArgs パラメータを使用してメタデータを指定
        extra_args = {
            "ContentType": content_type,
        }

        s3.upload_file(local_file, bucket, s3_key, ExtraArgs=extra_args)
        print("Upload Successful")

    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")


# ファイルをアップロードする際に ContentType を指定
upload_to_s3(
    local_file="./static/image/wordcloud.png",
    bucket="wordcloud--bucket",
    s3_key="result/wordcloud.png",
)
