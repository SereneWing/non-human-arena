"""Mental activity and emotional models for roles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MentalConfig:
    """Mental activity configuration."""
    
    enable_mental_activity: bool = True
    skip_probability: float = 0.1
    mental_activity_visibility: float = 0.3
    max_activities: int = 50
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enable_mental_activity": self.enable_mental_activity,
            "skip_probability": self.skip_probability,
            "mental_activity_visibility": self.mental_activity_visibility,
            "max_activities": self.max_activities,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MentalConfig:
        """Create from dictionary."""
        if data is None:
            return cls()
        return cls(
            enable_mental_activity=data.get("enable_mental_activity", True),
            skip_probability=data.get("skip_probability", 0.1),
            mental_activity_visibility=data.get("mental_activity_visibility", 0.3),
            max_activities=data.get("max_activities", 50),
        )


@dataclass
class EmotionalModel:
    """Emotional model for AI character."""
    
    dimensions: List[str] = field(
        default_factory=lambda: ["valence", "arousal", "dominance"]
    )
    initial_emotion: str = "neutral"
    max_intensity: float = 1.0
    decay_rate: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimensions": self.dimensions,
            "initial_emotion": self.initial_emotion,
            "max_intensity": self.max_intensity,
            "decay_rate": self.decay_rate,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmotionalModel:
        """Create from dictionary."""
        if data is None:
            return cls()
        return cls(
            dimensions=data.get("dimensions", ["valence", "arousal", "dominance"]),
            initial_emotion=data.get("initial_emotion", "neutral"),
            max_intensity=data.get("max_intensity", 1.0),
            decay_rate=data.get("decay_rate", 0.1),
        )


@dataclass
class SpeakingStyle:
    """Speaking style configuration."""
    
    formality: float = 0.5
    length_preference: str = "medium"
    tone: str = "neutral"
    vocabulary_level: str = "normal"
    use_emoji: bool = False
    interruptions: bool = False
    pause_frequency: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "formality": self.formality,
            "length_preference": self.length_preference,
            "tone": self.tone,
            "vocabulary_level": self.vocabulary_level,
            "use_emoji": self.use_emoji,
            "interruptions": self.interruptions,
            "pause_frequency": self.pause_frequency,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpeakingStyle:
        """Create from dictionary."""
        if data is None:
            return cls()
        return cls(
            formality=data.get("formality", 0.5),
            length_preference=data.get("length_preference", "medium"),
            tone=data.get("tone", "neutral"),
            vocabulary_level=data.get("vocabulary_level", "normal"),
            use_emoji=data.get("use_emoji", False),
            interruptions=data.get("interruptions", False),
            pause_frequency=data.get("pause_frequency", 0.0),
        )
