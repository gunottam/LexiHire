class ResumeTokenizer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        tokens = []
        current_token = ""

        for char in self.text:
            if char == '\n':
                if current_token.strip() != "":
                    tokens.append(current_token.strip())
                current_token = ""
            else:
                current_token += char

        if current_token.strip() != "":
            tokens.append(current_token.strip())

        return tokens
    
