from agents.base_agent import BaseAmazonAgent


class OfficialReportAgent(BaseAmazonAgent):
    """Agent for rewriting official reports with technical language

    This agent takes informal or poorly written official reports (e.g., police reports)
    and reformats them with proper technical language, grammar, and professional
    terminology while preserving all original information and facts.
    """

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "official_report_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "official_report_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "OfficialReportAgent"

    def rewrite_report(self, report_text):
        """
        Rewrite an official report with technical language and proper formatting

        Args:
            report_text: Original report text to rewrite

        Returns:
            dict: Dictionary with 'result' (rewritten report) and 'tokens' (token count)
        """
        return self._generate("official report rewriting", report_text=report_text)
