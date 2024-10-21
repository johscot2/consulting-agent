# Import necessary libraries
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from swarm import Swarm, Agent
from tavily import TavilyClient
import json
import logging
from datetime import datetime
import requests
import re

# Set up logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize clients
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not openai_api_key or not tavily_api_key:
    raise ValueError("API keys not found in environment variables")

client = Swarm()
tavily_client = TavilyClient(api_key=tavily_api_key)

def tavily_search(query):
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            max_results=10,
            sort_by="relevance_and_recency"
        )
        return response
    except Exception as e:
        logger.error(f"Tavily search error: {str(e)}")
        return {"error": str(e)}

# Define agents
info_extractor = Agent(
    name="Info Extractor",
    model="gpt-4o",
    instructions="""
    Extract detailed company information from the provided URL and Tavily search results.
    Focus on recent and relevant information about the company's IT infrastructure, size, industry, and recent developments. Size is based off the number of employees at the company and is either small, medium, or large.
    Your response MUST ONLY contain a valid JSON object with the following structure, and nothing else:
    {
        "company_name": "string",
        "industry": "string",
        "size": "string",
        "location": "string",
        "it_infrastructure": {
            "current_systems": ["string", ...],
            "technologies_used": ["string", ...],
            "recent_upgrades": ["string", ...]
        },
        "recent_developments": ["string", ...],
        "key_decision_makers": ["string", ...],
        "business_goals": ["string", ...],
        "challenges": ["string", ...],
        "competitors": ["string", ...],
        "budget_information": "string",
        "compliance_requirements": ["string", ...],
        "customer_base": "string",
        "growth_plans": "string",
        "website_keywords": ["string", ...],
        "social_media_presence": {
            "platforms": ["string", ...],
            "activity_level": "string"
        },
        "news_mentions": [
            {
                "title": "string",
                "date": "string",
                "summary": "string",
                "url": "string"
            },
            ...
        ],
        "tavily_sources": ["url", ...]
    }
    Ensure that you fill in as many fields as possible based on the available information. If information for a field is not available, use "Not available" as the value.
    Use the Tavily search function to supplement information not found on the company website.
    Include all relevant Tavily search result URLs in the 'tavily_sources' field.
    """,
    functions=[tavily_search],
    api_key=openai_api_key
)

pain_point_analyzer = Agent(
    name="Pain Point Analyzer",
    model="gpt-4o",
    instructions="""
    Analyze pain points and desired outcomes based on the extracted information and Tavily search results.
    Use the company information provided by the Info Extractor to craft targeted Tavily search queries.
    Focus on identifying specific IT-related challenges the company is facing and their desired technological improvements.
    Provide a detailed analysis of each pain point and desired outcome, including potential impacts on the business.
    Include specific facts, statistics, and quotes from the Tavily search results to support your analysis.
    Your response MUST be a valid JSON object with the following structure:
    {
        "pain_points": [
            {
                "point": "string",
                "description": "string (200-300 words)",
                "impact": "string (100-150 words)",
                "supporting_facts": ["string", ...],
                "sources": ["url", ...]
            },
            ...
        ],
        "desired_outcomes": [
            {
                "outcome": "string",
                "description": "string (200-300 words)",
                "benefit": "string (100-150 words)",
                "supporting_facts": ["string", ...],
                "sources": ["url", ...]
            },
            ...
        ]
    }
    Ensure each pain point and desired outcome is thoroughly explained and supported by facts from the Tavily search results.
    """,
    functions=[tavily_search],
    api_key=openai_api_key
)

industry_challenges_identifier = Agent(
    name="Industry Challenges Identifier",
    model="gpt-4o",
    instructions="""
    Identify industry-wide IT challenges based on the extracted information, pain points, and Tavily search results.
    Use the company information and industry details provided by the Info Extractor to craft targeted Tavily search queries.
    Focus on recent trends, regulatory changes, and technological advancements affecting the company's specific industry.
    Provide a comprehensive analysis of how these challenges might impact the company specifically.
    Include detailed examples, case studies, and statistics from the Tavily search results to support your analysis.
    Your response MUST be a valid JSON object with the following structure:
    {
        "industry_challenges": [
            {
                "challenge": "string",
                "description": "string (200-300 words)",
                "impact": "string (100-150 words)",
                "supporting_facts": ["string", ...],
                "sources": ["url", ...]
            },
            ...
        ],
        "trends": [
            {
                "trend": "string",
                "description": "string (200-300 words)",
                "potential_impact": "string (100-150 words)",
                "supporting_facts": ["string", ...],
                "sources": ["url", ...]
            },
            ...
        ]
    }
    Ensure each challenge and trend is thoroughly explained and supported by specific examples and data from the Tavily search results.
    """,
    functions=[tavily_search],
    api_key=openai_api_key
)

solution_reporter = Agent(
    name="Solution Reporter",
    model="gpt-4o",
    instructions="""
    Recommend detailed IT solutions based on the identified pain points, desired outcomes, and industry challenges.
    Use the company information, pain points, and industry challenges identified by previous agents to craft targeted Tavily search queries about the selling company's solutions.
    The selling company will be provided by the user. Ensure all recommendations are specific to products and services offered by this company.
    Focus on solutions offered by the selling company that directly address the customer's needs.
    Provide specific product recommendations, implementation strategies, and potential benefits for each solution.
    Include relevant case studies, success stories, and detailed statistics from the Tavily search results.
    Your response MUST be a valid JSON object with the following structure:
    {
        "selling_company": "string",
        "solutions": [
            {
                "product": "string",
                "description": "string (200-300 words)",
                "addresses": ["pain_point_or_challenge", ...],
                "benefits": ["string", ...],
                "implementation": "string (150-200 words)",
                "case_study": "string (200-250 words)",
                "supporting_facts": ["string", ...],
                "sources": ["url", ...]
            },
            ...
        ]
    }
    Ensure each solution is thoroughly explained, clearly linked to the customer's needs, and supported by specific examples and data from the Tavily search results.
    All solutions must be products or services offered by the selling company provided by the user.
    """,
    functions=[tavily_search],
    api_key=openai_api_key
)

def clean_and_parse_json(raw_content):
    # Remove any markdown formatting and find JSON content
    clean_content = raw_content.replace('```json', '').replace('```', '').strip()
    json_match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
    
    if json_match:
        json_content = json_match.group(1)
        print("Extracted JSON content:", json_content[:500] + "..." if len(json_content) > 500 else json_content)
        logger.debug(f"Extracted JSON content: {json_content}")
    else:
        print("No JSON object found in the content")
        logger.error(f"No JSON object found. Raw content: {clean_content}")
        return None

    # Parse the JSON
    try:
        parsed_json = json.loads(json_content)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        print(f"Problematic content: {json_content[:500]}...")
        logger.error(f"JSON Decode Error: {str(e)}")
        logger.error(f"Problematic content: {json_content}")
        return None

def main():
    logger.debug("Starting main function")
    print("Welcome to the IT Solutions Sales Team!")
    
    company_url = input("Please enter the customer's company website URL: ")
    logger.debug(f"User input company URL: {company_url}")

    combined_output = {}

    try:
        # Run Info Extractor
        logger.debug("Running Info Extractor")
        info_response = client.run(info_extractor, [{"role": "user", "content": f"Extract detailed info from: {company_url}"}])
        raw_content = info_response.messages[-1]["content"]
        logger.debug(f"Raw Info Extractor output: {raw_content}")
        company_info = clean_and_parse_json(raw_content)
        if company_info:
            combined_output["company_info"] = company_info
        else:
            print("Failed to parse company info. Please check the logs and try again.")
            return

        # Run Pain Point Analyzer
        logger.debug("Running Pain Point Analyzer")
        pain_response = client.run(pain_point_analyzer, [
            {"role": "system", "content": "Use the following company info for context:"},
            {"role": "user", "content": json.dumps(company_info)},
            {"role": "user", "content": "Analyze pain points and desired outcomes based on this information. Use Tavily to search for additional relevant information."}
        ])
        raw_content = pain_response.messages[-1]["content"]
        logger.debug(f"Raw Pain Point Analyzer output: {raw_content}")
        pain_points = clean_and_parse_json(raw_content)
        if pain_points:
            combined_output["pain_points"] = pain_points
        else:
            print("Failed to parse pain points. Please check the logs and try again.")
            return

        # Run Industry Challenges Identifier
        logger.debug("Running Industry Challenges Identifier")
        challenges_response = client.run(industry_challenges_identifier, [
            {"role": "system", "content": "Use the following information for context:"},
            {"role": "user", "content": json.dumps({"company_info": company_info, "pain_points": pain_points})},
            {"role": "user", "content": "Identify industry challenges based on this information. Use Tavily to search for additional relevant information. Ensure your response is a valid JSON object."}
        ])
        raw_content = challenges_response.messages[-1]["content"]
        logger.debug(f"Raw Industry Challenges Identifier output: {raw_content}")
        industry_challenges = clean_and_parse_json(raw_content)
        if industry_challenges:
            combined_output["industry_challenges"] = industry_challenges
        else:
            print("Failed to parse industry challenges. Please check the logs and try again.")
            logger.error("Failed to parse industry challenges")
            # Instead of returning, we'll continue with the process
            combined_output["industry_challenges"] = {"error": "Failed to parse"}

        # Get selling company
        selling_company = input("\nWhat company are you selling for? ")
        logger.debug(f"User input selling company: {selling_company}")
        combined_output["selling_company"] = selling_company

        # Run Solution Reporter
        logger.debug("Running Solution Reporter")
        solution_response = client.run(solution_reporter, [
            {"role": "system", "content": "Use the following information for context:"},
            {"role": "user", "content": json.dumps(combined_output)},
            {"role": "user", "content": f"Recommend solutions from {selling_company} based on this information. Use Tavily to search for specific solutions and case studies from {selling_company}."}
        ])
        raw_content = solution_response.messages[-1]["content"]
        logger.debug(f"Raw Solution Reporter output: {raw_content}")
        solutions = clean_and_parse_json(raw_content)
        if solutions:
            combined_output["solutions"] = solutions
        else:
            print("Failed to parse solutions. Please check the logs and try again.")
            return

        # Save the combined output to a JSON file
        with open('combined_analysis.json', 'w') as f:
            json.dump(combined_output, f, indent=2)
        print("\nCombined analysis has been saved to 'combined_analysis.json'")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        logger.exception("Exception details:")

    # Save whatever we have in combined_output, even if there were errors
    with open('combined_analysis.json', 'w') as f:
        json.dump(combined_output, f, indent=2)
    print("\nAnalysis has been saved to 'combined_analysis.json'")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred in main: {str(e)}")
        logger.exception(f"An error occurred in main: {str(e)}")
