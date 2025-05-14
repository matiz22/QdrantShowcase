from openai import OpenAI
client = OpenAI()

def get_openai_embedding(text: str, model: str = "text-embedding-3-large") -> list:
    """
    Generate embeddings for the given text using OpenAI's embedding model.

    Args:
        text (str): The input text to embed.
        model (str): The OpenAI embedding model to use. Default is 'text-embedding-ada-002'.

    Returns:
        list: A list of floats representing the embedding vector.
    """
    try:
        response = client.embeddings.create(input = [text], model=model).data[0].embedding
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")
