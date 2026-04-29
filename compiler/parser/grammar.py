"""
Resume Context-Free Grammar (CFG)
===================================
Formal grammar definition for resume structure.
Used by the recursive descent parser in parser.py.

Production Rules:
─────────────────

Resume          → ContactBlock? Section+ EOF
ContactBlock    → (WORD | EMAIL | PHONE | URL | SYMBOL | NUMBER | NEWLINE)+
                  (until first HEADER token)

Section         → HEADER NEWLINE SectionBody
SectionBody     → Entry+

Entry           → SkillEntry
                | ExperienceEntry
                | EducationEntry
                | CertEntry
                | ProjectEntry
                | GenericEntry

SkillEntry      → SkillItem (SEPARATOR SkillItem)*
SkillItem       → WORD (WORD | NUMBER | PLUS | HASH | DOT)*
SEPARATOR       → COMMA | PIPE | NEWLINE | BULLET

ExperienceEntry → TitleLine DateLine? BulletList?
TitleLine       → WORD+ (DASH | PIPE | COMMA) WORD+  NEWLINE
DateLine        → DATE (DASH DATE)? NEWLINE
BulletList      → BulletItem+
BulletItem      → BULLET WORD+ NEWLINE

EducationEntry  → DegreeLine DateLine? DetailLine?
DegreeLine      → WORD+ NEWLINE
DetailLine      → (WORD | NUMBER | SYMBOL)+ NEWLINE

CertEntry       → WORD+ (DASH WORD+)? DateLine? NEWLINE

ProjectEntry    → ProjectTitle NEWLINE (BulletList | DescLines)?
ProjectTitle    → WORD+ (DASH WORD+)?
DescLines       → (WORD | SYMBOL | NUMBER)+ NEWLINE

GenericEntry    → (WORD | NUMBER | SYMBOL | DATE)+ NEWLINE

Notes:
  - The parser is lenient: it never fully rejects a resume.
  - Structural issues are reported as diagnostics, not fatal errors.
  - Sections are dispatched by their HEADER type to specific sub-parsers.
"""
