# IT Solutions Sales Team Assistant

This project is an AI-powered assistant designed to help IT solutions sales teams analyze potential customers and generate tailored sales strategies. The system uses a multi-agent approach with OpenAI's GPT models and the Tavily search API to gather and process information about target companies.

## Project Overview

The IT Solutions Sales Team Assistant utilizes the Swarm library and Tavily API to create a system of four specialized agents that work together to analyze potential customers and generate detailed reports on IT solutions. The system focuses on information extraction, pain point analysis, industry challenge identification, and solution recommendation.

## Core Functionalities

1. Information extraction from company websites and Tavily search results
2. Multi-agent system for comprehensive IT problem analysis
3. Pain point and desired outcome identification
4. Industry-specific challenge and trend analysis
5. Tailored IT solution recommendations
6. Detailed JSON output for each stage of the analysis
7. Error handling and logging for robust operation

## Agents

1. **Info Extractor**: Extracts detailed company information from the provided URL and Tavily search results.
2. **Pain Point Analyzer**: Analyzes pain points and desired outcomes based on the extracted information and additional Tavily searches.
3. **Industry Challenges Identifier**: Identifies industry-wide IT challenges and trends based on the company information and pain points.
4. **Solution Reporter**: Recommends detailed IT solutions based on the identified pain points, desired outcomes, and industry challenges.

## Setup

1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository to your local machine.
3. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

Run the main script:

Project overview
This project utilizes the Swarm library and Tavily API to create a system of four agents that answer user questions and generate detailed reports on IT problem solutions. The system integrates web scraping, OpenAI for information extraction, Supabase for data storage, and Pinecone for vector storage and retrieval.
Core functionalities

Web scraping and information extraction
Multi-agent system for IT problem analysis
Data storage and retrieval
Customized report generation


Current file structure
Copyproject_root/
│
├── agents/
│   ├── agent_triage.py
│   ├── agent_pain.py
│   ├── agent_industry.py
│   ├── agent_solution.py
│   └── __init__.py
│
├── utils/
│   ├── web_scraper.py
│   ├── openai_processor.py
│   ├── supabase_handler.py
│   ├── pinecone_handler.py
│   └── tavily_api.py
│
├── main.py
├── config.py
├── requirements.txt
└── README.md
Detailed workflow

User provides a URL and their company name
Web scraping (Beautiful Soup) extracts information from the URL
OpenAI processes the scraped data to extract customer details (location, name, industry, size)
Customer information is stored in Supabase
Agent A determines which specialized agent to use
Agent B uses Tavily API to identify IT pain points and desired outcomes
Agent C uses Tavily API to discover key industry technology challenges
Relevant information from Agents B and C is vectorized and stored in Pinecone
Agent D generates a detailed report on IT solutions using the user's company technologies
All agent outputs are stored in Supabase

This structure provides an overview of the project, its core functionalities, the roles of each agent, and a basic file structure to implement the system. You can further expand on each section as needed for your specific implementation.
