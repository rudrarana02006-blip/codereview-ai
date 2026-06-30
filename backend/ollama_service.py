import httpx
import json
import os

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL_NAME = "llama3.2:3b"

SYSTEM_PROMPT = """
You are an expert code reviewer. You will be provided with a raw git diff, a PR description, or a block of code.
Analyze the input and provide a structured code review.

Your output MUST be in valid JSON format. Do not include any markdown formatting blocks like ```json in your response, just the raw JSON string.

Required JSON Structure:
{
  "summary": "Plain-English explanation of what the diff/code does — no jargon, readable by non-technical stakeholders.",
  "risks": [
    {
      "description": "Potential bugs, security concerns, unhandled edge cases, or breaking changes.",
      "severity": "low | medium | high"
    }
  ],
  "suggestions": [
    {
      "description": "Specific improvement recommendations.",
      "line_reference": "Line number or reference if applicable, else null"
    }
  ],
  "overall_rating": "Looks Good | Needs Minor Changes | Needs Major Rework - with a one-line reason."
}

Ensure that your JSON is strictly formatted and valid.
"""

async def generate_code_review(raw_input: str) -> dict:
    async with httpx.AsyncClient() as client:
        payload = {
            "model": MODEL_NAME,
            "prompt": f"{SYSTEM_PROMPT}\n\nINPUT TO REVIEW:\n{raw_input}",
            "format": "json",
            "stream": False,
        }
        
        try:
            response = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract JSON from response
            response_text = data.get("response", "")
            try:
                review_json = json.loads(response_text)
                return review_json
            except json.JSONDecodeError:
                # Sometimes LLMs add markdown blocks despite instructions
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "", 1)
                if response_text.endswith("```"):
                    response_text = response_text[::-1].replace("```", "", 1)[::-1]
                return json.loads(response_text.strip())
                
        except httpx.ConnectError:
            # Provide a fallback mock review so the user can test the UI without having Ollama installed
            import asyncio
            await asyncio.sleep(1.5) # Simulate AI thinking time
            
            # Simple heuristic to make the mock feel slightly dynamic
            lang = "code"
            if "def " in raw_input or "print(" in raw_input and "import " in raw_input or "num1 = " in raw_input:
                lang = "Python"
            elif "function" in raw_input or "const " in raw_input or "=>" in raw_input:
                lang = "JavaScript/TypeScript"
            elif "#include" in raw_input or "printf" in raw_input or "scanf" in raw_input:
                lang = "C/C++"
                
            return {
                "summary": f"[MOCK PREVIEW - OLLAMA OFFLINE] This is a simulated code review for the provided {lang} snippet since Ollama is not running. (Install Ollama to get real AI reviews!)",
                "risks": [
                    {
                        "description": "The logic lacks proper input validation or error handling, which could lead to unexpected behavior.",
                        "severity": "medium"
                    },
                    {
                        "description": "Values are hardcoded, reducing the reusability of this snippet.",
                        "severity": "low"
                    }
                ],
                "suggestions": [
                    {
                        "description": "Consider wrapping this logic in a function to make it reusable.",
                        "line_reference": "General"
                    },
                    {
                        "description": "Add type hints or explicit declarations for better readability.",
                        "line_reference": "General"
                    }
                ],
                "overall_rating": "Looks Good"
            }
        except Exception as e:
            raise Exception(f"Failed to generate code review from Ollama: {str(e)}")
