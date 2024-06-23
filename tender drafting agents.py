
import os
import autogen
from autogen import register_function
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) 


def read_tenders_knowledge_base(tenders_repository:str) -> str:
    '''
    read the repository of previously submitted tenders content from tenders repository directory.


    Parameters:
            tenders_repository (str) : File directory path given by user.
    Returns:
        A list with the content of previously submitted tenders
    '''
    from PyPDF2 import PdfReader
    # To avoid AI agent to pass some random directory path from the internet which might be a problem, 
    # To be on the safer side we are hard coding the directory path
    tenders_repository = "C:/Users/tsrav/Documents/Proposals AI/Tender submissions"
    knowledge_base = []

    tenders_docs = os.listdir(tenders_repository)
    for file_name in tenders_docs:
        reader = PdfReader(os.path.join(tenders_repository, file_name))
        knowledge_base.append(f'\n{file_name} Tender Document\n')
        for page in reader.pages:
            page = reader.pages[0]
            text = page.extract_text()
            knowledge_base.append(text)
    return knowledge_base


def read_proposal_document(rfp_document:str) -> str:
    '''
    read the content of the request for proposal document.

    Parameters:
            rfp_document (str) : File path given by user.
    Returns:
        A list which contains the content of request for proposal document
    '''
    from PyPDF2 import PdfReader

    # To avoid AI agent to pass some random file path from the internet which might be a problem, 
    # To be on the safer side we are hard coding the file path
    rfp_document = "C:/Users/tsrav/Downloads/request for proposal.pdf"
    request_for_proposal = []
    reader = PdfReader(rfp_document)
    for page in reader.pages:
        page = reader.pages[0]
        text = page.extract_text()
        request_for_proposal.append(text)
    return request_for_proposal


def read_suggestions(suggestions_fp : str) -> str:
    '''
    Read predefined human suggestions, maintained in a txt file

    Parameters:
            suggestions_fp (str) : File path given by user.
    Returns:
        A string which contains suggestions
    '''
    suggestions = []
    # suggestions = ''
    with open(suggestions_fp, 'r') as file:
        for line in file:
            suggestions.append(line)
            # suggestions += line
    return suggestions


def write_suggestions(user_inputs : str, suggestions_fp: str) -> str:
    '''
    Takes user_inputs given by user and write the user inputs to the file located in file path suggestions_fp
    Parameters:
            user_inputs (str) : Inputs given by user
            suggestions_fp (str) : File path of the file for which user inputs should be written to
    '''
    with open(suggestions_fp, 'a') as file:
        file.write(f'\n {user_inputs}')
    return f'User inputs are written to file located in {suggestions_fp}'


llm_config = {"model": "gpt-3.5-turbo",
              "api_key": os.getenv("API_KEY")}


rfp_reader = autogen.AssistantAgent(
    name="RFP Document Reader",
    max_consecutive_auto_reply=5,
    # max_turns=2,
    is_termination_msg=lambda x: (x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")),
    llm_config=llm_config,
    code_execution_config={"work_dir": ".", "use_docker": False},
    function_map={"read_proposal_document": read_proposal_document}
)
    
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: (x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")),
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "tasks",
        "use_docker": False,
    }, 
)

writer = autogen.AssistantAgent(
    name="writer",
    llm_config=llm_config,
    human_input_mode="NEVER",
    system_message="""
        You are a professional writer, known for
        your insightful and engaging articles.
        You transform complex concepts into compelling narratives.
        Ask for human inputs for suggestions and corrections in the the draft tender response.
        """
)

user_proxy_human_input = autogen.UserProxyAgent(
    name="User_Proxy_Human_Input",
    human_input_mode="ALWAYS",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        # "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  
)


# Register the user defined functions to the agents.
register_function(
    read_proposal_document,
    caller=rfp_reader,  
    executor=user_proxy, 
    name="read_proposal_document",
    description="read the content of the request for proposal document", 
)

register_function(
    read_tenders_knowledge_base,
    caller=rfp_reader, 
    executor=user_proxy,
    name="read_tenders_knowledge_base", 
    description="read the repository of previously submitted tenders content from tenders repository directory"
)

register_function(
    read_suggestions,
    caller=writer, 
    executor=user_proxy_human_input,
    name="read_suggestions", 
    description="read the suggestions"
)

task = '''write a draft tender in response to the questions asked in the request for proposal document by analyzing the previous tender documents, 
file path of the request for proposal document is "C:/Users/tsrav/Downloads/request for proposal.pdf" and file directory of the previous tender documents is "C:/Users/tsrav/Documents/Proposals AI/Tender submissions"
'''

task1 = 'Based on the draft tender response given by user, change the draft tender response based on the suggestions given in file path "C:/Users/tsrav/Documents/Proposals AI/Draft Tender Suggestions.txt"'


chat_results = autogen.initiate_chats(
    [
        {   "sender": user_proxy,
            "recipient": rfp_reader,
            "message": task,
            "summary_method": "last_msg",
            "summary_args": {"summary_prompt" : 
            "Return the draft tender document provided by RFP Document Reader"},
        },
         {  "sender": user_proxy_human_input,
            "recipient": writer,
            "message": task1,
            "summary_method": "reflection_with_llm",
            "carryover": "Ask for human inputs for corrections in the the draft tender response",
        },
    ]
)