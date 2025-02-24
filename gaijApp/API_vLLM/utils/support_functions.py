"""
    Utility scripts 
"""
import re

# ====  dictionary with all the field names ( standar , in english and in Norwegian)
def fieldNames_dict():
    fields_NOR = ["Foretaksnavn", "Organisasjonsnummer","Forretningsadresse","Organisasjonsform","Lederskap","Datterselskaper","Morselskap","Revisor"]
    fields_ENG = ["company_name","company_id","company_address","company_type","leadership","subsidiaries","parent_company","auditor"]
    fields_general = ["name","ID","address","type","leadership","subsidiaries","parent","auditor"]
    dataFields_dict = dict()
    for i in range(len(fields_general)):
        field = fields_general[i]
        dataFields_dict[field] = dict()
        dataFields_dict[field]['NOR'] = fields_NOR[i]
        dataFields_dict[field]['ENG'] = fields_ENG[i]
    
    return dataFields_dict

# === list of the fields requested to be extracted   
def get_fields(prmpt_settings):
    # function to get a list of all he requested fields in the prompt 
    reqst_fields = []
        # Name
    if prmpt_settings.name_Flag == True:
        reqst_fields.append('name')
         # ID
    if prmpt_settings.id_Flag == True:
        reqst_fields.append('ID')
        # Address
    if prmpt_settings.adrs_Flag == True:
        reqst_fields.append('address')
        # Type of company
    if prmpt_settings.typ_Flag == True:
        reqst_fields.append('type')
        # Leadership of the company
    if prmpt_settings.lead_Flag == True:
        reqst_fields.append('leadership')
        # Subsidiaries
    if prmpt_settings.subs_Flag == True:
        reqst_fields.append('subsidiaries')
        # Parent Company
    if prmpt_settings.parnt_Flag == True:
        reqst_fields.append('parent')
        # Auditor Name 
    if prmpt_settings.audit_Flag == True:
        reqst_fields.append('auditor')
    
    return reqst_fields

# === dictionary that allows for dot structure  
class DotDict(dict):
    """A dictionary that supports dot notation."""
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]
        

def is_number(item):
    " check whether it is a number "
    # remove extra spaces 
    try:
        item = re.sub(r"\s+", " ", item)
        item = re.sub(r" ", "", item) 
    except TypeError:
        item = item
    if (not item)==False:
        try:
            float(item)  # Attempt to convert to a float
            return True
        except ValueError:
            return False
    else:
        return False

def is_percentage(item):
    "check whether it is a percentage"    
    if isinstance(item, str) and item.strip().endswith("%"):
        try:
            # Remove "%" and convert to a float
            value = float(item.strip()[:-1])
            # Check if the value is in the range 0-100
            return True
        except ValueError:
            return False
    return False
    
class Dic2DotDict(dict):
    """A dictionary that supports dot notation."""
    def __init__(self, *args, **kwargs):
        # Initialize dictionary as usual
        super().__init__(*args, **kwargs)
        # Convert nested dictionaries
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"'DotDict' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"'DotDict' object has no attribute '{name}'")