from agents.base_agent import BaseAmazonAgent


class PromptOptimizerAgent(BaseAmazonAgent):
    """Agent for rewriting prompts following the KERNEL structure

    This agent takes any prompt as input and rewrites it following the KERNEL
    framework (Knowledge, Example, Rules, Nuances, Execution, Limits) to make
    it more effective and clearer for LLM comprehension.

    The output is always in English, but preserves Italian product names,
    proper nouns, and location names exactly as they appear in the input.
    """

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "prompt_optimizer_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "prompt_optimizer_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "PromptOptimizerAgent"

    def optimize_prompt(self, prompt_text):
        """
        Rewrite a prompt following the KERNEL structure

        Args:
            prompt_text: Original prompt text to optimize

        Returns:
            dict: Dictionary with 'result' (optimized prompt) and 'tokens' (token count)
        """
        return self._generate("dummy_link", "prompt optimization", prompt_text=prompt_text)
