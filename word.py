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
        "こと",
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
    s3_object_key = "result/wordcloud.png"  # フォルダを含むキー

    api_gateway_endpoint = (
        "https://7uf9jiyfpf.execute-api.ap-northeast-1.amazonaws.com/wordcloud"
    )

    headers = {"x-custom-auth": "true"}

    with open(local_output_image_path, "rb") as file:
        files = {"file": (s3_object_key, file, "image/png")}  # s3_object_key を使用する
        response = requests.post(api_gateway_endpoint, files=files, headers=headers)

    if response.status_code == 200:
        s3_image_url = response.json().get("s3_image_url")
        print(f"S3 Image URL: {s3_image_url}")
        return s3_image_url
    else:
        print(f"Error uploading to S3 via API Gateway: {response.text}")
        raise Exception("S3 upload via API Gateway failed")
