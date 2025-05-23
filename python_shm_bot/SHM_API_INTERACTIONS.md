# SHM API Interaction Points for Telegram Bot

This document details the API interaction points between the Python Telegram Bot and the SHM (Server Hosting Manager) system.

## 1. General Principles

### Authentication/User Identification

*   **Current Strategy:** User identification is currently simplified. The bot uses the **Telegram username** of the interacting user as the `login` parameter when calling SHM API endpoints.
*   **Limitations & Future Needs:** This approach has significant limitations:
    *   **Security:** Telegram usernames can be changed and potentially impersonated if not properly verified.
    *   **Mapping:** It assumes a direct 1:1 mapping between Telegram usernames and SHM user logins, which may not always be the case. Users might have different usernames across systems or no SHM account.
    *   **Robust Solution Needed:** For a production environment, a more robust and secure user identification and authentication mechanism is crucial. This could involve:
        *   A one-time registration process where Telegram users link their account to their SHM account.
        *   OAuth2 flow if SHM supports it.
        *   API tokens specific to users, managed within SHM and provided to the bot by the user through a secure channel.
*   **SHM API Base URL:** The base URL for all SHM API calls is configured via the `SHM_API_URL` environment variable, loaded from the `.env` file (e.g., `SHM_API_URL=https://your-shm-domain.com/api/`).

## 2. Interaction with `misc/bot_api.tt` (via `run_template/misc_bot_api`)

This endpoint is designed to fetch user-specific details and a list of their services from SHM. It's assumed to be implemented in SHM as a template (e.g., `misc/bot_api.tt`) that is executed via a generic "run template" API endpoint.

*   **Purpose:**
    *   Fetch the authenticated user's details (e.g., balance, SHM login, SHM user ID).
    *   Fetch a list of services associated with the authenticated user, including their status and expiration dates.
*   **Bot Commands Using It:**
    *   `/balance` (currently implemented to fetch and display user balance).
    *   Potentially a future `/services` command to list user services.
*   **SHM Endpoint (Conceptual):** `[SHM_API_URL]/run_template/misc_bot_api`
    *   `[SHM_API_URL]` is the base URL from the environment variable.
    *   `run_template/misc_bot_api` is the path that SHM would map to execute the `misc/bot_api.tt` template (or an equivalent API handler).
*   **HTTP Method:** `GET`
*   **Query Parameters:**
    *   `login=<shm_user_login>`: The login identifier for the SHM user. Currently, the bot uses the Telegram username.
    *   `format=json`: Specifies that the response should be in JSON format.
*   **Success Response (Expected JSON Structure):**
    The structure is based on the data typically available from `user.list_for_api` and `selectUser.services.list_for_api` in SHM.

    ```json
    {
      "user": {
        "user_id": "string",  // e.g., "12345"
        "login": "string",    // e.g., "telegram_username" or actual SHM login
        "balance": "string_or_number", // e.g., "100.50" or 100.50
        // ... other user fields as returned by user.list_for_api
        "email": "string",
        "fname": "string",
        "lname": "string"
      },
      "services": [
        {
          // ... fields for each service as returned by selectUser.services.list_for_api
          "id": "string_or_number",       // e.g., "s1001"
          "name": "string",             // e.g., "Basic Web Hosting"
          "status": "string",           // e.g., "Active", "Expired", "Suspended"
          "status_id": "string_or_number",
          "expire": "date_string_or_null", // e.g., "2024-12-31" or null
          "price": "string_or_number"
          // ... other relevant service fields
        }
        // ... more services
      ]
    }
    ```
*   **Failure Response:**
    *   **Specific SHM Error (JSON):** SHM might return a JSON response indicating no data or a specific error, for example:
        ```json
        {"response": "No data"} 
        ```
        or
        ```json
        {"error": "User not found"}
        ```
    *   **Standard HTTP Errors:** The API client in the bot also handles standard HTTP error codes (4xx, 5xx) which would indicate issues like authentication failure, endpoint not found, or server errors on the SHM side. These are typically returned as `None` by the `call_shm_api` function after logging the error.

## 3. Requirements for a New `/order_service` Endpoint (Hypothetical)

This section outlines the conceptual requirements for a new SHM API endpoint that would allow users to order new services via the Telegram bot. **This endpoint does not currently exist and would need to be developed within the SHM system.**

*   **Purpose:** Allow a registered and identified user to order or request a new service available in SHM.
*   **Conceptual SHM Endpoint:** `[SHM_API_URL]/api/order_service` (This is an example; the actual path would be determined during SHM development).
*   **HTTP Method:** `POST`
*   **Request Body (Example JSON):**
    The request body would need to identify the user and the service they wish to order.

    ```json
    {
      "shm_user_login": "<user_identifier_for_shm>", // Could be the SHM login, user_id, or an API token.
                                                     // Must align with the robust authentication strategy.
      "service_id_to_order": "<service_id_from_shm_catalog>", // The specific ID of the service to be ordered.
      "billing_cycle": "monthly", // Optional: e.g., monthly, annually
      "payment_details": { // Optional, depending on SHM's billing workflow and if payment is immediate.
        "method": "from_balance", // e.g., "from_balance", "credit_card_on_file", "new_card_token"
        "card_token": "tok_xxxxxxxxxxxx" // If a new card is used
      }
    }
    ```
*   **Success Response (Example JSON):**
    A successful response should confirm the order and provide details.

    ```json
    {
      "status": "success",
      "order_id": "<unique_order_id_from_shm>", // e.g., "ORD123456"
      "service_id_activated": "<activated_service_instance_id>", // e.g., "s2002"
      "message": "Service 'Example Hosting' ordered successfully. It will be active shortly.",
      "next_due_date": "2025-01-15" // If applicable
    }
    ```
*   **Failure Response (Example JSON):**
    A failure response should indicate the reason for the failure.

    ```json
    {
      "status": "error",
      "message": "Failed to order service: Insufficient account balance.",
      // Specific error codes could also be useful:
      "error_code": "INSUFFICIENT_FUNDS" 
    }
    ```
    Other examples for `message`:
    *   "Failed to order service: Invalid service ID."
    *   "Failed to order service: User authentication failed."
    *   "Failed to order service: This service cannot be ordered at this time."

*   **SHM Implementation Note:**
    The actual implementation of this functionality within SHM would require a new API endpoint or a new SHM template. This template/handler would be responsible for:
    1.  Authenticating the user based on `shm_user_login` or a token.
    2.  Validating the `service_id_to_order`.
    3.  Checking user eligibility (e.g., sufficient balance, no outstanding invoices, prerequisites met).
    4.  Processing the order (creating the service, generating an invoice, applying payment).
    5.  Returning an appropriate success or failure response.

This documentation should be updated as the SHM API evolves and new integration points are added.
