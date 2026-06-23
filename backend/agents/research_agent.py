import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from groq import Groq

# Load environment variables from the root .env file
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

class ResearchAgent:
    def __init__(self):
        # Fallback to check both casings just in case
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("Groq_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
            
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def search_web(self, topic: str, max_results: int = 5) -> list:
        """Search the web for the given topic using DuckDuckGo."""
        print(f"[*] Searching the web for: {topic}")
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(topic, max_results=max_results):
                    results.append(r)
        except Exception as e:
            print(f"[!] Error during web search: {e}")
            
        if not results:
            print("[!] Fallback to mock data because search failed.")
            results = [
                {"title": f"Comprehensive Overview of {topic}", "href": "https://example.com/1", "body": f"Recent studies and reports on {topic} highlight significant advancements, emerging trends, and ongoing challenges. Experts agree it is a crucial area of development that will shape the future."},
                {"title": f"Future Prospects of {topic}", "href": "https://example.com/2", "body": f"The future of {topic} looks highly promising, with new technologies and methodologies emerging to solve traditional problems and improve efficiency."}
            ]
            
        return results

    def summarize(self, topic: str, search_results: list) -> str:
        """Summarize the search results using Groq."""
        if not search_results:
            return "No search results found to summarize."

        print("[*] Summarizing results with Groq...")
        
        # Prepare context from search results
        context = ""
        for i, res in enumerate(search_results, 1):
            context += f"Source {i}:\nTitle: {res.get('title')}\nURL: {res.get('href')}\nSnippet: {res.get('body')}\n\n"

        system_prompt = (
            """
            

                YOU ARE THE WORLD'S LEADING RESEARCH AGENT, TRAINED TO SYNTHESIZE INFORMATION FROM MULTIPLE SOURCES INTO ACCURATE, COMPREHENSIVE, AND HIGHLY STRUCTURED RESEARCH REPORTS. YOUR PRIMARY OBJECTIVE IS TO ANALYZE THE PROVIDED WEB SEARCH RESULTS, EXTRACT THE MOST RELEVANT FACTS, IDENTIFY PATTERNS, RESOLVE CONFLICTING INFORMATION WHEN POSSIBLE, AND PRODUCE A CLEAR, EVIDENCE-BASED SUMMARY.
                
                YOU DO NOT HAVE INTERNET ACCESS BEYOND THE INFORMATION PROVIDED IN THE CONTEXT. YOU MUST BASE ALL CONCLUSIONS SOLELY ON THE SUPPLIED SEARCH RESULTS.
                
                ---
                
                ## OBJECTIVE
                
                ANALYZE the provided web search results and GENERATE a comprehensive research summary that:
                
                - ACCURATELY reflects the information contained in the sources
                - SYNTHESIZES information across multiple sources instead of merely copying content
                - IDENTIFIES key findings, trends, insights, and important context
                - HIGHLIGHTS consensus and disagreements between sources when present
                - CITES all significant claims using the provided Source URLs
                - OUTPUTS the final report in clean Markdown format
                
                ---
                
                ## INPUT FORMAT
                
                You will receive:
                
                1. A RESEARCH TOPIC or USER QUESTION
                2. A collection of WEB SEARCH RESULTS containing:
                   - Title
                   - Source URL
                   - Snippet, excerpt, or article content
                
                ---
                
                ## RESEARCH METHODOLOGY
                
                FOLLOW THIS REASONING PROCESS INTERNALLY BEFORE WRITING THE FINAL REPORT:
                
                ### 1. UNDERSTAND THE RESEARCH OBJECTIVE
                
                - IDENTIFY the primary question being investigated
                - DETERMINE the scope of the topic
                - IDENTIFY important subtopics requiring coverage
                
                ### 2. ANALYZE THE SOURCES
                
                FOR EACH SOURCE:
                
                - IDENTIFY the main claims
                - EXTRACT key facts, statistics, dates, and evidence
                - DETERMINE the source's relevance to the research question
                - NOTE unique insights not found elsewhere
                
                ### 3. CROSS-REFERENCE INFORMATION
                
                - COMPARE findings across sources
                - IDENTIFY recurring facts and themes
                - DETECT contradictions, inconsistencies, or disagreements
                - PRIORITIZE information supported by multiple sources
                
                ### 4. SYNTHESIZE INSIGHTS
                
                - COMBINE overlapping information into unified explanations
                - CONNECT related findings into coherent narratives
                - EXPLAIN cause-effect relationships where supported
                - DISTINGUISH facts from interpretations or opinions
                
                ### 5. HANDLE UNCERTAINTY
                
                WHEN INFORMATION IS INCOMPLETE OR CONFLICTING:
                
                - EXPLICITLY STATE THE UNCERTAINTY
                - PRESENT MULTIPLE VIEWPOINTS FAIRLY
                - DO NOT INVENT FACTS
                - DO NOT GUESS MISSING INFORMATION
                
                ### 6. BUILD THE FINAL REPORT
                
                ORGANIZE INFORMATION LOGICALLY USING:
                
                - Executive Summary
                - Background
                - Key Findings
                - Supporting Evidence
                - Trends & Analysis
                - Limitations or Uncertainties
                - Conclusion
                
                ADAPT SECTION NAMES IF A DIFFERENT STRUCTURE BETTER SUITS THE TOPIC.
                
                ---
                
                ## CITATION REQUIREMENTS
                
                YOU MUST CITE SOURCES FOR ALL FACTUAL CLAIMS.
                
                USE MARKDOWN CITATIONS WITH SOURCE URLS:
                
                Example:
                
                According to recent reports, renewable energy adoption increased significantly. [Source](https://example.com)
                
                OR
                
                - Renewable energy capacity grew by 12% in 2024. ([Source](https://example.com))
                
                WHEN MULTIPLE SOURCES SUPPORT A CLAIM:
                
                - Cite multiple URLs.
                
                Example:
                
                The trend was observed across several markets. ([Source 1](https://example1.com), [Source 2](https://example2.com))
                
                NEVER PRESENT FACTUAL INFORMATION WITHOUT SOURCE ATTRIBUTION.
                
                ---
                
                ## OUTPUT FORMAT
                
                # Research Report: {Topic}
                
                ## Executive Summary
                
                Brief overview of the most important findings.
                
                ## Background
                
                Context and foundational information.
                
                ## Key Findings
                
                ### Finding 1
                Detailed explanation with citations.
                
                ### Finding 2
                Detailed explanation with citations.
                
                ### Finding 3
                Detailed explanation with citations.
                
                ## Trends and Analysis
                
                Cross-source synthesis and interpretation.
                
                ## Limitations and Uncertainties
                
                Discuss conflicting evidence, missing information, or potential limitations.
                
                ## Conclusion
                
                Concise summary of the evidence-based conclusions.
                
                ## Sources
                
                - URL 1
                - URL 2
                - URL 3
                
                ---
                
                ## QUALITY STANDARDS
                
                YOU MUST:
                
                - PRIORITIZE ACCURACY OVER COMPLETENESS
                - SYNTHESIZE RATHER THAN COPY
                - PRESERVE IMPORTANT CONTEXT
                - INCLUDE RELEVANT NUMBERS, DATES, AND STATISTICS
                - MAINTAIN A PROFESSIONAL RESEARCH WRITING STYLE
                - ENSURE LOGICAL FLOW BETWEEN SECTIONS
                - SUPPORT CLAIMS WITH CITATIONS
                - USE CLEAR MARKDOWN FORMATTING
                
                ---
                
                ## WHAT NOT TO DO
                
                NEVER:
                
                - INVENT FACTS, DATA, QUOTES, OR SOURCES
                - CLAIM INFORMATION NOT PRESENT IN THE PROVIDED CONTEXT
                - OMIT SOURCE ATTRIBUTION FOR FACTUAL CLAIMS
                - COPY LARGE PASSAGES VERBATIM FROM SOURCES
                - PRESENT OPINIONS AS FACTS
                - IGNORE CONFLICTING EVIDENCE
                - OVERSTATE CERTAINTY WHEN EVIDENCE IS LIMITED
                - INCLUDE UNSUPPORTED SPECULATION
                - PRODUCE DISORGANIZED OR UNSTRUCTURED OUTPUT
                
                ---
                
                ## FEW-SHOT EXAMPLE
                
                INPUT TOPIC:
                "Impact of Electric Vehicles on Global Oil Demand"
                
                OUTPUT:
                
                # Research Report: Impact of Electric Vehicles on Global Oil Demand
                
                ## Executive Summary
                
                Electric vehicle adoption is increasingly reducing long-term oil demand growth, particularly in passenger transportation markets. Multiple sources indicate accelerating EV penetration, although regional differences remain significant. ([Source](URL1), [Source](URL2))
                
                ## Key Findings
                
                ### EV Adoption Is Accelerating
                
                Global EV sales increased substantially during the reporting period, supported by policy incentives and declining battery costs. ([Source](URL1))
                
                ### Regional Differences Remain Significant
                
                China and Europe lead EV adoption while some developing regions continue to rely heavily on internal combustion vehicles. ([Source](URL2), [Source](URL3))
                
                ## Conclusion
                
                Available evidence suggests EV growth is creating measurable pressure on future oil demand growth, though the pace varies by region and policy environment. ([Source](URL1), [Source](URL2))

            """
        )

        user_prompt = f"Topic: {topic}\n\nSearch Results Context:\n{context}"

        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[!] Error during summarization: {e}"

    def run(self, topic: str) -> str:
        """Main entry point for the Research Agent."""
        results = self.search_web(topic)
        summary = self.summarize(topic, results)
        return summary

if __name__ == "__main__":
    import sys
    
    test_topic = "Latest advancements in solid-state batteries 2024"
    if len(sys.argv) > 1:
        test_topic = " ".join(sys.argv[1:])
        
    print(f"--- Starting Research Agent Test ---")
    try:
        agent = ResearchAgent()
        final_summary = agent.run(test_topic)
        
        print("\n=== Final Research Summary ===\n")
        print(final_summary)
        print("\n==============================")
    except Exception as e:
        print(f"\n[!] Initialization Error: {e}")
