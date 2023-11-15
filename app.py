# app.py
from flask import Flask, render_template, request, session, redirect, url_for
from word import create_cloud

app = Flask(__name__)
app.secret_key = "安全なシークレットキー"  # これをアプリケーションに適したセキュアなシークレットキーに変更してください


# データを取得するエンドポイントを作成
@app.route("/generate_wordcloud")
def generate_wordcloud():
    # ここでGoogle Apps Scriptからデータを取得する処理を追加
    # 例: Google Sheets APIを使用してデータを取得する
    # 仮のデータを生成
    data = ["テキストデータ1", "テキストデータ2", "テキストデータ3"]
    image_path = create_cloud(data)

    # 画像パスをセッションに保存
    session["image_path"] = image_path

    # ワードクラウド生成後にresult.htmlを表示
    return redirect(url_for("result"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result/")
def result():
    # セッションから画像パスを取得
    image_path = session.pop("image_path", None)

    # 画像パスをテンプレートに渡す
    return render_template("result.html", image_path=image_path)


if __name__ == "__main__":
    app.run()
