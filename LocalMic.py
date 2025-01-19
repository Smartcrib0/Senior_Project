import pyaudio
import wave
from flask import Flask, request, jsonify

app = Flask(__name__)

# إعدادات تسجيل الصوت
FORMAT = pyaudio.paInt16  # صيغة الصوت (16 بت)
CHANNELS = 1             # قناة واحدة (Mono)
RATE = 44100             # معدل أخذ العينات (44.1 kHz)
CHUNK = 1024             # حجم كل حزمة بيانات
RECORD_SECONDS = 6       # مدة التسجيل بالثواني
OUTPUT_FILENAME = "output.wav"  # اسم ملف الصوت الناتج

# دالة لتسجيل الصوت
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    # تسجيل الصوت
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

    return OUTPUT_FILENAME

# نقطة النهاية لتسجيل الصوت
@app.route('/record', methods=['GET'])
def record():
    try:
        # تسجيل الصوت
        file_path = record_audio()
        return jsonify({"message": "Recording successful!", "file": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# نقطة النهاية لتحميل ملف الصوت
@app.route('/get_audio', methods=['GET'])
def get_audio():
    try:
        # قراءة ملف الصوت
        with open(OUTPUT_FILENAME, 'rb') as f:
            audio_data = f.read()
        return (audio_data, 200, {
            'Content-Type': 'audio/wav',
            'Content-Disposition': f'attachment; filename={OUTPUT_FILENAME}'
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
