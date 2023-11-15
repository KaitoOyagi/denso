# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash
from word import create_cloud

app = Flask(__name__)
app.secret_key = "安全なシークレットキー"  # これをアプリケーションに適したセキュアなシークレットキーに変更してください


# データを取得するエンドポイントを作成
@app.route("/generate_wordcloud")
def generate_wordcloud():
    try:
        data = ["テキストデータ1", "テキストデータ2", "テキストデータ3"]
        image_path = create_cloud(data)

        # 画像パスをセッションに保存
        session["image_path"] = image_path

        # エラーハンドリングが成功した場合はそのままリダイレクト
        return redirect(url_for("result"))
    except Exception as e:
        # エラーが発生した場合はエラーメッセージをフラッシュ
        flash(f"ワードクラウドの生成中にエラーが発生しました: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result/")
def result():
    # セッションから画像パスを取得
    image_path = session.pop("image_path")

    # 画像パスをテンプレートに渡す
    return render_template("result.html")


if __name__ == "__main__":
    app.run(debug=True)
