"""
Utility buat load model EfficientNet-B0 dan menjalankan prediksi.
Model di-load sekali aja (lazy singleton) biar ga reload tiap ada request,
soalnya load .h5 itu berat/lambat kalau dilakukan berulang.
"""

import os
import numpy as np
from django.conf import settings

# Urutan HARUS sama persis dengan class_indices yang di-print pas training di Colab:
# {'bekantan': 0, 'orangutan_kalimantan': 1, 'orangutan_sumatra': 2}
CLASS_NAMES = ['bekantan', 'orangutan_kalimantan', 'orangutan_sumatra']

MODEL_FILENAME = 'primate_classifier_efficientnetb0.h5'
IMG_SIZE = (224, 224)

_model = None  # cache model supaya cuma di-load sekali per proses server


def get_model():
    global _model
    if _model is None:
        from tensorflow.keras.models import load_model
        model_path = os.path.join(settings.ML_MODEL_DIR, MODEL_FILENAME)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model tidak ditemukan di {model_path}. "
                f"Pastikan file '{MODEL_FILENAME}' hasil training Colab "
                f"sudah dipindah ke classifier/ml_model/"
            )
        _model = load_model(model_path)
    return _model


def predict_image(file_obj):
    """
    file_obj: file-like object berisi gambar (JPG/PNG).
    Return: list of (label, confidence) tuple, diurutkan dari confidence
            tertinggi ke terendah.
    """
    from tensorflow.keras.applications.efficientnet import preprocess_input
    from tensorflow.keras.preprocessing import image as keras_image
    from PIL import Image

    img = Image.open(file_obj).convert('RGB').resize(IMG_SIZE)
    arr = keras_image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)

    model = get_model()
    preds = model.predict(arr, verbose=0)[0]

    results = list(zip(CLASS_NAMES, (float(p) for p in preds)))
    results.sort(key=lambda pair: pair[1], reverse=True)
    return results
