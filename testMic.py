import sounddevice as sd
import wave
import socket

# إعدادات الصوت
SAMPLE_RATE = 44100  # عدد العينات في الثانية
DURATION = 6  # مدة التسجيل بالثواني
FILENAME = "recording.wav"  # اسم ملف التسجيل

# تسجيل الصوت وحفظه كملف
def record_audio(filename, duration, sample_rate):
    print("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # انتظار انتهاء التسجيل
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    print("Recording saved:", filename)

# إرسال الملف عبر الشبكة
def send_file(filename, server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))
        with open(filename, "rb") as file:
            client_socket.sendall(file.read())
    print("File sent to server:", server_ip)

if __name__ == "__main__":
    record_audio(FILENAME, DURATION, SAMPLE_RATE)
    send_file(FILENAME, "192.168.173.235", 5000)  # استبدل 5000 بالمنفذ المستخدم على اللابتوب
