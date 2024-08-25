import streamlit as st
from tavily import TavilyClient
from typing import List, Dict, Tuple
from config import get_tavily_api_key

# Initialize Tavily client using Streamlit secrets
tavily_api_key = get_tavily_api_key()
tavily = TavilyClient(api_key=tavily_api_key)

def search_info(query: str, num_results: int = 3) -> Tuple[List[Dict], Dict]:
    """
    Search for information using the Tavily Search API.
    
    :param query: The search query
    :param num_results: Number of results to return
    :return: Tuple of (List of dictionaries containing search results, Debug info)
    """
    debug_info = {'request': {'query': query, 'num_results': num_results}, 'response': {}}
    try:
        response = tavily.search(query=query, max_results=num_results)
        debug_info['response'] = response
        return response['results'], debug_info
    except Exception as e:
        st.error(f"Error occurred while searching: {e}")
        debug_info['response'] = {'error': str(e)}
        return [], debug_info

def get_authentic_info(context: str, info_type: str) -> Tuple[str, Dict]:
    """
    Get authentic information based on the context and type of information needed.
    
    :param context: The context of the phishing email
    :param info_type: Type of information needed (e.g., 'website', 'email', 'person')
    :return: Tuple of (A string containing the authentic information, Debug info)
    """
    query = f"{context} {info_type}"
    results, debug_info = search_info(query)
    
    if not results:
        return f"No authentic {info_type} found", debug_info
    
    if info_type == 'website':
        return results[0]['url'], debug_info
    elif info_type == 'email':
        # Extract email from the content (this is a simple example and might need refinement)
        for result in results:
            content = result['content']
            if '@' in content:
                return content.split('@')[0] + '@example.com', debug_info  # Obfuscate the domain for safety
    elif info_type == 'person':
        return results[0]['title'], debug_info
    
    return results[0]['content'][:100], debug_info  # Return a snippet of the content for other types

# Example usage (only run this if the file is executed directly)
if __name__ == "__main__":
    context = "tech startup in Silicon Valley"
    for info_type in ['website', 'email', 'person']:
        result, debug = get_authentic_info(context, info_type)
        print(f"{info_type.capitalize()}: {result}")
        print(f"Debug info: {debug}\n")