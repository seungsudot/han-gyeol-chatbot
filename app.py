from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route("/chat", methods=["POST"])
def chat():
    try:
        kakao_request = request.get_json()
        user_message = kakao_request['userRequest']['utterance']  # 카카오 메시지
    except Exception as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400

    # GPT 모델 호출
    try:
        completion = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:승수-한결-2025_2",
            messages=[
                {"role": "system", "content": "You are 한결, a friendly Korean friend. 말투는 따뜻하고 자연스럽게 해줘."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        gpt_reply = completion.choices[0].message.content.strip()
    except Exception as e:
        gpt_reply = "지금은 서버가 잠시 바쁜가봐. 잠시 후에 다시 물어봐줘!"

    # 카카오 오픈빌더 응답 포맷
    response_body = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": gpt_reply
                    }
                }
            ]
        }
    }

    return jsonify(response_body)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
