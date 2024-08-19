import gradio as gr
from jinja2 import Environment, FileSystemLoader
import pdfkit
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from datetime import datetime

# Configuration de l'environnement Jinja2
env = Environment(loader=FileSystemLoader('.'))
template_cv = env.get_template('cv_software.html')
template_letter_cover = env.get_template('cv_letter_cover.html')

# Modèle et template pour les questions
template_cv_qa = """Context: {context}

Question: {question}

Answer: reponds en francais à la question en maximum 3 mots et en utilisant le context sans ajouter des informations. Et ne construit pas forcement des phrases."""

prompt_cv = ChatPromptTemplate.from_template(template_cv_qa)
model = OllamaLLM(model="mistral")


# Fonction pour extraire les informations
def extract_info(question, context):
    chain = prompt_cv | model
    return chain.invoke({"question": question, "context": context}).strip()


# Fonction principale pour extraire les informations du CV
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

    # Sauvegarder le PDF du CV
    pdf_file = "cv_" + data["name"] + ".pdf"
    # Rendu du template avec les données
    html_out = template_cv.render(data)

    # Génération du PDF à partir du HTML rendu
    pdfkit.from_string(html_out, pdf_file)

    return pdf_file


# Fonction principale pour générer la lettre de motivation
def generate_cover_letter(text_source, job_offer):
    candidate_details = {
        "name": extract_info("What is the candidate's name?", text_source),
        "address": extract_info("What is the candidate's address?", text_source),
        "email": extract_info("What is the candidate's email?", text_source),
        "phone": extract_info("What is the candidate's phone number?", text_source),
        "current_date": datetime.now().strftime("%d %B %Y")
    }

    company_details = {
        "company_name": extract_info("What is the company's name?", job_offer),
        "company_address": extract_info("What is the company's address?", job_offer),
        "company_city": extract_info("Where is the company's location?", job_offer),
        "job_title": extract_info("What is the job title?", job_offer)
    }

    # Générer la lettre de motivation
    template_letter = """Candidate Information: {candidate_info}

    Job Offer: {job_offer}

    Write a cover letter in French, aligning the candidate's skills and experiences with the job offer requirements. Met des sauts de ligne quand c'est nécessaire "\n"
    """

    prompt_letter = ChatPromptTemplate.from_template(template_letter)
    chain_letter = prompt_letter | model

    cover_letter = chain_letter.invoke({"candidate_info": text_source, "job_offer": job_offer}).strip()

    # Fusionner les informations dans le template HTML
    html_content = template_letter_cover.render(
        name=candidate_details["name"],
        address=candidate_details["address"],
        email=candidate_details["email"],
        phone=candidate_details["phone"],
        company_name=company_details["company_name"],
        company_address=company_details["company_address"],
        company_city=company_details["company_city"],
        current_date=candidate_details["current_date"],
        job_title=company_details["job_title"],
        body=cover_letter
    )

    # Enregistrer le contenu HTML en tant que fichier PDF
    pdf_file = 'lettre_de_motivation.pdf'
    pdfkit.from_string(html_content, pdf_file)

    return pdf_file


# Créer l'interface Gradio
def gradio_interface(Presentation, Offre_Emploie):
    pdf_cv = extract_cv_info(Presentation)
    pdf_letter = generate_cover_letter(Presentation, Offre_Emploie)
    return pdf_cv, pdf_letter


# Interface avec deux champs texte pour entrer le texte source et l'offre d'emploi, et deux boutons pour télécharger les PDF
interface = gr.Interface(
    fn=gradio_interface,
    inputs=["textbox", "textbox"],
    outputs=[gr.File(label="Download CV PDF"), gr.File(label="Download Cover Letter PDF")],
    title="CV and Cover Letter Generator",
    description="Enter a text describing a CV and a job offer to extract key information into downloadable PDFs.",
)

# Lancer l'interface
interface.launch()
