"""PowerPoint population and formatting utilities.

This module populates predefined PowerPoint templates with structured
one-pager content and applies consistent formatting, bullet rules,
and text styling.
"""

import re

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

def apply_bold_to_paragraph(paragraph) -> None:
    """Apply bold formatting to marked segments in a PowerPoint paragraph.

    Text enclosed in double asterisks is rendered in bold. Existing runs
    are removed and rebuilt to ensure consistent formatting.

    Example:
        Input text:
            Responsible for **collecting** and **analyzing** data.

        Output:
            collecting and analyzing rendered in bold.

    Args:
        paragraph: A python-pptx paragraph object.
    """
    text = paragraph.text
    parts = re.split(r"(\*\*.*?\*\*)", text)

    for _ in range(len(paragraph.runs)):
        paragraph._element.remove(paragraph.runs[0]._r)

    for part in parts:
        run = paragraph.add_run()

        if part.startswith("**") and part.endswith("**"):
            run.text = part[2:-2]
            run.font.bold = True
        else:
            run.text = part

def populate_pptx(
    df_text: pd.DataFrame,
    coe_selected: str,
) -> str:
    """Populate a PowerPoint template with generated one-pager content.

    The function maps DataFrame sections to named shapes in the template,
    applies bullet rules, formats titles, and enforces typography standards.

    Args:
        df_text: DataFrame containing section_name and output columns.
        coe_selected: Selected center of excellence identifier.

    Returns:
        Path to the generated PowerPoint file.

    Raises:
        FileNotFoundError: If the selected template does not exist.
        ValueError: If the input DataFrame is invalid.
    """
    if coe_selected.lower() == "digi core":
        template_path = "data/input/SC&O TEMPLATE DigiCore.pptx"
    else:
        template_path = "data/input/SC&O TEMPLATE.pptx"

    prs = Presentation(template_path)
    slide = prs.slides[0]

    bullet_sections = {
        "industry experience",
        "functional experience",
        "certifications/training",
    }

    for _, row in df_text.iterrows():
        section_name = row["section_name"].strip().lower()
        new_text = str(row["output"]).strip()

        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue

            if (
                shape.name.strip().lower()
                != row["section_name"].strip().lower()
            ):
                continue

            text_frame = shape.text_frame
            text_frame.clear()

            lines = new_text.splitlines()

            if section_name.startswith("role"):
                title_line = f"**{lines[0].strip()}**"
                formatted_lines = "\n".join(
                    [title_line]
                    + [f"• {line}" for line in lines[1:]]
                )

            elif section_name in bullet_sections:
                formatted_lines = "\n".join(
                    [f"• {line}" for line in lines]
                )

            else:
                formatted_lines = "\n".join(lines)

            text_frame.text = formatted_lines

            for paragraph in text_frame.paragraphs:
                apply_bold_to_paragraph(paragraph)

                shape_name = shape.name.strip().lower()

                if shape_name == "name":
                    run = paragraph.runs[0]
                    run.text = run.text.upper().strip()

                elif shape_name == "tower":
                    run = paragraph.runs[0]
                    run.font.name = "Graphik Black"
                    run.font.size = Pt(24)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.text = run.text.upper().strip()

                else:
                    for run in paragraph.runs:
                        run.font.name = "Graphik"
                        run.font.size = Pt(9)
                        run.font.color.rgb = RGBColor(0, 0, 0)

    output_path = "data/output/updated_presentation.pptx"
    prs.save(output_path)

    print("Presentation was successfully created")

    return output_path
