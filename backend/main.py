import pdfplumber
import pandas as pd
from openai import OpenAI
import json
import os
import sys
from dotenv import load_dotenv
from ai_functions import *
from populate_pptx import *


# if len(sys.argv) < 2:
#     print("Usage: python main.py <path_to_pdf>")
#     sys.exit(1)
# else:
#     pdf_path = sys.argv[1]
#     print(pdf_path)

if __name__ == "__main__":
    input_dir = "data/input_testing"
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

for file_name in os.listdir(input_dir):
    print(file_name)
    if file_name.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_dir, file_name)
        print(pdf_path)
        output_path = os.path.join(output_dir, file_name.replace(".pdf", "_one_pager.xlsx"))
        output_path = os.path.normpath(output_path)
        
        # 1. Generate the structured data (DataFrame)
        # df = generate_one_pager(pdf_path, output_path)

        # # Save intermediate Excel or CSV for inspection (optional)
        # csv_path = os.path.join(output_dir, file_name.replace(".pdf", "_summary.csv"))
        # df.to_csv(csv_path, index=False)
        # print(f"✅ Summary saved at: {csv_path}")

        df = pd.read_excel('data/output/CV_Sandra Popielarczyk_one_pager.xlsx')
        # 2️. Generate PowerPoint
        pptx_path = populate_pptx(df)
        print(f"🎯 PowerPoint created: {pptx_path}")

print("✅ All files processed successfully!")
