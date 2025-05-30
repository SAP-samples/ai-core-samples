# Setup SAP AI Launchpad and SAP AI Core
[SAP AI Launchpad](https://help.sap.com/docs/ai-launchpad) is a multitenant SaaS application on SAP BTP. You can use SAP AI Launchpad to manage AI use cases across different AI runtimes. SAP AI Launchpad also provides generative AI capabilities via the [Generative AI Hub in SAP AI Core](https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/generative-ai-hub-in-sap-ai-core-7db524ee75e74bf8b50c167951fe34a5) and is available in the Cloud Foundry environment. You can also connect the SAP HANA database as an AI runtime to work with the HANA Predictive Analysis Library (PAL), or connect SAP AI Services to work with the SAP AI Service Data Attribute Recommendation.

## [1/4] Open SAP Business Technology Platform
👉 Open your [BTP cockpit](https://emea.cockpit.btp.cloud.sap/cockpit).

👉 Navigate to the subaccount: `GenAI CodeJam`.

## [2/4] Open SAP AI Launchpad and connect to SAP AI Core
👉 Go to **Instances and Subscriptions**. Check whether you see an **SAP AI Core** instance and an **SAP AI Launchpad** subscription.

![BTP Cockpit](images/btp.png)

With SAP AI Launchpad you can administer all your machine learning operations. ☝️ Make sure you have the extended plan of SAP AI Core to leverage Generative AI Hub. To connect SAP AI Core to SAP AI Launchpad you need the SAP AI Core service key.

![SAP AI Core service key](images/service-key.png)

☝️ In this subaccount the connection between the SAP AI Core service instance and the SAP AI Launchpad application is already established. Otherwise you would have to add a new runtime using the SAP AI Core service key information.

👉 Open **SAP AI Launchpad**.

## [3/4] Create a new resource group for your team
SAP AI Core tenants use [resource groups](https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/resource-groups) to isolate AI resources and workloads. Scenarios (e.g. `foundation-models`)
and executables (a template for training a model or creation of a deployment) are shared across all resource groups.

> Make sure to create a **NEW** resource group for your team.</br> DO NOT USE THE DEFAULT RESOURCE GROUP!

👉 Open the `SAP AI Core Administration` tab and select `Resource Groups`. 

👉 **Create** a new resource group with your team's name.

![SAP AI Launchpad - Recourse Group 1/2](images/resource_group.png)

👉 Go back to **Workspaces**.

👉 Select your connection and your resource group.

👉 Make sure it is selected. It should show up at the top next to SAP AI Launchpad.

☝️ You will need the name of your resource group in [Exercise 04-create-embeddings](04-create-embeddings.ipynb).

> If your resource group does not show up, use the **browser(!)** refresh button to refresh the page.

![SAP AI Launchpad - Recourse Group 2/2](images/resource_group_2.png)

[Next Exercise](01-explore-genai-hub.md)
