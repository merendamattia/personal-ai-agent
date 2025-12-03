import logging
import os
from abc import ABC, abstractmethod

from datapizza.agents import Agent
from dotenv import load_dotenv

from tools.web_fetch import create_web_fetch_tool
from utils.client_utils import get_client
from utils.prompt_loader import load_prompt
from utils.token_utils import count_tokens
from utils.url_utils import expand_short_url

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseAmazonAgent(ABC):
    """Base class for Amazon agents with common functionality"""

    def __init__(self, api_key, model, provider="google"):
        """
        Initialize the BaseAmazonAgent

        Args:
            api_key: API key for the provider
            model: Model name
            provider: Provider name ('openai' or 'google', default: 'google')
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.agent = None
        self.run_prompt_template = None

        logger.info(
            f"Initializing {self.__class__.__name__} with model: {model} (provider: {provider})"
        )
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the internal agent"""
        # Load prompts (subclasses define which prompts to load)
        system_prompt = load_prompt(self.get_system_prompt_filename())
        self.run_prompt_template = load_prompt(self.get_run_prompt_filename())

        logger.info("Creating web fetch tool with truncation support")

        # Create the web fetch tool with truncation
        web_fetch_tool = create_web_fetch_tool()

        # Get the appropriate client based on provider
        client = get_client(self.provider, self.api_key, self.model)

        # Create agent with the tool
        self.agent = Agent(
            name=self.get_agent_name(),
            tools=[web_fetch_tool],
            client=client,
            system_prompt=system_prompt,
        )

        logger.info("Agent initialized successfully")

    def _generate(self, output_type, **kwargs):
        """
        Generate output based on the provided parameters

        Args:
            output_type: Type of output being generated (for logging)
            **kwargs: Additional parameters to pass to the prompt template

        Returns:
            dict: Dictionary with keys 'result' (generated text) and 'tokens' (token count)
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")

        logger.info(f"Generating {output_type}")

        # Format the run prompt with the provided parameters
        run_prompt = self.run_prompt_template.format(**kwargs)

        # Count tokens in both system prompt and run prompt
        system_prompt = load_prompt(self.get_system_prompt_filename())
        system_token_count = count_tokens(system_prompt)
        run_token_count = count_tokens(run_prompt)
        total_token_count = system_token_count + run_token_count

        logger.info(f"System prompt contains {system_token_count} tokens")
        logger.info(f"Run prompt contains {run_token_count} tokens")
        logger.info(f"Total input tokens: {total_token_count}")

        # Run the agent
        response = self.agent.run(run_prompt)
        result = response.text

        logger.info(
            f"{output_type.capitalize()} generated successfully (tokens: {total_token_count})"
        )
        return {"result": result, "tokens": total_token_count}

    def _generate_with_link(self, link, output_type, **kwargs):
        """
        Generate output for the given product link

        Args:
            link: Product URL or text content
            output_type: Type of output being generated (for logging)
            **kwargs: Additional parameters to pass to the prompt template

        Returns:
            dict: Dictionary with keys 'result' (generated text) and 'tokens' (token count)
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")

        logger.info(
            f"Generating {output_type} for: {link[:50] if len(link) > 50 else link}"
        )

        # Only expand URL if it's a real link (starts with http)
        if link.startswith(("http://", "https://")):
            expanded_link = expand_short_url(link)
            logger.info(f"Using link: {expanded_link}")
        else:
            expanded_link = link
            logger.info(f"Using content text")

        # Build the prompt parameters
        prompt_params = {"link": expanded_link}
        prompt_params.update(kwargs)

        # Format the run prompt with the provided parameters
        run_prompt = self.run_prompt_template.format(**prompt_params)

        # Count tokens in both system prompt and run prompt
        system_prompt = load_prompt(self.get_system_prompt_filename())
        system_token_count = count_tokens(system_prompt)
        run_token_count = count_tokens(run_prompt)
        total_token_count = system_token_count + run_token_count

        logger.info(f"System prompt contains {system_token_count} tokens")
        logger.info(f"Run prompt contains {run_token_count} tokens")
        logger.info(f"Total input tokens: {total_token_count}")

        # Run the agent
        response = self.agent.run(run_prompt, tool_choice="required_first")
        result = response.text

        logger.info(
            f"{output_type.capitalize()} generated successfully (tokens: {total_token_count})"
        )
        return {"result": result, "tokens": total_token_count}

    @abstractmethod
    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        pass

    @abstractmethod
    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        pass

    @abstractmethod
    def get_agent_name(self):
        """Return the name of the agent"""
        pass
