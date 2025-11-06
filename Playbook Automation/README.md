# Jira Automation with Ansible

This repository provides a number of Ansible playbooks for various Jira activities on the CDPAR project.
It uses the CloudZero API, Jira API and Salesforce API to get the required details.

## Requirements

This example requires an execution environment with dependencies to run the automation; and a set of configuration variables.

### Execution Environment Setup

> **_NOTE 1:_** These steps need to be run using Python version 3.9 or greater.

> **_NOTE 2:_** A container engine is required to be run. The instructions here are for Docker.

0. Ensure you have a version of Python >= 3.9 and have docker running.

    ```bash
    python --version

    docker info
    ```

1. Create and activate a new `virtualenv` and install `ansible-core` and `ansible-navigator`

    ```bash
    python -m venv ~/cdp-navigator; 

    source ~/cdp-navigator/bin/activate; 

    pip install ansible-core ansible-navigator
    ```

1. Clone this repository.

    ```bash
    git clone https://github.infra.cloudera.com/dennaloh/jira-automation.git; 
    ```

1. Change your working directory to this project.

    ```bash
    cd jira-automation
    ```

Further instructions to setup `ansible-navigator` are on the Cloudera Labs [`cldr-runner` project's help guide](https://github.com/cloudera-labs/cldr-runner/blob/main/NAVIGATOR.md).

## Execution

### Workshop Cloud Cost Tracker

The `workshop-cloudcost-tracker.yml` playbook tracks the total cloud costs for any in progress hands-on lab and workshop environments.

It works by querying all _In Progress_ tickets in the `CDPAR` Jira project that have the `SE-Workshop` component. From this, it extracts the Cloud Account used and queries the CloudZero API to get the total running costs for that account. The running cost is then added as a comment in the Jira ticket.

* Run the playbook with the following command:

    ```bash
    ansible-navigator run workshop-cloudcost-tracker.yml --ask-vault-password --enable-prompts
    ```

    * At the prompt enter the password for the vault.

### Update Jira Opp status

The `update_opp.yml` playbook updates the opp status based on the Salesforce Opp stage.

It works by querying all tickets in the `CDPAR` Jira project that have a non-empty `SFDC opp link` field. From this, it extracts the Opportunity ID and queries the Salesforce API to get the current opp stage for that opp. The opp stage is then used to update the Opp won field.

* Run the playbook with the following command:

    ```bash
    ansible-navigator run update_opp.yml --ask-vault-password --enable-prompts
    ```

    * At the prompt enter the password for the vault.