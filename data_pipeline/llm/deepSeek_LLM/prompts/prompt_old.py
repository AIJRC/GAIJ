" Script with old prompt to extract: info, notes summaries and red flags"


def prompt_data(contextText):
    """ 
    prompt to extract the data from the document

    """
    
    user_question  = """
         Please extract the following information from the tax record, only providing it in a JSON format no explanation of <think>:
        
        - "company_name": The name of the company.
        - "company_id": The company tax number.
        - "company_address": The company's address.
        - "organization_type": The type of the company as specified on the first page of the tax record.
        - "leadership": This is a nested dictionary with a list of all the people in leadership including board members and shareholders following this structure:
            - "name": Full name of person in leadership.
            - "role": Role of the person (if available).
        - "subsidiaries": List of the subsidiaries of the company only include the name (empty list if none).
        - "parent_company": Name of the parent company (null if not available).
        - "mentioned_companies": List of all the companies mentioned in the document.
        - "mentioned_people": List of all the people mentioned extracted from the document.
        - "auditor": Name of the auditor or the firm of the auditor.

    Please ensure that all fields are included, even if they are empty or null.
    Only return the JSON response; do not add explanations, comments, or repeated entries.
    The name of the company can not be: Brønnøysund.
    The address of the company can not be: postboks 900, 8910, Brønnøysund.
   
    """
    #         - "auditor_note": Summary of the note provided by the auditor (null if not provided).

    system_prompt = """ You are a helpful assystant that deals with extracting data from Nowegian Company's Tax records. The user will provide you a tax record of a company and you will output only a JSON format with the data, Please extract the relevant information of this company including:
    name of the company, ID, address, type of organization, subsidiaries, and leadership, financial status, employees number, short report about the financial health of the company.
    Extract it on a JSON of the following format: 
    {
  "company_name": ,
  "company_id": ",
  "company_address": ,
  "organization_type": ,
  "leadership": [{"name": ,       
            "role": }],
  "subsidaries": [],
  "parent company": ,
 "mentioned_companies": [],
 "mentioned_people": [], 
 "auditor":
 }    
    Do not add any explanation in the begining, only provide the JSON. If there is no information for any of the fields have a null entry"""
   # ,
 # "auditor_note":
    return [user_question + contextText,system_prompt]    
    
def prompt_notes(contextText):
    """
    prompt to extract the notes information
    
    """
    user_question  = """
         Please extract the following information from the tax record, only providing it in a JSON format no explanation of <think>:
        
        - "Note": A nested dictionary with a summary of all the notes present in the document
           - "number": number of the note
           - "title": translated title of the extracted note
           - "summary": sumarized content of the extracted note
        - "Footnotes": A nested dictionary with the summary of all the found footnotes 
            - "summary": summary of the footnote 
    """
    
    system_prompt = """
    You are an expert in extracting structured data from Norwegian company tax records and translating it to English. 
    The user will provide a tax record document. 
    The document is divided into several pages, each containing different sections that may include: general information, income statement, balance, notes. Each page may also include footnotes at the end of the page.
    Your role is to extract relevant information from the note section in a structured JSON format.
    Extraction Rules
    Notes Extraction:
        Identify all sections following this structure: Note <number> - <title> (e.g., Note 2 - Skattekostnad på ordinært resultat).
        Extract the note number (number) and note title (title).
        Identify the note content, which starts after the title and continues until the next note appears.
        Summarize the core details of the note, ensuring any mentioned companies, persons, or key financial details are retained and translate them into English. Provide at least two to three sentences.
        
        Keep the extracted title.
        Translate keeping the summary in English.

    Footnotes Extraction:
        Identify footnotes, which typically after the slide number and before the next page number.
        Summarize the key details from the footnotes in English.
        
    Expected Output Format (JSON)

    Your response must be strictly in JSON format with the following structure:
    {
  "notes": [
    {
      "number": "<Extracted Note Number>",
      "title": "<Extracted Note Title>",
      "summary": "<Summarized Content in English>"
    },
    {
      "number": "<Extracted Note Number>",
      "title": "<Translated Note Title>",
      "summary": "<Summarized Content in English>"
    }
  ],
  "footnotes": [
    {
      "summary": "<Summarized Footnote Content in English>"
    }
  ]
}

    Additional Instructions
    Keep the text in English
    Do not include any extra text or explanations outside of the JSON output.
    Ensure all extracted data is accurate and concise, while keeping key financial details.
    Maintain original Norwegian names of companies and individuals, but translate the explanatory text into English.

    
    
    """
    return [user_question + contextText,system_prompt]     


def prompt_RF(contextText):
    """
    prompt to extract information about the red flags provided by the journalists
    
    """
    user_question  = """
         Please extract the following information from the tax record, only providing it in a JSON format no explanation of <think>:
        
        - "Red_flags": A nested dictionary with information about the different aspects of the document
            - "one_off_expense": Review the financial statement provided and extract any details related to large one-off items, extraordinary income, or extraordinary costs. Focus on sections such as 'Exceptional Items,' 'Non-Recurring Items,' or 'Notes to the Financial Statements.' Include the nature of the item, the amount, and any relevant explanations.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "internal_transactions": Please identify and extract any information related to frequent internal transactions between group companies. Include details such as the nature of the transactions (e.g., sales, services, loans), the companies involved, the frequency of the transactions, and any amounts or financial impacts mentioned.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "unclear_instruments": Please identify and extract any information related to unclear or complicated financial instruments. Include details such as the type of instrument (e.g., derivatives, structured products, swaps), the nature of the complexity (e.g., valuation methods, risks, terms and conditions), and any explanations or disclosures provided about their use or impact.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "change_auditor": Review the document and extract any information related to a change of auditor, particularly instances where the change appears to lack a clear or justified reason. Focus on sections such as 'Auditor's Report,' 'Notes to the Financial Statements,' 'Corporate Governance,' or 'Regulatory Disclosures.' Include details such as the timing of the change, the companies involved, any stated reasons for the change, and whether the explanation provided is vague, insufficient, or raises concerns.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "change_accounting": Please identify and extract any information related to changes in accounting principles or policies that have led to improved financial results. Include details such as the nature of the change (e.g., revenue recognition, depreciation methods), the rationale provided for the change, the financial impact (e.g., increased revenue, reduced expenses), and any disclosures or explanations about how the change affects the reported results.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "adjusments": Review the document and extract any information related to adjustments made to previous years' accounts. Focus on sections such as 'Notes to the Financial Statements,' 'Prior Period Adjustments,' 'Restatements,' or 'Changes in Accounting Estimates.' Include details such as the nature of the adjustment, the financial impact, the years affected, and any explanations or justifications provided for the adjustments.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "negative_wProfit": Please identify and extract any information related to instances where the company reports negative operational cash flows despite showing a profit on the income statement. Include details such as the reasons for the discrepancy (e.g., timing differences, working capital changes, non-cash items), the specific cash flow items contributing to the negative operational cash flow (e.g., accounts receivable, inventory, accounts payable), and any explanations or disclosures provided by the company.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "dependency": Review the document and extract any information related to an increasing dependence on financing to cover operational expenses. Focus on sections such as 'Cash Flow Statement,' 'Management Discussion and Analysis (MD&A),' 'Notes to the Financial Statements,' 'Financing Activities,' or 'Liquidity and Capital Resources.' Include details such as the types of financing used, the reasons for the increased reliance, the financial impact, and any explanations or disclosures provided by the company.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details
            - "outstanding_receivables": Please identify and extract any information related to large outstanding receivables. Include details such as the amount of receivables, the aging of receivables (e.g., overdue amounts), the reasons provided for the high balances (e.g., slow-paying customers, economic conditions), any concerns raised about bad debts or collection risks, and whether there are indications of potential accounting manipulation (e.g., revenue recognition issues, unusual trends).
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details  
            - "guarantee": Review the document and extract any information related to guarantee obligations or pledges that are not clearly explained. Focus on sections such as 'Notes to the Financial Statements,' 'Contingencies,' 'Commitments and Guarantees,' or 'Risk Factors.' Include details such as the nature of the guarantee or pledge, the parties involved, the amounts or scope of the obligation, and any areas where the explanation is vague, incomplete, or raises concerns about transparency.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details  
            - "pensions": Review the document and extract any information related to large pension obligations that may create liquidity problems. Focus on sections such as 'Notes to the Financial Statements,' 'Pension Plans,' 'Employee Benefits,' 'Liquidity and Capital Resources,' or 'Risk Factors.' Include details such as the size of the pension obligations, the funding status of the pension plans, the potential impact on cash flow and liquidity, and any concerns or disclosures about the company's ability to meet these obligations.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details  
            - "hidden_leasing": Review the document and extract any information related to hidden or undisclosed leasing obligations, particularly operating leases that may obscure the company's true liabilities. Focus on sections such as 'Notes to the Financial Statements,' 'Leases,' 'Commitments and Contingencies,' or 'Off-Balance Sheet Arrangements.' Include details such as the nature of the leases, the amounts involved, the duration of the leases, and any concerns or disclosures about how these obligations are reported (or not reported) in the financial statements.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "tax_benefits": Review the document and extract any information related to large deferred tax benefits where there is insufficient probability of realization. Focus on sections such as 'Notes to the Financial Statements,' 'Deferred Tax Assets,' 'Income Taxes,' 'Valuation Allowances,' or 'Risk Factors.' Include details such as the size of the deferred tax assets, the reasons for the uncertainty around their realization, any disclosures about valuation allowances, and any concerns or risks highlighted by the company or auditors.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "tax_payments": Review the document and extract any information related to abnormally low or varying tax payments, or outstanding tax payments. Focus on sections such as 'Notes to the Financial Statements,' 'Income Taxes,' 'Tax Disputes,' 'Contingencies,' or 'Risk Factors.' Include details such as the amounts of tax payments, the reasons for the anomalies, any disclosures about tax disputes or contingencies, and any concerns or risks highlighted by the company or auditors regarding tax compliance or liabilities.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "auditor_reservations": Please identify and extract any information where the auditor expresses reservations, qualifications, or highlights significant uncertainties in their report. Include details such as the nature of the reservation or uncertainty (e.g., going concern issues, material misstatements, limitations in audit scope), the specific areas of the financial statements affected, and any explanations or recommendations provided by the auditor.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "no_audit":Review the document and extract any information related to a lack of audit or frequent changes in auditors. Focus on sections such as 'Auditor's Report,' 'Corporate Governance,' 'Regulatory Disclosures,' or 'Notes to the Financial Statements.' Include details such as the reasons for the lack of audit or auditor changes, the frequency of auditor changes, any concerns raised about the quality or independence of the audit process, and any disclosures or explanations provided by the company.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "concern":Please identify and extract any information related to 'Going Concern' issues, where the company or auditor expresses doubts about the company's ability to continue operating. Include details such as the reasons for the uncertainty (e.g., financial losses, liquidity problems, debt defaults), the company's plans to address the issues (e.g., restructuring, refinancing), and any disclosures or warnings provided by the company or auditor about the risks to continued operations.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "change_address": Review the document and extract any information related to a sudden change of address by the company to another part of Norway. Focus on sections such as 'Corporate Information,' 'Regulatory Disclosures,' 'Announcements,' or 'Notes to the Financial Statements.' Include details such as the old and new addresses, the reasons provided for the change (if any), the timing of the change, and any concerns or implications raised about the move.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details 
            - "balance_values": Please identify and extract any information related to write-downs of values in the balance sheet. Include details such as the assets affected (e.g., inventory, goodwill, property, plant, and equipment), the reasons for the write-downs (e.g., impairment, market conditions, obsolescence), the amounts written down, and any explanations or disclosures provided by the company about the impact on financial performance.
                - "flag": true of false depending whether it is present in the document
                - "details": if true a detailed explanation of the details
            - "delivery_date": Please identify the delivery date of the tax record
            - "auditor_name": Please identify the name of the auditor and/or the company

    """
    
    system_prompt = """
    You are an expert in extracting structured data from Norwegian company tax records and translating it to English. 
    The user will provide a tax record document. 
    The document is divided into several pages, each containing different sections that may include: general information, income statement, balance, notes. Each page may also include footnotes at the end of the page.
    Your role is to extract relevant information requested by the user and provide it in the following structure. 
        
    Expected Output Format (JSON)

    Your response must be strictly in JSON format with the following structure:
    {
  "Red_flags": 
    {
      "one_off_expense": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "internal_transactions": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "unclear_instruments": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "change_auditor": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "change_accounting": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "adjusments": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "negative_wProfit": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "dependency": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "outstanding_receivables": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "guarantee": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "pensions": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "hidden_leasing": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "tax_payments": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "tax_benefits": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "auditor_reservations": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "no_audit": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },

    "concern": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "change_address": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "balance_values": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "delivery_date": "<date of delivery of tax record>",
    "auditor_name": "<name of the auditor>"
            
    }
    
}

    Additional Instructions
    Keep the text in English
    Do not include any extra text or explanations outside of the JSON output.
    Ensure all extracted data is accurate and concise, while keeping key financial details.
    Maintain original Norwegian names of companies and individuals, but translate the explanatory text into English.

    
    
    """
    return [user_question + contextText,system_prompt]    


def prompt_rf_v2(contextText):
    """
    prompt to extract information about the red flags provided by the journalists v2
    
    """
    user_question  = """
    Please extract the following information from the tax record, providing it in a JSON format. Focus only on explicitly stated information in the document. If a red flag is not explicitly mentioned, mark it as `false` with no details.

- "Red_flags": A nested dictionary with information about the different aspects of the document. For each red flag, provide:
  - "flag": `true` if the red flag is explicitly mentioned in the document, otherwise `false`.
  - "details": If `true`, provide a detailed explanation of the red flag based on the document, that includes evidence from where it was taken. If `false`, set to `null`.

Categories:
1. "one_off_expense": Large, non-recurring items explicitly mentioned in the financial statements or notes.
2. "internal_transactions": Transactions between group companies explicitly described in the document.
3. "unclear_instruments": Complex financial instruments (e.g., derivatives, swaps) with unclear valuation methods or risks.
4. "change_auditor": A change in auditor, explicitly mentioned with or without reasons provided.
5. "change_accounting": Changes in accounting principles or policies explicitly described in the notes.
6. "adjustments": Adjustments to previous years' accounts explicitly mentioned in the notes.
7. "negative_wProfit": Negative operational cash flow explicitly mentioned despite a profit on the income statement.
8. "dependency": Explicit reliance on financing to cover operational expenses, as stated in the cash flow statement or notes.
9. "outstanding_receivables": Large outstanding receivables explicitly mentioned, including aging or collection risks.
10. "guarantee": Guarantee obligations or pledges explicitly described in the notes.
11. "pensions": Large pension obligations explicitly mentioned, including funding status or liquidity concerns.
12. "hidden_leasing": Hidden or off-balance sheet leasing obligations explicitly described in the notes.
13. "tax_benefits": Large deferred tax assets explicitly mentioned, with uncertainty about realization.
14. "tax_payments": Abnormally low or varying tax payments explicitly mentioned, including disputes or contingencies.
15. "auditor_reservations": Auditor reservations or qualifications explicitly stated in the auditor's report.
16. "no_audit": Explicit statement that the financial statements were not audited.
17. "concern": Explicit concerns about the company's ability to continue operations (going concern).
18. "change_address": A sudden change of address explicitly mentioned in the document.
19. "balance_values": Write-downs of asset values explicitly mentioned in the notes.

Additional Fields:
- "delivery_date": The date the tax record was delivered (explicitly stated in the document).
- "auditor_name": The name of the auditor explicitly mentioned in the document (if applicable).

Example: This is just an example with the structure it should have it shull not be copied
{
  "Red_flags": {
    "one_off_expense": {
      "flag": false,
      "details": null
    },
    "internal_transactions": {
      "flag": true,
      "details": "The company received a loan with the concept of car of NOK 5 million from a related party named X, as disclosed in the notes."
    },
    ...
  },
  "delivery_date": "2021-05-20",
  "auditor_name": null
}
"""
    system_prompt = """
    You are an expert in extracting structured data from Norwegian company tax records and translating it to English. 
    The user will provide a tax record document. 
    The document is divided into several pages, each containing different sections that may include: general information, income statement, balance, notes. Each page may also include footnotes at the end of the page.
    Your role is to extract relevant information requested by the user and provide it in the following structure. 
        
    Expected Output Format (JSON)

    Your response must be strictly in JSON format with the following structure:
    {
  "Red_flags": 
    {
      "one_off_expense": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "internal_transactions": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "unclear_instruments": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "change_auditor": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "change_accounting": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "adjusments": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "negative_wProfit": {
            "flag": "<True or False>",
            "details": "<if true a detailed description >"
        }
    },
    "dependency": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "outstanding_receivables": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "guarantee": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "pensions": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "hidden_leasing": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "tax_payments": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "tax_benefits": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "auditor_reservations": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "no_audit": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },

    "concern": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "change_address": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "balance_values": {
            "flag": "<True or False>",
            "details": "<if true a summary >"
        }
    },
    "delivery_date": "<date of delivery of tax record>",
    "auditor_name": "<name of the auditor>"
            
    }
    
}

    Additional Instructions
    Keep the text in English
    Do not include any extra text or explanations outside of the JSON output.
    Ensure all extracted data is accurate and concise, while keeping key financial details.
    Maintain original Norwegian names of companies and individuals, but translate the explanatory text into English.

    
    
    """
    return [user_question + contextText,system_prompt]  