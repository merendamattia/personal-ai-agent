from agents.base_agent import BaseAmazonAgent


class EmailRewriterAgent(BaseAmazonAgent):
    """Agent for rewriting emails with different tones

    This agent takes any email as input and rewrites it with a specified tone
    (formal, friendly, diplomatic, etc.), making it more effective while
    maintaining the original intent.
    """

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "email_rewriter_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "email_rewriter_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "EmailRewriterAgent"

    def rewrite_email(self, email_text, tone="professional"):
        """
        Rewrite an email with a specified tone

        Args:
            email_text: Original email text to rewrite
            tone: Desired tone (e.g., "professional", "friendly", "diplomatic", "formal")

        Returns:
            dict: Dictionary with 'result' (rewritten email) and 'tokens' (token count)
        """
        return self._generate("email rewriting", email_text=email_text, tone=tone)
