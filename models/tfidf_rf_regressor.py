import re
from typing import List
from items import Item
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from config_deploy import MIN_DF, MAX_DF, NGRAM_RANGE, N_ESTIMATORS, SEED, N_FEATURES

class RFRegressor:
    
    def __init__(self, train: List[Item], test: List[Item]):
        self.test = test
        self.train_desc = [self.get_description(item.prompt) for item in train]
        self.test_desc = [self.get_description(item.prompt) for item in test]
        self.train_price = [item.price for item in train]
        self.test_price = [item.price for item in test]    
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            max_df=MAX_DF, # present in no more then 80% of docs
            min_df=MIN_DF, # present at least 5 docs
            ngram_range=NGRAM_RANGE,
            stop_words= 'english'
        )
        
    def get_description(self, doc: str) -> str:
        """
        Scrubs car prompt.
        Args:
            doc (str): prompt from Item class

        Returns:
            str: clean description
        """
        doc = doc.replace('How much does this cost to the nearest dollar?','')
        doc = doc.split("\n\nPrice is $")[0]
        doc = re.sub(r"\b\w+(?:_\w+){2,}\b", "", doc) # remove category
        doc = doc.strip()
        return doc
    
    def get_vectors_and_features(self, docs, test=None):
        if test:
            tfidf_vectors = self.vectorizer.transform(docs)
        else:
            tfidf_vectors = self.vectorizer.fit_transform(docs)
        feature_names = self.vectorizer.get_feature_names_out()
        return tfidf_vectors, feature_names
    
    def get_key_words(self) -> List[str]:
        tfidf_vectors, feature_names = self.get_vectors_and_features(self.train_desc)
        dense = tfidf_vectors.todense()
        denselist = dense.tolist()

        all_keywords = []

        for description in denselist:
            x = 0
            keywords = []
            for word in description:
                if word > 0:
                    keywords.append(feature_names[x])
                x += 1
            all_keywords.append(keywords)
            
        return all_keywords

    def get_features_and_targets(self):
        # get vectors, fit and transform train set
        tfidf_vectors_train = self.get_vectors_and_features(self.train_desc)[0]
        X_train = np.array([vector.toarray() for vector in tfidf_vectors_train])
        X_train = np.squeeze(X_train)
        # get vectors, transform test set
        tfidf_vectors_test = self.get_vectors_and_features(self.test_desc, test=True)[0]
        X_test = np.array([vector.toarray() for vector in tfidf_vectors_test])
        X_test = np.squeeze(X_test)
        # assign price as target
        y_train = self.train_price
        y_test = self.test_price
        return X_train, X_test, y_train, y_test
    
    def fit_model(self, X_train, y_train):
        # Create and train the Random Forest Regression model
        rf_regressor = RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=SEED) 
        rf_regressor.fit(X_train, y_train)
        return rf_regressor
    
    
    # add tf-idf vector to test item objects to run in test harness
    def add_vector(self, vectors):
        for item, row in zip(self.test, vectors):
            item.vector = row
    
    def get_feature_importances(self, model: RandomForestRegressor, n_features: int=N_FEATURES) -> None:        
        feature_importances = model.feature_importances_
        indices = np.argsort(feature_importances)[::-1]
        feature_names = self.get_vectors_and_features(self.train_desc)[1]
        # Print features in order of importance
        print("\nFeatures sorted by importance:")
        for i in indices[:n_features]:
            print(f"{feature_names[i]}: {feature_importances[i]}")
    
        