import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from regal_checker import regal_check

app = Flask(__name__)

# LINE Bot APIの設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/webhook", methods=['POST'])
def webhook():
    """LINEからWebhookを受け取る場所"""
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ユーザーがテキストメッセージを送ってきたときの処理"""
    user_message = event.message.text.strip()

    # REGALチェックを実行
    is_ok, check_result = regal_check(user_message)

    # チェック結果をユーザーに返す
    reply_text = f"📨 あなたが送ろうとしたメッセージ:\n{user_message}\n\n{check_result}"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# アプリを起動する部分
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)