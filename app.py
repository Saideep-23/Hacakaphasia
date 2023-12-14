from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)

# Replace 'path_to_your_excel_file.xlsx' with the actual path to your Excel file
excel_file_path = r'C:\Users\SDK\Desktop\super\data.xlsx' #file path to the excel absolute address
df = pd.read_excel(excel_file_path)

# Extract abstracts from the DataFrame
documents = df['Abstract'].tolist()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Results route
@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        user_input = request.form['user_input']

        # Optionally, you can check if the user wants to end the conversation
        if user_input.lower() == 'end':
            return jsonify({'bot_response': 'Goodbye!', 'continue_conversation': False})

        documents.append(user_input)

        # TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Calculate cosine similarity between the user input and dataset sentences
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

        # Sort the sentences based on similarity and get the indices
        related_indices = cosine_similarities.argsort()[:-6:-1]

        # Check if there is a match
        if cosine_similarities.size > 0 and cosine_similarities[related_indices[0]] > 0.0:
            # Extract the top 5 related sentences
            top_related_sentences = [documents[index] for index in related_indices if index < len(documents)]

            # Join the sentences to form a summary
            summary = ". ".join(top_related_sentences) + "."

            # Use Sumy for extractive summarization
            parser = PlaintextParser.from_string(summary, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary_sentences = summarizer(parser.document, 3)  # Adjust the number of sentences in the summary as needed

            # Display the enhanced summary
            enhanced_summary = " ".join(str(sentence) for sentence in summary_sentences)

            # Display the information in a table format
            publication_info = []
            for index in related_indices:
                if 0 <= index < len(df):
                    publication_info.append({
                        'Publication Year': int(df.iloc[index]['Publication Year']),
                        'Publication Link': df.iloc[index]['URL']
                    })

            # Optionally, you can check if the conversation should continue
            continue_conversation = True  # Adjust this condition as needed

            # Respond with the bot's message and whether the conversation should continue
            bot_response = "This is a sample bot response."
            return jsonify({'bot_response': bot_response,
                            'enhanced_summary': enhanced_summary,
                            'publication_info': publication_info,
                            'continue_conversation': continue_conversation})
        else:
            # Respond with a message indicating no match
            return jsonify({'bot_response': 'No matching sentence found.', 'continue_conversation': True})

if __name__ == '__main__':
    app.run(debug=True)
