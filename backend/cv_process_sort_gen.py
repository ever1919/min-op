"""CV processing and one-pager content generation module.

This module extracts text from PDF resumes, uses OpenAI models to generate
structured summaries and roles, and returns the results as a pandas DataFrame
for downstream PowerPoint generation.
"""

import json
import os
import re

import pdfplumber
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract plain text from all pages of a PDF file.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        The extracted text from all pages, concatenated and trimmed.
    """
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


def generate_sections(
    cv_text: str,
    coe_selected: str,
    tower_selected: str,
) -> str:
    """Generate fixed one-pager sections using an LLM prompt.

    This function loads a COE-specific prompt template, combines it with
    the extracted CV text and user selections, and requests structured
    output from the OpenAI API.

    Args:
        cv_text: Extracted text content from the CV.
        coe_selected: Selected center of excellence.
        tower_selected: Selected tower category.

    Returns:
        A JSON-formatted string containing section names and content.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
        OpenAIError: If the API request fails.
    """
    with open(
        f"prompt_dictionary/{coe_selected.lower()}.md",
        "r",
        encoding="utf-8",
    ) as f:
        coe_prompt = f.read()

    prompt_completed = f"""
    You are an AI assistant that summarizes a candidate CV into specific structured sections.
    Do NOT create new sections.
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
        messages=[
            {
                "role": "user",
                "content": prompt_completed,
                "reasoning-effort": "medium",
            }
        ],
    )

    return response.choices[0].message.content.strip()

def generate_roles(cv_text: str, coe_selected: str) -> list[str]:
    """Generate relevant professional roles from a CV.

    The output is formatted into role blocks separated by line breaks and
    truncated based on the selected COE.

    Args:
        cv_text: Extracted text content from the CV.
        coe_selected: Selected center of excellence.

    Returns:
        A list of formatted role descriptions.
    """
    if coe_selected.lower() != "digi core":
        coe_selected = "other"

    with open(
        f"prompt_dictionary/{coe_selected.lower()}_roles.md",
        "r",
        encoding="utf-8",
    ) as f:
        coe_roles_prompt = f.read()

    prompt = f"""
    You are an AI assistant that extracts and summarizes relevant professional experience
    from a candidate CV into distinct role blocks.

    {coe_roles_prompt}

    Candidate CV:
    {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
                "reasoning-effort": "medium",
            }
        ],
    )

    text = response.choices[0].message.content.strip()

    roles = [
        r.strip()
        for r in re.split(r"\n\s*\n", text)
        if r.strip()
    ]

    if coe_selected.lower() == "digi core":
        roles = roles[:4]
    else:
        roles = roles[:9]

    return roles


def generate_one_pager(
    cv_path: str,
    coe_selected: str,
    tower_selected: str,
    save_debug: bool = True,
) -> pd.DataFrame:
    """Generate a complete one-pager summary from a CV.

    This function orchestrates the full pipeline:
    - Extracts text from the PDF
    - Generates fixed sections
    - Generates relevant roles
    - Builds a structured DataFrame
    - Optionally saves debug output

    Args:
        cv_path: Path to the input CV PDF file.
        coe_selected: Selected center of excellence.
        tower_selected: Selected tower category.
        save_debug: Whether to save the intermediate CSV output.

    Returns:
        A pandas DataFrame containing section names and generated content.

    Raises:
        Exception: Propagates any error occurring during generation.
    """
    try:
        cv_text = extract_text_from_pdf(cv_path)

        print("Generating sections...")
        sections = generate_sections(
            cv_text,
            coe_selected,
            tower_selected,
        )
        response_dic = json.loads(sections)

        print("Generating relevant experience roles...")
        roles = generate_roles(cv_text, coe_selected)

        for i, element in enumerate(roles):
            response_dic[f"Role_{i + 1}"] = element

        df = pd.DataFrame(
            list(response_dic.items()),
            columns=["section_name", "output"],
        )

        if save_debug:
            csv_path = "data/output/one_pager_summary.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8")
            print(f"Debug saved at: {os.path.abspath(csv_path)}")

        return df

    except Exception as exc:
        print(f"Error generating one pager: {str(exc)}")
        raise