import librosa
import numpy as np

def load_audio(file):
    y, sr = librosa.load(file, sr=16000)
    return y, sr

def normalize_audio(y):
    return librosa.util.normalize(y)