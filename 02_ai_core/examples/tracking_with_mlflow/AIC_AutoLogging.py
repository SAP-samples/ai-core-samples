import mlflow
import datetime
from sapai import tracking
import os

class TrackingContext(object):
    """
    The TrackingContext class can be used as a context manager,
    a minimal example:

    > import mlflow 
    > from sklearn.linear_model import LinearRegression 
    > from AIC_Autologging import TrackingContext 
    >
    > X = np.array([[1,1],[1,2],[3,3], [5,4]) 
    > Y = np.dot(X, np.array([1,2]))+2 
    > model = LinearRegression() 
    >
    > mlflow.sklearn.autolog() 
    > with TrackingContext(): 
    >    model.fit(X,y) 


    When executed on AI Core, the tracked metrics from mlflow are passed to
    the SAP AI Tracking SDK and are visualized in AI Launchpad.

    """

    def __init__(self, experiment_name="experiment"):
        self.ON_AIC = 'AICORE_EXECUTION_ID' in os.environ
        print("AICORE_EXECUTION_ID", self.ON_AIC)
        self.experiment_name = experiment_name
        try:
            self.experiment_id = mlflow.create_experiment(self.experiment_name)
        except:
            current_experiment = dict(mlflow.get_experiment_by_name(self.experiment_name))
            self.experiment_id = current_experiment['experiment_id']

        cwd = os.getcwd()
        mlflow.set_tracking_uri(f"file:{cwd}/mlruns")
        self.context = mlflow.start_run()
    
    def fetch_logged_data(self, run_id, labels):
        client = mlflow.tracking.MlflowClient()
        data = client.get_run(run_id).data
        metrics = []
        for k in data.metrics.keys():
            for m in client.get_metric_history(run_id, k):
                date = datetime.datetime.fromtimestamp(m.timestamp/1000.).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                metrics.append([{'name': m.key, 'value':m.value,
                    'timestamp': date, 'step': m.step,'labels':labels}])
        return metrics
        
    def __enter__(self):
        self.context.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.context.__exit__(type, value, traceback)
        labels = [{'name':'experiment_name', 'value':self.experiment_name},
                {'name':'experiment_id', 'value':self.experiment_id},
                {'name':'run_id', 'value':self.context.info.run_id}]

        data = self.fetch_logged_data(self.context.info.run_id,labels)
        
        for el in data:
            print(el)
            if self.ON_AIC:
                tracking.log_metrics(el)