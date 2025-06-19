import google.generativeai as genai
import aiohttp
import asyncio
from typing import List, Dict, Optional
import json
import re

class GeminiSearchBot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Configure Gemini 2.0 Flash model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
    
    def extract_search_queries(self, message: str, context: List[Dict] = None) -> List[str]:
        """Extract search queries from the message and context"""
        # Create context string if available
        context_str = ""
        if context:
            recent_messages = []
            for conv in context[-5:]:  # Last 5 conversations for context
                if conv.get('message'):
                    recent_messages.append(f"User: {conv['message']}")
                if conv.get('response'):
                    recent_messages.append(f"Bot: {conv['response'][:100]}...")
            context_str = "\n".join(recent_messages)
        
        # Prompt to extract search queries
        prompt = f"""
        Based on this conversation context and the current message, extract 1-3 specific web search queries that would help answer the user's question or provide relevant information.

        Context (recent conversation):
        {context_str}

        Current message: {message}

        Please provide search queries that are:
        1. Specific and targeted
        2. Likely to return relevant results
        3. Consider the conversation context
        4. Written in a way that search engines can understand

        Return only the search queries, one per line, without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            search_queries = []
            
            if response.text:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-'):
                        # Clean up the query
                        query = re.sub(r'^[0-9]+\.?\s*', '', line)  # Remove numbering
                        query = query.strip('"\'')  # Remove quotes
                        if query:
                            search_queries.append(query)
            
            return search_queries[:3]  # Limit to 3 queries
            
        except Exception as e:
            print(f"Error extracting search queries: {e}")
            # Fallback: use the message as a search query
            return [message] if len(message) > 3 else []
    
    async def search_web(self, query: str) -> Dict:
        """Perform web search using Google Custom Search API alternative"""
        # Note: This is a simplified search function
        # In production, you'd use Google Custom Search API or other search services
        
        search_prompt = f"""
        I need you to act as a web search engine. Based on this search query: "{query}"
        
        Please provide information that would typically be found through web search, including:
        1. Current and relevant information about the topic
        2. Multiple perspectives if applicable  
        3. Recent developments or news if relevant
        4. Factual data and statistics when available
        
        Format your response as if you're providing search results with relevant, up-to-date information.
        """
        
        try:
            response = self.model.generate_content(search_prompt)
            return {
                'query': query,
                'results': response.text if response.text else "No results found",
                'success': True
            }
        except Exception as e:
            return {
                'query': query,
                'results': f"Search error: {str(e)}",
                'success': False
            }
    
    async def generate_response(self, message: str, search_results: List[Dict], 
                              context: List[Dict] = None) -> str:
        """Generate a comprehensive response based on search results and context"""
        
        # Prepare context string
        context_str = ""
        if context:
            recent_messages = []
            for conv in context[-3:]:  # Last 3 conversations
                if conv.get('message'):
                    recent_messages.append(f"User: {conv['message']}")
                if conv.get('response'):
                    recent_messages.append(f"Assistant: {conv['response'][:150]}...")
            context_str = "\n".join(recent_messages)
        
        # Prepare search results string
        search_info = ""
        for i, result in enumerate(search_results, 1):
            if result.get('success'):
                search_info += f"\nSearch Query {i}: {result['query']}\nResults: {result['results']}\n"
        
        # Generate comprehensive response
        response_prompt = f"""
        You are a helpful AI assistant that provides comprehensive answers based on web search results and conversation context.

        Conversation Context:
        {context_str}

        Current User Message: {message}

        Web Search Information:
        {search_info}

        Please provide a helpful, informative response that:
        1. Directly addresses the user's question or message
        2. Uses the search information to provide accurate, current details
        3. Considers the conversation context for continuity
        4. Is conversational and engaging
        5. Cites or references the information sources when relevant
        6. Keeps the response concise but comprehensive (aim for 2-4 paragraphs)

        If the search results don't contain relevant information, acknowledge this and provide what helpful information you can based on your knowledge.
        """
        
        try:
            response = self.model.generate_content(response_prompt)
            return response.text if response.text else "I apologize, but I couldn't generate a proper response at this time."
            
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try again."
    
    async def process_message(self, message: str, context: List[Dict] = None) -> Dict:
        """Process a message end-to-end: extract queries, search, and generate response"""
        
        # Extract search queries
        search_queries = self.extract_search_queries(message, context)
        
        if not search_queries:
            return {
                'response': "I'm not sure what to search for. Could you please be more specific?",
                'search_queries': [],
                'search_results': []
            }
        
        # Perform searches
        search_results = []
        for query in search_queries:
            result = await self.search_web(query)
            search_results.append(result)
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        # Generate response
        response = await self.generate_response(message, search_results, context)
        
        return {
            'response': response,
            'search_queries': search_queries,
            'search_results': search_results
        }