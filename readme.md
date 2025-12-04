### Project Saul
## General search and RAG model

# v1.0
Saul is an ai agent which has been orchestrated as web application using python [FAST-API] as backend system.
It has general searching capabilities using gemini 2.5 flash lite model and has persistent memory blocks for storing user conversation without user access management.

# v1.1
In new release, RAG capabilities has been added to it.
Saul now comes with chat interface UI where it can be used as RAG model. As of now, two features have been included.
    - User can provide the documentation url (website url), which will be skimmed and stored in memory (vector DB).
    - User can query across those data by shooting out queries to saul.
Saul uses natively served ollama models to perform this capabilities this ensures data privacy.
The old end points are still up and it can be accessed through swagger page.

# future plans
Planning to scale its capabilities so that saul can act as an internal knowledge source for organizations.
Acting as helper bot within organization for below given multiple applications:
    - system design and process level queries(source: confluence)
    - steps to resolve known errors(source: SNOW, KEDB)