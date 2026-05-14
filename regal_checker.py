import os
import json
from groq import Groq
from config import GROQ_API_KEY, KNOWLEDGE_FOLDER, CUSTOM_RULES_FILE

# Groqクライアントを作成
client = Groq(api_key=GROQ_API_KEY)

# knowledge_baseフォルダから全Markdownファイルを読み込む関数
def load_all_knowledge():
    knowledge_text = ""
    folder_path = os.path.join(os.path.dirname(__file__), KNOWLEDGE_FOLDER)
    
    if not os.path.exists(folder_path):
        return "知識フォルダが見つかりません。"
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    knowledge_text += f"\n--- {filename} ---\n{content}\n"
            except Exception as e:
                knowledge_text += f"\n--- {filename} の読み込みに失敗 ---\n"
    
    return knowledge_text.strip()

# 知識を起動時に1回だけ読み込む（メモリに保持）
ALL_KNOWLEDGE = load_all_knowledge()

# custom_rules.json を読み込む関数
def load_custom_rules():
    try:
        file_path = os.path.join(os.path.dirname(__file__), CUSTOM_RULES_FILE)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rules", [])
    except:
        return []

ALL_CUSTOM_RULES = load_custom_rules()

# REGAL簡易チェックの本体関数
def regal_check(message_text: str):
    """
    送信されたメッセージを不動産特化でチェックします。
    戻り値: (is_ok: bool, result_message: str)
    """
    try:
        # まずカスタムルールで簡易チェック
        for rule in ALL_CUSTOM_RULES:
            if rule["keyword"] in message_text:
                return False, f"⚠️ {rule['message']}\n（根拠: {rule['law']}）"

        # Groqに全知識を渡して賢くチェック
        system_prompt = f"""
あなたは不動産事業に特化した「REGAL（リーガル簡易チェック）システム」です。
以下の不動産知識を厳密に守って、ユーザーのメッセージをチェックしてください。

【不動産知識データベース】
{ALL_KNOWLEDGE}

【チェックのルール】
- 宅建士などの資格が必要な表現は「必須」と明記されているか確認
- 宅建業法32条（誇大広告禁止）に違反する表現（根拠のない「最高」「抜群」など）は警告
- 重要事項説明は宅建士限定
- 税金・建築・契約の説明は根拠必須
- NGなら具体的な修正案も出す

ユーザーのメッセージ: {message_text}

結果は以下の形式で**必ず**返してください：
OKかどうか: （OK or NG）
理由: （簡潔に）
修正案: （必要なら）
"""

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Groqで高速・安価なモデル
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_text}
            ],
            temperature=0.3,
            max_tokens=600
        )

        result = response.choices[0].message.content.strip()

        # 結果を解析してOK/NG判定
        if "OKかどうか: OK" in result or "OK" in result[:100]:
            return True, f"✅ REGALチェック通過！\n\n{result}"
        else:
            return False, f"⚠️ REGALチェックで問題が見つかりました\n\n{result}"

    except Exception as e:
        # エラーが起きてもアプリが止まらないように
        return False, f"❌ チェック中にエラーが発生しました: {str(e)}\n\n管理者に連絡してください。"

# テスト用（ファイルを実行したときに動く）
if __name__ == "__main__":
    test_text = "駅徒歩3分以内で日当たり良好です。重要事項説明します。"
    ok, msg = regal_check(test_text)
    print(msg)