import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re

class TextClustering:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.pca = PCA(n_components=2, random_state=42)
        
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove extra whitespace and convert to lowercase
        text = ' '.join(text.split()).lower()
        return text
    
    def fit_transform(self, comments):
        """Fit the clustering model and return cluster assignments"""
        # Preprocess comments
        processed_comments = [self.preprocess_text(comment) for comment in comments]
        
        # Remove empty comments
        processed_comments = [comment for comment in processed_comments if comment.strip()]
        
        if len(processed_comments) < self.n_clusters:
            # If we have fewer comments than clusters, adjust n_clusters
            self.n_clusters = max(2, len(processed_comments) // 2)
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        
        # Vectorize text
        self.tfidf_matrix = self.vectorizer.fit_transform(processed_comments)
        
        # Perform clustering
        cluster_labels = self.kmeans.fit_predict(self.tfidf_matrix)
        
        # Store results
        self.processed_comments = processed_comments
        self.cluster_labels = cluster_labels
        
        return cluster_labels
    
    def get_cluster_keywords(self, top_n=10):
        """Get top keywords for each cluster"""
        feature_names = self.vectorizer.get_feature_names_out()
        cluster_keywords = {}
        
        for i in range(self.n_clusters):
            # Get cluster center
            cluster_center = self.kmeans.cluster_centers_[i]
            # Get top features for this cluster
            top_indices = cluster_center.argsort()[-top_n:][::-1]
            top_keywords = [feature_names[idx] for idx in top_indices]
            cluster_keywords[f'Cluster {i+1}'] = top_keywords
            
        return cluster_keywords
    
    def get_cluster_summary(self):
        """Get summary statistics for each cluster"""
        cluster_summary = {}
        
        for i in range(self.n_clusters):
            cluster_comments = [comment for j, comment in enumerate(self.processed_comments) 
                             if self.cluster_labels[j] == i]
            
            cluster_summary[f'Cluster {i+1}'] = {
                'size': len(cluster_comments),
                'percentage': len(cluster_comments) / len(self.processed_comments) * 100,
                'sample_comments': cluster_comments[:3]  # First 3 comments as samples
            }
            
        return cluster_summary
    
    def visualize_clusters(self):
        """Create 2D visualization of clusters"""
        # Reduce dimensionality for visualization
        tfidf_2d = self.pca.fit_transform(self.tfidf_matrix.toarray())
        
        # Create DataFrame for plotting
        df = pd.DataFrame({
            'x': tfidf_2d[:, 0],
            'y': tfidf_2d[:, 1],
            'cluster': self.cluster_labels
        })
        
        # Create plot
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, self.n_clusters))
        
        for i in range(self.n_clusters):
            cluster_data = df[df['cluster'] == i]
            plt.scatter(cluster_data['x'], cluster_data['y'], 
                       c=[colors[i]], label=f'Cluster {i+1}', alpha=0.7, s=50)
        
        plt.title('Comment Clusters Visualization (PCA)', fontsize=16, fontweight='bold')
        plt.xlabel('First Principal Component', fontsize=12)
        plt.ylabel('Second Principal Component', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt
    
    def generate_cluster_wordclouds(self):
        """Generate word clouds for each cluster"""
        wordclouds = {}
        
        for i in range(self.n_clusters):
            cluster_comments = [comment for j, comment in enumerate(self.processed_comments) 
                             if self.cluster_labels[j] == i]
            
            if cluster_comments:
                cluster_text = ' '.join(cluster_comments)
                
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis',
                    max_words=50
                ).generate(cluster_text)
                
                wordclouds[f'Cluster {i+1}'] = wordcloud
        
        return wordclouds
    
    def get_cluster_analysis(self, comments):
        """Complete cluster analysis pipeline"""
        # Perform clustering
        cluster_labels = self.fit_transform(comments)
        
        # Get analysis results
        results = {
            'cluster_labels': cluster_labels.tolist(),
            'n_clusters': self.n_clusters,
            'cluster_keywords': self.get_cluster_keywords(),
            'cluster_summary': self.get_cluster_summary(),
            'total_comments': len(self.processed_comments)
        }
        
        return results 