"""
IR Optimizer
=============
Performs optimization passes on the Intermediate Representation:
  1. Deduplication — remove duplicate skills
  2. Merge — combine equivalent skill names
  3. Standardize — lowercase, strip whitespace
  4. Noise removal — filter out very short or meaningless tokens
"""

from compiler.semantic.analyzer import SKILL_ALIASES

# Words that should never be treated as skills
NOISE_WORDS = {
    "and", "or", "the", "a", "an", "in", "of", "for", "to", "with",
    "on", "at", "by", "is", "are", "was", "were", "be", "been",
    "etc", "other", "others", "various", "good", "strong", "proficient",
    "knowledge", "understanding", "familiar", "experience", "experienced",
    "using", "used", "use", "tools", "technologies", "skills", "skill",
    "include", "including", "ability", "able", "work", "working",
    "team", "related", "based", "basic", "advanced", "intermediate",
}


class Optimizer:
    """
    Optimizes the IR dictionary.

    Usage:
        optimizer = Optimizer(ir, diagnostics)
        optimized_ir = optimizer.optimize()
    """

    def __init__(self, ir, diagnostics=None):
        self.ir = ir
        self.diagnostics = diagnostics

    def optimize(self):
        """Run all optimization passes."""
        self._standardize_skills()
        self._deduplicate_skills()
        self._remove_noise_skills()
        self._merge_equivalent_skills()
        self._clean_experience()
        self._update_metadata()
        return self.ir

    def _standardize_skills(self):
        """Lowercase and strip all skill names."""
        self.ir["skills"] = [
            s.lower().strip() for s in self.ir["skills"] if s and s.strip()
        ]

    def _deduplicate_skills(self):
        """Remove exact duplicate skills, preserving order."""
        seen = set()
        unique = []
        removed = 0
        for skill in self.ir["skills"]:
            if skill not in seen:
                seen.add(skill)
                unique.append(skill)
            else:
                removed += 1
        self.ir["skills"] = unique
        if removed and self.diagnostics:
            self.diagnostics.info(
                "optimizer",
                f"Removed {removed} duplicate skill(s)",
            )

    def _remove_noise_skills(self):
        """Filter out single-character and known noise words."""
        original_count = len(self.ir["skills"])
        self.ir["skills"] = [
            s for s in self.ir["skills"]
            if len(s) > 1 and s not in NOISE_WORDS
        ]
        removed = original_count - len(self.ir["skills"])
        if removed and self.diagnostics:
            self.diagnostics.info(
                "optimizer",
                f"Filtered out {removed} noise/trivial skill(s)",
            )

    def _merge_equivalent_skills(self):
        """
        Merge skills that are aliases of each other.
        E.g., if both "js" and "javascript" are present, keep only "javascript".
        """
        # Build a reverse map: canonical → all aliases present
        canonical_map = {}
        for skill in self.ir["skills"]:
            canon = SKILL_ALIASES.get(skill, skill)
            if canon not in canonical_map:
                canonical_map[canon] = []
            canonical_map[canon].append(skill)

        merged = []
        merge_count = 0
        for canon, aliases in canonical_map.items():
            merged.append(canon)
            if len(aliases) > 1:
                merge_count += 1
                if self.diagnostics:
                    self.diagnostics.info(
                        "optimizer",
                        f"Merged equivalent skills {aliases} → '{canon}'",
                    )

        self.ir["skills"] = merged
        if merge_count and self.diagnostics:
            self.diagnostics.info(
                "optimizer",
                f"Merged {merge_count} group(s) of equivalent skills",
            )

    def _clean_experience(self):
        """Clean up experience entries."""
        for exp in self.ir["experience"]:
            # Strip whitespace from bullets
            exp["bullets"] = [
                b.strip() for b in exp.get("bullets", []) if b and b.strip()
            ]
            # Strip title and company
            if exp.get("title"):
                exp["title"] = exp["title"].strip()
            if exp.get("company"):
                exp["company"] = exp["company"].strip()

    def _update_metadata(self):
        """Refresh metadata after optimization."""
        self.ir["metadata"]["total_skills"] = len(self.ir["skills"])
