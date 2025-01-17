import sounddevice as sd
import wavio

# دالة لتسجيل الصوت وإرساله إلى السيرفر
def record_and_send_audio():
    duration = 6  # مدة التسجيل بالثواني
    sample_rate = 44100
    channels = 2
    filename = "recorded_audio.wav"

    # تسجيل الصوت
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, sample_rate, sampwidth=2)

    # إرسال الصوت إلى السيرفر
    with open(filename, 'rb') as audio_file:
        files = {'file': audio_file}
        response = requests.post("http://<server_ip>:5000/process_audio", files=files)
        print("Audio response:", response.json())

# في دالة إرسال الفيديو، بناءً على استجابة السيرفر:
def send_frame_to_server(frame):
    _, encoded_frame = cv2.imencode('.jpg', frame)
    response = requests.post(SERVER_URL, files={'frame': encoded_frame.tobytes()})
    server_response = response.json()
    print("Server response:", server_response)

    # إذا اكتشف الطفل، قم بتسجيل الصوت
    if server_response.get("detected"):
        record_and_send_audio()
