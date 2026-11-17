"""Compara preprocesamientos OCR sin modificar las imágenes originales."""

from __future__ import annotations

import json
import re
import time
import argparse
from pathlib import Path

import cv2
import easyocr
import numpy as np


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "results"

IMAGES = {
    "ejcorreo": ROOT / "data" / "ejcorreo.png",
    "ejwpp": ROOT / "data" / "ejwpp.jpg",
}

# Transcripción manual de lo que es legible en las imágenes de prueba.
GROUND_TRUTH = {
    "ejcorreo": (
        "Welcome to Email Tracking Via web form Agent Internal 1 minute ago Assign "
        "Email reading has been tracked by Email Tracking app Email was read 7 seconds "
        "after it was sent Sent on 13:05:49 9 January 2024 Europe/Kyiv Read on 13:05:56 "
        "9 January 2024 Europe/Kyiv Email body Welcome to Email Tracking If you have any "
        "questions or need any assistance please do not hesitate to contact our customer "
        "support team at contact@growthdot.com We are here to help you"
    ),
    "ejwpp": (
        "Abuela en línea 22 DE AGOSTO DE 2014 Elias cual es mi contraseña de facebook "
        "23:10 Abuela no tienes facebook 23:10 Ok 23:10"
    ),
}

IMPORTANT_TERMS = {
    "ejcorreo": ["contact@growthdot.com", "Email Tracking", "Europe/Kyiv"],
    "ejwpp": ["contraseña", "facebook", "Abuela"],
}


def normalize(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^\w@./:+]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def metrics(reference: str, hypothesis: str) -> dict[str, float]:
    reference_normalized = normalize(reference)
    hypothesis_normalized = normalize(hypothesis)
    reference_words = reference_normalized.split()
    hypothesis_words = hypothesis_normalized.split()
    return {
        "cer": round(edit_distance(reference_normalized, hypothesis_normalized) / max(1, len(reference_normalized)), 4),
        "wer": round(edit_distance(reference_words, hypothesis_words) / max(1, len(reference_words)), 4),
    }


def preprocess(image: np.ndarray) -> dict[str, np.ndarray]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    upscaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(upscaled)
    _, otsu = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(upscaled, None, h=10, templateWindowSize=7, searchWindowSize=21)
    _, denoised_otsu = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return {
        "original": image,
        "grayscale": gray,
        "upscale_2x": upscaled,
        "upscale_clahe": clahe,
        "upscale_otsu": otsu,
        "upscale_denoise_otsu": denoised_otsu,
    }


def run(
    image_names: list[str] | None = None,
    variant_names: list[str] | None = None,
    output_name: str = "ocr_evaluation.json",
) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reader = easyocr.Reader(["es", "en"], gpu=False, verbose=False)
    payload: dict[str, object] = {
        "engine": "EasyOCR",
        "languages": ["es", "en"],
        "gpu": False,
        "images": {},
    }

    selected_images = image_names or list(IMAGES)
    for image_name in selected_images:
        image_path = IMAGES[image_name]
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(image_path)
        image_result: dict[str, object] = {
            "path": str(image_path.relative_to(ROOT)).replace("\\", "/"),
            "shape": list(image.shape),
            "ground_truth": GROUND_TRUTH[image_name],
            "variants": {},
        }
        variants = preprocess(image)
        selected_variants = variant_names or list(variants)
        for variant_name in selected_variants:
            variant = variants[variant_name]
            started = time.perf_counter()
            detections = reader.readtext(variant, detail=1, paragraph=False)
            elapsed = time.perf_counter() - started
            text = "\n".join(item[1] for item in detections)
            scores = [float(item[2]) for item in detections]
            result = {
                "text": text,
                "regions": len(detections),
                "mean_confidence": round(float(np.mean(scores)), 4) if scores else None,
                "min_confidence": round(float(np.min(scores)), 4) if scores else None,
                "elapsed_seconds": round(elapsed, 3),
                **metrics(GROUND_TRUTH[image_name], text),
                "important_terms": {
                    term: normalize(term) in normalize(text)
                    for term in IMPORTANT_TERMS[image_name]
                },
            }
            image_result["variants"][variant_name] = result
            preview_path = OUTPUT_DIR / f"{image_name}_{variant_name}.png"
            cv2.imwrite(str(preview_path), variant)
            print(
                f"{image_name}/{variant_name}: CER={result['cer']:.4f}, "
                f"WER={result['wer']:.4f}, regiones={result['regions']}"
            , flush=True)
        payload["images"][image_name] = image_result

    output = OUTPUT_DIR / output_name
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resultado: {output}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default=",".join(IMAGES))
    parser.add_argument("--variants", default="original,grayscale,upscale_2x,upscale_clahe,upscale_otsu,upscale_denoise_otsu")
    parser.add_argument("--output", default="ocr_evaluation.json")
    arguments = parser.parse_args()
    run(arguments.images.split(","), arguments.variants.split(","), arguments.output)
