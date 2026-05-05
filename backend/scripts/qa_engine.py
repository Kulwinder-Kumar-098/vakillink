import os
import json
from groq import Groq
from retrieval_from_qdrant import LegalRetriever
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

class LegalQAEngine:
    def __init__(self):
        self.retriever = LegalRetriever()
        self.client = Groq(api_key=GROQ_API_KEY)
        
    def ask(self, query: str):
        print(f"\n[AI] Processing query: {query}...")
        
        # 1. Retrieve context
        results = self.retriever.search(query)
        
        if not results:
            return "I'm sorry, I couldn't find any relevant legal precedents in my database for this specific query."
            
        # 2. Construct Prompt
        context_blocks = []
        for i, res in enumerate(results):
            block = (
                f"DOCUMENT {i+1}\n"
                f"SOURCE: {res['law_name']} ({res['domain']})\n"
                f"LEGAL ISSUE: {res['legal_issue']}\n"
                f"RELEVANT ACTS/SECTIONS: {res['acts']} | {res['sections']}\n"
                f"EXCERPT: {res['chunk_text']}\n"
            )
            context_blocks.append(block)
            
        context_text = "\n".join(context_blocks)
        
        system_msg = (
            "You are a Senior Legal Counsel specializing in Indian Law. "
            "Your task is to provide a comprehensive, precise legal analysis based ON THE PROVIDED EXCERPTS. "
            "1. Cite specific case names, sections of the IPC/CrPC/Constitution, and Acts mentioned in the context. "
            "2. Focus on constitutional protections under Article 17 (Abolition of Untouchability) and Article 21 (Right to Life and Dignity). "
            "3. Mention specific legislations like 'Prohibition of Employment as Manual Scavengers and their Rehabilitation Act, 2013' if found in context. "
            "4. Format your response using Markdown with bold headers."
        )
        
        user_msg = f"USER QUERY: {query}\n\nLEGAL CONTEXT EXCERPTS:\n{context_text}"
        
        # 3. Generate Answer
        try:
            completion = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"

if __name__ == "__main__":
    engine = LegalQAEngine()
    query = "What are the rights of manual scavengers under the Indian Constitution?"
    answer = engine.ask(query)
    print("\n" + "="*50)
    print("LEGAL ANALYSIS")
    print("="*50)
    print(answer)
    print("="*50)
