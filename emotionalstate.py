"""
1. Create a data structure that represents the emotional state of an entity across multiple emotional domains.
2. Values should be between -1.0 and 1.0.
3. The output of the model should be useable as a json format string for a GPT3 prompt to flavor or influence the emotional sentiment of the model's response.
"""

from enum import Enum
from typing import Tuple
import json
import numpy as np


def normalize(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        return EmotionalState(
            (result.emotions[EmotionalDomain.JOY] + 1) / 2,
            (result.emotions[EmotionalDomain.FEAR] + 1) / 2,
            (result.emotions[EmotionalDomain.DISGUST] + 1) / 2,
            (result.emotions[EmotionalDomain.SADNESS] + 1) / 2,
            (result.emotions[EmotionalDomain.ANGER] + 1) / 2,
            (result.emotions[EmotionalDomain.SURPRISE] + 1) / 2
        )

    return inner


class EmotionalDomain(Enum):
    """Emotional domain"""

    JOY = 1
    FEAR = 2
    DISGUST = 3
    SADNESS = 4
    ANGER = 5
    SURPRISE = 6


class EmotionalState:
    """Emotional state"""

    def __init__(self, joy: float, fear: float, disgust: float, sadness: float, anger: float, surprise: float):
        """Initialize emotional state"""

        self._emotions = {EmotionalDomain.JOY: joy, EmotionalDomain.FEAR: fear, EmotionalDomain.DISGUST: disgust,
                          EmotionalDomain.SADNESS: sadness, EmotionalDomain.ANGER: anger, EmotionalDomain.SURPRISE: surprise}

    def decay(self, decay_rate=0.25):
        """Decay emotional state"""
        return EmotionalState(round(self.emotions[EmotionalDomain.JOY] * decay_rate, 2),
                              round(self.emotions[EmotionalDomain.FEAR] *
                                    decay_rate, 2),
                              round(self.emotions[EmotionalDomain.DISGUST] *
                                    decay_rate, 2),
                              round(self.emotions[EmotionalDomain.SADNESS] *
                                    decay_rate, 2),
                              round(self.emotions[EmotionalDomain.ANGER] *
                                    decay_rate, 2),
                              round(self.emotions[EmotionalDomain.SURPRISE] * decay_rate, 2))

    @property
    def emotions(self) -> dict:
        """Get emotions"""

        return self._emotions

    @emotions.setter
    def emotions(self, joy: float, fear: float, disgust: float, sadness: float, anger: float, surprise: float):
        """Set emotions"""

        self._emotions = {EmotionalDomain.JOY: joy, EmotionalDomain.FEAR: fear, Emotional
                          .DISGUST: disgust, EmotionalDomain.SADNESS: sadness, EmotionalDomain.ANGER: anger,
                          EmotionalDomain.SURPRISE: surprise}

    def __str__(self):
        """String representation"""

        return f'Joy: {self._emotions[EmotionalDomain.JOY]} - Fear: {self._emotions[EmotionalDomain.FEAR]} - ' \
               f'Disgust: {self._emotions[EmotionalDomain.DISGUST]} - Sadness: {self._emotions[EmotionalDomain.SADNESS]} - ' \
               f'Anger: {self._emotions[EmotionalDomain.ANGER]} - Surprise: {self._emotions[EmotionalDomain.SURPRISE]}'

    def __repr__(self):
        """Representation"""

        return f'Joy: {self._emotions[EmotionalDomain.JOY]}, Fear: {self._emotions[EmotionalDomain.FEAR]}, ' \
               f'Disgust: {self._emotions[EmotionalDomain.DISGUST]}, Sadness: {self._emotions[EmotionalDomain.SADNESS]}, ' \
               f'Anger: {self._emotions[EmotionalDomain.ANGER]}, Surprise: {self._emotions[EmotionalDomain.SURPRISE]}'

    @normalize
    def __add__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Add two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(
            self.emotions[EmotionalDomain.JOY] +
            other.emotions[EmotionalDomain.JOY],
            self.emotions[EmotionalDomain.FEAR] +
            other.emotions[EmotionalDomain.FEAR],
            self.emotions[EmotionalDomain.DISGUST] +
            other.emotions[EmotionalDomain.DISGUST],
            self.emotions[EmotionalDomain.SADNESS] +
            other.emotions[EmotionalDomain.SADNESS],
            self.emotions[EmotionalDomain.ANGER] +
            other.emotions[EmotionalDomain.ANGER],
            self.emotions[EmotionalDomain.SURPRISE] +
            other.emotions[EmotionalDomain.SURPRISE]
        )

    @normalize
    def __sub__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Subtract two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(self.emotions[EmotionalDomain.JOY] - other.emotions[EmotionalDomain.JOY],
                              self.emotions[EmotionalDomain.FEAR] -
                              other.emotions[EmotionalDomain.FEAR],
                              self.emotions[EmotionalDomain.DISGUST] -
                              other.emotions[EmotionalDomain.DISGUST],
                              self.emotions[EmotionalDomain.SADNESS] -
                              other.emotions[EmotionalDomain.SADNESS],
                              self.emotions[EmotionalDomain.ANGER] -
                              other.emotions[EmotionalDomain.ANGER],
                              self.emotions[EmotionalDomain.SURPRISE] - other.emotions[EmotionalDomain.SURPRISE])

    @normalize
    def __mul__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Multiply two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(self.emotions[EmotionalDomain.JOY] * other.emotions[EmotionalDomain.JOY],

                              self.emotions[EmotionalDomain.FEAR] *
                              other.emotions[EmotionalDomain.FEAR],
                              self.emotions[EmotionalDomain.DISGUST] *
                              other.emotions[EmotionalDomain.DISGUST],
                              self.emotions[EmotionalDomain.SADNESS] *
                              other.emotions[EmotionalDomain.SADNESS],
                              self.emotions[EmotionalDomain.ANGER] *
                              other.emotions[EmotionalDomain.ANGER],
                              self.emotions[EmotionalDomain.SURPRISE] * other.emotions[EmotionalDomain.SURPRISE])

    @normalize
    def __rmul__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Reverse multiply two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(self.emotions[EmotionalDomain.JOY] * other.emotions[EmotionalDomain.JOY],
                              self.emotions[EmotionalDomain.FEAR] *
                              other.emotions[EmotionalDomain.FEAR],
                              self.emotions[EmotionalDomain.DISGUST] * other.emotions[EmotionalDomain.DISGUST
                                                                                      ],
                              self.emotions[EmotionalDomain.SADNESS] *
                              other.emotions[EmotionalDomain.SADNESS],
                              self.emotions[EmotionalDomain.ANGER] *
                              other.emotions[EmotionalDomain.ANGER],
                              self.emotions[EmotionalDomain.SURPRISE] * other.emotions[EmotionalDomain.SURPRISE])

    @normalize
    def __truediv__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Divide two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(self.emotions[EmotionalDomain.JOY] / other.emotions[EmotionalDomain.JOY],
                              self.emotions[EmotionalDomain.FEAR] /
                              other.emotions[EmotionalDomain.FEAR],
                              self.emotions[EmotionalDomain.DISGUST] /
                              other.emotions[EmotionalDomain.DISGUST],
                              self.emotions[EmotionalDomain.SADNESS] /
                              other.emotions[EmotionalDomain.SADNESS],
                              self.emotions[EmotionalDomain.ANGER] /
                              other.emotions[EmotionalDomain.ANGER],
                              self.emotions[EmotionalDomain.SURPRISE] / other.emotions[EmotionalDomain.SURPRISE])

    @normalize
    def __rtruediv__(self, other: 'EmotionalState') -> 'EmotionalState':
        """Reverse divide two emotional states"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return EmotionalState(other.emotions[EmotionalDomain.JOY] / self.emotions[EmotionalDomain.JOY],
                              other.emotions[EmotionalDomain.FEAR] /
                              self.emotions[EmotionalDomain.FEAR],
                              other.emotions[EmotionalDomain.DISGUST] /
                              self.emotions[EmotionalDomain.DISGUST],
                              other.emotions[EmotionalDomain.SADNESS] /
                              self.emotions[EmotionalDomain.SADNESS],
                              other.emotions[EmotionalDomain.ANGER] /
                              self.emotions[EmotionalDomain.ANGER],
                              other.emotions[EmotionalDomain.SURPRISE] / self.emotions[EmotionalDomain.SURPRISE])

    def __eq__(self, other: 'EmotionalState') -> bool:
        """Check for equality"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return np.allclose(self.emotions[EmotionalDomain.JOY], other.emotions[EmotionalDomain.JOY]) and \
            np.allclose(self.emotions[EmotionalDomain.FEAR], other.emotions[EmotionalDomain.FEAR]) and \
            np.allclose(self.emotions[EmotionalDomain.DISGUST], other.emotions[EmotionalDomain.DISGUST]) and \
            np.allclose(self.emotions[EmotionalDomain.SADNESS], other.emotions[EmotionalDomain.SADNESS]) and \
            np.allclose(self.emotions[EmotionalDomain.ANGER], other.emotions[EmotionalDomain.ANGER]) and \
            np.allclose(self.emotions[EmotionalDomain.SURPRISE],
                        other.emotions[EmotionalDomain.SURPRISE])

    def __gt__(self, other: 'EmotionalState') -> bool:
        """Check if greater than"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return self.emotions[EmotionalDomain.JOY] > other.emotions[EmotionalDomain.JOY] and \
            self.emotions[EmotionalDomain.FEAR] > other.emotions[EmotionalDomain.FEAR] and \
            self.emotions[EmotionalDomain.DISGUST] > other.emotions[EmotionalDomain.DISGUST] and \
            self.emotions[EmotionalDomain.SADNESS] > other.emotions[EmotionalDomain.SADNESS] and \
            self.emotions[EmotionalDomain.ANGER] > other.emotions[EmotionalDomain.ANGER] and \
            self.emotions[EmotionalDomain.SURPRISE] > other.emotions[EmotionalDomain.SURPRISE]

    def __ge__(self, other: 'EmotionalState') -> bool:
        """Check if greater than or equal to"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return self.emotions[EmotionalDomain.JOY] >= other.emotions[EmotionalDomain.JOY] and \
            self.emotions[EmotionalDomain.FEAR] >= other.emotions[EmotionalDomain.FEAR] and \
            self.emotions[EmotionalDomain.DISGUST] >= other.emotions[EmotionalDomain.DISGUST] and \
            self.emotions[EmotionalDomain.SADNESS] >= other.emotions[EmotionalDomain.SADNESS] and \
            self.emotions[EmotionalDomain.ANGER] >= other.emotions[EmotionalDomain.ANGER] and \
            self.emotions[EmotionalDomain.SURPRISE] >= other.emotions[EmotionalDomain.SURPRISE]

    def __lt__(self, other: 'EmotionalState') -> bool:
        """Check if less than"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return self.emotions[EmotionalDomain.JOY] < other.emotions[EmotionalDomain.JOY] and \
            self.emotions[EmotionalDomain.FEAR] < other.emotions[EmotionalDomain.FEAR] and \
            self.emotions[EmotionalDomain.DISGUST] < other.emotions[EmotionalDomain.DISGUST] and \
            self.emotions[EmotionalDomain.SADNESS] < other.emotions[EmotionalDomain.SADNESS] and \
            self.emotions[EmotionalDomain.ANGER] < other.emotions[EmotionalDomain.ANGER] and \
            self.emotions[EmotionalDomain.SURPRISE] < other.emotions[EmotionalDomain.SURPRISE]

    def __le__(self, other: 'EmotionalState') -> bool:
        """Check if less than or equal to"""

        if not isinstance(other, EmotionalState):
            raise ValueError('The other value must be of type EmotionalState.')

        return self.emotions[EmotionalDomain.JOY] <= other.emotions[EmotionalDomain.JOY] and \
            self.emotions[EmotionalDomain.FEAR] <= other.emotions[EmotionalDomain.FEAR] and \
            self.emotions[EmotionalDomain.DISGUST] <= other.emotions[EmotionalDomain.DISGUST] and \
            self.emotions[EmotionalDomain.SADNESS] <= other.emotions[EmotionalDomain.SADNESS] and \
            self.emotions[EmotionalDomain.ANGER] <= other.emotions[EmotionalDomain.ANGER] and \
            self.emotions[EmotionalDomain.SURPRISE] <= other.emotions[EmotionalDomain.SURPRISE]

    @staticmethod
    def random() -> 'EmotionalState':
        """Generate a random emotional state"""

        return EmotionalState(np.random.uniform(-1, 1), np.random.uniform(-1, 1), np.random.uniform(-1, 1),
                              np.random.uniform(-1, 1), np.random.uniform(-1, 1), np.random.uniform(-1, 1))

    @staticmethod
    def from_json(jsons: str) -> 'EmotionalState':
        """Initialize from JSON"""
        print(jsons)
        emotions = json.loads(jsons)['emotions']

        return EmotionalState(joy=emotions['joy'], fear=emotions['fear'], disgust=emotions['disgust'],
                              sadness=emotions['sadness'], anger=emotions['anger'], surprise=emotions['surprise'])

    def to_json(self) -> str:
        """Convert to JSON"""

        return f'{{ "joy": {self._emotions[EmotionalDomain.JOY]}, "fear": {self._emotions[EmotionalDomain.FEAR]},' \
               f' "disgust": {self._emotions[EmotionalDomain.DISGUST]}, "sadness": {self._emotions[EmotionalDomain.SADNESS]},' \
               f' "anger": {self._emotions[EmotionalDomain.ANGER]}, "surprise": {self._emotions[EmotionalDomain.SURPRISE]} }}'

    @staticmethod
    def from_tuple(emotions: Tuple[float, float, float, float, float, float]) -> 'EmotionalState':
        """Initialize from a tuple"""

        return EmotionalState(joy=emotions[0], fear=emotions[1], disgust=emotions[2], sadness=emotions[3],
                              anger=emotions[4], surprise=emotions[5])

    def to_tuple(self) -> Tuple[float, float, float, float, float, float]:
        """Convert to a tuple"""

        return self._emotions[EmotionalDomain.JOY], self._emotions[EmotionalDomain.FEAR], \
            self._emotions[EmotionalDomain.DISGUST], self._emotions[EmotionalDomain.SADNESS], \
            self._emotions[EmotionalDomain.ANGER], self._emotions[EmotionalDomain.SURPRISE]


if __name__ == '__main__':
    es1 = EmotionalState(0.5, 0.7, 0.3, -0.5, -0.8, 0.9).random()
    es2 = EmotionalState(0.5, 0.7, 0.3, -0.5, -0.8, 0.9).random()
    es3 = es1 + es2
    es4 = es1 - es2
    es5 = es1 * es2
    es6 = es1 / es2

    print(f'es1: {es1}')
    print(f'es2: {es2}')
    print(f'es3: {es3}')
    print(f'es4: {es4}')
    print(f'es5: {es5}')
    print(f'es6: {es6}')

    json_str = f'{{"emotions": {{"joy": {es1._emotions[EmotionalDomain.JOY]}, "fear": {es1._emotions[EmotionalDomain.FEAR]},' \
               f' "disgust": {es1._emotions[EmotionalDomain.DISGUST]}, "sadness": {es1._emotions[EmotionalDomain.SADNESS]},' \
               f' "anger": {es1._emotions[EmotionalDomain.ANGER]}, "surprise": {es1._emotions[EmotionalDomain.SURPRISE]} }}}}'

    print(json_str)

    es7 = EmotionalState.from_json(json_str)

    print(f'es7: {es7}')

    print(f'JSON string from emotional state: {es7.to_json()}')

    tuple_test = (0.5, 0.7, 0.3, -0.5, -0.8, 0.9)

    print(tuple_test)

    es8 = EmotionalState.from_tuple(tuple_test)

    print(f'es8: {es8}')

    tuple_from_emotional_state = (0.5, 0.7, 0.3, -0.5, -0.8, 0.9)

    print(tuple_from_emotional_state)
