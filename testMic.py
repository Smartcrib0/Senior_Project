from flask import Flask, request, jsonify, send_file
import sounddevice as sd
import numpy as np
import wave
import os

app = Flask(__name__)

# إعداد المسار المؤقت لحفظ تسجيل الصوت
TEMP_AUDIO_FILE = "temp_audio.wav"

def record_audio(duration, filename):
    try:
        # تسجيل الصوت باستخدام sounddevice
        fs = 22050  # معدل العينة (هرتز)
        print("Recording audio...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # الانتظار حتى ينتهي التسجيل
        print("Recording finished.")

        # حفظ التسجيل كملف WAV
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # قناة واحدة (أحادي)
            wf.setsampwidth(2)  # حجم العينة 2 بايت (16 بت)
            wf.setframerate(fs)
            wf.writeframes(audio.tobytes())
        return True
    except Exception as e:
        print(f"خطأ أثناء تسجيل الصوت: {e}")
        return False

@app.route('/record', methods=['POST'])
def record():
    try:
        # الحصول على مدة التسجيل من الطلب
        data = request.get_json()
        duration = data.get("duration", 6)  # الافتراضي: 6 ثوانٍ

        # تسجيل الصوت
        if record_audio(duration, TEMP_AUDIO_FILE):
            return send_file(TEMP_AUDIO_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Failed to record audio"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # حذف الملف المؤقت بعد إرساله
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
