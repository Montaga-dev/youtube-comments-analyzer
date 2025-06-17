from typing import List, Dict, Any
from .text_classification import TextClassifier

class MLPipeline:
    def __init__(self):
        self.classifier = TextClassifier()
    
    def analyze_texts(self, texts: List[str], use_transformer: bool = False, model_name: str = None) -> Dict[str, Any]:
        """Analyze texts using only text classification."""
        sentiment_results = self.classifier.predict_batch(texts, use_transformer, model_name)
        combined_results = []
        for i in range(len(texts)):
            combined_results.append({
                "text": texts[i],
                "sentiment": sentiment_results[i]["sentiment"],
                "sentiment_confidence": sentiment_results[i]["confidence"],
                "sentiment_method": sentiment_results[i]["method"]
            })
        return {
            "results": combined_results,
            "summary": {
                "total_texts": len(texts),
                "sentiment_distribution": self._get_sentiment_distribution(sentiment_results)
            }
        }
    
    def _get_sentiment_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        distribution = {"positive": 0, "neutral": 0, "negative": 0}
        for result in results:
            distribution[result["sentiment"]] += 1
        return distribution 