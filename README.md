# Car Pricer
Car pricer is Car Gurus for classic cars. It's relatively straight forward to build a model to price modern cars. There's a depreciation schedule based on mileage, year, etc., standard option packages, and lots of volume.
Car Gurus does this well. But classic cars is a different story. Markets are sparse and each car is unique. There's no depreciation schedule. There's some information in knowing the make, model, and year, but 
most of the information is contained in the description (ie. How was the engine rebuilt? How much was spent on the new paint job?... and other details of the restoration.). 
In other words, pricing modern cars is a structured data problem; pricing classic cars is an unstructured data problem.

This project is an attempt to build a pricing model for classic cars by leveraging LLMs and other techniques to infer price from a description.

## Key Components

### Utility Files
- utils.py: utility functions for loading and writing data
- database.py: creates db, table, and inserts data
- items.py: Item class creates a clean, curated datapoint of a car listing (Attrs: title, price, category, features, prompt)
- loaders.py: ItemLoader class uses Item class. Loads records from database, transforms them to items.
- testing.py: test harness used for evaluation. Takes a trained model and test set, runs inference, and outputs eval results and graph.
- config: config.py and config_deploy.py contain all hardcoded variables for import into the scripts where they are used.
### Scraper
- scraper.py: Scraper class used to gather dataset.
- process_ids.py: runs Scraper class on each listing id (collecting description and details), then saves records in json.
### Pricing Model
- specialist_agent.py: calls car-pricer service deployed on Modal through service.py
- rag_agent.py: fetches top_k similar cars from ChromaDB, adds them to the context for the LLM to use to price the new car description.
- tfidf_rf_regressor.py: TF-IDF Random Forest Regressor model that creates weights and embedding artifacts used by rf_agent.
- rf_agent.py: calls random forest model to price the new car description.
- ensemble_agent.py
### Agent Framework
- agent.py: Superclass for all agents used t
- planning_agent.py:
- messaging_agent.py:
- memory.json:
- deal_agent_framework.py:
### Deployment
- service.py: loads "specialist" quantized 4bit OSS model finetuned on the training set from local folder and spins up Modal VM to run inference on car descriptions.
- classic_car_pricer.py:
### Notebooks
Excluding the colab notebook, these notebooks were used for experimenting, testing, and building the functions that make up the final classes and scripts.
- dataset.ipynb:
- baseline_models.ipynb:
- finefune_frontier.ipynb:
- [finetune_oss](https://drive.google.com/drive/folders/1lvzq8rCwP8t8WpKIUMSWVoDY2Tt__E3r?usp=sharing): folder with OSS finetune colab notebook (needed to rent a GPU)
- deploy_testing.ipynb:
- get_deals.ipynb:
- build_ui.ipynb:

## To Do
