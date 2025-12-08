from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import aiohttp
import datetime
import uuid
import google.generativeai as genai
import re

import app.agent.run_agent as run_agent
from app.utility.chunker import simple_chunk_text
from app.utility.rag_tool import search
from app.utility.response_formatter import *
from app.core.settings import settings

router = APIRouter()

def clean_llm_response(text: str) -> str:
    """Clean up LLM response by handling escaped characters."""
    try:
        # Handle double-encoded strings
        text = text.encode().decode('unicode_escape')
    except:
        pass
    
    # Manual replacements
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', ' ')
    text = text.replace('\\r', '')
    text = text.replace('\\"', '"')
    text = text.replace("\\'", "'")
    
    # Clean excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()

async def generate_with_ollama(model, prompt):
    """
    Generate text using Ollama
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SERVER_SIDE_CALL}:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        ) as response:
            if response.status == 200:
                print("-------response--------")
                print(response)
                data = await response.json()
                return data["response"]
            else:
                # print(await response.json())
                raise Exception(f"Ollama generation failed: {response.status}")

@router.post("/ask",summary="What saul has learnt ?",
             description="Shoot out the question, saul will answer using the knowledge obtained through scraper")
async def ask_to_agent(query: str):
    try:
        result = await search(query=query)

        print(f"result::: {result}")

        if not result:
            return "Sauluh is clueless....."

        context_parts = []
        sources = []
            
        for idx, result in enumerate(result, 1):
            chunk_text = result["payload"].get("text", "")
            source_url = result["payload"].get("source_url", "Unknown")
            chunk_index = result["payload"].get("chunk_index", "N/A")
            score = result["score"]
            
            # Add to context with source number
            context_parts.append(f"[Source {idx}] (Relevance: {score:.2f})\n{chunk_text}")
            
            # Collect source information
            
            sources.append({
                "source_number": idx,
                "url": source_url,
                "chunk_index": chunk_index,
                "relevance_score": round(score, 3),
                "preview": chunk_text
            })
        
        context = "\n\n".join(context_parts)

        print(f"context:: {context}")
        
        # Step 3: Generate answer using Gemini
        prompt = f"""You are a knowledgeable assistant, called SAUL. Answer the user's question based on the context provided from a knowledge base.

                Context from knowledge base:
                {context}

                User Question: {query}

                Instructions:
                - Provide a clear and accurate answer based on the context above
                - If the context doesn't fully answer the question, acknowledge what information is missing
                - Reference sources when making specific claims (e.g., "According to Source 1 and add reference url...")
                - Be concise but thorough
                - If sources contradict each other, mention both perspectives.
                - Add the reference urls for both the context that you are claiming as well as for the context from knowledge base.
                - Add the reference urls to your answer only if it is fetched from that or else not required.
                - Extract the mail ids or contact numbers/contact names and display it at the last, stating as POC.
                - Add POC only if the sources has any or don't add POC field.

                Formatting Rules:
                - Use proper paragraphs with blank lines between them
                - Use bullet points (with - or *) for lists
                - Use numbered lists (1. 2. 3.) when showing steps
                - Bold important terms by wrapping in **text**
                - Cite sources naturally: "According to Source 1, ..."
                - Keep paragraphs concise (3-4 sentences max)
                


                Answer:"""

        # local model
        # model = "llama3.2:3b"
        model = "llama3.2:1b"
        response = await generate_with_ollama(model, prompt)

        response = clean_and_format_response(response)
        answer = format_sources_citation(response,sources)

        answer = format_lists(answer)
        answer = format_to_human_readable(answer)
        
        
        # answer = response.encode().decode('unicode_escape')

        
        
        print( {
            "query": query,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(result)
        })

        # final_source = " Ref url: "

        # for source in sources:
        #     final_source += source.get('url') +', '

        return answer
    
    except Exception as e:
        print(f"Error in ask_to_agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
