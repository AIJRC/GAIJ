" Script with the prompts for extracting red flags"



def prompt_finance():
    
    " extract information about financial complexity and risk"
    
    user_question = """ Please analyze the tax record and extract the following information.  
Only provide explicitly stated details—do not infer or assume information.  

- **"finance"**: A nested dictionary containing information about financial complexity and risk factors in the document.  

  For each **category**, provide:  
  - **"flag"**: `true` if the category is explicitly mentioned in the document, otherwise `false`.  
  - **"details"**: If `"flag"` is `true`, provide a detailed explanation including relevant evidence, such as page numbers or section references. If `"flag"` is `false`, set `"details"` to `null`.  

  **Categories:**  
  - **"unclear_instruments"**: Unclear or complicated financial instruments (e.g., derivatives, structured products, swaps).  
  - **"hidden_leasing"**: Hidden or undisclosed leasing obligations (especially operating leases).  
  - **"guarantee"**: Guarantee obligations or pledges.  
  - **"balance_values"**: Write-downs of asset values (e.g., impairments, market downturns).  
  - **"dependency"**: Increased reliance on financing for operations.  

    
     """

    system_prompt = """ You are an expert in assessing financial complexity and risk factors from Norwegian annual tax records. Your task is to analyze a provided tax record document and extract relevant information about the company's financial structure and risk. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.

### Instructions:
1. **Focus on the following aspects:**
   - **Unclear or Complicated Financial Instruments**("unclear_instruments"): Identify derivatives, structured products, swaps, or other instruments with complex valuation methods, risks exposure , or unclear terms.
   - **Hidden or Undisclosed Leasing Obligations** ("hidden_leasing"): Look for operating leases that may obscure the company's true liabilities.
   - **Guarantee Obligations or Pledges** ("guarantee"): Identify any guarantees or pledges that are not clearly explained.
   - **Write-downs of Values** ("balance_values"): Note any write-downs in the balance sheet due to impairment, market conditions, or obsolescence affecting asset valuations.
   - **Dependency on Financing** ("dependency"): Assess whether there is an increased reliance on external financing to cover operations.

2. **Extraction Rules:**
   - Do not fabricate information. Base your analysis strictly on evidence from the document and not in the provided examples. Do not infer or assume information.
   - If no evidence is found for a specific aspect, set the flag to `False` and leave the details field empty.
   - If an issue is identified set the flag to 'True' on the appropriate field and provide a concise summary of the evidence, including amounts, concepts, and involved parties.

3. **Output Format:**
   - Provide the extracted information in the following JSON structure:

```json
{
  "finance": {
    "unclear_instruments": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "hidden_leasing": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "guarantee": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "balance_values": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "dependency": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    }
  }
}
    """
    
    return [user_question,system_prompt]



def prompt_transactions():
    
    " extract information about unusual transactions"
    
    user_question = """ Please analyze the tax record and extract the following information.  
Only provide explicitly stated details—do not infer or assume information.  

- **"transactions"**: A nested dictionary containing information about unusual transactions in the document.  

  For each **category**, provide:  
  - **"flag"**: `true` if the category is explicitly mentioned in the document, otherwise `false`.  
  - **"details"**: If `"flag"` is `true`, provide a detailed explanation including relevant evidence, such as page numbers or section references. If `"flag"` is `false`, set `"details"` to `null`.  

  **Categories:**  
  - **"one_off_expense"**: Large extraordinary transactions.
  - **"internal_transactions"**: Transactions between group companies.
  - **"outstanding_receivables"**: Large outstanding receivable. 
  
    
     """

    system_prompt = """ You are an expert in assessing unusual transactions from Norwegian annual tax records. Your task is to analyze a provided tax record document and extract relevant information about the company's transactions. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.

### Instructions:
1. **Focus on the following aspects:**
   - **Large one-off items or extraordinary income/costs** (`one_off_expense`): Identify any non-recurring or extraordinary transactions explicitly mentioned in the financial statements or notes. These are typically reported as separate line items or described in the notes as "unusual," "non-recurring," or "extraordinary."
   - **Frequent internal transactions between group companies** (`internal_transactions`): Identify transactions between group companies (parent and subsidiaries) explicitly described in the document. These may include loans, sales, or other financial arrangements.
   - **Large outstanding receivables** (`outstanding_receivables`): Identify large receivables explicitly mentioned in the document, including any aging or collection risks described in the notes.

2. **Extraction Rules:**
   - Base your analysis strictly on evidence from the document. Do not infer or assume information.
   - If no evidence is found for a specific aspect, set the flag to `False` and leave the details field empty.
   - If an issue is identified, set the flag to `True` and provide a concise summary of the evidence, including amounts, concepts, and involved parties.

3. **Output Format:**
   - Provide the extracted information in the following JSON structure:

```json
{
  "transactions": {
    "one_off_expense": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "internal_transactions": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "outstanding_receivables": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    }
  }
}
    """
    
    return [user_question,system_prompt]
    
    
    
def prompt_accounting():
    
    " extract information about accounting concerns"
    
    user_question = """ Please analyze the tax record and extract the following information.
Only provide explicitly stated details—do not infer or assume information.

    "accounting": A nested dictionary containing information about accounting concerns in the document.

    For each category, provide:
        - "flag": true if the category is explicitly mentioned in the document, otherwise false.
        - "details": If "flag" is true, provide a detailed explanation including relevant evidence, such as page numbers or section references. If "flag" is false, set "details" to null.

    Categories:
        - "auditor_reservations": Identify any reservations, qualifications, or significant uncertainties expressed by the auditor in their report. Include details such as the nature of the reservation (e.g., going concern issues, material misstatements, limitations in audit scope), the specific areas of the financial statements affected, and any explanations or recommendations provided by the auditor.
        - "change_accounting": Identify changes in accounting principles or policies explicitly described in the notes.
        - "adjustments": Identify adjustments to previous years' accounts explicitly mentioned in the notes.
        - "tax_benefits": Identify large deferred tax assets explicitly mentioned, with uncertainty about their realization.
        - "tax_payments": Identify abnormally low or varying tax payments explicitly mentioned, including disputes or contingencies.
        - "no_audit": Identify any explicit statement that the financial statements were not audited.
        - "conditional_outcomes": Identify ongoing or potential litigation that could lead to large costs. Often found under subheaders such as "Conditional outcomes" or "Claims."

    Additionally extractc the following:
    "auditor_name": Identify the name of the person or company that conducted the audit.
    "delivery_date": Identify the date on which the tax record was submitted.
     """

    system_prompt = """ You are an expert in assessing accounting concerns from Norwegian annual tax records. Your task is to analyze a provided tax record document and extract relevant information about the company's accounting concerns. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.


### Instructions:
1. **Focus on the following aspects:**
    -  **Auditor reservations** (`auditor_reservations`): Identify any reservations, qualifications, or significant uncertainties expressed by the auditor in their report. Include details such as the nature of the reservation (e.g., going concern issues, material misstatements, limitations in audit scope), the specific areas of the financial statements affected, and any explanations or recommendations provided by the auditor.
    - **Changes in accounting principles that lead to improved results** (`change_accounting`): Identify changes in accounting principles or policies explicitly described in the notes.
    - **Adjustments to previous years' accounts** (`adjustments`): Identify adjustments to previous years' accounts explicitly mentioned in the notes.
    - **Large deferred tax benefits without sufficient probability of realization** (`tax_benefits`): Identify large deferred tax assets explicitly mentioned, with uncertainty about their realization.
    - **Abnormally low or varying tax payments** (`tax_payments`): Identify abnormally low or varying tax payments explicitly mentioned, including disputes or contingencies.
    - **Lack of audit** (`no_audit`): Identify any explicit statement that the financial statements were not audited.
    - **Ongoing or potential litigations** (`conditional_outcomes`): Identify ongoing or potential litigation that could lead to large costs. Often found under subheaders such as "Conditional outcomes" or "Claims."
    - **Name of the auditor** (`auditor_name`): Identify the name of the person or company that conducted the audit.
    - **Submission date of the annual tax record** (`delivery_date`): Identify the date on which the tax record was submitted.

2. **Extraction Rules:**
   - Do not fabricate information. Base your analysis strictly on evidence from the document and not in the provided examples. Do not infer or assume information.
   - If no evidence is found for a specific aspect, set the flag to `False` and leave the details field empty.
   - If an issue is identified set the flag to 'True' on the appropriate field and provide a concise summary of the evidence, including amounts, concepts, and involved parties.

3. **Output Format:**
   - Provide the extracted information in the following JSON structure:

```json
{
  "accounting": {
    "auditor_reservations": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "concern": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "change_auditor": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "change_accounting": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "adjusments": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "tax_benefits": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "tax_payments": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "no_audit": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "conditional_outcomes": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    }
  },
    "delivery_date": "<date of delivery of tax record>",
    "auditor_name": "<name of the auditor>"
  
}
    """
    
    return [user_question,system_prompt]



def prompt_liquidity():
    " extract information about liquidity or cash flow issues"
    
    user_question = """ Please analyze the tax record and extract the following information.  
Only provide explicitly stated details—do not infer or assume information.  

- **"liquidity"**: A nested dictionary containing information about liquidity or cash flow issues in the document.  

  For each **category**, provide:  
  - **"flag"**: `true` if the category is explicitly mentioned in the document, otherwise `false`.  
  - **"details"**: If `"flag"` is `true`, provide a detailed explanation including relevant evidence, such as page numbers or section references. If `"flag"` is `false`, set `"details"` to `null`.  

  **Categories:**  
  - **"negative_wProfit"**: Negative operational cash flows, while the income statement shows a profit.
  - **"pensions"**: Large pension obligation.

  
    
     """

    system_prompt = """ You are an expert in assessing liquidity or cash flow issues from Norwegian annual tax records. Your task is to analyze a provided tax record document and extract relevant information about the company's liquidity issues. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.

### Instructions:
1. **Focus on the following aspects:**
   - **Negative operational cash flows, while the income statement shows a profit** (`negative_wProfit`): identify and extract any information related to instances where the company reports negative operational cash flows despite showing a profit on the income statement. Include details such as the reasons for the discrepancy (e.g., timing differences, working capital changes, non-cash items), the specific cash flow items contributing to the negative operational cash flow (e.g., accounts receivable, inventory, accounts payable), and any explanations or disclosures provided by the company.
   - **Large pension obligations** (`pensions`): Review the document and extract any information related to large pension obligations that may create liquidity problems. Focus on sections such as 'Notes to the Financial Statements,' 'Pension Plans,' 'Employee Benefits,' 'Liquidity and Capital Resources,' or 'Risk Factors.' Include details such as the size of the pension obligations, the funding status of the pension plans, the potential impact on cash flow and liquidity, and any concerns or disclosures about the company's ability to meet these obligations.
2. **Extraction Rules:**
   - Base your analysis strictly on evidence from the document. Do not infer or assume information.
   - If no evidence is found for a specific aspect, set the flag to `False` and leave the details field empty.
   - If an issue is identified, set the flag to `True` and provide a concise summary of the evidence, including amounts, concepts, and involved parties.

3. **Output Format:**
   - Provide the extracted information in the following JSON structure:

```json
{
  "liquidity": {
    "negative_wProfit": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "pensions": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    }
    
  }
}
    """
    
    return [user_question,system_prompt]
    
    
def prompt_wordsContext(words):
    " extract the context in which the words of interest have been found"
    
    user_question = f""" Please analyze the tax record and extract the following information.  
Only provide explicitly stated details—do not infer or assume information.  

- **"words"**: A nested dictionary containing the sentence in which each of the words in the lists of {words} was employed.

  For each **word**, provide:  
  - **"sentence"**: the sentence in which the word was used.

    
     """
    
    
    
    system_prompt = f""" You are an expert extracting the context in which certain words have been employed from a from Norwegian annual tax records. Your task is to analyze a provided tax record document and extract the context in which the relevant words were used. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.

### Instructions:
1. **Focus on the following words:**
   -  {words}
   -  extract the sentence in which each of them were employed
2. **Extraction Rules:**
   - Base your analysis strictly on evidence from the document. Do not infer or assume information.
 
3. **Output Format:**
   - Provide the extracted information in the following JSON structure:""" + """

```json
{
  "flagged_words": {
    "word": {
      "sentence": "setence in which the word was used",
    },
    
  }
}
    """
    return [user_question,system_prompt]