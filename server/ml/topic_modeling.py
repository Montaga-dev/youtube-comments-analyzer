import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

class TopicModeling:
    def __init__(self, n_topics=5, max_features=1000):
        self.n_topics = n_topics
        self.max_features = max_features
        
        # Initialize vectorizer for LDA (uses count vectorizer)
        self.vectorizer = CountVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        # Initialize LDA model
        self.lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10,
            learning_method='online',
            learning_offset=50.0
        )
        
    def preprocess_text(self, text):
        """Clean and preprocess text for topic modeling"""
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace and convert to lowercase
        text = ' '.join(text.split()).lower()
        return text
    
    def fit_transform(self, comments):
        """Fit the topic model and return topic assignments"""
        # Preprocess comments
        processed_comments = [self.preprocess_text(comment) for comment in comments]
        
        # Remove empty comments
        processed_comments = [comment for comment in processed_comments if comment.strip()]
        
        if len(processed_comments) < self.n_topics:
            # If we have fewer comments than topics, adjust n_topics
            self.n_topics = max(2, len(processed_comments) // 2)
            self.lda_model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=10,
                learning_method='online',
                learning_offset=50.0
            )
        
        # Vectorize text
        self.doc_term_matrix = self.vectorizer.fit_transform(processed_comments)
        
        # Fit LDA model
        self.lda_model.fit(self.doc_term_matrix)
        
        # Get topic assignments for each document
        doc_topic_probs = self.lda_model.transform(self.doc_term_matrix)
        topic_assignments = np.argmax(doc_topic_probs, axis=1)
        
        # Store results
        self.processed_comments = processed_comments
        self.topic_assignments = topic_assignments
        self.doc_topic_probs = doc_topic_probs
        
        return topic_assignments
    
    def get_topic_words(self, top_n=10):
        """Get top words for each topic"""
        feature_names = self.vectorizer.get_feature_names_out()
        topic_words = {}
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            # Get top words for this topic
            top_words_idx = topic.argsort()[-top_n:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topic_words[f'Topic {topic_idx + 1}'] = top_words
            
        return topic_words
    
    def get_topic_summary(self):
        """Get summary statistics for each topic"""
        topic_summary = {}
        
        for i in range(self.n_topics):
            topic_comments = [comment for j, comment in enumerate(self.processed_comments) 
                            if self.topic_assignments[j] == i]
            
            # Calculate average probability for this topic
            topic_probs = [self.doc_topic_probs[j, i] for j in range(len(self.processed_comments)) 
                          if self.topic_assignments[j] == i]
            avg_prob = np.mean(topic_probs) if topic_probs else 0
            
            topic_summary[f'Topic {i + 1}'] = {
                'size': len(topic_comments),
                'percentage': len(topic_comments) / len(self.processed_comments) * 100,
                'avg_probability': avg_prob,
                'sample_comments': topic_comments[:3]  # First 3 comments as samples
            }
            
        return topic_summary
    
    def visualize_topic_distribution(self):
        """Create visualization of topic distribution"""
        topic_counts = Counter(self.topic_assignments)
        topics = [f'Topic {i+1}' for i in range(self.n_topics)]
        counts = [topic_counts.get(i, 0) for i in range(self.n_topics)]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(topics, counts, color=plt.cm.Set3(np.linspace(0, 1, self.n_topics)))
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        plt.title('Topic Distribution in Comments', fontsize=16, fontweight='bold')
        plt.xlabel('Topics', fontsize=12)
        plt.ylabel('Number of Comments', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        return plt
    
    def generate_topic_wordclouds(self):
        """Generate word clouds for each topic"""
        wordclouds = {}
        
        for i in range(self.n_topics):
            topic_comments = [comment for j, comment in enumerate(self.processed_comments) 
                            if self.topic_assignments[j] == i]
            
            if topic_comments:
                topic_text = ' '.join(topic_comments)
                
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='plasma',
                    max_words=50
                ).generate(topic_text)
                
                wordclouds[f'Topic {i + 1}'] = wordcloud
        
        return wordclouds
    
    def get_topic_coherence_scores(self):
        """Calculate topic coherence scores (simplified version)"""
        coherence_scores = {}
        feature_names = self.vectorizer.get_feature_names_out()
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            # Get top 10 words for coherence calculation
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            
            # Simple coherence measure: average pairwise similarity
            # This is a simplified version - in practice, you'd use more sophisticated measures
            coherence_score = np.mean(topic[top_words_idx])
            coherence_scores[f'Topic {topic_idx + 1}'] = coherence_score
            
        return coherence_scores
    
    def get_topic_analysis(self, comments):
        """Complete topic modeling analysis pipeline"""
        # Perform topic modeling
        topic_assignments = self.fit_transform(comments)
        
        # Get analysis results
        results = {
            'topic_assignments': topic_assignments.tolist(),
            'n_topics': self.n_topics,
            'topic_words': self.get_topic_words(),
            'topic_summary': self.get_topic_summary(),
            'coherence_scores': self.get_topic_coherence_scores(),
            'total_comments': len(self.processed_comments)
        }
        
        return results
    
    def get_document_topics(self, top_n=3):
        """Get top topics for each document with probabilities"""
        doc_topics = []
        
        for doc_idx, doc_probs in enumerate(self.doc_topic_probs):
            # Get top topics for this document
            top_topics_idx = doc_probs.argsort()[-top_n:][::-1]
            doc_topic_info = []
            
            for topic_idx in top_topics_idx:
                doc_topic_info.append({
                    'topic': f'Topic {topic_idx + 1}',
                    'probability': doc_probs[topic_idx]
                })
            
            doc_topics.append({
                'document_id': doc_idx,
                'comment': self.processed_comments[doc_idx][:100] + '...' if len(self.processed_comments[doc_idx]) > 100 else self.processed_comments[doc_idx],
                'top_topics': doc_topic_info
            })
        
        return doc_topics 