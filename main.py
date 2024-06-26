import sounddevice as sd
import numpy as np
import soundfile as sf
import os
import noisereduce as nr

import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk
from keras.models import load_model
import librosa

def record_audio():
    global recording, is_recording
    fs = 44100 
    duration = 3

    if not is_recording:
        is_recording = True
        recording_button.config(text='Stop Recording')
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float64')
        sd.wait()
        recording = nr.reduce_noise(y=recording[:, 0], sr=fs)
        is_recording = False
        recording_button.config(text='Start Recording')
        print("Recording finished. Noise reduced.")
    else:
        sd.stop()
        is_recording = False
        recording_button.config(text='Start Recording')


def save_audio():
    directory = 'Audios/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "test_sound.wav"
    file_path = os.path.join(directory, filename)
    
    print(f"Saving recording to {file_path}...")
    sf.write(file_path, recording, 44100)
    print("Recording saved.")

def play_audio():
    global recording
    if recording is None:
        if os.path.exists('Audios/test_sound.wav'):
            print("Playing audio...")
            recording, fs = sf.read('Audios/test_sound.wav')
            sd.play(recording, samplerate=44100)
            sd.wait()
            print("Playback finished.")
    else:
        print("Playing audio...")
        sd.play(recording, samplerate=44100)
        sd.wait()
        print("Playback finished.")

def predict_emotion():
    
    model = load_model('Models\emotion_detection_TESS_LSTM_1.keras')

    def extract_mfcc(filename):
        y, sr = librosa.load(filename, duration=3, offset=0.5)
        mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        return mfcc

    def predict(file):
        # TESS: 'angry', 'disgust', 'fear', 'happy', 'neutral', 'ps', 'sad'
        result_map = ['angry', 'disgust', 'fearful', 'happy', 'neutral', 'surprised', 'sad']

        # Mixed: 'angry', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised'
        # result_map = ['angry', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        
        mfcc = extract_mfcc(file)
        mfcc = np.expand_dims(mfcc, -1)
        y = model.predict(np.array([mfcc]))
        y = np.argmax(y, axis=1)[0]
        return result_map[y]
    
    
    # filepath = 'Audios/test_sound.wav'
    for file in os.listdir('Audios/'):
        if file.endswith('.wav'):
            filepath = f'Audios/{file}'
            break
    print(f"Predicting emotion for {filepath}...")
    emotion = predict(filepath)
    print(f"Predicted emotion: {emotion}")
    image_path = f"Images/{emotion}.png" 
    img = Image.open(image_path)
    img = img.resize((100, 100)) 
    img_photo = ImageTk.PhotoImage(img)
    image_label.config(image=img_photo)
    image_label.image = img_photo
    image_label.pack()
    return emotion

root = tk.Tk()
root.title("Emotion Predictor")
root.geometry('800x600')

recording = None
is_recording = False

recording_button = tk.Button(root, text='Start Recording', command=record_audio)
recording_button.pack(pady=20)

save_button = tk.Button(root, text='Save Recording', command=save_audio)
save_button.pack(pady=20)

play_button = tk.Button(root, text='Play Recording', command=play_audio)
play_button.pack(pady=20)

predict_button = tk.Button(root, text='Predict Emotion', command=predict_emotion)
predict_button.pack(pady=20)

image_label = Label(root)  
image_label.pack(pady=20) 

root.mainloop()
