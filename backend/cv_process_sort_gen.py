import pdfplumber
import pandas as pd
import io
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

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

def generate_roles(cv_text):
    """Generate up to 4 roles, formatted with bold keywords and line breaks only."""
    prompt = f"""
    You are an AI assistant that extracts and rewrites a candidate’s RELEVANT EXPERIENCE into up to 4 roles.

    Formatting and style:
    - Each role must have this structure:
        Role Title
        Responsibility or achievement #1
        Responsibility or achievement #2

    - But look similar in structure but more detailed to this example. Never copy anything but the structure and always use at least 3 or more lines per role:
        Data Analyst
        Led the **development** of **data pipelines** using **Python** and **SQL** to streamline data processing.
        Collaborated with **cross-functional teams** to implement **data visualization** solutions using **Power BI and Tableau**, enhancing decision-making capabilities.
        Implemented **statistical analysis** and **machine learning** models using **R** and Python to derive actionable insights from large datasets, improving business strategies.

    - Each role must have 3-4 lines, maximum 400 characters per line.
    - Focus on responsibilities and achievements that highlight skills, tools, or technologies.
    - Bold **keywords**, **skills**, or **technologies** only.
    - Keep output concise and professional English tone.
    - Do NOT use bullets or dashes — only separate lines with line breaks.
    - Exclude company names, institutions, and dates.
    - Maximum of 4 roles. If fewer exist, only return those. Do NOT create new roles.

    Candidate CV:
    {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt, "reasoning-effort": "medium"}],
    )

    text = response.choices[0].message.content.strip()

    # Split each role block by double line breaks
    roles = [r.strip() for r in text.split("\n\n") if r.strip()]
    return roles[:4]

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
        roles = generate_roles(cv_text)
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
