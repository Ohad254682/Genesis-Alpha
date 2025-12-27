"""
LLM utility functions for OpenAI integration
"""
from langchain_openai import ChatOpenAI
import time
from openai import APIConnectionError, APITimeoutError, APIError
from requests.exceptions import ConnectionError as RequestsConnectionError

# Try to import streamlit for caching (optional - if not available, caching won't work)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create a dummy decorator if streamlit is not available
    def cache_data(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    st = type('obj', (object,), {'cache_data': cache_data})()


def initialize_llm(api_key, max_retries=3):
    """
    Initialize the ChatOpenAI language model with connection error handling.

    Parameters:
    api_key (str): The API key for accessing the OpenAI service.
    max_retries (int): Maximum number of retry attempts for initialization.

    Returns:
    ChatOpenAI: The initialized language model.
    
    Raises:
    ConnectionError: If connection fails after all retries.
    """
    if not api_key:
        raise ValueError("API key is required to initialize the LLM.")
    
    last_error = None
    for attempt in range(max_retries):
        try:
            llm = ChatOpenAI(
                model="gpt-4o", 
                temperature=0, 
                api_key=api_key,
                timeout=30.0  # 30 second timeout
            )
            # Test the connection with a simple call
            try:
                llm.invoke("test")
            except Exception:
                pass  # Just testing if it initializes, ignore response
            return llm
        except (APIConnectionError, APITimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))  # Exponential backoff
            else:
                raise RequestsConnectionError(
                    f"Failed to initialize LLM after {max_retries} attempts. "
                    "Please check your internet connection or VPN. "
                    f"Error: {str(e)}"
                ) from e
        except APIError as e:
            # API errors (like invalid key) shouldn't be retried
            raise ValueError(f"OpenAI API error: {str(e)}") from e
    
    raise ConnectionError(
        f"Failed to initialize LLM after {max_retries} attempts. "
        "Please check your internet connection or VPN."
    )


@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours (LLM responses are expensive)
def get_llm_response(llm, prompt, max_retries=3, retry_delay=2):
    """
    Get the response from the language model for a given prompt with retry logic.
    Cached to reduce expensive API calls. Note: llm object is not used in cache key.
    
    Parameters:
    llm (ChatOpenAI): The initialized language model (not used in cache key).
    prompt (str): The prompt to send to the language model.
    max_retries (int): Maximum number of retry attempts.
    retry_delay (float): Delay between retries in seconds.

    Returns:
    str: The content of the language model's response.
    
    Raises:
    ConnectionError: If connection fails after all retries.
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            return response.content
        except (APIConnectionError, APITimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                raise RequestsConnectionError(
                    f"Failed to get LLM response after {max_retries} attempts. "
                    "Please check your internet connection or VPN. "
                    f"Error: {str(e)}"
                ) from e
        except APIError as e:
            # API errors (like rate limits, invalid requests) shouldn't be retried indefinitely
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1) * 2)  # Longer wait for rate limits
            else:
                raise ValueError(f"OpenAI API error: {str(e)}") from e
    
    raise ConnectionError(
        f"Failed to get LLM response after {max_retries} attempts. "
        "Please check your internet connection or VPN."
    )

