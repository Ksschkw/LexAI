# LexAI - Legal AI Assistant

## Overview
LEXAI (Legal AI Assistant) is a groundbreaking AI-powered LegalTech chatbot designed to provide accessible legal information based on the **Constitution of the Federal Republic of Nigeria 1999** (updated with First, Second, Third (2010), and Fourth (2017) Alterations). LEXAI aims to empower the 70% of Nigerians without legal access by offering a free, intuitive, and scalable solution. This project leverages open-source tools, a robust RAG (Retrieval-Augmented Generation) architecture, and a session-based chat history to deliver reasoned legal insights.

## Features
- **Legal Query Answering**: Retrieves and generates responses from the Nigerian Constitution with sub-second latency.
- **Reasoned Responses**: Every reply includes explicit reasoning, citing specific Constitution sections (e.g., "Found in Chapter IV, Section 33").
- **Session Persistence**: Stores chat history per session using a lightweight SQLite database for continuity.
- **Scalable Design**: Built with modularity for future enhancements (e.g., AWS migration, multimodal support).
- **Interactive Testing**: Includes a local interactive loop for rapid development and debugging.
- **Free Deployment**: Utilizes Northflank’s free tier for hosting, ensuring zero-cost operation.

## Tech Stack
- **Backend**: Python 3.9, FastAPI (for API), SwarmaURI (for RAG)
- **Language Model**: Groq API (llama3-8b-8192 model)
- **Vector Store**: TF-IDF (via SwarmaURI)
- **Database**: SQLite for chat history
- **Deployment**: Docker on Northflank
- **Preprocessing**: PyPDF for PDF text extraction
- **Logging**: Built-in Python logging for monitoring

## Setup
### Prerequisites
- Python 3.9+
- Docker (for deployment)
- Git (for cloning the repository)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ksschkw/lexai.git
   cd lexai
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Create a `.env` file in the root directory:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - Ensure no extra spaces or quotes around the API key.

4. **Prepare Data**:
   - Download the **Constitution of the Federal Republic of Nigeria 1999** PDF (274 pages, 3.88MB) and place it in the root directory as `Constitution-of-the-Federal-Republic-of-Nigeria.pdf`.
   - Update `config/settings.py` with the correct `CONSTITUTION_PATH` if renamed (default is the above filename).

5. **Initialize the Database**:
   - The chat history database (`lexai_chat_history.db`) will be created automatically on first run.

## Usage
### Local Testing
- Run the interactive loop:
  ```bash
  python main.py
  ```
- Type legal queries (e.g., "What are my rights?") and exit with "exit".
- Example output:
  ```
  Welcome to LEXAI! Type 'exit' to quit.
  Enter your legal query: What are my rights?
  Query: What are my rights?
  LEXAI Response: You have the right to life... [response]

  **Reasoning**: I found this in chunk 5 of the Constitution: 'Chapter IV, Section 33...'.
  ```

### API Usage
- Start the server:
  ```bash
  python main.py --server
  ```
- Send a POST request:
  ```bash
  curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "What are my rights?", "session_id": "test"}'
  ```
- Expected response:
  ```json
  {
    "query": "What are my rights?",
    "response": "You have the right to life... [response]\n\n**Reasoning**: I found this in chunk 5 of the Constitution: 'Chapter IV, Section 33...'"
  }
  ```

### Deployment to Northflank
1. Build the Docker image:
   ```bash
   docker build -t lexai .
   ```
2. Push to a container registry (e.g., Docker Hub) or use Northflank’s CLI.
3. Create a Northflank service:
   - Set `PORT=8000` in environment variables.
   - Deploy the image and obtain the URL (e.g., `http://lexai.northflank.app`).
4. Test the deployed API:
   ```bash
   curl -X POST "http://lexai.northflank.app/query" -H "Content-Type: application/json" -d '{"query": "What are my rights?", "session_id": "test"}'
   ```

## Roadmap
- **Pre-Hackathon (June 18 - July 20, 2025)**:
  - Extract and chunk the Constitution (50 chunks by June 22).
  - Deploy a minimal prototype to Northflank by July 15.
  - Submit hackathon application with solution link by July 20.
- **Hackathon (July 21 - July 29, 2025)**:
  - Process all 274 pages (200 chunks for performance).
  - Enhance with mock multimodal (PDF upload) and multiagent (translation) features in pitch.
  - Finalize demo and pitch slides by July 29.
- **Post-Hackathon (August 2025+)**:
  - Migrate to AWS with ₦500,000+ credits.
  - Implement full multimodal (voice input) and multiagent (translation, logging) features.
  - Explore freemium monetization.

## Architecture
- **Model-View-Controller (MVC)** Pattern:
  - **Model**: `model/` handles data (PDF preprocessing), vector store (TF-IDF), LLM (Groq), RAG, and database.
  - **View**: `view/api/endpoints.py` defines FastAPI routes.
  - **Controller**: `controller/query_handler.py` manages sessions and queries.
- **Modularity**: Each component is standalone, adhering to SOLID principles.

## Impact
- **Market**: Targets the $35B global LegalTech market, with a focus on Nigeria’s underserved population.
- **Innovation**: First free AI legal assistant for Nigeria, pushing boundaries with reasoned responses.

## Future Enhancements
- **Multimodal**: Support PDF uploads and voice queries (e.g., using Tesseract, speechrecognition).
- **Multiagent**: Add translation (e.g., English to Yoruba) and logging agents with LangGraph.
- **Scalability**: Migrate to AWS ECS for handling increased load.

## Author
Okafor Kosisochukwu Johnpaul (Kosi/Ksschkw)  
- [GitHub](https://github.com/Ksschkw)  
- [Portfolio](https://kosisochukwu.onrender.com)  
- WhatsApp: +2349019549473 *(for collaboration)*

## License
MIT License - Free for all, encouraging open-source contribution.

## Acknowledgements
- Inspired by MYRAGAGENT and the Startup Abuja Innovation Challenge.
- Built with love for Nigeria’s tech ecosystem!