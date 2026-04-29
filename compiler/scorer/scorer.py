"""
Resume Scoring Engine
======================
Rule-based, section-weighted scoring system.

Score breakdown (100 points total):
  - Skills:     40 points  (matched skills × point values, capped)
  - Experience:  30 points  (duration + relevance + bullet quality)
  - Education:   15 points  (degree level + field relevance)
  - Structure:   15 points  (completeness, formatting, contact info)

Key design decisions:
  - Each skill counted at most ONCE (no frequency abuse)
  - Graduated experience scale (diminishing returns)
  - Bonus for structured, complete resumes
"""

from .keywords import find_best_job_match


# ── Score weights ─────────────────────────────────────────────────────────
MAX_SKILLS_SCORE = 40
MAX_EXPERIENCE_SCORE = 30
MAX_EDUCATION_SCORE = 15
MAX_STRUCTURE_SCORE = 15
MAX_TOTAL = MAX_SKILLS_SCORE + MAX_EXPERIENCE_SCORE + MAX_EDUCATION_SCORE + MAX_STRUCTURE_SCORE

# ── Degree level points ──────────────────────────────────────────────────
DEGREE_POINTS = {
    "PHD": 10, "PH.D": 10, "DOCTORATE": 10,
    "MASTERS": 8, "MASTER": 8, "M.TECH": 8, "MTECH": 8,
    "M.SC": 8, "MSC": 8, "M.S": 8, "MS": 8, "M.A": 8,
    "MBA": 8, "M.B.A": 8, "MCA": 8, "M.COM": 8,
    "BACHELORS": 6, "BACHELOR": 6, "B.TECH": 6, "BTECH": 6,
    "B.E": 6, "BE": 6, "B.SC": 6, "BSC": 6, "B.S": 6, "BS": 6,
    "B.A": 6, "BA": 6, "BBA": 6, "BCA": 6, "B.COM": 6,
    "DIPLOMA": 4, "ASSOCIATE": 4, "ASSOCIATES": 4,
    "CERTIFICATE": 3,
    "12TH": 2, "HSC": 2, "HIGH SCHOOL": 2,
    "10TH": 1, "SSC": 1, "SECONDARY": 1,
}

# ── Experience duration scoring (months → points) ────────────────────────
# Graduated scale with diminishing returns
EXPERIENCE_TIERS = [
    (6, 3),      # 0-6 months: 3 pts
    (12, 6),     # 6-12 months: 6 pts
    (24, 10),    # 1-2 years: 10 pts
    (36, 14),    # 2-3 years: 14 pts
    (60, 18),    # 3-5 years: 18 pts
    (120, 22),   # 5-10 years: 22 pts
    (999, 25),   # 10+ years: 25 pts (capped)
]


class ResumeScorer:
    """
    Section-weighted resume scoring engine.

    Usage:
        scorer = ResumeScorer(ir, job_role, diagnostics)
        result = scorer.score()
    """

    def __init__(self, ir, job_role, diagnostics=None):
        self.ir = ir
        self.job_role = job_role
        self.diagnostics = diagnostics
        self.matched_role, self.role_data = find_best_job_match(job_role)

    def score(self):
        """
        Compute the full score breakdown.
        Returns a dict with total_score, normalized_score, and per-section breakdown.
        """
        skills_result = self._score_skills()
        exp_result = self._score_experience()
        edu_result = self._score_education()
        struct_result = self._score_structure()

        total = (
            skills_result["score"]
            + exp_result["score"]
            + edu_result["score"]
            + struct_result["score"]
        )
        total = min(total, MAX_TOTAL)
        normalized = round(total / MAX_TOTAL, 4)

        result = {
            "total_score": round(total, 2),
            "max_score": MAX_TOTAL,
            "normalized_score": normalized,
            "matched_job_role": self.matched_role,
            "breakdown": {
                "skills": skills_result,
                "experience": exp_result,
                "education": edu_result,
                "structure": struct_result,
            },
        }

        if self.diagnostics:
            self.diagnostics.info(
                "scorer",
                f"Final score: {total:.1f}/{MAX_TOTAL} "
                f"(normalized: {normalized:.4f}) "
                f"for role '{self.matched_role}'",
            )

        return result

    # ── Skills scoring (max 40 pts) ───────────────────────────────────────

    def _score_skills(self):
        role_skills = self.role_data.get("skills", {})
        raw_list = list(self.ir.get("skills") or [])
        if len(raw_list) > 2000:
            raw_list = raw_list[:2000]
        resume_skills = {s for s in raw_list if s}

        matched = []
        missing = []
        raw_points = 0

        for skill_name, points in role_skills.items():
            if skill_name in resume_skills:
                matched.append(skill_name)
                raw_points += points  # each skill counted AT MOST ONCE
            else:
                missing.append(skill_name)

        # Also check for partial matches, but only meaningful ones.
        # Require both to be 4+ chars and one must be a prefix of the other.
        for resume_skill in resume_skills:
            for role_skill, points in role_skills.items():
                if role_skill in matched:
                    continue
                # Only partial-match if both are reasonably long
                if len(role_skill) < 4 or len(resume_skill) < 4:
                    continue
                # One must start with the other (prefix match, not substring)
                if role_skill.startswith(resume_skill) or resume_skill.startswith(role_skill):
                    matched.append(role_skill)
                    raw_points += points
                    if role_skill in missing:
                        missing.remove(role_skill)

        # Normalize to max score
        max_possible = sum(role_skills.values()) if role_skills else 1
        score = min(MAX_SKILLS_SCORE, (raw_points / max_possible) * MAX_SKILLS_SCORE)
        score = round(score, 2)

        if self.diagnostics:
            self.diagnostics.info(
                "scorer",
                f"Skills: {score}/{MAX_SKILLS_SCORE} "
                f"({len(matched)} matched, {len(missing)} missing)",
            )

        return {
            "score": score,
            "max": MAX_SKILLS_SCORE,
            "matched": sorted(matched),
            "missing": sorted(missing[:10]),  # top 10 missing
            "total_resume_skills": len(resume_skills),
        }

    # ── Experience scoring (max 30 pts) ───────────────────────────────────

    def _score_experience(self):
        experience = self.ir.get("experience", [])
        meta = self.ir.get("metadata", {})
        total_months = meta.get("total_experience_months", 0)

        # Duration score (max 25 pts)
        duration_score = 0
        for threshold, pts in EXPERIENCE_TIERS:
            if total_months <= threshold:
                duration_score = pts
                break
        else:
            duration_score = EXPERIENCE_TIERS[-1][1]

        # Title relevance bonus (max 3 pts)
        title_bonus = 0
        title_keywords = self.role_data.get("title_keywords", [])
        for exp in experience:
            title = (exp.get("title") or "").lower()
            for tk in title_keywords:
                if tk in title:
                    title_bonus = 3
                    break
            if title_bonus:
                break

        # Bullet quality bonus (max 2 pts)
        total_bullets = sum(len(exp.get("bullets", [])) for exp in experience)
        bullet_bonus = min(2, total_bullets * 0.3)

        score = min(
            MAX_EXPERIENCE_SCORE,
            duration_score + title_bonus + bullet_bonus
        )
        score = round(score, 2)

        if self.diagnostics:
            self.diagnostics.info(
                "scorer",
                f"Experience: {score}/{MAX_EXPERIENCE_SCORE} "
                f"(duration={total_months}mo, title_bonus={title_bonus}, "
                f"bullets={total_bullets})",
            )

        return {
            "score": score,
            "max": MAX_EXPERIENCE_SCORE,
            "total_months": total_months,
            "entries_count": len(experience),
            "title_relevance_bonus": title_bonus,
            "bullet_count": total_bullets,
        }

    # ── Education scoring (max 15 pts) ────────────────────────────────────

    def _score_education(self):
        education = self.ir.get("education", [])

        # Degree level (max 10 pts)
        best_degree_score = 0
        best_degree = None
        for edu in education:
            degree = (edu.get("degree") or "").upper().strip()
            if degree in DEGREE_POINTS:
                pts = DEGREE_POINTS[degree]
                if pts > best_degree_score:
                    best_degree_score = pts
                    best_degree = degree

        # Field relevance (max 3 pts)
        field_bonus = 0
        preferred = self.role_data.get("preferred_education", [])
        for edu in education:
            field = (edu.get("field") or "").lower()
            institution = (edu.get("institution") or "").lower()
            combined = f"{field} {institution}"
            for pref in preferred:
                if pref in combined:
                    field_bonus = 3
                    break
            if field_bonus:
                break

        # GPA bonus (max 2 pts)
        gpa_bonus = 0
        for edu in education:
            gpa = edu.get("gpa")
            if gpa:
                try:
                    gpa_val = float(gpa)
                    if gpa_val >= 8.0:
                        gpa_bonus = 2
                    elif gpa_val >= 7.0:
                        gpa_bonus = 1.5
                    elif gpa_val >= 3.5:  # 4.0 scale
                        gpa_bonus = 2
                    elif gpa_val >= 3.0:
                        gpa_bonus = 1
                except ValueError:
                    pass

        score = min(
            MAX_EDUCATION_SCORE,
            best_degree_score + field_bonus + gpa_bonus
        )
        score = round(score, 2)

        if self.diagnostics:
            self.diagnostics.info(
                "scorer",
                f"Education: {score}/{MAX_EDUCATION_SCORE} "
                f"(degree={best_degree}, field_bonus={field_bonus}, "
                f"gpa_bonus={gpa_bonus})",
            )

        return {
            "score": score,
            "max": MAX_EDUCATION_SCORE,
            "best_degree": best_degree,
            "field_relevance_bonus": field_bonus,
            "gpa_bonus": gpa_bonus,
            "entries_count": len(education),
        }

    # ── Structure scoring (max 15 pts) ────────────────────────────────────

    def _score_structure(self):
        meta = self.ir.get("metadata", {})

        # Section completeness (max 6 pts)
        expected_sections = {"skills", "experience", "education"}
        found_sections = set()
        for section_key in ["skills", "experience", "education",
                            "certifications", "projects"]:
            if self.ir.get(section_key):
                found_sections.add(section_key)

        section_score = 0
        for sec in expected_sections:
            if sec in found_sections:
                section_score += 2  # 2 pts per required section

        # Bonus sections (max 2 pts)
        bonus_sections = found_sections - expected_sections
        bonus_score = min(2, len(bonus_sections))

        # Contact completeness (max 3 pts)
        contact_score = 0
        if meta.get("has_contact_name"):
            contact_score += 1
        if meta.get("has_contact_email"):
            contact_score += 1
        if meta.get("has_contact_phone"):
            contact_score += 1

        # Error penalty (up to -4 pts)
        error_penalty = 0
        if self.diagnostics:
            error_penalty = min(4, self.diagnostics.error_count() * 2)

        score = max(0, section_score + bonus_score + contact_score - error_penalty)
        score = min(MAX_STRUCTURE_SCORE, score)
        score = round(score, 2)

        if self.diagnostics:
            self.diagnostics.info(
                "scorer",
                f"Structure: {score}/{MAX_STRUCTURE_SCORE} "
                f"(sections={len(found_sections)}, "
                f"contact={contact_score}/3, "
                f"penalty={error_penalty})",
            )

        return {
            "score": score,
            "max": MAX_STRUCTURE_SCORE,
            "sections_found": sorted(found_sections),
            "contact_completeness": contact_score,
            "error_penalty": error_penalty,
        }
