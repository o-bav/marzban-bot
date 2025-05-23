# This is the main file for the Telegram bot.

import os
import logging
import asyncio  # Required for run_in_executor
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler  # Removed unused MessageHandler, filters

from shm_api_client import call_shm_api  # Import the SHM API client function

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define the /start command handler
async def start(update, context):
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! I am your SHM integrated bot.")


# Define the /help command handler
async def help_command_handler(update, context):
    """Sends a help message listing all available commands."""
    help_text = """\
Here are the available commands:
/start - Get a welcome message.
/help - Show this help message.
/balance - Check your SHM account balance.
/services - List your active SHM services.
/order_service <service_id> - Order a new SHM service. (e.g., /order_service basic_hosting)
"""
    await update.message.reply_text(help_text)
    logger.info(f"/help command executed by {update.effective_user.username}")


# Define the /balance command handler
async def balance_command_handler(update, context):
    """Fetches and displays the user's SHM balance."""
    user_info = f"user {update.effective_user.username} (ID: {update.effective_user.id})"
    logger.info(f"/balance command received from {user_info}")

    # --- SHM User Identification ---
    # IMPORTANT: Using Telegram username as 'login' for SHM API.
    # This is a simplification for initial development.
    # A production system would require a more robust and secure mechanism
    # to map Telegram users to SHM system users (e.g., a registration/linking process).
    telegram_username = update.effective_user.username
    if not telegram_username:
        await update.message.reply_text(
            "Your Telegram username is not set. I need your username to fetch your SHM balance."
        )
        logger.warning(f"User {update.effective_user.id} does not have a Telegram username set.")
        return

    # Using "run_template/misc_bot_api" as the placeholder endpoint.
    # This assumes SHM can execute a template like misc/bot_api.tt via such an endpoint.
    # The actual endpoint structure needs to be confirmed with the SHM API documentation.
    shm_endpoint = "run_template/misc_bot_api"
    log_msg = (
        f"Attempting SHM API endpoint: {shm_endpoint} "
        f"for /balance for {telegram_username}."
    )
    logger.info(log_msg)

    api_params = {'login': telegram_username, 'format': 'json'}

    # Call the SHM API using the async wrapper
    api_response = await call_shm_api_async_wrapper(shm_endpoint, params=api_params, method="GET")

    if api_response:
        try:
            # Based on misc/bot_api.tt, the structure is likely {'user': {'balance': 'value', ...}}
            # or possibly nested if 'ret' is a list, e.g. ret.first.balance
            # For now, assuming 'user' is a direct key in the response.
            user_data = api_response.get('user')
            if user_data and 'balance' in user_data:
                balance = user_data['balance']
                await update.message.reply_text(f"Your SHM balance is: {balance}")
                logger.info(f"Successfully retrieved balance for {telegram_username}: {balance}")
            else:
                warn_msg = (
                    f"Balance not found in API response for {telegram_username}. "
                    f"Response: {api_response}"
                )
                logger.warning(warn_msg)
                await update.message.reply_text(
                    "Could not retrieve your balance. Unexpected server data format."
                )
        except Exception as e:
            error_msg = (
                f"Error processing API response for {telegram_username}: {e}. "
                f"Response: {api_response}"
            )
            logger.error(error_msg)
            await update.message.reply_text(
                "Error processing your balance information. Please try again later."
            )
    else:
        error_msg = (
            f"Failed to get balance for {telegram_username}. "
            f"API call to {shm_endpoint} failed."
        )
        logger.error(error_msg)
        await update.message.reply_text("Could not retrieve your balance. Please try again later.")


# Define the /services command handler
async def services_command_handler(update, context):
    """Fetches and displays the user's SHM services."""
    user_info = f"user {update.effective_user.username} (ID: {update.effective_user.id})"
    logger.info(f"/services command received from {user_info}")

    telegram_username = update.effective_user.username
    if not telegram_username:
        await update.message.reply_text(
            "Your Telegram username is not set. I need your username to fetch your SHM services."
        )
        logger.warning(f"User {update.effective_user.id} does not have a Telegram username set.")
        return

    shm_endpoint = "run_template/misc_bot_api"
    log_msg = (
        f"Attempting SHM API endpoint: {shm_endpoint} "
        f"for /services for {telegram_username}."
    )
    logger.info(log_msg)

    api_params = {'login': telegram_username, 'format': 'json'}

    api_response = await call_shm_api_async_wrapper(shm_endpoint, params=api_params, method="GET")

    if api_response:
        try:
            services = api_response.get('services', [])
            if services:
                message_lines = ["Your SHM services:"]
                for service in services:
                    name = service.get('name', 'N/A')
                    status = service.get('status', 'N/A')
                    expire_date = service.get('expire', 'N/A')
                    # Ensure expire_date is formatted nicely if it's a date object or specific string
                    if expire_date and not isinstance(expire_date, str):
                        try:
                            # Attempt a basic formatting, actual date parsing might be needed
                            expire_date = str(expire_date).split(' ')[0]
                        except Exception:
                            expire_date = str(expire_date) # fallback

                    message_lines.append(
                        f"- Service: {name}, Status: {status}, Expires: {expire_date}"
                    )
                await update.message.reply_text("\n".join(message_lines))
                logger.info(f"Successfully retrieved {len(services)} services for {telegram_username}")
            else:
                await update.message.reply_text("You have no active services.")
                logger.info(f"No services found for {telegram_username}.")
        except Exception as e:
            error_msg = (
                f"Error processing API response for /services for {telegram_username}: {e}. "
                f"Response: {api_response}"
            )
            logger.error(error_msg)
            await update.message.reply_text(
                "Error processing your services information. Please try again later."
            )
    else:
        error_msg = (
            f"Failed to get services for {telegram_username}. "
            f"API call to {shm_endpoint} failed."
        )
        logger.error(error_msg)
        await update.message.reply_text("Could not retrieve your services at this time.")


# Define the /order_service command handler
async def order_service_command_handler(update, context):
    """Handles the /order_service <service_id> command."""
    # IMPORTANT: This command relies on a hypothetical SHM API endpoint
    # `api/order_service` which needs to be implemented on the SHM server side.
    user_info = f"user {update.effective_user.username} (ID: {update.effective_user.id})"
    logger.info(f"/order_service command received from {user_info}")

    # Argument Parsing
    if not context.args:
        await update.message.reply_text("Usage: /order_service <service_id>")
        return
    service_id_argument = context.args[0]

    # User Identification
    telegram_username = update.effective_user.username
    if not telegram_username:
        await update.message.reply_text(
            "Your Telegram username is not set. I need your username to order a service."
        )
        logger.warning(f"User {update.effective_user.id} tried /order_service without a username.")
        return

    # API Call Details
    shm_endpoint = "api/order_service"  # Hypothetical endpoint
    api_payload = {
        "shm_user_login": telegram_username,
        "service_id_to_order": service_id_argument
    }

    logger.info(
        f"Attempting to order service_id '{service_id_argument}' for {telegram_username} "
        f"via SHM API endpoint: {shm_endpoint}"
    )

    # Call the SHM API
    # Note: `call_shm_api` already correctly uses the `json` parameter for POST requests
    # if `params` is a dict, so it sends the payload as JSON body.
    api_response = await call_shm_api_async_wrapper(
        shm_endpoint,
        params=api_payload,  # This will be sent as JSON body for POST
        method="POST"
    )

    # Process Response (Hypothetical based on SHM_API_INTERACTIONS.md)
    if api_response:
        # Assuming a successful response structure like:
        # {"status": "success", "message": "Service ordered.", "order_id": "ORD123"}
        if api_response.get('status') == 'success':
            success_message = api_response.get('message', f"Service {service_id_argument} ordered successfully!")
            await update.message.reply_text(success_message)
            logger.info(
                f"Service {service_id_argument} ordered successfully for {telegram_username}. "
                f"Response: {api_response}"
            )
        else:
            # Assuming an error response structure like:
            # {"status": "error", "message": "Insufficient funds."}
            error_reason = api_response.get('message', "Unknown error from SHM.")
            full_error_message = f"Failed to order service {service_id_argument}. Reason: {error_reason}"
            await update.message.reply_text(full_error_message)
            logger.error(
                f"Failed to order service {service_id_argument} for {telegram_username}. "
                f"Reason: {error_reason}. Full API Response: {api_response}"
            )
    else:
        # API call itself failed (network error, timeout, 5xx, etc.)
        await update.message.reply_text(
            f"Failed to order service {service_id_argument}. "
            "Could not connect to the ordering system. Please try again later."
        )
        logger.error(
            f"API call failed for /order_service for {telegram_username}, service_id {service_id_argument}."
        )


# Wrapper to run synchronous call_shm_api in an async context
# python-telegram-bot handlers are async, but `requests` (used in call_shm_api) is synchronous.
async def call_shm_api_async_wrapper(*args, **kwargs):
    loop = asyncio.get_event_loop()
    # call_shm_api is I/O bound, so run_in_executor is appropriate
    return await loop.run_in_executor(None, call_shm_api, *args, **kwargs)


def main():
    """Starts the Telegram bot."""
    # Load environment variables from .env file
    load_dotenv()

    # Get Telegram Bot Token from environment variables
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    SHM_API_URL = os.getenv("SHM_API_URL")

    if not TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN not found in env variables. Please set it in .env file."
        )
        return

    if not SHM_API_URL:
        warn_msg = (
            "SHM_API_URL not found in env variables. "
            "SHM integration will be disabled."
        )
        logger.warning(warn_msg)
        # Store it as None or some indicator that it's not available
        # For now, just logging is fine as per requirements.

    # Create an Application instance
    application = Application.builder().token(TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))
    # Register the /balance command handler
    application.add_handler(CommandHandler("balance", balance_command_handler))
    # Register the /services command handler
    application.add_handler(CommandHandler("services", services_command_handler))
    # Register the /order_service command handler
    application.add_handler(CommandHandler("order_service", order_service_command_handler))
    # Register the /help command handler
    application.add_handler(CommandHandler("help", help_command_handler))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
