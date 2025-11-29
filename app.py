import argparse
import logging
import os

from dotenv import load_dotenv

from agents.amazon_reviewer_agent import AmazonReviewerAgent
from agents.amazon_sales_listing_agent import AmazonSalesListingAgent
from agents.email_rewriter_agent import EmailRewriterAgent
from agents.prompt_optimizer_agent import PromptOptimizerAgent

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_environment(provider):
    """Load environment variables for the specified provider"""
    load_dotenv()

    if provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")
        if not api_key or not model:
            raise ValueError("OPENAI_API_KEY and OPENAI_MODEL must be defined in .env")
    elif provider.lower() == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GOOGLE_MODEL")
        if not api_key or not model:
            raise ValueError("GOOGLE_API_KEY and GOOGLE_MODEL must be defined in .env")
    else:
        raise ValueError(f"Unsupported provider: {provider}. Available: openai, google")

    logger.info(f"Environment loaded with provider: {provider}, model: {model}")
    return api_key, model


def _parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate an Amazon product review, sales listing, optimize a prompt, or rewrite an email using an AI agent"
    )
    parser.add_argument(
        "link", nargs="?", help="Amazon product link, prompt text, or email text"
    )
    parser.add_argument(
        "--type",
        choices=["review", "listing", "optimize-prompt", "rewrite-email"],
        default="review",
        help="Output type: 'review' for product review, 'listing' for sales listing, 'optimize-prompt' for prompt optimization, or 'rewrite-email' for email rewriting (default: review)",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "google"],
        default="google",
        help="AI provider: 'openai' or 'google' (default: google)",
    )
    return parser.parse_args()


def main():
    """Main function"""
    try:
        logger.info("Starting Amazon review/listing generator or prompt optimizer")

        # Parse arguments
        args = _parse_arguments()
        link = args.link
        output_type = args.type
        provider = args.provider

        # Validate that link is provided
        if not link:
            logger.error("Link or prompt text is required")
            raise ValueError("Please provide a link or prompt text")

        logger.info(
            f"Processing: {link[:50]}... (type: {output_type}, provider: {provider})"
        )

        # Load environment
        api_key, model = _load_environment(provider)

        # Initialize appropriate agent based on type
        if output_type == "listing":
            agent = AmazonSalesListingAgent(api_key, model, provider=provider)
            logger.info("Sales Listing Agent initialized")

            # Generate sales listing
            logger.info("Generating sales listing...")
            output = agent.generate_listing(link)
            result = output["result"]
            tokens = output["tokens"]
            logger.info("Sales listing generated successfully")
        elif output_type == "optimize-prompt":
            agent = PromptOptimizerAgent(api_key, model, provider=provider)
            logger.info("Prompt Optimizer Agent initialized")

            # Optimize prompt
            logger.info("Optimizing prompt...")
            output = agent.optimize_prompt(link)
            result = output["result"]
            tokens = output["tokens"]
            logger.info("Prompt optimized successfully")
        elif output_type == "rewrite-email":
            agent = EmailRewriterAgent(api_key, model, provider=provider)
            logger.info("Email Rewriter Agent initialized")

            # Rewrite email
            logger.info("Rewriting email...")
            output = agent.rewrite_email(link)
            result = output["result"]
            tokens = output["tokens"]
            logger.info("Email rewritten successfully")
        else:
            agent = AmazonReviewerAgent(api_key, model, provider=provider)
            logger.info("Reviewer Agent initialized")

            # Generate review
            logger.info("Generating review...")
            output = agent.generate_review(link)
            result = output["result"]
            tokens = output["tokens"]
            logger.info("Review generated successfully")

        print(result)
        print(f"\n📊 Input tokens: {tokens}")

    except FileNotFoundError as e:
        logger.error(f"File not found - {e}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
