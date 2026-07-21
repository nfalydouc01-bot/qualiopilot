from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from extractor import extraire_texte
from analyzer import analyser_texte
from rapport import generer_rapport, sauvegarder_rapport
from database import get_session, Document, Texte, Analyse, initialiser_base

app = FastAPI(title="Qualiopilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
    chemin_fichier = os.path.join(UPLOAD_DIR, fichier.filename)
    with open(chemin_fichier, "wb") as f:
        shutil.copyfileobj(fichier.file, f)

    texte = extraire_texte(chemin_fichier)
    if not texte or texte.strip() == "":
        return JSONResponse(status_code=400, content={"erreur": "Impossible d'extraire le texte."})

    resultat_analyse = analyser_texte(texte)
    rapport = generer_rapport(fichier.filename, resultat_analyse)

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
