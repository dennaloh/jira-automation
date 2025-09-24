from fastapi import FastAPI, Request
from jira import JIRA
import os, dotenv, openai, re
from datetime import datetime, timedelta

dotenv.load_dotenv()
app = FastAPI()
REPLY_PREFACE = "If you did not request for an extension, please ignore this message."
AWS_ACCT_MSG = "cloud-aws-dev-cdp-trial"

openai.api_key = os.getenv("OPENAI_API_KEY")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
jira_server = os.getenv("JIRA_SERVER")

jira = JIRA(
    basic_auth=(email, api_token),
    server=jira_server
)

def detect_extension(comment):
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

def delete_comments(first, last):
    for i in range(first, last+1):
        print(i)
        try:
            comment = jira.comment("CDPAR-811", str(i))
            comment.delete()
        except Exception as e:
            continue

def extract_cloud_account(text):
    """
    Extracts a cloud account ID from the comment text.
    """
    pattern = re.escape(AWS_ACCT_MSG) + r"[\w-]*"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def get_acct_and_date_assigned(issue_key):
    issue = jira.issue(issue_key)
    for comment in issue.fields.comment.comments:
        comment_text = comment.body
        if AWS_ACCT_MSG in comment_text:
            cloud_acct = extract_cloud_account(comment_text)
            date_assigned = comment.created[:10]
            return cloud_acct, date_assigned
        
def get_date_assigned(issue_key):
    issue = jira.issue(issue_key)
    for comment in issue.fields.comment.comments:
        comment_text = comment.body
        if AWS_ACCT_MSG in comment_text:
            date_assigned = comment.created[:10]
            return date_assigned

@app.post("/webhook")
async def jira_webhook(request: Request):
    payload = await request.json()
    print("Received payload:", payload)
    comment_text = payload['comment']

    # issue_key = payload['issue']['key']
    issue_key = "CDPAR-803"

    # cloud_acct = payload['issue']['fields']['cloud_account'].split()[0]
    cloud_acct, date_assigned = get_acct_and_date_assigned(issue_key)

    # if REPLY_PREFACE not in comment_text and detect_extension(comment_text):
    if REPLY_PREFACE not in comment_text:
        # yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        # date_assigned = get_date_assigned(issue_key)

        yesterday = "2025-09-15"

        print(cloud_acct, date_assigned, yesterday)

        reply = "Total cost so far for all regions in account: https://app.cloudzero.com/explorer?activeCostType=real_cost&partitions=costcontext%3AService+Category&dateRange=Custom&startDate="+date_assigned+"T00%3A00%3A00Z&endDate="+yesterday+"T23%3A59%3A59Z&costcontext%3AAccount+Name="+cloud_acct+"+%28755369499673%29&costcontext%3ADepartment+Name=Sales+SE+Management&showRightFlyout=filters \n" + REPLY_PREFACE
        
        # jira.add_comment(issue_key, reply)
        print(reply)

        return {"status": "comment added"}

    return {"status": "ignored"}

# delete_comments(5713388, 5713487)