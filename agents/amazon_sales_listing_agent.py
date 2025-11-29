from agents.base_agent import BaseAmazonAgent


class AmazonSalesListingAgent(BaseAmazonAgent):
    """Agent for generating Amazon product sales listings"""

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "sales_listing_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "sales_listing_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "AmazonSalesListingAgent"

    def generate_listing(self, link, item_condition):
        """
        Generate a sales listing for the given product link

        Args:
            link: Product URL (can be Amazon or any other website)
            item_condition: The condition of the item

        Returns:
            dict: Dictionary with 'result' (listing text) and 'tokens' (token count)
        """
        return self._generate_with_link(
            link, "sales listing", item_condition=item_condition
        )
