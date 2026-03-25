from database import *
import urllib.parse
from flask import jsonify,request,session,render_template,redirect,url_for,Blueprint
from requests_oauthlib import OAuth2Session
from flask_login import login_required, login_user, current_user, logout_user
import secrets
from datetime import datetime, date, timedelta, timezone
import os, pickle, codecs
from typing import List
from langchain.chat_models import ChatOpenAI
from llm_provider import create_chat_model, PROVIDER_OPENAI
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]
google_client_id = os.environ.get('google_client_id')
google_client_secret = os.environ.get('google_client_secret')

if not google_client_id or not google_client_secret:
    print("=" * 60)
    print("WARNING: Google OAuth credentials not found!")
    print("Please set the following environment variables:")
    print("  - google_client_id")
    print("  - google_client_secret")
    print("")
    print("Get these from: https://console.cloud.google.com/apis/credentials")
    print("See server/.env.example for reference.")
    print("=" * 60)
word_limit = 50 # word limit for task brainstorming

rp = Blueprint('rp', __name__)


@rp.route("/rp/isLoggedIn", methods=['GET'])
def rp_isLoggedIn():
    url_host = urllib.parse.urlsplit(request.url).hostname
    if "5000" in request.url:
        redirect_uri = "http://"+url_host+":5000/rp/google_callback"
    else:    
        redirect_uri = "https://"+url_host+"/rp/google_callback"
    google = OAuth2Session(
        google_client_id, scope=scope, redirect_uri=redirect_uri)
    login_url, state = google.authorization_url(authorization_base_url)
    session['oauth_state'] = google_client_id
    if current_user.is_authenticated:
        if current_user.openai_key == "" or current_user.openai_key == None:
            keyAdded = None
        else:
            keyAdded = current_user.openai_key
        provider = getattr(current_user, 'llm_provider', 'openai') or 'openai'
        minimax_key = getattr(current_user, 'minimax_key', None)
        if provider == "minimax" and minimax_key:
            keyAdded = minimax_key
        return jsonify(isLoggedIn=current_user.is_authenticated,userId=current_user.id,key_added=keyAdded,image=current_user.profile_image,provider=provider)
    else:
        return jsonify(isLoggedIn=False,auth_url=login_url)

@rp.route("/rp/google_callback", methods=['GET'])
def rp_google_callback():
    url_host = urllib.parse.urlsplit(request.url).hostname
    if "5000" in request.url:
        redirect_uri = "http://"+url_host+":5000/rp/google_callback"
    else:
        redirect_uri = "https://"+url_host+"/rp/google_callback"
    google = OAuth2Session(
        google_client_id, scope=scope, redirect_uri=redirect_uri)
    token_url = "https://www.googleapis.com/oauth2/v4/token"
    welcome = False
    try:
        google.fetch_token(token_url, client_secret=google_client_secret,
                        authorization_response=request.url)
    except:
        pass
    response = google.get(
        'https://www.googleapis.com/oauth2/v1/userinfo').json()
    email = response["email"].lower()
    googleId = str(response["id"])
    name = response["name"]
    image = response["picture"]
    getAdmin = Admin.query.filter_by(email=email).first()
    if getAdmin == None:
        getAdmin = Admin(id=secrets.token_urlsafe(24), email=email,google_id=googleId, name=name,profile_image=image, created_date=datetime.now())
        db.session.add(getAdmin)
        db.session.commit()
    else:
        getAdmin.google_id = googleId
        getAdmin.profile_image = image
        db.session.commit()
    login_user(getAdmin, remember=True)
    return redirect("http://localhost:3000/")

class CAMELAgent:

    def __init__(
        self,
        system_message,
        model: ChatOpenAI,
        store
    ) -> None:
        self.model = model
        if store == None:
            self.system_message = system_message
            self.init_messages()
            # print("NEW")
        else:
            self.stored_messages = store
            self.system_message = store[0]
            # print("MESSAGES \n",self.stored_messages,"\n SYSTEM MESSAGE \n",self.system_message)

    def reset(self) -> None:
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        self.stored_messages = [self.system_message]
        # for msg in self.stored_messages:
            # print("INTIALIZED",msg.content,"\n")

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        # for msg in self.stored_messages:
            # print("UPDATED",msg.content,"\n")
        return self.stored_messages

    def step(
        self,
        input_message: HumanMessage,
    ) -> AIMessage:
        messages = self.update_messages(input_message)
        output_message = self.model(messages)
        self.update_messages(output_message)

        return output_message

    def store_messages(self) -> None:
        return self.stored_messages




def starting_convo(assistant_role_name,user_role_name,task,provider=None,api_key=None):
    task_specifier_sys_msg = SystemMessage(content="You can make a task more specific.")
    task_specifier_prompt = (
    """Here is a task that {assistant_role_name} will help {user_role_name} to complete: {task}.
    Please make it more specific. Be creative and imaginative.
    Please reply with the specified task in {word_limit} words or less. Do not add anything else."""
    )
    task_specifier_template = HumanMessagePromptTemplate.from_template(template=task_specifier_prompt)
    task_specify_agent = CAMELAgent(task_specifier_sys_msg, create_chat_model(provider=provider,api_key=api_key,temperature=1.0),None)
    task_specifier_msg = task_specifier_template.format_messages(assistant_role_name=assistant_role_name,
                                                                user_role_name=user_role_name,
                                                                task=task, word_limit=word_limit)[0]
    specified_task_msg = task_specify_agent.step(task_specifier_msg)
    # print(f"Specified task: {specified_task_msg.content}")
    specified_task = specified_task_msg.content

    assistant_inception_prompt = (
    """Never forget you are a {assistant_role_name} and I am a {user_role_name}. Never flip roles! Never instruct me!
    We share a common interest in collaborating to successfully complete a task.
    You must help me to complete the task.
    Here is the task: {task}. Never forget our task!
    I must instruct you based on your expertise and my needs to complete the task.

    I must give you one instruction at a time.
    You must write a specific solution that appropriately completes the requested instruction.
    You must decline my instruction honestly if you cannot perform the instruction due to physical, moral, legal reasons or your capability and explain the reasons.
    Do not add anything else other than your solution to my instruction.
    You are never supposed to ask me any questions you only answer questions.
    You are never supposed to reply with a flake solution. Explain your solutions.
    Your solution must be declarative sentences and simple present tense.
    Unless I say the task is completed, you should always start with:

    Solution: <YOUR_SOLUTION>

    <YOUR_SOLUTION> should be specific and provide preferable implementations and examples for task-solving.
    Always end <YOUR_SOLUTION> with: Next request."""
    )

    user_inception_prompt = (
    """Never forget you are a {user_role_name} and I am a {assistant_role_name}. Never flip roles! You will always instruct me.
    We share a common interest in collaborating to successfully complete a task.
    I must help you to complete the task.
    Here is the task: {task}. Never forget our task!
    You must instruct me based on my expertise and your needs to complete the task ONLY in the following two ways:

    1. Instruct with a necessary input:
    Instruction: <YOUR_INSTRUCTION>
    Input: <YOUR_INPUT>

    2. Instruct without any input:
    Instruction: <YOUR_INSTRUCTION>
    Input: None

    The "Instruction" describes a task or question. The paired "Input" provides further context or information for the requested "Instruction".

    You must give me one instruction at a time.
    I must write a response that appropriately completes the requested instruction.
    I must decline your instruction honestly if I cannot perform the instruction due to physical, moral, legal reasons or my capability and explain the reasons.
    You should instruct me not ask me questions.
    Now you must start to instruct me using the two ways described above.
    Do not add anything else other than your instruction and the optional corresponding input!
    Keep giving me instructions and necessary inputs until you think the task is completed.
    When the task is completed, you must only reply with a single word <CAMEL_TASK_DONE>.
    Never say <CAMEL_TASK_DONE> unless my responses have solved your task."""
    )
    return specified_task,assistant_inception_prompt,user_inception_prompt

def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str,assistant_inception_prompt,user_inception_prompt):
    
    assistant_sys_template = SystemMessagePromptTemplate.from_template(template=assistant_inception_prompt)
    assistant_sys_msg = assistant_sys_template.format_messages(assistant_role_name=assistant_role_name, user_role_name=user_role_name, task=task)[0]
    
    user_sys_template = SystemMessagePromptTemplate.from_template(template=user_inception_prompt)
    user_sys_msg = user_sys_template.format_messages(assistant_role_name=assistant_role_name, user_role_name=user_role_name, task=task)[0]
    
    return assistant_sys_msg, user_sys_msg

@rp.route("/rp/start", methods=['POST'])
def start_rp():
    if not current_user.is_authenticated:
        return redirect("/agent_convo")
    provider = getattr(current_user, 'llm_provider', None) or PROVIDER_OPENAI
    if provider == "minimax":
        api_key = current_user.minimax_key
    else:
        api_key = current_user.openai_key
        os.environ["OPENAI_API_KEY"] = api_key
    assistant_role_name = request.json["role1"]
    user_role_name = request.json["role2"]
    task = request.json["task"]
    sessId = request.json["sessId"]
    if sessId == 0:
        getSession = Agent_Session(role_1=assistant_role_name,role_2=user_role_name,task=task,admin_id=current_user.id)
        db.session.add(getSession)
        db.session.commit()
        specified_task,assistant_inception_prompt,user_inception_prompt = starting_convo(assistant_role_name, user_role_name, task, provider=provider, api_key=api_key)
        assistant_sys_msg, user_sys_msg = get_sys_msgs(assistant_role_name, user_role_name, specified_task,assistant_inception_prompt,user_inception_prompt)
        assistant_agent = CAMELAgent(assistant_sys_msg, create_chat_model(provider=provider,api_key=api_key,temperature=0.2),None)
        user_agent = CAMELAgent(user_sys_msg, create_chat_model(provider=provider,api_key=api_key,temperature=0.2),None)
        # Reset agents
        assistant_agent.reset()
        user_agent.reset()

        # Initialize chats 
        assistant_msg = HumanMessage(
            content=(f"{user_sys_msg.content}. "
                        "Now start to give me introductions one by one. "
                        "Only reply with Instruction and Input."))

        user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
        user_msg = assistant_agent.step(user_msg)
    else:
        getSession = Agent_Session.query.filter_by(id=sessId).first()
        user_store = pickle.loads(codecs.decode((getSession.user_store).encode(), "base64"))
        assistant_store = pickle.loads(codecs.decode((getSession.assistant_store).encode(), "base64"))
        user_agent = CAMELAgent(None, create_chat_model(provider=provider,api_key=api_key,temperature=0.2),user_store)
        assistant_agent = CAMELAgent(None, create_chat_model(provider=provider,api_key=api_key,temperature=0.2),assistant_store)
        assistant_msg = HumanMessage(
            content=(f"{assistant_store[-1].content}"))

    # chat_turn_limit, n = 10, 0
    # while n < chat_turn_limit:
        # n += 1
    user_ai_msg = user_agent.step(assistant_msg)
    user_msg = HumanMessage(content=user_ai_msg.content)
    userMsg = user_msg.content.replace("Instruction: ","").replace("Input: None","").replace("Input: None.","")
    # print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")
    assistant_ai_msg = assistant_agent.step(user_msg)
    assistant_msg = HumanMessage(content=assistant_ai_msg.content)
    assistantMsg = assistant_msg.content.replace("Solution: ","").replace("Next request.","")
    # print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n")
    convoEnd = False
    if "<CAMEL_TASK_DONE>" in user_msg.content:
        convoEnd = True
    getUserStore = user_agent.store_messages()
    getSession.user_store = codecs.encode(pickle.dumps(getUserStore), "base64").decode()
    getAssistantStore = assistant_agent.store_messages()
    getSession.assistant_store = codecs.encode(pickle.dumps(getAssistantStore), "base64").decode()
    db.session.commit()
    return jsonify(sessId=getSession.id,userMsg=userMsg,assistantMsg=assistantMsg,convoEnd=convoEnd)


@rp.route("/rp/get_chat", methods=['get'])
def rp_get_chat():
    sessId = request.args.get('sessId')
    getSession = Agent_Session.query.filter_by(id=sessId).first()
    assistant_store =  pickle.loads(codecs.decode((getSession.assistant_store).encode(), "base64"))
    messages = []
    for store in assistant_store[2:]:
        if str(type(store)) == "<class 'langchain.schema.HumanMessage'>":
            messages.append({"role":0,"msg":store.content.replace("Instruction: ","").replace("Input: None","").replace("Input: None.","")})
        elif str(type(store)) == "<class 'langchain.schema.AIMessage'>":
            messages.append({"role":1,"msg":store.content.replace("Solution: ","").replace("Next request.","")})
    return jsonify(role1=getSession.role_1,role2=getSession.role_2,task=getSession.task,messages=messages)
