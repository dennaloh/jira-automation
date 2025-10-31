from fastapi import FastAPI, Request
from jira import JIRA
import os, dotenv, openai, json, requests
from datetime import datetime, timedelta

dotenv.load_dotenv()
app = FastAPI()
REPLY_PREFACE = "If you did not request for an extension, please ignore this message."
GOES_emails = ["akahan@cloudera.com", "rsuplina@cloudera.com", "ahennessy@cloudera.com", "therson@cloudera.com", "prashant.singh@cloudera.com", "jenright@cloudera.com"]
# "denna@cloudera.com", 
cloudzero_api_key = os.getenv("CLOUDZERO_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
jira_server = os.getenv("JIRA_SERVER")

jira = JIRA(
    basic_auth=(email, api_token),
    server=jira_server
)

def detect_extension(comment):
    prompt = f"""
You are a classifier. Decide if this Jira comment is asking
for a POC or workshop extension related to end dates or duration. 

- Reply only with 'YES' or 'NO'.
- 'YES' if the comment explicitly asks to change, extend, or update the end date of a POC or workshop.
- 'NO' if the comment is about capacity, quotas, budget, participants, or other unrelated details.

Examples:
1. "Can someone please update the POC end date to November 3rd?" -> YES
2. "We have a sudden rush of participants, can we increase cloud budget?" -> NO
3. "We would like to have this environment available until November 1st." -> YES
4. "The workshop size is 40 people for 4 hours." -> NO

Comment: {comment}
"""

    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.choices[0].message.content.strip().lower()
    return "yes" in result

def extract_cloud_account(account_str):
    """
    Extracts the actual CloudZero account ID from a prefixed string.
    Examples:
        "AWS - cloud-aws-dev-cdp-trial12" -> "cloud-aws-dev-cdp-trial12"
        "Azure-Field-Product-Experience-1" -> "Azure-Field-Product-Experience-1" (unchanged)
    """
    # If it contains ' - ', assume the last part is the account
    if ' - ' in account_str:
        return account_str.split(' - ')[-1].strip()
    else:
        return account_str.strip()

def get_cost_report(cloud_acct, region, start_date):
    API_BASE = "https://api.cloudzero.com/v2/billing/costs"
    headers = {
        "Authorization": f"Bearer {cloudzero_api_key}",
        "Accept": "application/json",
    }

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    filters = {"User:Defined:DepartmentName": ["Sales SE Management"]}
    if region:
        filters["Region"] = [region]

    params = {
        "start_date": start_date + "T00:00:00Z",
        "end_date": yesterday + "T00:00:00Z",
        "granularity": "daily",
        "group_by": "User:Defined:AccountName",
        "filters": json.dumps(filters),
        "cost_type": "real_cost"
    }

    all_costs = []
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(API_BASE, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        all_costs.extend(data.get("costs", []))
        cursor_info = data.get("pagination", {}).get("cursor", {})
        if cursor_info.get("has_next"):
            cursor = cursor_info.get("next_cursor")
        else:
            break

    # Local filter: only include accounts that start with cloud_acct
    filtered_costs = [
        rec for rec in all_costs
        if any(
            str(val).startswith(cloud_acct)
            for key, val in rec.items()
            if "User:Defined:AccountName" in key
        )
    ]

    total_cost = sum(rec.get("cost", 0) for rec in filtered_costs)
    
    print(total_cost)
    return round(total_cost, 2)

@app.post("/webhook")
async def jira_webhook(request: Request):
    payload = await request.json()
    comment_text = payload["comment"]
    print(f"Received comment: {comment_text}")
    comment_author = payload["author"]
    print(f"From: ", payload["author"])

    if REPLY_PREFACE not in comment_text and detect_extension(comment_text) and comment_author not in GOES_emails:
        print("Extension detected:", payload)

        cloud_acct = extract_cloud_account(payload["cloud_account"])
        region = payload["cloud_account_region"]
        start_date = payload["start_date"]
        total_cost = get_cost_report(cloud_acct, region, start_date)

        region_text = f" in {region}" if region else ""
        reply = f"Total spent to date for {cloud_acct}{region_text} since {start_date}: *${total_cost}*\nDo you need to request for a new budget?\n{REPLY_PREFACE}"
        
        # issue_key = payload["key"]
        # jira.add_comment(issue_key, reply)
        # print(datetime.now(), f"Added comment to {issue_key}")

        return reply

    return {"status": "ignored"}