import os
import requests
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)


def call_shm_api(endpoint: str, params: dict = None, method: str = "GET"):
    """
    Calls a specified endpoint of the SHM API.

    Args:
        endpoint (str): The API endpoint to call (e.g., "/status", "data/latest").
        params (dict, optional): A dictionary of parameters to send with the request.
                                 Defaults to None.
        method (str, optional): The HTTP method to use ("GET" or "POST"). Defaults to "GET".

    Returns:
        dict or None: The JSON response from the API if successful, None otherwise.
    """
    shm_api_url = os.getenv("SHM_API_URL")

    if not shm_api_url:
        logger.error("SHM_API_URL is not configured. Cannot make API calls.")
        return None

    # Construct the full URL, ensuring no double slashes
    full_url = f"{shm_api_url.rstrip('/')}/{endpoint.lstrip('/')}"

    try:
        # To prevent E501 if params is very long, truncate for the log message
        params_str = str(params)
        if len(params_str) > 40:  # Heuristic for truncation
            params_str = params_str[:37] + "..."
        # Use full_url as per subtask's suggested structure for the main call log
        logger.info(f"SHM API call: {method} {full_url}")
        if params:
            # Ensure params_str is logged. This line should be short.
            logger.info(f"Params: {params_str}")
        if method.upper() == "GET":
            response = requests.get(full_url, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(full_url, json=params, timeout=10)  # Assuming POST data is JSON
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        # Attempt to parse JSON
        try:
            json_response = response.json()
            # Split debug log to prevent E501
            logger.debug(f"SHM API response for {full_url}:")
            json_response_str = str(json_response)
            if len(json_response_str) > 500: # Heuristic limit for debug log
                json_response_str = json_response_str[:497] + "..."
            logger.debug(json_response_str)
            return json_response
        except ValueError:  # Includes JSONDecodeError
            logger.error(
                f"Failed to parse JSON response from {full_url}. Response text: {response.text}"
            )
            return None

    except requests.exceptions.HTTPError as http_err:
        error_log = (
            f"HTTP error for {full_url}: {http_err} - "
            f"Status: {response.status_code} - Resp: {response.text}"
        )
        logger.error(error_log)
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection error for {full_url}: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout error occurred while calling {full_url}: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"An unexpected error occurred while calling {full_url}: {req_err}")
        return None
    except Exception as e:
        logger.error(f"A general error occurred in call_shm_api for {full_url}: {e}")
        return None


if __name__ == '__main__':
    # Example usage (requires .env file with SHM_API_URL for testing)
    # Create a .env file in the telegram_bot directory with:
    # SHM_API_URL=https://jsonplaceholder.typicode.com
    # (this is a public test API)

    from dotenv import load_dotenv
    load_dotenv()  # Load .env from current directory or parent

    logger.info("Testing shm_api_client.py...")

    # Test GET request
    test_endpoint_get = "/todos/1"  # Example endpoint for jsonplaceholder
    logger.info(f"Calling GET {test_endpoint_get}")
    get_response = call_shm_api(test_endpoint_get)
    if get_response:
        logger.info(f"GET Response: {get_response}")
    else:
        logger.warning("GET Request failed or returned None.")

    # Test POST request
    test_endpoint_post = "/posts"  # Example endpoint for jsonplaceholder
    post_data = {"title": "foo", "body": "bar", "userId": 1}
    logger.info(f"Calling POST {test_endpoint_post} with data: {post_data}")
    post_response = call_shm_api(test_endpoint_post, params=post_data, method="POST")
    if post_response:
        logger.info(f"POST Response: {post_response}")
    else:
        logger.warning("POST Request failed or returned None.")

    # Test with a non-existent SHM_API_URL (temporarily unset it for this test if possible,
    # or test manually)
    # original_shm_api_url = os.environ.pop("SHM_API_URL", None)
    # logger.info("Testing with SHM_API_URL unset...")
    # no_url_response = call_shm_api(test_endpoint_get)
    # assert no_url_response is None, "Expected None when SHM_API_URL is not set."
    # logger.info("Test with SHM_API_URL unset passed.")
    # if original_shm_api_url:  # Restore it if it was set
    #     os.environ["SHM_API_URL"] = original_shm_api_url

    # Test with a non-existent endpoint (will likely result in 404)
    logger.info("Testing with a non-existent endpoint '/nonexistent'")
    not_found_response = call_shm_api("/nonexistent")
    # Depending on the API, this might return None or a specific error structure.
    # For jsonplaceholder, it's a 404, which call_shm_api should handle and return None.
    assert not_found_response is None, f"Expected None for a 404, got {not_found_response}"
    logger.info("Test with non-existent endpoint finished (expected None).")

    logger.info("shm_api_client.py testing complete.")
