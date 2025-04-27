class ResumeParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.symbol_table = {
            'skills': [],
            'education': [],
            'experience': [],
            'certifications': [],
        }

    def parse(self):
        self._identify_sections()
        return self.symbol_table
 
    def _identify_sections(self):
        current_section = None

        section_keywords = {
            'education': ['education', 'academics', 'qualification'],
            'experience': ['experience', 'work history', 'employment'],
            'skills': ['skills', 'technologies', 'technical expertise'],
            'certifications': ['certifications', 'certificates'],
        }

        for line in self.tokens:
            line_lower = line.lower()

            found_section = None
            for section, keywords in section_keywords.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        found_section = section
                        break
                if found_section:
                    break

            if found_section:
                current_section = found_section
                continue

            if current_section:
                self.symbol_table[current_section].append(line)
