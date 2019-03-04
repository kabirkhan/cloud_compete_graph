Cloud Compete Graph (CCG)
==============================

CCG is a Concept Graph to the maps and analyzes the cloud compete landscape.

Current Cloud Providers:
- [Microsoft Azure](https://azure.microsoft.com/)
- [Amazon Web Services](https://aws.amazon.com/)
- [Google Cloud](https://cloud.google.com/)
- More coming soon...

## API

**API Docs for interacting with the graph and using extracting Cloud Service Named Entities from raw text**

https://kabirkhan.github.io/cloud_compete_graph/docs/

**Graph API**

https://cloudconceptgraph.azure-api.net

## Components

1. Azure Cosmos DB Graph Database
This is the core of the project, the actual concept graph

2. Cloud services Search Index
Allows you to search and get autocomplete queries for services from all cloud providers.

Published search index with CORS="*" enabled.

3. Named Entity Recognition model for identifying services in unstructured text data.
Imagine you're reading an article about Azure's serverless cloud offerings.
This model can extract Azure Functions, function app, function, etc in context and resolve that entity to the Azure Functions entity in the graph. From there you can get all the service metadata, a link to learn more and related services like AWS Lambda from Amazon Web Services

Currently this model only supports Azure services. I'm working on expanding this functionality.

All NER models are trained using Prodigy and [Spacy](https://spacy.io) and can be loaded like any other spacy model

```python
import spacy
nlp = spacy.load('models/ner_azure_v0')
text = "Azure functions, Microsoft's serverless offering now supports linux and python" 
doc = nlp(text)
list(doc.ents)
```

## How it's made

Info coming soon. For now use the points above to use the preconfigured service.
I'll add instructions and better pipelines for building everything yourself.

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
