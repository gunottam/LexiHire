"""
AST Node Definitions
=====================
Defines the Abstract Syntax Tree node classes for parsed resumes.
Every node has a to_dict() method for JSON serialization.
"""


class ASTNode:
    """Base class for all AST nodes."""
    def to_dict(self):
        raise NotImplementedError


class ResumeNode(ASTNode):
    def __init__(self):
        self.contact = None
        self.sections = []

    def to_dict(self):
        return {
            "type": "Resume",
            "contact": self.contact.to_dict() if self.contact else None,
            "sections": [s.to_dict() for s in self.sections],
        }


class ContactNode(ASTNode):
    def __init__(self):
        self.name = None
        self.email = None
        self.phone = None
        self.links = []
        self.raw_lines = []

    def to_dict(self):
        return {
            "type": "Contact",
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "links": self.links,
        }


class SectionNode(ASTNode):
    def __init__(self, section_type, header_value="", line=None):
        self.section_type = section_type
        self.header_value = header_value
        self.entries = []
        self.line = line

    def to_dict(self):
        return {
            "type": "Section",
            "section_type": self.section_type,
            "entries": [e.to_dict() for e in self.entries],
            "line": self.line,
        }


class SkillNode(ASTNode):
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def to_dict(self):
        return {"type": "Skill", "name": self.name, "line": self.line}


class ExperienceNode(ASTNode):
    def __init__(self, line=None):
        self.title = None
        self.company = None
        self.start_date = None
        self.end_date = None
        self.bullets = []
        self.line = line

    def to_dict(self):
        return {
            "type": "Experience",
            "title": self.title,
            "company": self.company,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "bullets": self.bullets,
            "line": self.line,
        }


class EducationNode(ASTNode):
    def __init__(self, line=None):
        self.degree = None
        self.institution = None
        self.field = None
        self.start_date = None
        self.end_date = None
        self.gpa = None
        self.line = line

    def to_dict(self):
        return {
            "type": "Education",
            "degree": self.degree,
            "institution": self.institution,
            "field": self.field,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gpa": self.gpa,
            "line": self.line,
        }


class CertificationNode(ASTNode):
    def __init__(self, name="", line=None):
        self.name = name
        self.issuer = None
        self.date = None
        self.line = line

    def to_dict(self):
        return {
            "type": "Certification",
            "name": self.name,
            "issuer": self.issuer,
            "date": self.date,
            "line": self.line,
        }


class ProjectNode(ASTNode):
    def __init__(self, line=None):
        self.name = None
        self.description = []
        self.technologies = []
        self.link = None
        self.line = line

    def to_dict(self):
        return {
            "type": "Project",
            "name": self.name,
            "description": self.description,
            "technologies": self.technologies,
            "link": self.link,
            "line": self.line,
        }


class EntryNode(ASTNode):
    def __init__(self, content="", line=None):
        self.content = content
        self.line = line

    def to_dict(self):
        return {"type": "Entry", "content": self.content, "line": self.line}
