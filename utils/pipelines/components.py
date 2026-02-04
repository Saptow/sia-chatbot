from haystack import component
from typing import List

@component
class ThresholdFilter:
    """
    A component that filters documents based on a similarity score threshold.
    """
    def __init__(self, threshold: float = 0.4):
        self.threshold = threshold
    
    @component.output_types(documents=list)
    def run(self, documents: List):
        filtered_docs = [doc for doc in documents if doc.score >= self.threshold]
        return {"documents": filtered_docs}
    
