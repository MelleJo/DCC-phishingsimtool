import streamlit as st
from tavily import TavilyClient
from typing import List, Dict

# Initialize Tavily client using Streamlit secrets
tavily_api_key = st.secrets["TAVILY_API_KEY"]
tavily = TavilyClient(api_key=tavily_api_key)

def search_info(query: str, num_results: int = 3) -> List[Dict]:
    """
    Search for information using the Tavily Search API.
    
    :param query: The search query
    :param num_results: Number of results to return
    :return: List of dictionaries containing search results
    """
    try:
        response = tavily.search(query=query, max_results=num_results)
        return response['results']
    except Exception as e:
        st.error(f"Error occurred while searching: {e}")
        return []

def get_authentic_info(context: str, info_type: str) -> str:
    """
    Get authentic information based on the context and type of information needed.
    
    :param context: The context of the phishing email
    :param info_type: Type of information needed (e.g., 'website', 'email', 'person')
    :return: A string containing the authentic information
    """
    query = f"{context} {info_type}"
    results = search_info(query)
    
    if not results:
        return f"No authentic {info_type} found"
    
    if info_type == 'website':
        return results[0]['url']
    elif info_type == 'email':
        # Extract email from the content (this is a simple example and might need refinement)
        for result in results:
            content = result['content']
            if '@' in content:
                return content.split('@')[0] + '@example.com'  # Obfuscate the domain for safety
    elif info_type == 'person':
        return results[0]['title']
    
    return results[0]['content'][:100]  # Return a snippet of the content for other types

# Example usage (only run this if the file is executed directly)
if __name__ == "__main__":
    context = "tech startup in Silicon Valley"
    print(get_authentic_info(context, 'website'))
    print(get_authentic_info(context, 'email'))
    print(get_authentic_info(context, 'person'))