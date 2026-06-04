import os
import pandas as pd
from sklearn.metrics  import mean_squared_error, mean_absolute_error, r2_score
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn
import numpy as np
import joblib
from mlproject.entity.config_entity import ModelEvaluationConfig 
from mlproject.constants import *
from mlproject.utils.common import read_yaml, create_directories, save_json
from pathlib import Path

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, predict):
        rmse = np.sqrt(mean_squared_error(actual, predict))
        mae = mean_absolute_error(actual, predict)
        r2 = r2_score(actual,predict)
        return rmse, mae, r2


    def log_into_mlflow(self):

        mlflow.set_tracking_uri(self.config.mlflow_uri) # Ensure this points to the .mlflow link
        os.environ['MLFLOW_TRACKING_USERNAME'] = "Manthan007"
        os.environ['MLFLOW_TRACKING_PASSWORD'] = "855107a7af7c57466b2c556a7c556df337a2bd2e"

        test_data = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)

        X_test = test_data.drop([self.config.target_column], axis=1)
        y_test = test_data[[self.config.target_column]]


        mlflow.set_registry_uri(self.config.mlflow_uri)
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme


        with mlflow.start_run():

            predicted_qualities = model.predict(X_test)

            (rmse, mae, r2) = self.eval_metrics(y_test, predicted_qualities)
            
            # Saving metrics as local
            scores = {"rmse": rmse, "mae": mae, "r2": r2}
            save_json(path=Path(self.config.metric_file_name), data=scores)

            mlflow.log_params(self.config.all_params)

            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("mae", mae)


            # Model registry does not work with file store
            if tracking_url_type_store != "file":

                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(model, "model")
            else:
                mlflow.sklearn.log_model(model, "model")
    