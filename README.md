# AI-Driven Systematic Reviews in the Brain-Heart Interconnectome

**Live System**:
[Live BHI Chatbot](http://ec2-52-60-155-21.ca-central-1.compute.amazonaws.com/)

This repository contains the official implementation of the AI-driven system described in the paper:

**An AI-Driven Live Systematic Reviews in the Brain-Heart Interconnectome: Minimizing Research Waste and Advancing Evidence Synthesis**

*Authors: Arya Rahgozar, Pouria Mortezaagha, Jodi Edwards, Douglas Manuel, Jessie McGowen, Merrick Zwarenstein, Dean Fergusson, Andrea Tricco, Kelly Cobey, Margaret Sampson, Malcolm King, Dawn Richards, Alexandra Bodnaruc, David Moher*

*Affiliation: Ottawa Hospital Research Institute, Ottawa, Ontario, Canada*

*Published: January 25, 2025*

**Abstract:**
The rapidly evolving field of the Brain-Heart Interconnectome (BHI) merges neurology and cardiology. Despite its potential, inefficiencies in evidence synthesis and suboptimal adherence to quality standards often result in research waste. To address these challenges, we developed an AI-driven system designed to streamline systematic reviews in the BHI domain.

**Access the full paper:** [arXiv:2501.17181](https://arxiv.org/abs/2501.17181)

## Overview

This AI-driven system aims to enhance the efficiency and quality of systematic reviews in the BHI field by:

- **Automating PICOS Detection:** Utilizing a Bi-directional Long Short-Term Memory (Bi-LSTM) model to assess compliance with Population, Intervention, Comparator, Outcome, and Study design (PICOS) criteria.

- **Enhancing Semantic Search:** Implementing Retrieval-Augmented Generation (RAG) combined with large language models (LLMs) for improved semantic retrieval.

- **Graph-Based Querying:** Storing graph-structured data using Neo4j to capture complex interactions among interventions, outcomes, and study designs.

- **Topic Modeling for Redundancy Assessment:** Applying BERTopic for thematic clustering to identify research redundancies and highlight underexplored topics.

- **Maintaining a Continuously Updated Database:** Providing real-time updates to support dynamic evidence synthesis.

## System Components

1. **PICOS Compliance Detection:**
   - *Model:* Bi-LSTM
   - *Accuracy:* 87% in distinguishing PICOS-compliant articles.

2. **Semantic Retrieval:**
   - *Models:* RAG combined with GPT-3.5 and GPT-4
   - *Performance:* RAG with GPT-3.5 outperformed GPT-4 for specialized BHI queries requiring graph-based and topic-driven insights.

3. **Study Design Classification:**
   - *Accuracy:* 95.7% overall in classifying study designs.

4. **Graph-Based Data Storage:**
   - *Database:* Neo4j
   - *Purpose:* Capturing interactions among interventions, outcomes, and study designs.

5. **Topic Modeling:**
   - *Tool:* BERTopic
   - *Purpose:* Thematic clustering for redundancy assessment and identification of underexplored topics.

## Installation

To set up the environment, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/bhi-systematic-review.git
   cd bhi-systematic-review
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Neo4j database:**
   - Download and install Neo4j from the [official website](https://neo4j.com/download/).
   - Start the Neo4j server and set up your database credentials.
   - Update the database connection settings in `config.py`.

## Usage

### Chatbot

Refer to the `UI_test` folder.

### PICO LSTM Model

This notebook focuses on training and evaluating a Bi-directional LSTM (Bi-LSTM) model for detecting PICOS compliance in research papers.

#### Steps to Use:

1. **Data Preparation:**
   - Prepare a dataset containing labeled abstracts or research paper texts.
   - Ensure that the labels reflect compliance with each element of the PICOS criteria.

2. **Model Training:**
   - The notebook performs the following:
     - **Data Tokenization:** Preprocesses and tokenizes text for LSTM input.
     - **Model Building:** Constructs a Bi-LSTM model using TensorFlow/Keras.
     - **Training:** Trains the model on the labeled dataset.
     - **Validation:** Validates the model and reports accuracy and loss metrics.

3. **Model Evaluation:**
   - Evaluate the model's performance on a validation set.
   - Outputs include classification reports, confusion matrices, and accuracy scores.

4. **Saving and Loading Model:**
   - Save the trained model for future use.
   - Load the model using the provided functions for predictions on new data.

#### Example Code Snippet:
```python
# Import required libraries
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Bidirectional

# Build the Bi-LSTM model
model = Sequential([
    Embedding(input_dim=5000, output_dim=128),
    Bidirectional(LSTM(64)),
    Dense(1, activation='sigmoid')
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val))
```

5. **Generating Predictions:**
   - Use the trained model to predict the compliance of new research papers.

---

## Results

The system has demonstrated the following performance:

- **PICOS Compliance Detection:** 87% accuracy
- **Study Design Classification:** 95.7% accuracy
- **Semantic Retrieval:** RAG with GPT-3.5 outperformed GPT-4 in specialized BHI queries.

These results indicate the system's effectiveness in reducing research waste by detecting redundancies and highlighting underexplored topics.

## Contributing

We welcome contributions from the community. To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m 'Add new feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Create a new Pull Request.

## License

This project is licensed under the Apache-2.0 license. See the `LICENSE` file for details.

## Acknowledgments

We thank the Ottawa Hospital Research Institute and all collaborators for their support and contributions to this project.

---

*For more details, please refer to the full paper: [arXiv:2501.17181](https://arxiv.org/abs/2501.17181)*
