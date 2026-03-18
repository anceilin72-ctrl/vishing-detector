import librosa
import numpy as np

def extract_features(y, sr):
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfcc = mfcc.mean(axis=1)

    spec = librosa.feature.melspectrogram(y=y, sr=sr)
    spec = spec.mean(axis=1)

    return np.hstack((mfcc, spec))