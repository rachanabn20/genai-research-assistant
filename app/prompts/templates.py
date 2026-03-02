"""
Prompt Engineering Templates
------------------------------
All prompts used by the application are defined here.

Prompt evolution example showing why good prompts matter:

BAD:    "Summarize this paper"
BETTER: "Read this research paper and summarize the key findings"
GOOD:   "You are a research analyst. Summarize this paper with sections
         for objective, method, findings, and limitations. Only use
         information from the paper. If something is not mentioned,
         say so."

The prompts below are production-grade versions of the GOOD example.
"""

SYSTEM_PROMPT = """You are an expert academic research assistant with deep expertise \
in analyzing research papers across all scientific domains.

YOUR CORE PRINCIPLES:
1. ACCURACY: Only state facts that are explicitly present in the provided paper content.
2. HONESTY: If the paper does not contain information to answer a question, say so clearly.
3. CLARITY: Explain complex concepts in clear, accessible language.
4. STRUCTURE: Organize your responses with clear headings and bullet points.
5. CITATION: Reference specific sections or findings from the paper when possible.

WHAT YOU MUST NEVER DO:
- Never fabricate or hallucinate information not in the paper
- Never provide personal opinions on the research quality
- Never make claims beyond what the paper states
- Never ignore the provided context and use general knowledge instead

RESPONSE STYLE:
- Use academic but accessible language
- Be concise but thorough
- Use bullet points for lists
- Use bold for key terms
- Include relevant quotes from the paper when helpful"""


SUMMARIZE_PROMPT = """Analyze the following research paper content and provide a \
comprehensive summary.

PAPER CONTENT:
{context}

Provide your summary in the following structure:

## Paper Overview
[2-3 sentence overview of what this paper is about]

## Research Objective
[What problem does this paper try to solve?]

## Methodology
[How did the authors approach the problem? What methods or techniques were used?]

## Key Findings
[List the main results and discoveries using bullet points]

## Conclusions
[What do the authors conclude? What are the implications?]

## Limitations
[What limitations do the authors acknowledge, if any?]

## Future Work
[What future research directions are suggested, if any?]

If any section cannot be determined from the provided content, explicitly state: \
"Not explicitly mentioned in the provided content."
"""


QA_PROMPT = """Answer the following question based ONLY on the provided research \
paper content.

RELEVANT PAPER SECTIONS:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer ONLY based on the information in the provided paper sections above.
2. If the answer is not found in the provided content, respond with: \
"I cannot find information about this in the provided paper sections. \
The paper may not cover this topic, or the relevant section was not retrieved."
3. Quote relevant passages when they directly answer the question.
4. Be specific and cite the part of the paper your answer comes from.
5. Keep your answer focused and concise.

ANSWER:"""


KEY_FINDINGS_PROMPT = """Extract the key findings from the following research paper content.

PAPER CONTENT:
{context}

Provide your analysis in the following structure:

## Key Findings

For each finding:
1. **Finding**: [State the finding clearly]
   - **Evidence**: [What data or results support this?]
   - **Significance**: [Why does this matter?]

## Quantitative Results
[List any specific numbers, percentages, metrics, or statistical results mentioned]

## Novel Contributions
[What is new or unique about this research compared to prior work?]

Only include findings explicitly stated in the paper. Do not infer or speculate."""


METHODOLOGY_PROMPT = """Analyze the research methodology described in the following \
paper content.

PAPER CONTENT:
{context}

Provide your analysis in the following structure:

## Research Design
[What type of study is this? Experimental, observational, review, etc.]

## Data Collection
[How was data collected? What datasets were used?]

## Methods and Techniques
[What specific methods, algorithms, or techniques were employed?]

## Evaluation Metrics
[How were results measured and evaluated?]

## Reproducibility
[Is enough detail provided to reproduce this study?]

Only describe what is explicitly stated in the paper content."""


def get_prompt(prompt_type: str) -> str:
    """
    Get a prompt template by type name.

    Args:
        prompt_type: One of 'summarize', 'qa', 'key_findings', 'methodology'

    Returns:
        The prompt template string with placeholders

    Raises:
        ValueError: If prompt_type is not recognized
    """
    prompts = {
        "summarize": SUMMARIZE_PROMPT,
        "qa": QA_PROMPT,
        "key_findings": KEY_FINDINGS_PROMPT,
        "methodology": METHODOLOGY_PROMPT,
    }

    if prompt_type not in prompts:
        raise ValueError(
            f"Unknown prompt type: '{prompt_type}'. "
            f"Available types: {list(prompts.keys())}"
        )

    return prompts[prompt_type]


def format_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a prompt template and fill in the placeholder variables.

    Usage:
        formatted = format_prompt("qa", context="paper text", question="What is?")
    """
    template = get_prompt(prompt_type)
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(
            f"Missing required variable {e} for prompt type '{prompt_type}'"
        )