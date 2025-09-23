from fastapi import FastAPI, Request
from jira import JIRA
import os, dotenv, openai

dotenv.load_dotenv()
app = FastAPI()
BOT_MARKER = "If this is not a request for extension, please ignore this message."

openai.api_key = os.getenv("OPENAI_API_KEY")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
jira_server = os.getenv("JIRA_SERVER")

jira = JIRA(
    basic_auth=(email, api_token),
    server=jira_server
)

def detect_extension(comment: str) -> bool:
    prompt = f"""You are a classifier. Decide if this Jira comment is asking
    for a POC extension. Reply only with 'YES' or 'NO'.

    Comment: {comment}
    """

    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.choices[0].message.content.strip().lower()
    return "yes" in result

def get_all_comments(issue_key):
    issue = jira.issue(issue_key)
    return [{
        'id': comment.id,
        'author': comment.author.displayName,
        'body': comment.body,
        'created': comment.created,
        'updated': comment.updated
    } for comment in issue.fields.comment.comments]

@app.post("/webhook")
async def jira_webhook(request: Request):
    payload = await request.json() # FastAPI handles proper JSON parsing
    comment_text = payload['comment']
    issue_key = payload['issue']['key']
    if BOT_MARKER not in comment_text:
        print(comment_text)

    if BOT_MARKER not in comment_text and detect_extension(comment_text):
        print("EXTENSION REQUEST DETECTED")
        jira.add_comment(
            issue_key,
            f"If this is not a request for extension, please ignore this message."
        )
        return {"status": "comment added"}

    return {"status": "ignored"}
