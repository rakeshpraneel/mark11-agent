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
        
        
        prompt = f"""You are a knowledgeable assistant, called SAUL. Answer the user's question based on the context provided from a knowledge base.

                Context from knowledge base:
                {context}

                User Question: {query}

                Instructions:
                - Provide a clear and accurate answer based on the context above.
                - If the question is pin pointed then make sure to answer it precisely.
                - Let's say when was "Indian Penal Code published" is the question then answer it like "Indian penal code was published in certain year."
                - If the context doesn't fully answer the question, acknowledge what information is missing.
                - Sources should be only of reference url. Mention Source number and its url.
                - Do not mention according to source if the source reference url is not available for the context.
                - Don't mention the Source number or refer to any source, only if there is reference url.
                - Skip the source citing, if the source doesn't has any reference urls.
                - Mention the sources at the end of the response under the title sources used. (refer to sample output for structure)
                - Be concise but thorough
                - If sources contradict each other, mention both perspectives.
                - At the end of the response add the source numbers for the claims made and respective reference url.
                - Add the reference urls for both the context that you are claiming as well as for the context from knowledge base.
                - Add the reference urls to your answer only if it is fetched from that or else not required.
                - Extract the mail ids or contact numbers/contact names and display it at the last, stating as POC.
                - Add POC only if the sources has any or don't add POC field.

                Formatting Rules:
                - Use proper paragraphs with blank lines between them
                - Use bullet points (with - or *) for lists
                - Use numbered lists (1. 2. 3.) when showing steps
                - Bold important terms by wrapping in **text**
                - Cite source urls like: Source 1: "<source url>..."
                - Cite the source urls point by point.
                - Keep paragraphs concise (3-4 sentences max)
                - Refer to sample output and produce the output in similar format.

                Sample Input:
                    "What is Confluent ?"
                Sample output:
                
                    "Confluence is a collaborative platform designed to help teams communicate, manage projects, and document workflows in real-time. It integrates seamlessly with other tools within an organization's ecosystem.

                    Confluence can be utilized in diverse environments such as:
                        • Project Management
                        • Content Collaboration
                        • Document Sharing

                    Sources Used:
                    1. Source 1: https://www.kolekti.com/resources/guides/create-the-best-confluence-pages - Provides insights into how Confluence can be used for organizing content, using macros, and creating better pages.
                    2. Source 2: https://www.kolekti.com/resources/guides/create-the-best-confluence-pages - Offers advice on enhancing the design of Confluence pages by changing text color and styles.
                    3. Source 4: https://www.kolekti.com/resources/guides/create-the-best-confluence-pages - Explains how to use templates in Confluence and adding the anchor macro.
                    4. Source 5: https://www.kolekti.com/resources/guides/create-the-best-confluence-pages - Highlights additional features like Smart Designer and content formatting macros.


                Answer:"""

        # local model
        # model = "llama3.2:3b"
        model = "qwen2.5:1.5b"
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
