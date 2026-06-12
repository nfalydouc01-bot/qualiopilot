import fitz  # pymupdf
import pytesseract
from PIL import Image
import os

# Chemin vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extraire_texte(chemin_fichier):
    extension = os.path.splitext(chemin_fichier)[1].lower()

    if extension == ".pdf":
        texte = ""
        doc = fitz.open(chemin_fichier)
        for page in doc:
            texte += page.get_text()
        return texte

    elif extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        image = Image.open(chemin_fichier)
        texte = pytesseract.image_to_string(image, lang="fra")
        return texte

    else:
        return "Format non supporté : " + extension


# Test rapide
if __name__ == "__main__":
    chemin = input("Entre le chemin d'un fichier (PDF ou image) : ")
    resultat = extraire_texte(chemin)
    print("\n--- TEXTE EXTRAIT ---")
    print(resultat)