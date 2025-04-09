# Global constant for hook templates (merged generic and clickbaity examples)
HOOK_TEMPLATES = [
    "If you _______, stop scrolling!",
    "The BEST way to _______.",
    "Put your phone down",
    "THIS is what happens when _______.",
    "Have you heard of _______?",
    "Did you know _______?",
    "Here's a fun fact: _______.",
    "This will blow your mind . . .",
    "Here's the truth about _______.",
    "Did it ever occur to you that _______?",
    "Forget everything you know about _______.",
    "If you’re seeing this…",
    "If You Love [Topic], Watch This…",
    "For Anyone Who [Action]…",
    "If You’re Into [Topic], Don’t Miss This…",
    "If You Care About [Topic], You Need to Know…",
    "This Is Essential for [Action] Fans…",
    "You Won’t Believe…",
    "This Will Blow Your Mind…",
    "Unbelievable, But True…",
    "You’ve Never Seen Anything Like This…",
    "Wait Until You See This…",
    "This Is Unreal…",
    "How I Did This In [Short Time]",
    "How I Made This in 5 Minutes…",
    "Quickest Way to [Action]…",
    "The Reason Behind [Topic]…",
    "Why [Topic] Matters…",
    "This Is Why [Action] Works…",
    "The Truth About [Topic]…",
    "Here’s What You Need to Know About [Topic]…",
    "Things You Didn’t Know About…",
    "Little-Known Facts About [Topic]…",
    "Surprising Things About [Topic]…",
    "Did You Know These 3 Things About [Topic]?",
    "3 Secrets of [Topic]…",
    "3 Unbelievable Facts About [Topic]…",
    "How to Get [Result] Fast…",
    "What Would Happen If You [Action]…",
    "This Is What Happens When You [Action]…",
    "See What Happens If You Try This…",
    "What Occurs When You [Action]…",
    "Ever Wondered What Happens If You [Action]?",
    "In Just 10 Seconds, I Did This…",
    "Before You [Action], Watch This",
    "Don’t [Action] Until You See This…",
    "Watch This Before You Decide…",
    "Essential Tips Before You [Action]…",
    "Must-See Info Before You [Action]…",
    "Don’t Make This Mistake When You [Action]…",
    "How I Achieved [Result] in No Time…",
    "The Secret to [Action]…",
    "Insider Tip for [Topic]…",
    "A Little-Known Trick for [Action]…",
    "Want to Know a Secret?…",
    "Here’s What They Don’t Tell You About [Topic]…",
    "Only 1% of People Know…",
    "Few People Know This…",
    "This Is Something Most People Don’t Know…",
    "Hardly Anyone Knows About This…",
    "Only a Small Percentage of People Understand This…",
    "This Is a Well-Kept Secret…",
    "Let Me Show You How To…",
    "I’ll Show You How to [Action]…",
    "Here’s How to Do [Action]…",
    "Let Me Walk You Through This…",
    "Step-by-Step Guide to [Action]…",
    "Here’s How It’s Done…",
    "Check Out This Transformation",
    "Watch This Incredible Transformation…",
    "From Start to Finish…",
    "See How This Changed…",
    "Before and After…",
    "Look at This Amazing Change…",
    "Here’s What Happened When…",
    "This Is What Happened When I [Action]…",
    "Here’s the Result of [Action]…",
    "What Happened After I Tried [Action]…",
    "I Did [Action], Here’s What Happened…",
    "The Outcome of [Action] Was Surprising…",
    "Guess What Happened Next?",
    "Can You Guess What Happens Next?",
    "What Do You Think Happened?",
    "Predict the Outcome of This…",
    "What Happened Next Will Surprise You…",
    "Guess the Ending…",
    "This Is What You’ve Been Doing Wrong…",
    "Stop Doing This Wrong…",
    "Common Mistakes People Make with [Topic]…",
    "Here’s What You’ve Been Missing…",
    "The Right Way to [Action]…",
    "Most People Get This Wrong…"
]

def construct_prompt(marketing_inputs: dict, refined_keywords: list, sentiment: dict,
                     reddit_hook_examples: list, n_hooks: int, base_instruction: str = None) -> str:
    """
    Constructs the final prompt to generate hooks. If a base_instruction is provided (from the UI),
    it is used as the initial instruction; otherwise a default is used.
    """
    if base_instruction is None:
        base_instruction = ("You are a creative copywriter who specializes in producing hooks that immediately capture attention. "
                            "Your task is to generate creative, clickbaity, and engaging hook options using the inputs below. "
                            "Each hook should blend elements from the provided hook templates with language inspired by the product and Reddit data. "
                            "Do not be generic; be bold, vivid, and tailored to the product.")
    
    prompt = base_instruction + "\n\n"
    
    if marketing_inputs:
        prompt += "Product/Service Information:\n"
        for key, value in marketing_inputs.items():
            prompt += f"- {key}: {value}\n"
        prompt += "\n"
    
    prompt += "Refined Keywords:\n"
    prompt += f"- {', '.join(refined_keywords)}\n\n"
    
    prompt += "Reddit Insights (Sentiment):\n"
    prompt += f"- Overall Sentiment: {sentiment}\n\n"
    
    if sentiment.get("compound", 0) < 0.3:
        prompt += "Note: The overall sentiment from Reddit is slightly negative. Emphasize a hopeful, transformative tone in the hooks.\n\n"
    else:
        prompt += "Note: The overall sentiment from Reddit is positive. Emphasize an upbeat, energizing tone in the hooks.\n\n"
    
    prompt += "Hook Templates (Examples/Base Structures):\n"
    for template in HOOK_TEMPLATES:
        prompt += f"- {template}\n"
    prompt += "\n"
    
    prompt += "Examples of hooks extracted from Reddit:\n"
    if reddit_hook_examples:
        for example in reddit_hook_examples:
            prompt += f"- {example}\n"
    else:
        prompt += "- No examples available.\n"
    prompt += "\n"
    
    prompt += f"Using the information above, generate {n_hooks} creative and engaging hooks. "
    prompt += "Each hook should combine elements from the hook templates with language inspired by the product and Reddit. "
    prompt += "Provide each hook on a separate line."
    
    return prompt
