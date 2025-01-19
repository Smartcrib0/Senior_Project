import pyaudio
import wave
from flask import Flask, jsonify, send_file

# إعدادات تسجيل الصوت
FORMAT = pyaudio.paInt16  # صيغة الصوت (16 بت)
CHANNELS = 1             # قناة واحدة (Mono)
RATE = 44100             # معدل أخذ العينات (44.1 kHz)
CHUNK = 1024             # حجم كل حزمة بيانات
RECORD_SECONDS = 5       # مدة التسجيل بالثواني
OUTPUT_FILENAME = "output.wav"  # اسم ملف الصوت الناتج

# تطبيق Flask
app = Flask(__name__)

def record_audio():
    """تسجيل الصوت وحفظه في ملف WAV"""
    audio = pyaudio.PyAudio()

    # فتح قناة تسجيل
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished!")

    # إنهاء التسجيل
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # حفظ الصوت في ملف
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

@app.route('/record', methods=['GET'])
def record():
    """تسجيل الصوت عند الطلب"""
    try:
        record_audio()
        return jsonify({"message": "Recording successful!", "file": OUTPUT_FILENAME}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio', methods=['GET'])
def get_audio():
    """إرجاع ملف الصوت كاستجابة"""
    try:
        return send_file(OUTPUT_FILENAME, mimetype="audio/wav", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
