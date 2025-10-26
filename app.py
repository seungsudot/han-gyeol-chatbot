from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)  #카카오·UptimeRobot 등 외부 요청 허용
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# GET /chat 요청 처리 (헬스체크용)
@app.route("/chat", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200



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
            model="ft:gpt-4o-mini-2024-07-18:seungsu:2025-2:CUoDuCEI",
            messages=[
                {"role": "system", "content": "You are 한결, a friendly Korean friend. 말투는 친구랑 대화하듯 자연스럽게 해줘."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
            max_tokens=150,   # 응답 길이 제한 → 속도 향상
            timeout=4         # 4초 내 응답 제한 (카카오 타임아웃 방지)
        )
        gpt_reply = completion.choices[0].message.content.strip()
    except Exception as e:
        gpt_reply = "승수가 서버비 안내서 에러났다. ㅅㅂ 돈 좀 줘라"

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




