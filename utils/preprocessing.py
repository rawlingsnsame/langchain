import re
import unicodedata


def preprocess_query(query: str) -> str:
    """
    Lightweight query preprocessing
    """
    # Normalize unicode characters
    query = (
        unicodedata.normalize("NFKD", query).encode("ascii", "ignore").decode("utf-8")
    )

    # Remove special characters and extra whitespaces
    query = re.sub(r"[^\w\s]", "", query)

    # Convert to lowercase
    query = query.lower()

    # Remove common stop words
    stop_words = {"the", "a", "an", "in", "to", "for", "of", "and", "or", "is", "are"}
    query_words = [word for word in query.split() if word not in stop_words]

    return " ".join(query_words)
