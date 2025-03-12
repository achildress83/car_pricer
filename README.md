# Car Pricer
Car Gurus for classic cars. It's relatively straight forward to build a model to price modern cars. There's a depreciation schedule based on mileage, year, etc., standard option packages, and lots of volume.
Car Gurus does this well. But classic cars is a different story. Markets are sparse and each car is unique. There's no depreciation schedule. There's some information in knowing the make, model, and year, but 
most of the information is contained in the description (ie. How was the engine rebuilt? How much was spent on the new paint job?... and other details of the restoration.). 
In other words, pricing modern cars is a structured data problem; pricing classic cars is an unstructured data problem.

This project is an attempt to build a pricing model for classic cars by leveraging LLMs and other techniques to infer price from a description.
## Key Components

### Utility Files
- utils.py: utility functions for loading and writing data
- testing.py: test harness used for evaluation. Takes a trained model and test set, runs inference, and outputs eval results and graph.
### Scraper
- scraper.py: Scraper class used to gather dataset.
### Pricing Model
- specialist_agent.py: calls car-pricer service deployed on Modal through service.py
- rag_agent.py
- rf_agent.py
- ensemble_agent.py
### Agent Framework
- agent.py: Superclass for all agents used t
- planning_agent.py
- messaging_agent.py
### Deployment
- service.py: loads "specialist" quantized 4bit OSS model finetuned on the training set from local folder and spins up Modal VM to run inference on car descriptions.
- 
### Notebooks
