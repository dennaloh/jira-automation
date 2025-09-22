from fastapi import FastAPI, Request
from jira import JIRA

app = FastAPI()

# Authentication
jira = JIRA(
    basic_auth=("", ""),
    server=""
)

def get_all_comments(issue_key):
    """Get all comments on an issue"""
    issue = jira.issue(issue_key)
    return [{
        'id': comment.id,
        'author': comment.author.displayName,
        'body': comment.body,
        'created': comment.created,
        'updated': comment.updated
    } for comment in issue.fields.comment.comments]

print(get_all_comments("CDPAR-770"))

KEYWORDS = ["extend", "budget"]

@app.post("/webhook")
async def jira_webhook(request: Request):
    payload = await request.json()
    issue_key = payload['issue']['key']
    comment_text = payload['comment']['body'].lower()

    if any(word in comment_text for word in KEYWORDS):
        reply = "Thanks for your comment! We'll review the extension/budget request."
        try:
            jira.add_comment(issue_key, reply)
        except Exception as e:
            print(f"Failed to post comment: {e}")
        return {"status": "replied"}
    
    return {"status": "ignored"}
