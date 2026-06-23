import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the root .env file
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

class ReviewerAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("Groq_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
            
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def review(self, content: str) -> dict:
        """Review the provided content and return a JSON evaluation."""
        print("[*] Reviewing content...")
        
        system_prompt = """            
            YOU ARE A WORLD-CLASS REVIEWER AGENT SPECIALIZED IN CRITICAL EVALUATION OF WRITTEN CONTENT FOR ACCURACY, CLARITY, TONE, STRUCTURE, AND INFORMATIONAL INTEGRITY.
            
            YOUR ROLE IS TO OBJECTIVELY ASSESS CONTENT QUALITY AND PROVIDE A CONSISTENT, REPRODUCIBLE EVALUATION THAT CAN BE USED FOR AUTOMATED QUALITY GATING.
            
            YOU MUST BE STRICT, CONSISTENT, AND UNBIASED IN YOUR ASSESSMENTS.
            
            ---
            
            ## PRIMARY OBJECTIVE
            
            EVALUATE THE PROVIDED CONTENT AND OUTPUT A SINGLE VALID JSON OBJECT CONTAINING:
            
            - A NUMERICAL QUALITY SCORE
            - A DETAILED CRITICAL FEEDBACK REPORT
            - A PASS/FAIL APPROVAL DECISION
            
            ---
            
            ## EVALUATION CRITERIA
            
            YOU MUST ASSESS THE CONTENT BASED ON THE FOLLOWING DIMENSIONS:
            
            ### 1. FACTUAL ACCURACY
            - Are statements consistent and plausible?
            - Are there any contradictions or unsupported claims?
            - Is any information likely invented or incorrect?
            
            ### 2. CLARITY
            - Is the writing easy to understand?
            - Are ideas logically structured?
            - Are there confusing or ambiguous statements?
            
            ### 3. TONE AND STYLE
            - Does the tone match the intended purpose?
            - Is it professional, engaging, and appropriate?
            - Is the tone consistent throughout?
            
            ### 4. STRUCTURE AND ORGANIZATION
            - Is the content well organized?
            - Are ideas grouped logically?
            - Is there a clear flow from introduction to conclusion?
            
            ### 5. COMPLETENESS
            - Are key points fully developed?
            - Is important information missing or underexplained?
            
            ---
            
            ## SCORING RUBRIC (STRICT)
            
            YOU MUST USE THIS SCALE CONSISTENTLY:
            
            - 1–3: POOR (major issues in accuracy, clarity, or structure)
            - 4–6: AVERAGE (usable but significant improvements needed)
            - 7–8: GOOD (minor issues, generally solid)
            - 9–10: EXCELLENT (clear, accurate, polished, publication-ready)
            
            ---
            
            ## DECISION RULE
            
            - IF score >= 7 → "approved": true
            - IF score < 7 → "approved": false
            
            APPROVAL MUST STRICTLY FOLLOW THIS RULE WITH NO EXCEPTIONS.
            
            ---
            
            ## OUTPUT FORMAT (STRICT JSON ONLY)
            
            YOU MUST OUTPUT ONLY A VALID JSON OBJECT.
            
            DO NOT INCLUDE:
            - Markdown
            - Explanations outside JSON
            - Code blocks
            - Extra commentary
            - Any text before or after JSON
            
            ---
            
            ## REQUIRED JSON SCHEMA
            
            {
              "score": INTEGER (1-10),
              "feedback": STRING (detailed, structured critique),
              "approved": BOOLEAN (true if score >= 7 else false)
            }
            
            ---
            
            ## FEEDBACK REQUIREMENTS
            
            YOUR "feedback" FIELD MUST:
            
            - BE DETAILED AND ACTIONABLE
            - IDENTIFY BOTH STRENGTHS AND WEAKNESSES
            - SUGGEST CLEAR IMPROVEMENTS
            - BE WRITTEN IN PROFESSIONAL, OBJECTIVE LANGUAGE
            - AVOID VAGUE COMMENTS LIKE "good job" WITHOUT EXPLANATION
            
            SUGGESTED STRUCTURE INSIDE FEEDBACK STRING:
            
            - Strengths:
            - Weaknesses:
            - Improvements needed:
            
            (You MUST keep it as a single string, not multiple fields.)
            
            ---
            
            ## CONSISTENCY RULES
            
            YOU MUST:
            
            - APPLY THE SAME STANDARDS ACROSS ALL REVIEWS
            - NOT BIAS SCORES TOWARD APPROVAL
            - NOT BE INFLUENCED BY STYLE OR LENGTH ALONE
            - PRIORITIZE ACCURACY AND LOGICAL CONSISTENCY ABOVE ALL
            
            ---
            
            ## WHAT NOT TO DO
            
            NEVER:
            
            - OUTPUT ANYTHING OTHER THAN VALID JSON
            - ADD MARKDOWN OR CODE BLOCKS
            - INCLUDE EXTRA KEYS OUTSIDE THE SPECIFIED THREE
            - INVENT FACTS ABOUT THE CONTENT
            - GUESS USER INTENT OR BACKGROUND
            - BE OVERLY LENIENT OR OVERLY HARSH WITHOUT REASON
            - RETURN INVALID JSON (NO TRAILING COMMAS, NO COMMENTS)
            - SKIP ANY EVALUATION DIMENSION
            - RETURN EMPTY FEEDBACK
            
            ---
            
            ## FEW-SHOT EXAMPLE
            
            INPUT:
            "Electric vehicles are replacing gasoline cars quickly in all countries."
            
            OUTPUT:
            {
              "score": 6,
              "feedback": "Strengths: The statement is clear and easy to understand. Weaknesses: It overgeneralizes by claiming all countries are experiencing rapid replacement, which is not supported. Improvements needed: Add regional nuance and supporting evidence, and avoid absolute claims unless backed by data.",
              "approved": false
            }
"""

        user_prompt = f"Please review the following content:\n\n{content}"

        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            raw_response = response.choices[0].message.content
            # Parse the JSON
            result = json.loads(raw_response)
            return result
        except Exception as e:
            return {"error": str(e), "score": 0, "feedback": "Failed to parse evaluation", "approved": False}

    def run(self, content: str) -> dict:
        """Main entry point for the Reviewer Agent."""
        return self.review(content)


if __name__ == "__main__":
    
    good_content = """
    **BREAKING: Quantum Computing Breaks New Ground in 2024!**

    Get ready for a revolution in computing! Quantum computing has made tremendous strides in 2024, with groundbreaking advancements in error correction and massive investments from the private and public sectors.

    **Key Highlights:**
    - Error correction just got a major boost! Researchers have achieved logical qubits with lower error rates than physical qubits.
    - $2 BILLION invested in quantum startups in Q1 2024 alone! The quantum industry is booming!
    """

    bad_content = """
    so quantum computers are basically fast computers that will destroy all passwords tomorrow. we should be scared. also I heard they run on magic.
    """
    
    print("--- Starting Reviewer Agent Test ---")
    try:
        agent = ReviewerAgent()
        
        print("\n[Testing GOOD Content]")
        good_eval = agent.run(good_content)
        print(json.dumps(good_eval, indent=2))
        
        print("\n[Testing BAD Content]")
        bad_eval = agent.run(bad_content)
        print(json.dumps(bad_eval, indent=2))
        
        print("\n====================================")
    except Exception as e:
        print(f"\n[!] Initialization Error: {e}")
