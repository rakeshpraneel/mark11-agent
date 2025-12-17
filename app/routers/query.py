from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import aiohttp
import datetime
import uuid
import google.genai as genai
import re
import requests

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
async def ask_to_agent(query: str, request: Request):
    try:
        # result = await search(query=query)

        # print(f"result::: {result}")

        # if not result:
        #     return "Sauluh is clueless....."

        # context_parts = []
        # sources = []
            
        # for idx, result in enumerate(result, 1):
        #     chunk_text = result["payload"].get("text", "")
        #     source_url = result["payload"].get("source_url", "Unknown")
        #     chunk_index = result["payload"].get("chunk_index", "N/A")
        #     score = result["score"]
            
        #     # Add to context with source number
        #     context_parts.append(f"[Source {idx}] (Relevance: {score:.2f})\n{chunk_text}")
            
        #     # Collect source information
            
        #     sources.append({
        #         "source_number": idx,
        #         "url": source_url,
        #         "chunk_index": chunk_index,
        #         "relevance_score": round(score, 3),
        #         "preview": chunk_text
        #     })
        
        # context = "\n\n".join(context_parts)

        # print(f"context:: {context}")
        
        
        prompt = f"""You are a knowledgeable and context-grounded assistant, Saul. Optimized for Retrieval-Augmented Generation (RAG).
                ****
                Your job is to **answer the user’s question in the way mentioned below**.
                ---
                ## **User Question:**
                {query}
                ---
                ## **Response Instructions (Strict):**
                ### **1. Grounding & Accuracy**
                * If the question is very specific (e.g., *“When was the Indian Penal Code published?”*), give a precise answer:
                → **“The Indian Penal Code was published in <year>.”**
                ### **2. Missing Information**
                * If you are unable to find full answer for the question, explicitly state what is missing.
                * Never hallucinate facts.
                ### **3. Sources & Citation Rules**
                * Add urls from which the data was collected.
                * List sources at the end under a separate heading **“Sources Used:”**
                * Format each source as:
                `1. Source <number>: "<url>
                * Cite **only the URLs used to justify claims**, not all search results.
                * If sources contradict each other, mention both perspectives.
                ### **4. POC Extraction**
                * If the search result contains **emails, phone numbers, or contact names**, extract them and list them under **“POC:”**
                * If none exist, **do not include a POC section**.

                ### **5. Formatting Requirements**

                * Use short paragraphs (max 3–4 sentences each).
                * Use bullet points (`-` or `•`) for lists.
                * Use numbered lists only when describing steps.
                * Bold important terms using `**` … `**`.
                * Keep the answer concise but complete.
                * Add blank lines between paragraphs.
                * Follow the same structure and clarity as the sample output.
                ---
                ## **Output Structure (Strictly Follow This):**
                ```
                <Concise direct answer fetched from search result>
                <Additional explanation in short paragraphs>
                <Sources Used:>
                1. Source 1: "<url>" – Explanation
                2. Source 2: "<url>" – Explanation
                (Include only if URLs exist)
                <POC:>
                - <name / email / phone> 
                (Include only if applicable)
                ```
                ---
                ## **Sample Style Reference**
                (Do not repeat this in the final answer — this is just for stylistic alignment.)
                ```
                Confluence is a collaborative platform designed to help teams document workflows, share knowledge, and manage projects in real-time. It integrates well with organizational ecosystems.
                Confluence is typically used for:
                • Project management
                • Content collaboration
                • Documentation workflows
                Sources Used:
                1. Source 1: https://example1.com – Provides insights on organizing content.
                2. Source 2: https://example2.com – Describes page structure improvements.
                ```
                ---
                ## **Now produce the final answer following all instructions.**
                """

        # local model
        # model = "llama3.2:3b"
        
        await run_agent.run_agent(prompt)

        client_host = request.client.host

        try:
            response = await run_agent.process_msg(query, client_host)

            answer = clean_and_format_response(response)
            # # answer = format_sources_citation(response,sources)

            # answer = format_lists(answer)
            # answer = format_to_human_readable(answer)
            return JSONResponse(status_code=200, content=str(answer))
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        print(f"Error in ask_to_agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
