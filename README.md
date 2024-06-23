## Ai Agents to create a draft tender document in response to the request for proposal(RFP)

### Data Sources
    Request for proposal document
    Previous tender documents repository - ./Tender submissions
    Predefined human inputs - Draft Tender Suggestions.txt
    * All the data sources have been created using chatgpt, the information present is in the document is not real.


### Challenges to work on
    1. As AI agents interactions and the llm outputs are non deterministic, have to work on making the output deterministic.
    2. Currently this repo is using cache folder to give the expected output, delete the cache folder and everytime you run the code the output will be different everytime.
    3. The interactions between the AI agents to be controlled in such a way that the interactions will be constructive towards the outlined task.

    <b>How to make the output more deterministic.</b>
        1. User few shot prompting instead of zero shot prompting, in this repo we have used zero shot prompting
        2. Use seeding, in this repo we have used cache.
        3. Use system messages for Agents to reduce the scope of though process.
        4. Fine tune the llm with the example tender documents after masking the sensitive data. LLM might give more deterministic output.

### Back logs
    1. Human inputs given by user to be saved/appended to Draft Tender Suggestions.txt
    2. Writing the output of AI agent to PDF file.
    3. Improve the solution using more predefined human inputs defined in Draft Tender Suggestions.txt, currently only 1 suggestion is given.
    4. Making the output more deterministic.
