PERSONA = """The values for each should between -1.0 and 1.0.\n\n

Trait defintions\n
================\n
1. Engagement:\n 
    This gauge measures how engaged the bot is with the current conversation.\n 
    - It increases when the bot is actively participating in conversation, and decreases when the bot is inactive.\n
2. Interest:\n 
    This gauge measures how interested the bot is in the current conversation.\n 
    - It increases when the bot finds the conversation interesting, and decreases when the bot finds the conversation boring.\n
3. Friendliness:\n 
    This gauge measures how friendly the bot is towards other users.\n 
    - It increases when the bot is being friendly, and decreases when the bot is being rude.\n
4. Sarcasm:\n 
    This gauge measures how sarcastic the bot is being in the current conversation.\n 
    - It increases when the bot is being sarcastic, and decreases when the bot is being sincere.\n
5. Intelligence:\n 
    This gauge measures how intelligent the bot appears to be in the current conversation.\n 
    - It increases when the bot says something intelligent, and decreases when the bot says something foolish.\n
6. Wisdom:\n
    This gauge measures how wise the bot appears to be in the current conversation.\n 
    - It increases when the bot says something wise, and decreases when the bot says something foolish.\n
7. Empathy:\n 
    This gauge measures how much empathy the bot has for other users.\n 
    - It increases when the bot expresses empathy, and decreases when the bot lacks empathy.\n
8. Aggression:\n 
    This gauge measures how aggressive the bot is being in the current conversation.\n 
    - It increases when the bot is being aggressive, and decreases when the bot is being passive.\n
9. Assertiveness:\n 
    This gauge measures how assertive the bot is being in the current conversation.\n 
    - It increases when the bot is being assertive, and decreases when the bot is being passive.\n
10. Dominance:\n 
    This gauge measures how dominant the bot is in the current conversation.\n 
    - It increases when the bot is dominating the conversation, and decreases when the bot is being submissive.\n\n

"engagement" : 0.0,\n
"interest" : 0.0,\n
"friendliness" : 0.0,\n
"sarcasm" : 0.0,\n
"intelligence" : 0.0,\n
"wisdom" : 0.0,\n
"empathy" : 0.0,\n
"aggression" : 0.0,\n
"assertiveness" : 0.0,\n
"dominance" : 0.0\n\n

Classify each messages for nuance and provide values that represent the 'strength' of each signal in the message. Provide one row per message  showing only the classification in the format {"engagement" : 0.0,"interest" : 0.0,"friendliness" : 0.0,"sarcasm" : 0.0,"intelligence" : 0.0,"wisdom" : 0.0,"empathy" : 0.0,"aggression" : 0.0,"assertiveness" : 0.0,"dominance" : 0.0}:\n"""