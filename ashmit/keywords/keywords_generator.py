# pip install python-dotenv pydantic langchain-google-genai
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class SkillItem(BaseModel):
    keyword: str = Field(..., description="The name of the skill or certification")
    priority: int = Field(..., ge=0, le=29, description="The rank (0 = highest)")
    weight: float = Field(..., gt=0.0, lt=1.0, description="Market demand weight between 0 and 1")

class SkillList(BaseModel):
    skills: list[SkillItem]

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)

structured_model = llm.with_structured_output(SkillList)

prompt = """
You are an expert in career guidance and job market analysis.

Based on current global job market trends, generate the top 30 most in-demand skills and certifications for the job title: "{job_title}".

Instructions:
- Return a JSON object with a single key "skills", whose value is an array of skill entries.
- Each skill entry must include:
  - "keyword": the name of the skill or certification
  - "priority": an integer from 0 to 29 (0 = highest demand)
  - "weight": a float between 0 and 1 (non-inclusive) representing the skill's relative demand in the job market
- Ensure weights are consistent with priority (higher priority = higher weight).
"""

def get_and_save_keywords(job_title: str, output_file: str):
    try:
        prompt_filled = prompt.format(job_title=job_title)
        result = structured_model.invoke(prompt_filled)
        data_dict = [item.model_dump() for item in result.skills]
        with open(output_file, "w") as f:
            json.dump(data_dict, f, indent=2)
        print(f"Keywords with weights saved to {output_file} :)")
        return data_dict
    except Exception as e:
        print(f"Failed: {e} :(")
        return None

if __name__ == "__main__":
    job = input("Enter a job title: ")
    get_and_save_keywords(job, output_file="keywords.json")
