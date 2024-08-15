import gradio as gr
from transformers import pipeline
import pdfkit

from jinja2 import Environment, FileSystemLoader
import pdfkit
from transformers import pipeline

# Configuration de l'environnement Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('cv_software.html')

# Charger le modèle de question-réponse
qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")


# Fonction pour extraire les réponses à partir du texte source
def extract_info(question, context):
    return qa_pipeline(question=question, context=context)["answer"]


# Fonction principale pour traiter le texte et retourner les informations extraites
def extract_cv_info(text_source):
    data = {
        "name": extract_info("What is the full name?", text_source),
        "email": extract_info("What is the email address?", text_source),
        "phone": extract_info("What is the phone number?", text_source),
        "address": extract_info("What is the address?", text_source),
        "profile": extract_info("What is the professional profile?", text_source),
        "experiences": [
            {
                "title": extract_info("What is the title of the first job?", text_source),
                "company": extract_info("What is the name of the first company?", text_source),
                "start_date": extract_info("When did the first job start?", text_source),
                "end_date": extract_info("When did the first job end?", text_source),
                "description": extract_info("What was the description of the first job?", text_source)
            },
            {
                "title": extract_info("What is the title of the second job?", text_source),
                "company": extract_info("What is the name of the second company?", text_source),
                "start_date": extract_info("When did the second job start?", text_source),
                "end_date": extract_info("When did the second job end?", text_source),
                "description": extract_info("What was the description of the second job?", text_source)
            }
        ],
        "projects": [
            {
                "title": extract_info("What is the title of the first project?", text_source),
                "tech": extract_info("What technologies were used in the first project?", text_source),
                "description": extract_info("What is the description of the first project?", text_source),
                "details": extract_info("What were the main details of the first project?", text_source).split('.')
            },
            {
                "title": extract_info("What is the title of the second project?", text_source),
                "tech": extract_info("What technologies were used in the second project?", text_source),
                "description": extract_info("What is the description of the second project?", text_source),
                "details": extract_info("What were the main details of the second project?", text_source).split('.')
            }
        ],
        "skills": extract_info("What are your key skills?", text_source).split(', '),
        "education": [
            {
                "degree": extract_info("What is the highest degree?", text_source),
                "institution": extract_info("Which university is associated with the highest degree?", text_source),
                "start_date": extract_info("When did the highest degree start?", text_source),
                "end_date": extract_info("When did the highest degree end?", text_source)
            }
        ]
    }

    # Sauvegarder le PDF
    pdf_file = "cv_" + data["name"] + ".pdf"
    # Rendu du template avec les données
    html_out = template.render(data)

    # Génération du PDF à partir du HTML rendu
    pdfkit.from_string(html_out, pdf_file)

    return pdf_file


# Créer l'interface Gradio
def gradio_interface(text_source):
    pdf_file = extract_cv_info(text_source)
    return pdf_file


# Interface avec un champ texte pour entrer le texte source et un bouton pour télécharger le PDF
interface = gr.Interface(
    fn=gradio_interface,
    inputs="textbox",
    outputs=gr.File(label="Download PDF"),
    title="CV Information Extractor",
    description="Enter a text describing a CV and extract key information into a downloadable PDF.",
)

# Lancer l'interface
interface.launch()
