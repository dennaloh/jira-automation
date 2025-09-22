import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random

TRAIN_DATA = [
    # Access requests
    ("Hello team, how do I login into Athens environment? I don't seem to have access to set my username and password", {"label": "access_request"}),
    ("Hi, can I please request access to an on premises control plane as mentioned here https://cloudera.atlassian.net/wiki/spaces/SE/pages/1762854318/CDP+Private+Cloud I'm working with SE org - @Amit Mishra / @Suraj Shivananda to build a demo and need to deploy a model in a private AI workbench.", {"label": "access_request"}),
    ("Hi Team, Please grant access to onprem Cluster with Cloudera AI for Demo setup ?", {"label": "access_request"}),
    ("Hi, please could I request access credentials?", {"label": "access_request"}),
    ("Hi Team, I'm new SE based in Melbourne. Please could you setup access for private cloud environment as per https://cloudera.atlassian.net/wiki/spaces/SE/pages/593659381/CDP+Private+Cloud+Environments . If this is not the right channel for access please let me know if I have to raise any jira request. Thank you!", {"label": "access_request"}),
    ("Hello! new user to Private Cloud here!! can I get access for Athens - trying to login to the demo environment listed in this page is there any wiki that lists demo videos on PVC cloud capabilities that I can view? Appreciate your help!!", {"label": "access_request"}),
    ("Hi Team, I need access to ARES. Could you please help me with that?", {"label": "access_request"}),
    ("Requesting access to Athens AD so I can work in CDP demo environments, specifically Observability playground.", {"label": "access_request"}),
    ("Good day, who can help me to get Athens credentials?", {"label": "access_request"}),

    # Credential resets
    ("Help needed - I need to reset my user: jingalls - password for ARES & ATHENS.  Please.", {"label": "credential_reset"}),
    ("Hi Team, My credentials on Ares and Athens environment are showing as invalid credentials. Can someone please help?", {"label": "credential_reset"}),
    ("Hi team, today I tried login https://console-ares-ocp.apps.field-team-ocp-01.kcloud.cloudera.com/ using the given password (was able to login before) but got \"Invalid credentials. Try again with correct credentials.\"", {"label": "credential_reset"}),
    ("Hi Team, I’d like to reset my tower foundry password to access Olympus and Ares but I can’t find the link anywhere in Confluence. Can someone please send me the URL?", {"label": "credential_reset"}),
    ("Hey.. Can I request a rest of my password for athens - cc @Prashant Singh", {"label": "credential_reset"}),
    ("Hi, I need assistance to reset my ares password  (userid: yrajashekharaiah)", {"label": "credential_reset"}),
    ("Hi team. I am unable to logon to Athens. My credentials are working on Ares. Could someone please take a look when you have a moment please?", {"label": "credential_reset"}),
    ("Hello,  I am connecting to Athens and getting an invalid credentials error (I am using the correct ones) was there an environment reset? Thanks", {"label": "credential_reset"}),
    ("Hi team, can you please reset my ares credentials? Thank you", {"label": "credential_reset"}),

    # Others
    ("Hi @Prashant Singh: Will need to provide some setup for my customer on Private cloud . I would need the use of ARES for a couple of hours atleast today . Can you let me know if can i go ahead ?", {"label": "other"}),
    ("Hi Team, Is there any chance of having CSM KOP 1.4 installed in the demo tenant. I'm interested to see Surveyor.", {"label": "other"}),
    ("@here ARES-ECS will be used by @Dennis Lee for customer engagement from 25th Aug until 29th August between 09:00 AM and 07:00 PM GMT+3. We will be keeping that environment dedicated for the purpose.", {"label": "other"}),
    ("hello, I was trying to check the Hive query history but I have 0 results, anything I’m missing? it’s on ARES", {"label": "other"}),
    ("Hi Team, I am encountering some resource constraints in launching CAI sessions / applications in ARES. Can someone help ? It is continuing to take forever to provision resources . There is a setting on custom quota and there isnt a lot of workload running on the AREAS. ( workbench goes-ocp CAI workbench)", {"label": "other"}),
]

TEST_DATA = [
    "The issue is across all prod control planes , so demo is also affected",
    "hi, I’m trying to see something in CDE in Ares or Athens and I’ve got the “valid ssl certificates required” when looking at jobs?",
    "Hello, I'm having trouble enabling the PM-Sandbox-AWS Environment with the following error - is anyone able to help?",
    "Hey Team, I’d like to use Athens to run a couple Spark Submit examples and as part of this I need to upload my pyspark app to an hdfs location. I tried to create a folder, however it seems I have no permissions. Can you please help? :thread:"
]

nlp = spacy.blank("en")  # create blank model
textcat = nlp.add_pipe("textcat")  # add text classifier

# Add labels
textcat.add_label("access_request")
textcat.add_label("credential_reset")
textcat.add_label("other")

# Training
optimizer = nlp.begin_training()

for i in range(10):  # 10 iterations
    random.shuffle(TRAIN_DATA)
    batches = minibatch(TRAIN_DATA, size=2)
    for batch in batches:
        examples = []
        for text, annotation in batch:
            doc = nlp.make_doc(text)
            examples.append(Example.from_dict(doc, {"cats": {annotation["label"]: 1.0}}))
        nlp.update(examples, sgd=optimizer)

# Test
for msg in TEST_DATA:
    doc = nlp(msg)
    print(doc.cats)