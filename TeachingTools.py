from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
import re


@tool
def search_python_resources(query: str, skill_level: str = "beginner"):
    """
    Search for Python programming information from trusted educational sources.
    Focuses on official documentation, tutorials, and reputable learning platforms.
    Can be tailored to different skill levels: beginner, intermediate, or professional.
    """
    # Handle dictionary inputs (workaround for agent tool calling issue)
    if isinstance(query, dict):
        query = query.get('description', '') if 'description' in query else str(query)
    if isinstance(skill_level, dict):
        skill_level = skill_level.get('description', 'beginner') if 'description' in skill_level else 'beginner'
    
    try:
        # Base reliable Python education sites
        base_sites = "site:docs.python.org OR site:python.org OR site:stackoverflow.com"

        # Add level-specific resources
        if skill_level.lower() == "beginner":
            level_sites = " OR site:realpython.com OR site:w3schools.com OR site:codecademy.com OR site:freecodecamp.org OR site:pythonforbeginners.com"
        elif skill_level.lower() == "intermediate":
            level_sites = " OR site:realpython.com OR site:geeksforgeeks.org OR site:medium.com OR site:towardsdatascience.com OR site:python-course.eu"
        else:  # professional/advanced
            level_sites = " OR site:realpython.com OR site:peps.python.org OR site:github.com OR site:pydata.org OR site:python-advanced.org OR site:pycon.org"

        sites = f"{base_sites}{level_sites}"
        enhanced_query = f"{sites} {query}"

        search = DuckDuckGoSearchResults(
            num_results=5,  # Reduced to get more relevant results
            backend="lite",
            safesearch="Moderate"
        )

        results = search.run(enhanced_query)

        # Filter out irrelevant results
        if "no results" in results.lower():
            # Fallback to a broader search if no results found
            return search.run(f"Python programming {query}")
        return results

    except Exception as e:
        return f"Search error: {str(e)}. Try simpler terms like '{query.split()[0]} in Python'"