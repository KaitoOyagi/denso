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

matplotlib.use("Agg")


def create_cloud(data):
    # valuesからテキストデータを抽出
    text_data = " ".join(data)

    # テキストデータから「・」を削除
    text_data = text_data.replace("・", "")

    # テキストデータをトークナイズ
    custom_dict_path = "./dictionary.csv"
    t = Tokenizer(udic=custom_dict_path, udic_type="simpledic", udic_enc="utf8")
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
    # word_list = [word for word in word_list if word_count[word] > 1]

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
        "ない",
        "し",
        "あり",
        "する",
        "(",
        ")",
        "出来る",
        "的",
        "仕事",
        "高い",
        "高さ",
        "あ",
        "い",
        "う",
        "え",
        "お",
        "か",
        "き",
        "く",
        "け",
        "こ",
        "さ",
        "し",
        "す",
        "せ",
        "そ",
        "た",
        "ち",
        "つ",
        "て",
        "と",
        "な",
        "に",
        "ぬ",
        "ね",
        "の",
        "は",
        "ひ",
        "ふ",
        "へ",
        "ほ",
        "ま",
        "み",
        "む",
        "め",
        "も",
        "や",
        "ゆ",
        "よ",
        "ら",
        "り",
        "る",
        "れ",
        "ろ",
        "わ",
        "を",
        "ん",
    ]
    fpath = "./DENSOSansTP2017-Bold.woff"

    color_palette = [
        "#8246AF",
        "#F08CAF",
        "#DC0032",
        "#FAB932",
        "#1E9146",
        "#0091BE",
    ]

    def custom_color(word, font_size, position, orientation, font_path, random_state):
        return random.choice(color_palette)

    wordcloud = WordCloud(
        font_path=fpath,  # フォントを指定しない
        width=900,
        height=600,
        background_color="white",
        stopwords=set(stop_words),
        max_words=50,
        min_font_size=4,
        collocations=False,
        color_func=custom_color,
    ).generate(words)

    # ファイルに保存
    local_output_image_path = "./static/image/wordcloud.png"
    wordcloud.to_file(local_output_image_path)

    # S3に画像をアップロード
    s3_bucket_name = "denso-wordcloud"  # Replace with your S3 bucket name
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
            aws_access_key_id="AKIAYQDI7YN5UK3HF6UW",
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
