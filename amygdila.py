from emotionalstate import EmotionalState
from sentimentparser import get_sentiment_score

test_strings = [
    "I am happy to be here today.",
    "It looks interesting but the smell is so bad.",
    "You suck, you're not very useful.",
    "Why did the chicken cross the road?.",
    "It's really quite shrimple.",
    "The frog is sitting on the log.",
    "I'm not satisfied, you've hurt me.",
    "The dingus over there did it lol",
    "Is that really how you think?", "Relatable as fuck",
    "Well, if you paint your nails, you'll look like a faggot so.",
    "tale as old as time",
    "It's true",
    "girl leave boy",
    "Unless I'm just seeing the wrong thing in that last imagine.",
    "boy stick a 12 gauge in his fucking mouth",
    "Yep",
    "Someday soon 😊",
    "this is why im outside of the entire thing",
    "seen too many of my old bros nearly neck or shoot themselves over women",
    "Be a bro, give them a hand(y).",
    "i spent the better portion of my mid to late teens",
    "trying to make sure one of my old bros who got really fucked by life",
    "doesnt neck himself",
    "The key is to stop caring about your partners",
    "If you don't feel love then you'll be fine",
    "and i succeeded, he didnt neck himself, he grew out of it",
    "and now hes doing better",
    "and i am no longer needed",
    "A handy is a hand job mate. It was a sex joke.",
    "i know it was",
    "but you can abstract hand job to action that helps",
    "and that was my action that helped",
]

es_init = EmotionalState(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
emotional_state_continuum = []
print(es_init)

for text in test_strings:
	state = get_sentiment_score(text)
	if state != None:
		es_frame = EmotionalState(float(state[0]),float(state[1]),float(state[2]),float(state[3]),float(state[4]),float(state[5]))
		emotional_state_continuum.append(es_frame)
		es_init += es_frame
		es_init = es_init.decay()
		print(f"\n\n{text}\n\tFrame-> {es_frame}\n\tState-> {es_init}")





