apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: first-pipeline # Executable ID (max length 64 lowercase-hyphen-separated), please modify this to any value if you are not the only user of your SAP AI Core instance. Example: `first-pipeline-1234`
  annotations:
    scenarios.ai.sap.com/description: "Introduction to SAP AI Core"
    scenarios.ai.sap.com/name: "Tutorial"
    executables.ai.sap.com/description: "Greets the user"
    executables.ai.sap.com/name: "Hello Pipeline"
  labels:
    scenarios.ai.sap.com/id: "learning"
    ai.sap.com/version: "1.0"
spec:
  entrypoint: mypipeline
  templates:
  - name: mypipeline
    steps:
    - - name: greet
        template: greeter

  - name: greeter
    container:
      image: docker.io/python:latest
      command:
        - python3
        - '-c'
      args:
       - |
        print("Hello from SAP AI Core")
