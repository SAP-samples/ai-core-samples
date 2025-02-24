# Using Advanced AI techniques with SAP's Generative AI Hub
This [repository](https://github.com/SAP-samples/ai-core-samples/tree/main/10_Learning_Journeys) is prepared to provide examples for the specific enablement: "Using Advanced AI techniques with SAP's Generative AI Hub.

**Please Download the entire repository before you execute the notebook.

This will download the notebook dataset too.
Please make sure that the <key.json> or <whatever name> your ai-core service key that you downloaded from BTP for ai core credentials, you keep the json in the same path as to where you downloaded the repository and change the name from <key.json> to config.json
Make sure that the config.json is inside the 10_learning_journeys folder in the downloaded repository**
### Files

- `Prompt for emails generation.docx`: This fle contains the prompt to create the emails and generated emails. Generated emails can be used to create grounding data repository.

# Grounding pre-requisite:

Before running the notebook, you need to create the knowledge base with the relevant documents.

Using the generated emails in the file `Prompt for emails generation.docx`, provide the chunks of document via vector API and create data repository required for the grounding.
Refer the document [here](https://help.sap.com/docs/sap-ai-core/generative-ai-hub-restructure/grounding?state=DRAFT&profile=20227684#option-2-provide-the-chunks-of-document-via-vector-api-directly) for the detailed steps.