from metaflow import FlowSpec, step, kubernetes, argo, Parameter
from AIC_AutoLogging import TrackingContext
import mlflow
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

class TrainFlow(FlowSpec):
    alpha = Parameter('alpha',help='Alpha',default=0.01)

    @kubernetes(image="docker.io/<repository>/image:0.0.1",secrets=['default-object-store-secret'])
    @argo(input_artifacts=[{"name": "housing","path": "/data/housing.csv"}])
    @step
    def start(self):
        print(self.alpha)
        mlflow.sklearn.autolog()
        housing = pd.read_csv('/data/housing.csv')

        X_train, X_test, y_train, y_test = train_test_split(housing.loc[:, housing.columns != 'Target'], housing['Target'])
        linreg = Ridge(alpha=self.alpha)
        with TrackingContext() as run:
            linreg.fit(X_train, y_train)

        self.next(self.end)

    @kubernetes(image="docker.io/<repository>/image:0.0.1", ",secrets=['default-object-store-secret'])
    @step
    def end(self):
        print('End of flow')