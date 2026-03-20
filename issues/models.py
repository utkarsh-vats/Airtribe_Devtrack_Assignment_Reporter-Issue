from django.db import models
from abc import ABC, abstractmethod

class Issue(ABC):
    def __init__(self, id, title, description, status, priority, reporter_id):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id

    def validate(self):
        if not self.reporter_id:
            raise ValueError("Reporter ID cannot be empty")

    @abstractmethod
    def describe(self):
        return f"{self.title} - [{self.priority}]"
    
class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} - needs immediate attention"
    
class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} - low priority, handle when free"