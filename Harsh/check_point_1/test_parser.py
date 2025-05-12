import os
import json
from tokenizer import ResumeTokenizer
from parser_service import ResumeParser


folder_path = "C:/Users/ashmi/Desktop/Lexihire/ashmit/resumes"


for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)

        print(f"Processing {filename}...")

        with open(file_path, 'r', encoding='utf-8') as file:
            resume_text = file.read()

        tokenizer = ResumeTokenizer(resume_text)
        tokens = tokenizer.tokenize()

        parser = ResumeParser(tokens)
        symbol_table = parser.parse()

        modified_content = json.dumps(symbol_table, indent=4)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        print(f"Done processing {filename} ✅\n")
