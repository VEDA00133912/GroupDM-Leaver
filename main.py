import discord
import threading
import io
import contextlib
from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)
client = None
client_thread = None
latest_result = {}
log_buffer = io.StringIO()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} is Online!")
        try:
            group_dms = [dm for dm in self.private_channels if isinstance(dm, discord.GroupChannel)]
            left_count = 0
            for dm in group_dms:
                await dm.leave()
                left_count += 1

            latest_result["success"] = True
            latest_result["left_count"] = left_count

            if left_count == 0:
                print("グループDMが見つかりませんでした")
            else:
                print(f"{left_count}件のグループDMから退出しました")
        except Exception as e:
            latest_result.update({"success": False, "error": str(e), "left_count": 0})
            print("退出中にエラーが発生しました:", e)

def run_discord(token):
    global client
    try:
        client = MyClient(self_bot=True, chunk_guilds_at_startup=False)
        client.run(token)
    except Exception as e:
        latest_result.update({"success": False, "error": str(e), "left_count": 0})
        print("ログインに失敗しました:", e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_bot():
    global client_thread, latest_result, log_buffer

    token = request.form["token"]
    latest_result.clear()
    log_buffer = io.StringIO()

    if client_thread and client_thread.is_alive():
        return jsonify({"success": False, "log": "現在実行中です"})

    with contextlib.redirect_stdout(log_buffer):
        client_thread = threading.Thread(target=run_discord, args=(token,))
        client_thread.start()

        for _ in range(10):
            if "success" in latest_result:
                break
            time.sleep(0.5)

    return jsonify({
        "success": latest_result.get("success", False),
        "left_count": latest_result.get("left_count", 0),
        "log": log_buffer.getvalue()
    })

if __name__ == "__main__":
    app.run(debug=True)