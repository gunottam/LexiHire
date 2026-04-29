import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Groq client setup
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

# Fallback keywords in case Groq is unavailable or returns bad JSON
DEFAULT_KEYWORDS = [
    {"keyword": "javascript", "priority": 0, "weight": 1.0},
    {"keyword": "react", "priority": 1, "weight": 0.95},
    {"keyword": "typescript", "priority": 2, "weight": 0.9},
    {"keyword": "css", "priority": 3, "weight": 0.85},
    {"keyword": "html", "priority": 4, "weight": 0.8},
    {"keyword": "node", "priority": 5, "weight": 0.75},
    {"keyword": "express", "priority": 6, "weight": 0.7},
    {"keyword": "redux", "priority": 7, "weight": 0.65},
    {"keyword": "testing", "priority": 8, "weight": 0.6},
    {"keyword": "web accessibility", "priority": 9, "weight": 0.55},
]

# Prompt template
prompt_template = """
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

# Main function to generate keywords
def generate_keywords(job_title: str, output_path: str = "outputs/keywords.json"):
    if client is None:
        return {"status": "fallback", "keywords": DEFAULT_KEYWORDS, "message": "GROQ_API_KEY is not set; using defaults"}

    try:
        filled_prompt = prompt_template.format(job_title=job_title)
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume skill ranker. Return JSON only."
                },
                {"role": "user", "content": filled_prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )

        content = completion.choices[0].message.content
        parsed = json.loads(content)
        skills = parsed.get("skills", []) if isinstance(parsed, dict) else []
        if not isinstance(skills, list):
            raise ValueError("Response missing 'skills' list")

        validated_skills = []
        for item in skills:
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("keyword", "")).strip()
            if not keyword:
                continue
            try:
                priority = int(item.get("priority", 0))
            except Exception:
                priority = 0
            try:
                weight = float(item.get("weight", 0.0))
            except Exception:
                weight = 0.0
            validated_skills.append({
                "keyword": keyword,
                "priority": priority,
                "weight": weight
            })

        if not validated_skills:
            raise ValueError("No skills returned from Groq response")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validated_skills, f, indent=2)

        return {"status": "success", "keywords": validated_skills, "output_file": output_path}
    except Exception as e:
        # If Groq failed or JSON was invalid, fall back to default keywords
        return {"status": "fallback", "keywords": DEFAULT_KEYWORDS, "message": str(e)}
