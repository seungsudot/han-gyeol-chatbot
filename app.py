from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import threading
import requests
import os

app = Flask(__name__)
CORS(app)  # 카카오·UptimeRobot 등 외부 요청 허용

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# GET /chat 요청 처리 (헬스체크용)
@app.route("/chat", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200


# 백그라운드에서 카카오로 GPT 결과 전송
def send_to_kakao(user_id, text):
    try:
        headers = {
            "Authorization": f"KakaoAK {os.environ['KAKAO_ADMIN_KEY']}",
            "Content-Type": "application/json"
        }

        data = {
            "receiver_uuids": [user_id],  # userRequest.user.id 값 사용
            "template_object": {
                "object_type": "text",
                "text": text,
                "link": {
                    "web_url": "https://han-gyeol-chatbot.onrender.com"
                }
            }
        }

        r = requests.post(
            "https://kapi.kakao.com/v1/api/talk/friends/message/default/send",
            headers=headers,
            json=data,
            timeout=5
        )

        print("📤 Kakao send result:", r.status_code, r.text)
    except Exception as e:
        print("❌ Kakao send error:", e)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        kakao_request = request.get_json()
        user_message = kakao_request["userRequest"]["utterance"]  # 카카오 메시지
        user_id = kakao_request["userRequest"]["user"]["id"]
    except Exception as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400

    # ✅ 카카오에 즉시 응답 (5초 내)
    quick_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": "아 잠만 생각중"}}
            ]
        }
    }

    # ✅ GPT 백그라운드 처리 (타임아웃 방지)
    def process_gpt():
        try:
            completion = client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:seungsu:2025-2:CUoDuCEI",
                messages=[
                    {"role": "system", "content": "You are 한결, a friendly Korean friend. 말투는 친구랑 대화하듯 자연스럽게 해줘."},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=150
            )
            gpt_reply = completion.choices[0].message.content.strip()
            send_to_kakao(user_id, gpt_reply)
        except Exception as e:
            print("❌ GPT error:", e)
            send_to_kakao(user_id, "오류났네ㅋㅋㅋ")

    threading.Thread(target=process_gpt).start()
    return jsonify(quick_response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
