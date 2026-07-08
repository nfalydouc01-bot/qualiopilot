from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # <-- Ajout de l'import pour le CORS
import shutil
import os
from extractor import extraire_texte
from analyzer import analyser_texte
from rapport import generer_rapport, sauvegarder_rapport
from database import get_session, Document, Texte, Analyse, initialiser_base

app = FastAPI(title="Qualiopilot API")

# --- CONFIGURATION DU CORS ---
# Permet au Front-End React de communiquer avec cette API FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (POST, GET, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes
)

# Dossier temporaire pour stocker les fichiers uploadés
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup():
    initialiser_base()

@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API Qualiopilot"}

@app.post("/upload")
async def upload_document(fichier: UploadFile = File(...)):
    # Sauvegarder le fichier uploadé
    chemin_fichier = os.path.join(UPLOAD_DIR, fichier.filename)
    with open(chemin_fichier, "wb") as f:
        shutil.copyfileobj(fichier.file, f)

    # Étape 1 : Extraire le texte
    texte = extraire_texte(chemin_fichier)
    if not texte or texte.strip() == "":
        return JSONResponse(status_code=400, content={"erreur": "Impossible d'extraire le texte."})

    # Étape 2 : Analyser avec l'IA
    resultat_analyse = analyser_texte(texte)

    # Étape 3 : Générer le rapport
    rapport = generer_rapport(fichier.filename, resultat_analyse)

    # Étape 4 : Sauvegarder dans la base de données
    session = get_session()
    document = Document(
        nom_fichier=fichier.filename,
        type_fichier=os.path.splitext(fichier.filename)[1],
        chemin=chemin_fichier
    )
    session.add(document)
    session.commit()

    texte_db = Texte(document_id=document.id, contenu=texte)
    session.add(texte_db)

    analyse_db = Analyse(document_id=document.id, resultat=str(resultat_analyse))
    session.add(analyse_db)
    session.commit()
    session.close()

    return {
        "fichier": fichier.filename,
        "analyse": resultat_analyse,
        "rapport": rapport
    }
