# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash
from word import create_cloud
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = "安全なシークレットキー"  # これをアプリケーションに適したセキュアなシークレットキーに変更してください
# アプリケーションのセッションの設定
app.config["SESSION_TYPE"] = "filesystem"


executor = ThreadPoolExecutor(2)  # 適切なスレッド数を選択


@app.route("/trigger_wordcloud", methods=["POST"])
def trigger_wordcloud():
    try:
        # POST リクエストからデータを取得
        data = request.json

        # WordCloud生成を非同期で行う
        future = executor.submit(create_cloud, data)

        # 画像パスをセッションに保存
        session["image_path"] = future.result()

        # 成功時のレスポンス
        return {
            "status": "success",
            "message": "WordCloud generation started successfully",
        }

    except Exception as e:
        # エラーが発生した場合のレスポンス
        return {"status": "error", "message": str(e)}


@app.route("/generate_wordcloud")
def generate_wordcloud():
    try:
        data = ["テキストデータ1", "テキストデータ2", "テキストデータ3"]
        image_path = create_cloud(data)

        # 画像パスをセッションに保存
        session["image_path"] = image_path

        # デバッグ用：セッションの内容を表示
        print(session)

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
    image_path = session.get("image_path")

    # 画像パスが存在しない場合のエラーハンドリング
    if image_path is None:
        return "Error: No image path in session"

    # 画像パスをテンプレートに渡す
    return render_template("result.html", image_path=image_path)


if __name__ == "__main__":
    app.run(debug=True)
