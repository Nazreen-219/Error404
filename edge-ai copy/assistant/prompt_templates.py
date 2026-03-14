def build_prompt(text: str):

    prompt = f"""
You are assisting a CSC operator.

The operator will speak in Hindi or Hinglish.

Extract information from the sentence and return structured output.

Sentence:
{text}

Return ONLY valid JSON.
Do not add markdown fences.
Do not add explanation text.
If a field is unknown, use "unknown" for strings and [] for lists.

Fields:
application_type
documents_present
documents_missing

Example:

{{
"application_type": "sand mining",
"documents_present": ["mining_plan","land_document"],
"documents_missing": ["forest_noc"]
}}
"""

    return prompt
