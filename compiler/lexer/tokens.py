"""
Token Definitions for the Resume Lexer
=======================================
Defines all token types recognized by the lexer and the Token dataclass.
"""

from enum import Enum, auto


class TokenType(Enum):
    """All token types emitted by the resume lexer."""

    # ── Structural ──
    HEADER = auto()       # Section header (SKILLS, EDUCATION, EXPERIENCE, etc.)
    NEWLINE = auto()      # Line break
    EOF = auto()          # End of input

    # ── Content ──
    WORD = auto()         # Alphabetic word (may include apostrophes/hyphens)
    NUMBER = auto()       # Numeric literal (integer or decimal)
    DATE = auto()         # Date pattern (MM/YYYY, YYYY, Month YYYY, etc.)
    EMAIL = auto()        # Email address
    PHONE = auto()        # Phone number
    URL = auto()          # Web URL (http/https/www)

    # ── Punctuation ──
    BULLET = auto()       # Bullet marker (•, ►, ▪, -, *, ●)
    COMMA = auto()        # ,
    COLON = auto()        # :
    SEMICOLON = auto()    # ;
    DASH = auto()         # – — -  (used as separator, not bullet)
    PIPE = auto()         # |
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    SLASH = auto()        # /
    HASH = auto()         # #
    DOT = auto()          # .
    AT = auto()           # @  (standalone, not in email)
    PLUS = auto()         # +
    AMPERSAND = auto()    # &
    SYMBOL = auto()       # Any other punctuation / symbol


class Token:
    """
    A single token produced by the lexer.

    Attributes:
        type:   TokenType enum value
        value:  The raw string value of the token
        line:   1-indexed source line number
        column: 1-indexed source column number
    """

    __slots__ = ("type", "value", "line", "column")

    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self):
        val = self.value if len(self.value) <= 20 else self.value[:17] + "..."
        return f"Token({self.type.name}, {val!r}, L{self.line}:C{self.column})"
