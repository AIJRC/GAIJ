" Script with the prompts for extracting red flags - single prompt "



def prompt_RF_v2():
  " prompt to extract red flags form the tax "

  system_prompt = """
You are an expert analyst of Norwegian annual tax records. Your task is to extract EXPLICITLY STATED information about financial risks, transactions, accounting issues, and liquidity concerns.

**Rules:**
1. Only use information directly stated in the document - NO INFERENCES OR ASSUMPTIONS
2. For each category:
   - Set "flag": true **only** if explicitly mentioned
   - Include exact evidence (text quotes, page numbers, section names) in "details" when flag=true
   - If no evidence, set "flag": false and "details": null
3. Use Norwegian accounting terminology from the document
"""

  user_prompt = """
Analyze the tax record and extract information about these categories. ONLY use explicitly stated details:

{
  "finance": {
    "unclear_instruments": "Derivatives, structured products, swaps with complex terms",
    "hidden_leasing": "Undisclosed operating lease obligations",
    "guarantee": "Guarantees/pledges not clearly explained",
    "balance_values": "Asset write-downs (impairments, market declines)",
    "dependency": "Reliance on external financing for operations"
  },
  "transactions": {
    "one_off_expense": "Non-recurring extraordinary transactions",
    "internal_transactions": "Inter-company transactions",
    "outstanding_receivables": "Large receivables with collection risks"
  },
  "accounting": {
    "auditor_reservations": "Auditor qualifications/concerns",
    "change_accounting": "Accounting policy changes",
    "adjustments": "Prior year account adjustments",
    "tax_benefits": "Large deferred tax assets with realization risks", 
    "tax_payments": "Abnormal tax payments/disputes",
    "no_audit": "Unaudited statements",
    "conditional_outcomes": "Pending litigation/claims"   
  },
  "liquidity": {
    "negative_wProfit": "Negative cash flow despite profit",
    "pensions": "Large pension obligations"
  },
  "auditor_name": "Name of auditing firm/person",
  "delivery_date": "Tax record submission date",
  "mentioned_companies": "All the companies mentioned in the document",
  "mentioned_people": "All the people mentioned in the company"
}

Format response as JSON with this structure:
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
  },
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
  },
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
    },
    
  "liquidity": {
    "negative_wProfit": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    },
    "pensions": {
      "flag": "<True or False>",
      "details": "<if true, a detailed description>"
    }
    },
    "delivery_date": "<date of delivery of tax record>",
    "auditor_name": "<name of the auditor>",
    "mentioned_companies": "<list of all the mentioned companies",
    "mentioned_people": "<list of all the mentioned people>"
    
  }
  
     

"""
  return[user_prompt,system_prompt]



def prompt_RF():
    " prompt to extract red flags form the tax "
    
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
  
-**"transactions"**: A nested dictionary containing information about unusual transactions in the document.  

  For each **category**, provide:  
  - **"flag"**: `true` if the category is explicitly mentioned in the document, otherwise `false`.  
  - **"details"**: If `"flag"` is `true`, provide a detailed explanation including relevant evidence, such as page numbers or section references. If `"flag"` is `false`, set `"details"` to `null`.  

  **Categories:**  
  - **"one_off_expense"**: Large extraordinary transactions.
  - **"internal_transactions"**: Transactions between group companies.
  - **"outstanding_receivables"**: Large outstanding receivable. 
  
-**"accounting"**: A nested dictionary containing information about accounting concerns in the document.

    For each category, provide:
        -**"flag"**: true if the category is explicitly mentioned in the document, otherwise false.
        -**"details"**: If "flag" is true, provide a detailed explanation including relevant evidence, such as page numbers or section references. If "flag" is false, set "details" to null.

    **Categories**:
        - **"auditor_reservations"**: Identify any reservations, qualifications, or significant uncertainties expressed by the auditor in their report. Include details such as the nature of the reservation (e.g., going concern issues, material misstatements, limitations in audit scope), the specific areas of the financial statements affected, and any explanations or recommendations provided by the auditor.
        - **"change_accounting"**: Identify changes in accounting principles or policies explicitly described in the notes.
        - **"adjustments"**: Identify adjustments to previous years' accounts explicitly mentioned in the notes.
        - **"tax_benefits"**: Identify large deferred tax assets explicitly mentioned, with uncertainty about their realization.
        - **"tax_payments"**: Identify abnormally low or varying tax payments explicitly mentioned, including disputes or contingencies.
        - **"no_audit"**: Identify any explicit statement that the financial statements were not audited.
        - **"conditional_outcomes"**: Identify ongoing or potential litigation that could lead to large costs. Often found under subheaders such as "Conditional outcomes" or "Claims."

    **Additionally extractc the following:**
        - **"auditor_name"**: Identify the name of the person or company that conducted the audit.
        - **"delivery_date"**: Identify the date on which the tax record was submitted.
    
- **"liquidity"**: A nested dictionary containing information about liquidity or cash flow issues in the document.  

  For each **category**, provide:  
  - **"flag"**: `true` if the category is explicitly mentioned in the document, otherwise `false`.  
  - **"details"**: If `"flag"` is `true`, provide a detailed explanation including relevant evidence, such as page numbers or section references. If `"flag"` is `false`, set `"details"` to `null`.  

  **Categories:**  
  - **"negative_wProfit"**: Negative operational cash flows, while the income statement shows a profit.
  - **"pensions"**: Large pension obligation.

    
     """
     
    system_prompt = """ You are an expert in assessing several aspects of Norwegian annual tax records, including: financial complexity and risk factors, unusual transactions, accounting concerns, and liquidity or cash flow issues. 
    Your task is to analyze a provided tax record document and extract relevant information about the requested aspects. The document is divided into several pages, each containing sections such as general information, income statement, balance sheet, and notes. Each page may also include footnotes.

### Instructions:
1. **Focus on the following aspects:**
    
    - **"finance"**:
        - **Unclear or Complicated Financial Instruments**("unclear_instruments"): Identify derivatives, structured products, swaps, or other instruments with complex valuation methods, risks exposure , or unclear terms.
        - **Hidden or Undisclosed Leasing Obligations** ("hidden_leasing"): Look for operating leases that may obscure the company's true liabilities.
        - **Guarantee Obligations or Pledges** ("guarantee"): Identify any guarantees or pledges that are not clearly explained.
        - **Write-downs of Values** ("balance_values"): Note any write-downs in the balance sheet due to impairment, market conditions, or obsolescence affecting asset valuations.
        - **Dependency on Financing** ("dependency"): Assess whether there is an increased reliance on external financing to cover operations.
    - **"transactions"**:
        - **Large one-off items or extraordinary income/costs** (`one_off_expense`): Identify any non-recurring or extraordinary transactions explicitly mentioned in the financial statements or notes. These are typically reported as separate line items or described in the notes as "unusual," "non-recurring," or "extraordinary."
        - **Frequent internal transactions between group companies** (`internal_transactions`): Identify transactions between group companies (parent and subsidiaries) explicitly described in the document. These may include loans, sales, or other financial arrangements.
        - **Large outstanding receivables** (`outstanding_receivables`): Identify large receivables explicitly mentioned in the document, including any aging or collection risks described in the notes.
    - **"accounting"**:
        -  **Auditor reservations** (`auditor_reservations`): Identify any reservations, qualifications, or significant uncertainties expressed by the auditor in their report. Include details such as the nature of the reservation (e.g., going concern issues, material misstatements, limitations in audit scope), the specific areas of the financial statements affected, and any explanations or recommendations provided by the auditor.
        - **Changes in accounting principles that lead to improved results** (`change_accounting`): Identify changes in accounting principles or policies explicitly described in the notes.
        - **Adjustments to previous years' accounts** (`adjustments`): Identify adjustments to previous years' accounts explicitly mentioned in the notes.
        - **Large deferred tax benefits without sufficient probability of realization** (`tax_benefits`): Identify large deferred tax assets explicitly mentioned, with uncertainty about their realization.
        - **Abnormally low or varying tax payments** (`tax_payments`): Identify abnormally low or varying tax payments explicitly mentioned, including disputes or contingencies.
        - **Lack of audit** (`no_audit`): Identify any explicit statement that the financial statements were not audited.
        - **Ongoing or potential litigations** (`conditional_outcomes`): Identify ongoing or potential litigation that could lead to large costs. Often found under subheaders such as "Conditional outcomes" or "Claims."
        - **Name of the auditor** (`auditor_name`): Identify the name of the person or company that conducted the audit.
        - **Submission date of the annual tax record** (`delivery_date`): Identify the date on which the tax record was submitted.
    - **"liquidity"**:
        - **Negative operational cash flows, while the income statement shows a profit** (`negative_wProfit`): identify and extract any information related to instances where the company reports negative operational cash flows despite showing a profit on the income statement. Include details such as the reasons for the discrepancy (e.g., timing differences, working capital changes, non-cash items), the specific cash flow items contributing to the negative operational cash flow (e.g., accounts receivable, inventory, accounts payable), and any explanations or disclosures provided by the company.
        - **Large pension obligations** (`pensions`): Review the document and extract any information related to large pension obligations that may create liquidity problems. Focus on sections such as 'Notes to the Financial Statements,' 'Pension Plans,' 'Employee Benefits,' 'Liquidity and Capital Resources,' or 'Risk Factors.' Include details such as the size of the pension obligations, the funding status of the pension plans, the potential impact on cash flow and liquidity, and any concerns or disclosures about the company's ability to meet these obligations.

2. **Extraction Rules:**
   - Do not fabricate information. Base your analysis strictly on evidence from the document and not in the provided examples. Do not infer or assume information.
   - If no evidence is found for a specific aspect, set the flag to `False` and leave the details field empty.
   - If an issue is identified set the flag to 'True' on the appropriate field and provide a concise summary of the evidence, including amounts, concepts, and involved parties.
   - After extraction if the flag is set to true, check if there is a possibility the data you extracted is incorrect or fabricated. Be very strict, if the answer is yes, set the flag to false and the details to 'null'.

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
  },
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
  },
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
    },
    "delivery_date": "<date of delivery of tax record>",
    "auditor_name": "<name of the auditor>"
  },
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