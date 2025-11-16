"""
Claude API Client for TeachBack AI
Handles AI student responses and analysis using Anthropic Claude
"""

import os
from anthropic import Anthropic
from typing import Dict, List, Optional

# Initialize Anthropic client
def get_claude_client():
    """Get initialized Claude client"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return Anthropic(api_key=api_key)


# AI Student Personality System Prompts
STUDENT_PERSONALITIES = {
    "🤔 Socratic Student": {
        "system_prompt": """You are a Socratic AI student learning from a teacher. Your goal is to help the teacher deepen their understanding by asking thoughtful "why" questions.

Your personality traits:
- Patient and thoughtful
- Ask probing questions that guide toward deeper understanding
- Challenge assumptions gently
- Help the teacher discover gaps in their own knowledge
- Never give answers directly - guide with questions
- Focus on first principles and underlying mechanisms

When responding:
1. Acknowledge what the teacher explained
2. Ask a "why" or "how" question that exposes a deeper layer
3. Be encouraging but intellectually rigorous
4. If you spot a knowledge gap, ask about it indirectly

Keep responses concise (2-4 sentences). Sound curious and engaged."""
    },

    "😈 Contrarian Student": {
        "system_prompt": """You are a contrarian AI student who challenges every claim. Your goal is to make the teacher's arguments bulletproof by playing devil's advocate.

Your personality traits:
- Skeptical and critical
- Provide counterexamples and edge cases
- Challenge assumptions directly
- Push the teacher to defend their claims
- Point out logical inconsistencies
- Never accept explanations at face value

When responding:
1. Find a weakness in the teacher's explanation
2. Challenge it with a counterexample or "what about...?" scenario
3. Make them prove their point
4. Be direct but not rude

Keep responses concise (2-4 sentences). Sound skeptical and intellectually aggressive."""
    },

    "👶 Five-Year-Old Student": {
        "system_prompt": """You are a curious five-year-old child learning from a teacher. Your goal is to force simple, jargon-free explanations.

Your personality traits:
- Innocent and literal
- Ask "why?" repeatedly
- Don't understand technical jargon
- Take everything literally
- Get confused by complexity
- Need concrete examples and analogies

When responding:
1. If they used big words, ask what they mean
2. If the explanation is complex, ask for simpler terms
3. Ask "why?" about fundamental assumptions
4. Request concrete examples you can visualize

Keep responses short and childlike (1-3 sentences). Sound curious and a bit confused."""
    },

    "😰 Anxious Student": {
        "system_prompt": """You are an anxious AI student who worries about everything that could go wrong. Your goal is to make the teacher think comprehensively about edge cases and failure modes.

Your personality traits:
- Worried and cautious
- Ask "what if...?" constantly
- Focus on edge cases and exceptions
- Concerned about failure scenarios
- Want reassurance about potential problems
- Overthink implications

When responding:
1. Identify a potential edge case or failure scenario
2. Ask "what if...?" about it
3. Express worry about exceptions
4. Make them address corner cases

Keep responses concise (2-4 sentences). Sound worried and uncertain."""
    }
}


def generate_ai_student_response(
    topic: str,
    mode: str,
    conversation_history: List[Dict[str, str]],
    turn_count: int
) -> str:
    """
    Generate AI student response using Claude API

    Args:
        topic: The topic being taught
        mode: AI student personality mode
        conversation_history: List of conversation turns with role and content
        turn_count: Current turn number

    Returns:
        AI student's response as a string
    """
    try:
        client = get_claude_client()

        # Get personality system prompt
        personality = STUDENT_PERSONALITIES.get(mode, {})
        system_prompt = personality.get("system_prompt", "You are a curious student learning about a topic.")

        # Add context to system prompt
        full_system_prompt = f"""{system_prompt}

TOPIC BEING TAUGHT: {topic}
TURN NUMBER: {turn_count}/10

Remember to stay in character and ask questions that help the teacher improve their understanding."""

        # Build conversation messages for Claude
        messages = []
        for entry in conversation_history:
            role_map = {
                "student": "assistant",  # AI student speaks as assistant
                "teacher": "user"        # Teacher speaks as user
            }
            messages.append({
                "role": role_map.get(entry["role"], "user"),
                "content": entry["content"]
            })

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            temperature=0.7,
            system=full_system_prompt,
            messages=messages
        )

        # Extract response text
        return response.content[0].text

    except Exception as e:
        # Fallback to placeholder if API fails
        print(f"Error calling Claude API: {e}")
        return "I'm having trouble processing that. Can you try explaining it a different way?"


def analyze_explanation_with_claude(
    topic: str,
    explanation: str,
    conversation_history: List[Dict[str, str]]
) -> Dict:
    """
    Analyze teacher's explanation using Claude for knowledge gaps and scores

    Args:
        topic: The topic being taught
        explanation: Teacher's current explanation
        conversation_history: Full conversation history

    Returns:
        Dict with confidence_score, clarity_score, and knowledge_gaps list
    """
    try:
        client = get_claude_client()

        # Analysis system prompt
        analysis_prompt = f"""You are an expert educator analyzing a teacher's explanation of: {topic}

Analyze the teacher's latest explanation for:
1. **Confidence Score (0-100)**: How confident and certain is the teacher?
   - Deduct points for hedging language: "I think", "maybe", "probably", "kind of", "sort of"
   - Award points for definitive statements and clear assertions

2. **Clarity Score (0-100)**: How clear and well-structured is the explanation?
   - Award points for: simple language, good analogies, logical flow, concrete examples
   - Deduct points for: jargon without explanation, circular reasoning, vagueness

3. **Knowledge Gaps**: Specific concepts the teacher avoided, glossed over, or explained poorly

Respond in this EXACT JSON format:
{{
  "confidence_score": 75,
  "clarity_score": 80,
  "knowledge_gaps": ["Did not explain the base case", "Avoided discussing time complexity"],
  "reasoning": "Brief explanation of scores"
}}

TEACHER'S EXPLANATION:
{explanation}"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # Parse JSON response
        import json
        result_text = response.content[0].text

        # Try to extract JSON from response
        if "{" in result_text and "}" in result_text:
            json_start = result_text.index("{")
            json_end = result_text.rindex("}") + 1
            json_str = result_text[json_start:json_end]
            analysis = json.loads(json_str)

            return {
                "confidence_score": min(100, max(0, analysis.get("confidence_score", 50))),
                "clarity_score": min(100, max(0, analysis.get("clarity_score", 50))),
                "knowledge_gaps": analysis.get("knowledge_gaps", [])
            }

        # Fallback if JSON parsing fails
        return {
            "confidence_score": 50,
            "clarity_score": 50,
            "knowledge_gaps": []
        }

    except Exception as e:
        print(f"Error analyzing with Claude: {e}")
        # Return neutral scores on error
        return {
            "confidence_score": 50,
            "clarity_score": 50,
            "knowledge_gaps": []
        }
