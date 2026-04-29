"""
Built-in Job Role Keyword Database
====================================
Hand-crafted keyword sets for common job roles with point values.
No external APIs or models — all data is local and deterministic.
"""

JOB_KEYWORDS = {
    "frontend developer": {
        "skills": {
            "javascript": 10, "react": 10, "typescript": 9, "css": 8,
            "html": 7, "nextjs": 8, "vue": 7, "angular": 7,
            "tailwindcss": 6, "sass": 5, "bootstrap": 5, "redux": 6,
            "webpack": 5, "vite": 5, "jquery": 4, "figma": 4,
            "rest-api": 6, "graphql": 6, "git": 5, "nodejs": 5,
            "responsive design": 5, "web accessibility": 5,
            "jest": 4, "testing": 4, "agile": 3, "svelte": 5,
        },
        "title_keywords": ["frontend", "front-end", "front end", "ui", "web developer"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "software", "information technology", "it"],
    },
    "backend developer": {
        "skills": {
            "python": 10, "nodejs": 10, "java": 9, "sql": 9,
            "postgresql": 8, "mongodb": 8, "rest-api": 9, "docker": 7,
            "kubernetes": 6, "aws": 7, "express": 7, "django": 8,
            "flask": 7, "fastapi": 7, "spring": 7, "springboot": 8,
            "redis": 6, "graphql": 6, "git": 5, "linux": 6,
            "cicd": 5, "mysql": 7, "microservices": 7, "rabbitmq": 5,
            "kafka": 5, "elasticsearch": 5, "go": 7, "rust": 6,
        },
        "title_keywords": ["backend", "back-end", "back end", "server", "api"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "software", "information technology"],
    },
    "full stack developer": {
        "skills": {
            "javascript": 10, "react": 9, "nodejs": 9, "python": 8,
            "typescript": 8, "sql": 8, "mongodb": 7, "postgresql": 7,
            "rest-api": 8, "docker": 6, "aws": 6, "git": 5,
            "html": 6, "css": 6, "express": 7, "nextjs": 7,
            "redux": 5, "graphql": 6, "linux": 5, "agile": 4,
            "django": 6, "flask": 5, "tailwindcss": 5, "firebase": 5,
        },
        "title_keywords": ["full stack", "fullstack", "full-stack"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "software", "information technology"],
    },
    "data scientist": {
        "skills": {
            "python": 10, "ml": 10, "deep-learning": 9, "tensorflow": 8,
            "pytorch": 8, "scikit-learn": 8, "pandas": 9, "numpy": 8,
            "sql": 7, "r": 6, "statistics": 8, "data-analysis": 8,
            "nlp": 7, "computer-vision": 6, "tableau": 5, "powerbi": 5,
            "spark": 6, "hadoop": 5, "aws": 5, "docker": 4,
            "jupyter": 5, "matplotlib": 5, "seaborn": 4, "keras": 6,
        },
        "title_keywords": ["data scientist", "data science", "ml engineer", "machine learning"],
        "min_experience_months": 6,
        "preferred_education": ["computer science", "data science", "statistics", "mathematics"],
    },
    "data analyst": {
        "skills": {
            "sql": 10, "python": 9, "excel": 9, "tableau": 8,
            "powerbi": 8, "data-analysis": 9, "pandas": 7,
            "statistics": 7, "r": 5, "data visualization": 7,
            "google analytics": 5, "etl": 5, "data modeling": 6,
            "numpy": 5, "matplotlib": 4, "jupyter": 4,
        },
        "title_keywords": ["data analyst", "business analyst", "analytics"],
        "min_experience_months": 6,
        "preferred_education": ["statistics", "mathematics", "data science", "computer science", "economics"],
    },
    "devops engineer": {
        "skills": {
            "docker": 10, "kubernetes": 10, "aws": 9, "linux": 9,
            "cicd": 9, "terraform": 8, "ansible": 7, "jenkins": 7,
            "git": 6, "python": 6, "bash": 7, "gcp": 7,
            "azure": 7, "prometheus": 6, "grafana": 5, "nginx": 5,
            "github-actions": 6, "helm": 5, "networking": 5,
            "monitoring": 5, "security": 5,
        },
        "title_keywords": ["devops", "sre", "site reliability", "platform engineer", "infrastructure"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "information technology", "software"],
    },
    "mobile developer": {
        "skills": {
            "react native": 9, "flutter": 9, "swift": 9, "kotlin": 9,
            "java": 7, "dart": 7, "javascript": 7, "typescript": 6,
            "firebase": 7, "rest-api": 7, "git": 5, "ios": 8,
            "android": 8, "xcode": 5, "android studio": 5, "redux": 5,
            "graphql": 5, "sqlite": 5, "figma": 4, "agile": 4,
        },
        "title_keywords": ["mobile", "ios", "android", "app developer", "react native", "flutter"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "software", "information technology"],
    },
    "cybersecurity analyst": {
        "skills": {
            "networking": 9, "linux": 9, "security": 10, "penetration testing": 9,
            "firewall": 7, "siem": 7, "vulnerability assessment": 8,
            "python": 7, "bash": 6, "nmap": 5, "wireshark": 6,
            "burp suite": 5, "ids": 5, "ips": 5, "compliance": 5,
            "encryption": 6, "incident response": 7, "forensics": 5,
            "oscp": 6, "ceh": 5, "aws": 5,
        },
        "title_keywords": ["security", "cybersecurity", "infosec", "soc", "penetration tester"],
        "min_experience_months": 12,
        "preferred_education": ["cybersecurity", "computer science", "information technology", "networking"],
    },
    "ui ux designer": {
        "skills": {
            "figma": 10, "adobe xd": 8, "sketch": 7, "prototyping": 9,
            "wireframing": 8, "user research": 8, "usability testing": 7,
            "design thinking": 7, "html": 5, "css": 5, "javascript": 4,
            "photoshop": 5, "illustrator": 5, "invision": 4,
            "interaction design": 7, "typography": 5, "color theory": 4,
            "responsive design": 6, "accessibility": 5, "agile": 3,
        },
        "title_keywords": ["ui", "ux", "designer", "product designer", "ui/ux"],
        "min_experience_months": 12,
        "preferred_education": ["design", "human-computer interaction", "graphic design", "computer science"],
    },
    "cloud engineer": {
        "skills": {
            "aws": 10, "azure": 9, "gcp": 9, "docker": 8,
            "kubernetes": 8, "terraform": 8, "linux": 7, "python": 6,
            "cicd": 7, "networking": 7, "security": 6, "serverless": 6,
            "cloudformation": 5, "ansible": 5, "monitoring": 5,
            "bash": 5, "lambda": 5, "s3": 4, "ec2": 4,
        },
        "title_keywords": ["cloud", "aws", "azure", "gcp", "infrastructure"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "information technology", "software"],
    },
    "machine learning engineer": {
        "skills": {
            "python": 10, "tensorflow": 9, "pytorch": 9, "ml": 10,
            "deep-learning": 9, "scikit-learn": 7, "pandas": 7, "numpy": 7,
            "docker": 6, "aws": 6, "mlops": 7, "data-analysis": 6,
            "nlp": 7, "computer-vision": 7, "spark": 5, "sql": 5,
            "kubernetes": 5, "git": 4, "linux": 5, "statistics": 6,
            "keras": 6, "onnx": 4, "model deployment": 6,
        },
        "title_keywords": ["ml engineer", "machine learning", "ai engineer", "deep learning"],
        "min_experience_months": 6,
        "preferred_education": ["computer science", "data science", "mathematics", "artificial intelligence"],
    },
    "software engineer": {
        "skills": {
            "python": 9, "java": 9, "javascript": 8, "cpp": 8,
            "sql": 8, "git": 7, "docker": 6, "linux": 6,
            "data structures": 8, "algorithms": 8, "rest-api": 7,
            "agile": 5, "testing": 6, "cicd": 5, "aws": 5,
            "typescript": 6, "microservices": 6, "system design": 7,
            "design patterns": 6, "oop": 7,
        },
        "title_keywords": ["software engineer", "software developer", "sde", "developer"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "software", "information technology"],
    },
    "product manager": {
        "skills": {
            "product strategy": 10, "agile": 9, "scrum": 8,
            "jira": 7, "data-analysis": 8, "sql": 6, "a/b testing": 7,
            "user research": 8, "wireframing": 6, "roadmapping": 8,
            "stakeholder management": 7, "analytics": 7, "figma": 5,
            "presentation": 5, "market research": 6,
            "prioritization": 7, "communication": 6,
        },
        "title_keywords": ["product manager", "product owner", "pm", "apm"],
        "min_experience_months": 12,
        "preferred_education": ["business", "computer science", "management", "mba"],
    },
    "database administrator": {
        "skills": {
            "sql": 10, "postgresql": 9, "mysql": 9, "mssql": 8,
            "oracle": 8, "mongodb": 7, "redis": 6, "database design": 8,
            "backup": 6, "replication": 6, "performance tuning": 8,
            "linux": 6, "python": 5, "bash": 5, "aws": 5,
            "docker": 4, "security": 5, "high availability": 6,
        },
        "title_keywords": ["dba", "database admin", "database engineer", "data engineer"],
        "min_experience_months": 12,
        "preferred_education": ["computer science", "information technology", "database"],
    },
}


def find_best_job_match(query):
    """
    Find the closest matching job role from JOB_KEYWORDS.
    Uses simple substring matching — no external libraries.

    Returns (matched_role_name, keywords_dict) or (query, default_keywords).
    """
    query_lower = query.lower().strip()

    # Exact match
    if query_lower in JOB_KEYWORDS:
        return query_lower, JOB_KEYWORDS[query_lower]

    # Substring match
    best_match = None
    best_score = 0
    for role_name, role_data in JOB_KEYWORDS.items():
        # Check if query is a substring of role name or vice versa
        score = 0
        if query_lower in role_name:
            score = len(query_lower) / len(role_name)
        elif role_name in query_lower:
            score = len(role_name) / len(query_lower)
        else:
            # Word overlap
            q_words = set(query_lower.split())
            r_words = set(role_name.split())
            overlap = q_words & r_words
            if overlap:
                score = len(overlap) / max(len(q_words), len(r_words))

        # Also check title_keywords
        for tk in role_data.get("title_keywords", []):
            if tk in query_lower or query_lower in tk:
                score = max(score, 0.8)

        if score > best_score:
            best_score = score
            best_match = role_name

    if best_match and best_score >= 0.3:
        return best_match, JOB_KEYWORDS[best_match]

    # Fallback: return a generic software engineer profile
    return query_lower, JOB_KEYWORDS.get("software engineer", {
        "skills": {},
        "title_keywords": [],
        "min_experience_months": 0,
        "preferred_education": [],
    })
