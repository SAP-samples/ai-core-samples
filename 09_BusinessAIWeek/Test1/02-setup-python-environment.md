# Setup SAP Business Application Studio and a dev space
> [SAP Business Application Studio](https://help.sap.com/docs/bas/sap-business-application-studio/what-is-sap-business-application-studio) is based on Code-OSS, an open-source project used for building Visual Studio Code. Available as a cloud service, SAP Business Application Studio provides a desktop-like experience similar to leading IDEs, with command line and optimized editors.

> At the heart of SAP Business Application Studio are the dev spaces. The dev spaces are comparable to isolated virtual machines in the cloud containing tailored tools and preinstalled runtimes per business scenario, such as SAP Fiori, SAP S/4HANA extensions, Workflow, Mobile and more. This simplifies and speeds up the setup of your development environment, enabling you to efficiently develop, test, build, and run your solutions locally or in the cloud.

## Open SAP Business Application Studio
👉 Go back to your [BTP cockpit](https://emea.cockpit.btp.cloud.sap/cockpit).

👉 Navigate to `Instances and Subscriptions` and open `SAP Business Application Studio`.

![Clone the repo](images/BTP_cockpit_BAS.png)


## Create a new Dev Space for CodeJam exercises

👉 Create a new Dev Space.

![Create a Dev Space 1](images/bas.png)

👉 Enter the name of the Dev space `GenAICodeJam`, select the `Basic` kind of application and `Python Tools` from Additional SAP Extensions.

👉 Click **Create Dev Space**.

![Create a Dev Space 2](images/create_dev_space.png)

You should see the dev space **STARTING**.

![Dev Space is Starting](images/dev_starting.png)

👉 Wait for the dev space to get into the **RUNNING** state and then open it.

![Dev Space is Running](images/dev_running.png)

## Clone the exercises from the Git repository

👉 Once you opened your dev space in BAS, use one of the available options to clone this Git repository with exercises using the URL below:

```sh
https://github.com/SAP-samples/generative-ai-codejam.git
```

![Clone the repo](images/clone_git.png)

👉 Click **Open** to open a project in the Explorer view.

![Open a project](images/clone_git_2.png)

## Open the Workspace

The cloned repository contains a file `codejam.code-workspace` and therefore you will be asked, if you want to open it. 

👉 Click **Open Workspace**.

![Automatic notification to open a workspace](images/open_workspace.png)

☝️ If you missed the previous dialog, you can go to the BAS Explorer, open the `codejam.code-workspace` file, and click **Open Workspace**.

You should see:
* `CODEJAM` as the workspace at the root of the hierarchy of the project, and
* `generative-ai-codejam` as the name of the top level folder.

👉 You can close the **Get Started** tab.

![Open a workspace](images/workspace.png)

## Configure the connection to Generative AI Hub

👉 Go back to your [BTP cockpit](https://emea.cockpit.btp.cloud.sap/cockpit).

👉 Navigate to `Instances and Subscriptions` and open the SAP AI Core instance's service binding.

![Service Binding in the BTP Cockpit](images/service_binding.png)

👉 Click **Copy JSON**.

👉 Return to BAS and create a new file `.aicore-config.json` in the `generative-ai-codejam/` directory.

👉 Paste the service key into `generative-ai-codejam/.aicore-config.json`, which should look similar to the following.

```json
{
  "appname": "7ce41b4e-e483-4fc8-8de4-0eee29142e43!b505946|aicore!b540",
  "clientid": "sb-7ce41b4e-e483-4fc8-8de4-0eee29142e43!b505946|aicore!b540",
  "clientsecret": "...",
  "identityzone": "genai-codejam-luyq1wkg",
  "identityzoneid": "a5a420d8-58c6-4820-ab11-90c7145da589",
  "serviceurls": {
    "AI_API_URL": "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com"
  },
  "url": "https://genai-codejam-luyq1wkg.authentication.eu10.hana.ondemand.com"
}
```

## Create a Python virtual environment and install the SAP's [Python SDK for Generative AI Hub]((https://pypi.org/project/generative-ai-hub-sdk/))

👉 Start a new Terminal.

![Extensions to install](images/start_terminal.png)

👉 Create a virtual environment using the following command:

```bash
python3 -m venv ~/projects/generative-ai-codejam/env --upgrade-deps
```

👉 Activate the `env` virtual environment like this and make sure it is activated:

```bash
source ~/projects/generative-ai-codejam/env/bin/activate
```

![venv](images/venv.png)

👉 Install the Generative AI Hub [Python SDK](https://pypi.org/project/generative-ai-hub-sdk/) (and the other packages listed below) using the following `pip install` commands.

```bash
pip install --require-virtualenv -U generative-ai-hub-sdk[all]
```

👉 We will also need the [HANA client for Python](https://pypi.org/project/hdbcli/).

```bash
pip install --require-virtualenv -U hdbcli
```

👉 We will also need the [SciPy package](https://pypi.org/project/scipy/).

```bash
pip install --require-virtualenv scipy
```

👉 We will also need the [pydf package](https://pypi.org/project/pypdf/) and [wikipedia](https://pypi.org/project/wikipedia/).

```bash
pip install --require-virtualenv pypdf wikipedia
```

<!-- 👉 And [LangChain Experimental](https://pypi.org/project/langchain-experimental/).

```bash
pip install --require-virtualenv generative-ai-hub-sdk[all] langchain-experimental
```-->


> From now on the exercises continue in BAS.

[Next exercise](03-prompt-llm.ipynb)
