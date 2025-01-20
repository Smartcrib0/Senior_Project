from flask import Flask, request, jsonify
import sounddevice as sd
import wavio
import threading
import os

app = Flask(__name__)

# إعداد المتغيرات
AUDIO_DIR = "recordings"  # مجلد حفظ التسجيلات
os.makedirs(AUDIO_DIR, exist_ok=True)

# تسجيل الصوت بشكل غير متزامن
def record_audio(filename, duration=6):
    sample_rate = 44100
    channels = 2
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, sample_rate, sampwidth=2)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    try:
        duration = int(request.json.get("duration", 6))  # المدة الافتراضية 6 ثواني
        filename = os.path.join(AUDIO_DIR, "detected_audio.wav")

        # تشغيل التسجيل في خيط منفصل
        threading.Thread(target=record_audio, args=(filename, duration), daemon=True).start()
        return jsonify({"status": "success", "message": "Recording started."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
