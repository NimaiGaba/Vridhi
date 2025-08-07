## Working

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Add parent dir

from llm_config import llm

def get_company_profile(company_name: str) -> str:
    prompt = f"Give a very  short 2-3 line business description of the company '{company_name}'. Include industry, main business, and sector."
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    company = input("Enter company name: ")
    print(get_company_profile(company))
