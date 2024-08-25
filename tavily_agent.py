import streamlit as st
from tavily import TavilyClient
import time

tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

def conduct_research(business_type, context_answers):
    research_results = {}
    
    try:
        # Combine business type and context answers into a single query
        query = f"{business_type}: " + " ".join(context_answers.values())
        
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        
        # Process and categorize the results
        for result in response['results']:
            category = result.get('category', 'Algemeen')
            if category not in research_results:
                research_results[category] = []
            research_results[category].append(result['content'][:200] + "...")  # Truncate long content
        
        # If we don't have enough results, do additional searches
        if len(research_results) < 3:
            additional_queries = [
                f"{business_type} recent news",
                f"{business_type} industry trends",
                f"{business_type} common software"
            ]
            for query in additional_queries:
                time.sleep(1)  # To avoid hitting rate limits
                response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
                for result in response['results']:
                    category = result.get('category', 'Algemeen')
                    if category not in research_results:
                        research_results[category] = []
                    research_results[category].append(result['content'][:200] + "...")
        
        return research_results
    except Exception as e:
        st.error(f"Fout bij het uitvoeren van onderzoek: {str(e)}")
        return {"Fout": [str(e)]}