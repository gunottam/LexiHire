"""
Intermediate Representation (IR) Builder
==========================================
Converts the AST into a clean, flat, text-independent
dictionary structure suitable for optimization and scoring.
"""

from compiler.ast_nodes.nodes import (
    SkillNode, ExperienceNode, EducationNode,
    CertificationNode, ProjectNode, EntryNode,
)


class IRBuilder:
    """
    Converts a ResumeNode AST into an IR dictionary.

    Usage:
        builder = IRBuilder(ast, diagnostics)
        ir = builder.build()
    """

    def __init__(self, ast, diagnostics=None):
        self.ast = ast
        self.diagnostics = diagnostics

    def build(self):
        """Build the IR dictionary from the AST."""
        ir = {
            "contact": self._build_contact(),
            "skills": [],
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "other_sections": {},
            "metadata": {},
        }

        for section in self.ast.sections:
            stype = section.section_type

            if stype == "skills":
                for entry in section.entries:
                    if isinstance(entry, SkillNode):
                        ir["skills"].append(entry.name)
                    elif isinstance(entry, EntryNode):
                        ir["skills"].append(entry.content)

            elif stype == "experience":
                for entry in section.entries:
                    if isinstance(entry, ExperienceNode):
                        ir["experience"].append({
                            "title": entry.title,
                            "company": entry.company,
                            "start_date": entry.start_date,
                            "end_date": entry.end_date,
                            "duration_months": self._calc_duration(
                                entry.start_date, entry.end_date
                            ),
                            "bullets": entry.bullets,
                        })
                    elif isinstance(entry, EntryNode):
                        ir["experience"].append({
                            "title": entry.content,
                            "company": None,
                            "start_date": None,
                            "end_date": None,
                            "duration_months": 0,
                            "bullets": [],
                        })

            elif stype == "education":
                for entry in section.entries:
                    if isinstance(entry, EducationNode):
                        ir["education"].append({
                            "degree": entry.degree,
                            "institution": entry.institution,
                            "field": entry.field,
                            "start_date": entry.start_date,
                            "end_date": entry.end_date,
                            "gpa": entry.gpa,
                        })
                    elif isinstance(entry, EntryNode):
                        ir["education"].append({
                            "degree": None,
                            "institution": entry.content,
                            "field": None,
                            "start_date": None,
                            "end_date": None,
                            "gpa": None,
                        })

            elif stype == "certifications":
                for entry in section.entries:
                    if isinstance(entry, CertificationNode):
                        ir["certifications"].append({
                            "name": entry.name,
                            "issuer": entry.issuer,
                            "date": entry.date,
                        })
                    elif isinstance(entry, EntryNode):
                        ir["certifications"].append({
                            "name": entry.content,
                            "issuer": None,
                            "date": None,
                        })

            elif stype == "projects":
                for entry in section.entries:
                    if isinstance(entry, ProjectNode):
                        ir["projects"].append({
                            "name": entry.name,
                            "description": entry.description,
                            "technologies": entry.technologies,
                            "link": entry.link,
                        })
                    elif isinstance(entry, EntryNode):
                        ir["projects"].append({
                            "name": entry.content,
                            "description": [],
                            "technologies": [],
                            "link": None,
                        })

            else:
                # Generic / other sections
                entries = []
                for entry in section.entries:
                    if isinstance(entry, EntryNode):
                        entries.append(entry.content)
                    else:
                        entries.append(str(entry.to_dict()))
                if entries:
                    ir["other_sections"][stype] = entries

        # Build metadata
        total_months = sum(
            exp.get("duration_months", 0) or 0
            for exp in ir["experience"]
        )
        ir["metadata"] = {
            "section_count": len(self.ast.sections),
            "total_skills": len(ir["skills"]),
            "total_experience_entries": len(ir["experience"]),
            "total_experience_months": total_months,
            "total_education_entries": len(ir["education"]),
            "total_certifications": len(ir["certifications"]),
            "total_projects": len(ir["projects"]),
            "has_contact_email": bool(
                ir["contact"] and ir["contact"].get("email")
            ),
            "has_contact_phone": bool(
                ir["contact"] and ir["contact"].get("phone")
            ),
            "has_contact_name": bool(
                ir["contact"] and ir["contact"].get("name")
            ),
        }

        if self.diagnostics:
            self.diagnostics.info(
                "ir",
                f"IR built: {ir['metadata']['total_skills']} skills, "
                f"{ir['metadata']['total_experience_entries']} experience entries, "
                f"{ir['metadata']['total_education_entries']} education entries",
            )

        return ir

    def _build_contact(self):
        if not self.ast.contact:
            return None
        c = self.ast.contact
        return {
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "links": c.links,
        }

    @staticmethod
    def _calc_duration(start_str, end_str):
        """
        Estimate duration in months between two date strings.
        Returns 0 if dates can't be parsed.
        """
        if not start_str or not end_str:
            return 0

        start_y, start_m = IRBuilder._parse_date_parts(start_str)
        end_y, end_m = IRBuilder._parse_date_parts(end_str)

        if not start_y or not end_y:
            return 0

        months = (end_y - start_y) * 12 + (end_m - start_m)
        return max(0, months)

    @staticmethod
    def _parse_date_parts(date_str):
        """Extract (year, month) from a date string. Returns (None, None) on failure."""
        if not date_str:
            return None, None

        lower = date_str.lower().strip()
        if lower in ("present", "current", "ongoing"):
            import datetime
            now = datetime.datetime.now()
            return now.year, now.month

        MONTH_MAP = {
            "jan": 1, "january": 1, "feb": 2, "february": 2,
            "mar": 3, "march": 3, "apr": 4, "april": 4,
            "may": 5, "jun": 6, "june": 6,
            "jul": 7, "july": 7, "aug": 8, "august": 8,
            "sep": 9, "sept": 9, "september": 9,
            "oct": 10, "october": 10, "nov": 11, "november": 11,
            "dec": 12, "december": 12,
        }

        # Try "Month YYYY"
        parts = lower.split()
        for part in parts:
            if part in MONTH_MAP:
                month = MONTH_MAP[part]
                # Find year
                for p in parts:
                    if p.isdigit() and len(p) == 4:
                        return int(p), month
                return None, None

        # Try MM/YYYY or MM-YYYY
        for sep in "/-.":
            if sep in date_str:
                segments = date_str.split(sep)
                if len(segments) == 2:
                    try:
                        a, b = segments
                        if len(b) == 4 and b.isdigit():
                            month = int(a) if a.isdigit() else 1
                            return int(b), month
                    except ValueError:
                        pass

        # Try standalone year
        digits = "".join(c for c in date_str if c.isdigit())
        if len(digits) >= 4:
            try:
                year = int(digits[:4])
                if 1950 <= year <= 2040:
                    return year, 1
            except ValueError:
                pass

        return None, None
