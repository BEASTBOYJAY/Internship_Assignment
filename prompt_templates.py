SUMMARIZER_TEMPLATE = """
You are an expert Legal Analyst and Policy Summarizer.
Please summarize the legislation/Act provided below.

Your summary must adhere to the following strict constraints:
1. Format: A single list of 5–10 bullet points total.
2. Content Focus: You must extract and cover the following aspects:
   - Purpose of the Act
   - Key definitions
   - Eligibility criteria
   - Obligations/Duties imposed
   - Enforcement elements (penalties, authorities, etc.)

Act Text:
"{context}"

Summary:
"""
JSON_EXTRACTION_TEMPLATE = """You are a legal analyst assistant. Your task is to analyze the provided legislative text 
    and extract specific clauses into a structured JSON format.

    Extract the following sections:
    1. Definitions: Key terms defined in the text.
    2. Obligations: Duties that must be performed.
    3. Responsibilities: Specific areas of authority or accountability.
    4. Eligibility: Criteria for qualification.
    5. Payments / Entitlements: Financial details, fees, or rights to benefits.
    6. Penalties / Enforcement: Consequences for non-compliance.
    7. Record-keeping / Reporting: Requirements for maintaining data or submitting reports.

    If a section is not found in the text, set the value to "Not mentioned".

    {format_instructions}

    LEGISLATIVE TEXT:
    {context}
    """

LESGISLATIVE_CHECK_TEMPLATE = """You are a legislative compliance auditor. Analyze the provided text against the following 6 mandatory rules.

    LEGISLATIVE TEXT:
    {context}

    RULES TO CHECK:
    1. Act must define key terms (e.g., Definitions section).
    2. Act must specify eligibility criteria.
    3. Act must specify responsibilities of the administering authority.
    4. Act must include enforcement or penalties.
    5. Act must include payment calculation or entitlement structure.
    6. Act must include record-keeping or reporting requirements.

    INSTRUCTIONS:
    - Analyze ALL 6 rules.
    - For each rule, determine if it passes or fails based on the text.
    - "status": "pass" if present, "fail" if missing.
    - "evidence": Cite the Section number or quote the text. If missing, write "Not found".
    - "confidence": An integer (0-100).

    {format_instructions}
    """
