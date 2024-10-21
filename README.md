# IT Solutions Sales Team Assistant

This project is an AI-powered assistant designed to help IT solutions sales teams analyze potential customers and generate tailored sales strategies. The system uses a multi-agent approach with OpenAI's GPT models and the Tavily search API to gather and process information about target companies.

## Features

- Multi-agent system for comprehensive analysis
- Integration with Tavily API for relevant and recent information retrieval
- Detailed JSON output for each stage of the analysis
- Error handling and logging for robust operation

## Setup

1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository to your local machine.
3. Install the required dependencies:   ```
   pip install -r requirements.txt   ```
4. Create a `.env` file in the project root directory and add your API keys:   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here   ```

## Usage

Run the main script:
