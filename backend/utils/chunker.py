import re

def chunk_text(text, max_chars=3000, overlap=200):
    """
    Split text into overlapping chunks for LLM processing.

    Args:
        text (str): The input document text.
        max_chars (int): Max characters per chunk.
        overlap (int): How many chars to overlap between chunks (for context).

    Returns:
        list[str]: List of text chunks.
    """
    if not text:
        return []

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars

        # Try to break at last sentence end before the limit
        if end < len(text):
            period = text.rfind('.', start, end)
            if period != -1 and period > start + max_chars // 2:
                end = period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap  # move with overlap
        if start < 0:
            start = 0

    return chunks


if __name__ == "__main__":
    # quick test
    sample = "This is a very long text. " * 200
    result = chunk_text(sample, max_chars=200, overlap=50)
    print(f"Chunks: {len(result)}")
    for i, c in enumerate(result[:3], 1):
        print(f"\n--- Chunk {i} ---\n{c[:100]}...")
