
# BHI-SystematicReview

## Overview
This application utilizes LangChain and OpenAI's API to provide an intelligent chat system. It's built to leverage retrieval-based question answering with the added benefit of contextual document compression, allowing for efficient and relevant responses. This setup helps simulate a more intuitive and interactive conversational experience with users, akin to a knowledgeable assistant.

## Key Features
- **OpenAI Language Models**: Uses advanced machine learning models to generate dynamic responses based on the context of the conversation.
- **Retrieval-Based Question Answering**: Integrates a retrieval system that fetches and filters information from a large corpus to find relevant answers.
- **Contextual Compression**: Employs document compression techniques to condense information into manageable snippets that retain essential information, enhancing the speed and relevance of responses.
- **Conversation Memory**: Implements a memory buffer that tracks the history of the conversation, allowing the system to reference previous exchanges and provide contextually relevant answers.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pouriamrt/BHI_chatbot.git
   cd BHI-SystematicReview
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY='your_openai_api_key_here'
   ```

### Running the Application

Start the chat application by running:
```bash
chainlit run app.py -w
```

Upon starting, the application will greet you and wait for your queries. Type your questions into the console to receive responses.


