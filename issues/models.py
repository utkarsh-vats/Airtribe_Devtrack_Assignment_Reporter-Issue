from django.db import models
from datetime import datetime
from abc import ABC, abstractmethod

class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
        }

class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.email:
            raise ValueError("Email cannot be empty")
        if '@' not in self.email:
            raise ValueError("Invalid email format")


class Issue(BaseEntity):
    STATUS_CHOICES = ['open', 'in progress', 'resolved', 'closed']
    PRIORITY_CHOICES = ['low', 'medium', 'high', 'critical']

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = created_at or str(datetime.now())

    def validate(self):
        if not self.reporter_id:
            raise ValueError("Reporter ID cannot be empty")
        if self.status not in self.STATUS_CHOICES:
            raise ValueError(f"Invalid status\n Status must be one of: {", ".join(self.STATUS_CHOICES)}")
        if self.priority not in self.PRIORITY_CHOICES:
            raise ValueError(f"Invalid priority\n Priority must be one of: {", ".join(self.PRIORITY_CHOICES)}")

    def describe(self):
        return f"{self.title} - [{self.priority}]"
    
class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} - needs immediate attention"
    
class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} - low priority, handle when free"