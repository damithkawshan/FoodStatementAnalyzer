import re

class BankConfig:
    """
    Base class for bank configurations.
    Each subclass should implement its own parsing logic.
    """
    def __init__(self, name, company_reg_no, pattern):
        self.name = name
        self.company_reg_no = company_reg_no
        self.pattern = pattern
        self.year = None
        self.month = None

    def parse_transaction(self, line):
        raise NotImplementedError


    def get_statement_metadata(self, statement_name):
        match = re.search(self.statement_name_format, statement_name)
        if match:
            self.month = match.group(1)[:3]
            self.year = match.group(2)
            return {
                "bank": self.name,
                "compang_reg_no": self.company_reg_no,
                "month": match.group(1),
                "year": match.group(2)
            }
        return None

class DBSBankConfig(BankConfig):
    def __init__(self):
        super().__init__(
            name="DBS Bank Ltd",
            company_reg_no="196800306E",
            pattern=r"^\s*(\d{2} \w{3}) (.+?) (\d+\.\d{2}) (DB)$"
        )
        self.statement_name_format = r"([A-Z][a-z]+)(\d{4})"

    def get_statement_metadata(self, statement_name):
        return super().get_statement_metadata(statement_name)
    
    def parse_transaction(self, line):
        match = re.match(self.pattern, line)
        if match:
            description = re.sub(r"\b(SINGAPORE|SG)\b", "", match.group(2), flags=re.IGNORECASE).strip()
            return {
                "bank_id": self.company_reg_no,
                "year": self.year,
                "month": self.month,
                "date": match.group(1),
                "description": description,
                "amount": float(match.group(3))
                # "type": match.group(4)
            }
        return None
    

class CitiBankConfig(BankConfig):
    def __init__(self):
        super().__init__(
            name="Citi Bank Singapore Ltd",
            company_reg_no="200309485K",
            pattern=r"^\s*(\d{2} \w{3}) (.+?) (\d+\.\d{2})$"
        )
        self.statement_name_format = r"_([A-Z][a-z]{2})(\d{4})_"

    def get_statement_metadata(self, statement_name):
        return super().get_statement_metadata(statement_name)
    
    def parse_transaction(self, line):
        match = re.match(self.pattern, line)
        if match:
            description = re.sub(r"\b(SINGAPORE|SG)\b", "", match.group(2), flags=re.IGNORECASE).strip()
            return {
                "bank_id": self.company_reg_no,
                "year": self.year,
                "month": self.month,
                "date": match.group(1),
                "description": description,
                "amount": float(match.group(3))
            }
        return None
