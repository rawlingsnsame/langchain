# Cameroon Tax Code AI Assistant

An AI-powered application that answers questions about Cameroon's tax code using OpenAI and Pinecone for vector search.
To perform chats with this App make a connection through its websocket

## Prerequisites

- Python 3.9+
- OpenAI API key
- Pinecone API key
- PDF document containing Cameroon tax code

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=cameroon-tax-doc
```

## Initial Setup

### Generating Embeddings

1. Place your tax code PDF in an accessible location
2. Update the PDF path in the embeddings generation script
3. Run the embedding generation script:
```bash
python generate_pdf_embeddings.py
```

This will:
- Extract text from the PDF
- Split the text into chunks
- Generate embeddings
- Store them in Pinecone

## Running the Application

1. Start the application:
```bash
python main.py
```

2. Example usage:
```python
prompt = "what is the personal income tax rate for Cameroon?"
response = main(prompt)
print(response)
```

## Project Structure

```
├── config/
│   └── settings.py         # Configuration settings
├── services/
│   ├── embedding_service.py    # OpenAI embeddings
│   ├── vectorstore_service.py  # Pinecone vector store
│   └── query_service.py        # Query processing
├── utils/
│   ├── error_management.py     # Error handling
│   └── preprocessing.py        # Query preprocessing
├── .env                    # Environment variables
├── mainbot.py                # Chatbot Holder
├── app.py                # Main Appplication entering point
└── requirements.txt       # Dependencies
```

## Error Handling

The application includes comprehensive error handling for:
- API connection issues
- Rate limiting
- Authentication errors
- Invalid inputs
- Server errors

Common errors will return user-friendly messages while logging detailed information for debugging.

## Configuration

Key settings can be modified in `config/settings.py`:
- Model selection
- Temperature
- Number of matching documents
- Retry settings
- Timeouts

## Troubleshooting

1. **Connection Issues**
   - Check your internet connection
   - Verify API keys are correct
   - Ensure Pinecone index exists

2. **Rate Limiting**
   - Reduce concurrent requests
   - Check API usage limits
   - Implement backoff strategy

3. **Memory Issues**
   - Reduce chunk size in text splitting
   - Decrease number of concurrent operations
   - Monitor memory usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Contact

[Add your contact information here]