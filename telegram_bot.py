import argparse
import logging
import os

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from agents.amazon_reviewer_agent import AmazonReviewerAgent
from agents.amazon_sales_listing_agent import AmazonSalesListingAgent

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_LINK, SELECTING_CONDITION, GENERATING_OUTPUT = range(3)

# Item condition options for sales listings
ITEM_CONDITIONS = [
    ("🏷️ Nuovo con cartellino", "nuovo_con_cartellino", "Nuovo con cartellino"),
    ("✨ Nuovo senza cartellino", "nuovo_senza_cartellino", "Nuovo senza cartellino"),
    ("🌟 Come nuovo / Eccellente", "come_nuovo", "Come nuovo / Eccellente"),
    ("👍 Buono", "buono", "Buono"),
    ("📦 Usato", "usato", "Usato"),
]

# Default condition for listings
DEFAULT_ITEM_CONDITION = "Nuovo"

# Global agent instances
reviewer_agent = None
listing_agent = None
provider = "google"  # Default provider


# Main keyboard layout
def get_main_keyboard():
    """Get the main keyboard with persistent buttons"""
    return ReplyKeyboardMarkup(
        [
            ["📝 Genera Recensione", "💼 Genera Annuncio"],
            ["ℹ️ Aiuto", "❌ Stop"],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def _initialize_agent():
    """Initialize the Amazon Reviewer and Sales Listing Agents"""
    global reviewer_agent, listing_agent
    try:
        # Determine which provider and keys to use
        if provider.lower() == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL")
            if not api_key or not model:
                logger.error("OPENAI_API_KEY and OPENAI_MODEL must be defined in .env")
                return False
        elif provider.lower() == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            model = os.getenv("GOOGLE_MODEL")
            if not api_key or not model:
                logger.error("GOOGLE_API_KEY and GOOGLE_MODEL must be defined in .env")
                return False
        else:
            logger.error(f"Unsupported provider: {provider}")
            return False

        reviewer_agent = AmazonReviewerAgent(api_key, model, provider=provider)
        listing_agent = AmazonSalesListingAgent(api_key, model, provider=provider)
        logger.info(
            f"Amazon Reviewer and Sales Listing Agents initialized successfully with provider: {provider}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")

    # Clear any previous user data
    context.user_data.clear()

    welcome_message = (
        f"👋 Ciao {user.first_name}!\n\n"
        "🤖 Sono il tuo Amazon AI Agent Bot.\n\n"
        "✨ Posso aiutarti a:\n"
        "• 📝 Generare recensioni dettagliate\n"
        "• 💼 Creare annunci di vendita professionali\n\n"
        "📱 Usa i pulsanti qui sotto per iniziare:"
    )

    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())
    return WAITING_FOR_LINK


async def handle_button_press(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle main menu button presses"""
    user_input = update.message.text.strip()

    # Remove extra spaces within the text as well
    user_input = " ".join(user_input.split())

    if user_input == "📝 Genera Recensione":
        context.user_data["output_type"] = "review"
        message = (
            "📎 Per favore, inviami il link del prodotto Amazon\n\n"
            "⏳ La generazione della recensione potrebbe richiedere qualche minuto...\n\n"
            "Usa il pulsante ❌ Stop per annullare in qualsiasi momento."
        )
        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    elif user_input == "💼 Genera Annuncio":
        context.user_data["output_type"] = "listing"
        message = (
            "📎 Per favore, inviami il link del prodotto\n\n"
            "🌐 Puoi usare link da qualsiasi sito (Amazon, eBay, siti produttori, ecc.)\n\n"
            "⏳ La generazione dell'annuncio potrebbe richiedere qualche minuto...\n\n"
            "Usa il pulsante ❌ Stop per annullare in qualsiasi momento."
        )
        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    elif user_input == "ℹ️ Aiuto":
        help_text = (
            "ℹ️ Guida Rapida\n\n"
            "Come usare il bot:\n"
            "1️⃣ Scegli cosa generare:\n"
            "   • 📝 Recensione prodotto (solo Amazon)\n"
            "   • 💼 Annuncio di vendita (qualsiasi sito)\n"
            "2️⃣ Incolla il link del prodotto\n"
            "3️⃣ Per gli annunci, seleziona la condizione\n"
            "4️⃣ Aspetta la generazione (1-2 minuti)\n"
            "5️⃣ Ricevi il tuo testo!\n\n"
            "Comandi disponibili:\n"
            "• /start - Menu principale\n"
            "• /help - Questa guida\n\n"
            "Supporto:\n"
            "Se il link non funziona, assicurati che:\n"
            "• Sia un URL valido\n"
            "• Inizi con `https://`\n\n"
        )
        await update.message.reply_text(help_text, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    elif user_input == "❌ Stop":
        goodbye_text = (
            "👋 Arrivederci!\n\n" "Usa /start quando vuoi generare un nuovo testo."
        )
        await update.message.reply_text(goodbye_text, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    else:
        # User sent something that's not a button - check if it's a product link
        if user_input.startswith(("http://", "https://")):
            return await handle_product_link(update, context)

        # Invalid input
        await update.message.reply_text(
            "❌ Non ho capito. Usa i pulsanti per continuare.",
            reply_markup=get_main_keyboard(),
        )
        return WAITING_FOR_LINK


async def handle_product_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle product link and generate review or show condition selection for listing"""
    link = update.message.text.strip()

    # Remove extra spaces within the link as well
    link = " ".join(link.split())

    # Validate the link
    if not link.startswith(("http://", "https://")):
        await update.message.reply_text(
            "❌ Link non valido\n\n" "Assicurati che inizi con `http://` o `https://`",
            reply_markup=get_main_keyboard(),
        )
        return WAITING_FOR_LINK

    # Get output type from context (default to review if not set)
    output_type = context.user_data.get("output_type", "review")

    # For reviews, still require Amazon links
    if output_type == "review":
        amazon_identifiers = ["amazon", "amzn", "a.co", "dp/", "ASIN"]
        if not any(identifier in link.lower() for identifier in amazon_identifiers):
            await update.message.reply_text(
                "❌ Non sembra un link Amazon\n\n"
                "Per favore, inviami un link da amazon.com",
                reply_markup=get_main_keyboard(),
            )
            return WAITING_FOR_LINK

    logger.info(f"User {update.effective_user.id} requested {output_type} for: {link}")

    # For listings, show condition selection
    if output_type == "listing":
        # Store the link for later use
        context.user_data["product_link"] = link

        # Create inline keyboard for condition selection
        keyboard = [
            [InlineKeyboardButton(display_label, callback_data=f"condition:{value}")]
            for display_label, value, _ in ITEM_CONDITIONS
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📋 Seleziona la condizione del prodotto:",
            reply_markup=reply_markup,
        )
        return SELECTING_CONDITION

    # For reviews, generate immediately
    return await generate_output(update, context, link, output_type)


async def handle_condition_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle item condition selection from inline keyboard"""
    query = update.callback_query
    await query.answer()

    # Parse the callback data
    callback_data = query.data
    if not callback_data.startswith("condition:"):
        return WAITING_FOR_LINK

    condition_value = callback_data.replace("condition:", "")

    # Find the human-readable label for the condition (without emoji)
    condition_label = None
    for _, value, clean_label in ITEM_CONDITIONS:
        if value == condition_value:
            condition_label = clean_label
            break

    if not condition_label:
        condition_label = DEFAULT_ITEM_CONDITION

    # Store the condition
    context.user_data["item_condition"] = condition_label

    # Get the stored link
    link = context.user_data.get("product_link")
    if not link:
        await query.edit_message_text(
            "❌ Errore: Link non trovato. Usa /start per ricominciare."
        )
        return WAITING_FOR_LINK

    logger.info(
        f"User {update.effective_user.id} selected condition: {condition_label}"
    )

    # Update the message to show selected condition
    await query.edit_message_text(
        f"✅ Condizione selezionata: {condition_label}\n\n"
        "⏳ Sto generando il tuo annuncio di vendita...\n\n"
        "Questo potrebbe richiedere qualche minuto... Per favore, aspetta.\n\n"
        "🔄 Analizzando il prodotto..."
    )

    # Generate the listing
    return await generate_output(
        update, context, link, "listing", message_obj=query.message
    )


async def generate_output(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    link: str,
    output_type: str,
    message_obj=None,
) -> int:
    """Generate review or listing output"""

    # Determine which message object to use for replies
    if message_obj is None:
        message_obj = update.message

    # Show loading message for reviews (listings already show it in condition handler)
    if output_type == "review":
        loading_msg = (
            "⏳ Sto generando la tua recensione...\n\n"
            "Questo potrebbe richiedere qualche minuto... Per favore, aspetta.\n\n"
            "🔄 Analizzando il prodotto..."
        )
        await message_obj.reply_text(loading_msg, reply_markup=get_main_keyboard())

    success_header = (
        "💼 ANNUNCIO DI VENDITA GENERATO"
        if output_type == "listing"
        else "📝 RECENSIONE GENERATA"
    )

    try:
        # Generate output using the appropriate agent
        if output_type == "listing":
            if listing_agent is None:
                await message_obj.reply_text(
                    "❌ Errore: L'agente non è stato inizializzato.\n\n"
                    "Usa /start per ricominciare.",
                    reply_markup=get_main_keyboard(),
                )
                return WAITING_FOR_LINK

            # Get the item condition
            item_condition = context.user_data.get(
                "item_condition", DEFAULT_ITEM_CONDITION
            )
            result = listing_agent.generate_listing(link, item_condition)
        else:
            if reviewer_agent is None:
                await message_obj.reply_text(
                    "❌ Errore: L'agente non è stato inizializzato.\n\n"
                    "Usa /start per ricominciare.",
                    reply_markup=get_main_keyboard(),
                )
                return WAITING_FOR_LINK

            result = reviewer_agent.generate_review(link)

        # Send the result as a single message
        await message_obj.reply_text(
            f"{success_header}\n\n{result}",
            reply_markup=get_main_keyboard(),
        )

        logger.info(
            f"{output_type.capitalize()} generated successfully for user {update.effective_user.id}"
        )

        # Clear user data after successful generation
        context.user_data.clear()

    except Exception as e:
        logger.error(f"Error generating {output_type}: {e}")
        await message_obj.reply_text(
            f"❌ Errore durante la generazione\n\n"
            f"`{str(e)}`\n\n"
            f"Per favore, riprova con un link diverso.",
            reply_markup=get_main_keyboard(),
        )
        # Clear user data after error
        context.user_data.clear()

    return WAITING_FOR_LINK


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "ℹ️ AI Agent Bot\n\n"
        "Come usare:\n"
        "1️⃣ Scegli cosa generare:\n"
        "   • 📝 Recensione prodotto (solo Amazon)\n"
        "   • 💼 Annuncio di vendita (qualsiasi sito)\n"
        "2️⃣ Incolla il link del prodotto\n"
        "3️⃣ Per gli annunci, seleziona la condizione\n"
        "4️⃣ Aspetta la generazione (1-2 minuti)\n"
        "5️⃣ Ricevi il tuo testo!\n\n"
        "Comandi disponibili:\n"
        "• /start - Menu principale\n"
        "• /help - Questa guida\n\n"
        "Note tecniche:\n"
        "• Alimentato da OpenAI GPT-4\n"
        "• Usa DataPizza AI Framework\n"
        "• Python Telegram Bot\n\n"
        "Supporto:\n"
        "Se hai problemi, assicurati che il link sia valido."
    )
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "👋 Operazione annullata\n\n" "Usa i pulsanti per continuare!",
        reply_markup=get_main_keyboard(),
    )
    # Clear user data
    context.user_data.clear()
    return WAITING_FOR_LINK


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Si è verificato un errore. Per favore, riprova con /start"
        )


def _parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Start the Amazon AI Agent Telegram Bot"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "google"],
        default="openai",
        help="AI provider: 'openai' or 'google' (default: openai)",
    )
    return parser.parse_args()


def main() -> None:
    """Start the bot"""
    global provider

    # Parse arguments
    args = _parse_arguments()
    provider = args.provider
    logger.info(f"Starting Telegram bot with provider: {provider}")

    # Initialize the agent
    if not _initialize_agent():
        logger.error("Failed to initialize agent. Exiting.")
        return

    # Get bot token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN must be defined in .env")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
        ],
        states={
            WAITING_FOR_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
            ],
            SELECTING_CONDITION: [
                CallbackQueryHandler(handle_condition_selection, pattern="^condition:"),
            ],
            GENERATING_OUTPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("cancel", cancel),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
