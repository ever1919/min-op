import pdfplumber
import pandas as pd
import io
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

# Extrae texto. Esto está ok.
def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of the PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def generate_sections(cv_text, coe_selected, tower_selected):
    """ Esta función toma como input el texto del CV (con o sin flavor) y llama al prompt segun la 
    torre seleccionada a fin de generar las secciones fijas del one-pager. Si el usuario no selecciona torre,
    se usa el prompt default.md, el cuál identifica la torre según el contenido del CV."""

    
    with open(f"prompt_dictionary/{coe_selected.lower()}.md", "r", encoding="utf-8") as f:
        coe_prompt = f.read()
    prompt_completed = f""" 
    
    You are an AI assistant that summarizes a candidate CV into specific structured sections. Do NOT create new sections.
    Write the output in English.
    Return an dictionary where the section is the Key and the its information is the Value.

    Formatting rules:
    - Use line breaks to separate each idea or item. Do NOT use bullet symbols or dashes.
    - Maintain concise, professional tone.
    - Exclude candidate name, company names, institutions, and dates.
    - Assume Graphik 9 font style.

    The user selected this tower {tower_selected}. Use this to guide your summary.

    {coe_prompt}
    
    Candidate CV: {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt_completed, "reasoning-effort": "medium"}],
    )
    return response.choices[0].message.content.strip()

def generate_roles(cv_text, coe_selected):
    """Generate roles based on the COE, formatted with bold keywords and line breaks only."""
    if coe_selected.lower() != "digi core":
        coe_selected = "other"

    with open(f"prompt_dictionary/{coe_selected.lower()}_roles.md", "r", encoding="utf-8") as f:
        coe_roles_prompt = f.read()
    prompt = f"""
    You are an AI assistant that extracts and summarizes relevant professional experience from a candidate CV into distinct role blocks.
    {coe_roles_prompt}

    Candidate CV:
    {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt, "reasoning-effort": "medium"}],
    )

    text = response.choices[0].message.content.strip()

    # Split each role block by double line breaks
    roles = [r.strip() for r in re.split(r"\n\s*\n", text) if r.strip()]
    if coe_selected.lower() == "digi core":
        roles = roles[:4]
    else:
        roles = roles[:9]
    return roles

def generate_one_pager(cv_path, coe_selected, tower_selected, save_debug=True):
    """Generate all sections and return DataFrame."""
    try:
        cv_text = extract_text_from_pdf(cv_path)

        # Generate fixed sections
        print("🔹 Generating: SECTIONS...")
        sections = generate_sections(cv_text, coe_selected, tower_selected)
        response_dic = json.loads(sections)

        # Generate dynamic roles
        print("🔹 Generating: RELEVANT EXPERIENCE (Roles)...")
        roles = generate_roles(cv_text, coe_selected)
        for i, element in enumerate(roles):
            response_dic[f"Role_{i+1}"] = element

        # Create and return DataFrame
        df = pd.DataFrame(list(response_dic.items()), columns=["section_name", "output"])

        # Save debug CSV if needed
        if save_debug:
            csv_path = f"data/output/one_pager_summary.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"✅ Debug saved at: {os.path.abspath(csv_path)}")
        
        return df

    except Exception as e:
        print(f"Error generating one pager: {str(e)}")
        raise
