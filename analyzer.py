import os
import anthropic
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

def analyser_texte(texte):
    if not texte or texte.strip() == "":
        return {"erreur": "Texte vide, impossible d'analyser."}

    prompt = f"""
Tu es un expert en certification Qualiopi pour les organismes de formation.
Analyse le texte suivant et fais une synthèse COURTE et CLAIRE, facile à lire rapidement.

Consignes strictes :
- Maximum 3 preuves de conformité (les plus importantes seulement)
- Maximum 3 éléments manquants (les plus importants seulement)
- Un commentaire de 2 phrases maximum, simple et direct
- Pas de jargon technique inutile, du langage clair

Réponds UNIQUEMENT en JSON avec ce format, rien d'autre :
{{
    "preuves_trouvees": ["preuve1", "preuve2", "preuve3"],
    "elements_manquants": ["element1", "element2", "element3"],
    "score_conformite": 75,
    "commentaire": "phrase courte et claire"
}}

Texte à analyser :
{texte[:3000]}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        texte_brut = message.content[0].text.strip()
        if texte_brut.startswith("```"):
            texte_brut = texte_brut.split("```")[1]
            if texte_brut.startswith("json"):
                texte_brut = texte_brut[4:]
            texte_brut = texte_brut.strip()
        resultat = json.loads(texte_brut)
    except Exception:
        resultat = {"reponse_brute": message.content[0].text}

    return resultat
