import os
import sys
import mlflow
import logging
import click
from src.utils import _transform_uri_to_path
from mlflow.tracking import MlflowClient


logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)


def _get_or_run(entrypoint, parameters, synchronous=True): #removed git commit and use_cache=True
    """
    Run the entrypoint with the given parameters.

    :param entrypoint: The entrypoint to run.
    :param parameters: The parameters to pass to the entrypoint.
    :param synchronous: Whether to run the entrypoint in a synchronous or asynchronous fashion.
    """
    logger.info("Launching new run for entrypoint={} and parameters={}".format(entrypoint, parameters))
    submitted_run = mlflow.run(".", entrypoint, parameters=parameters, synchronous = synchronous)
    succeeded = submitted_run.wait()
    return MlflowClient().get_run(submitted_run.run_id)

@click.command(help="Perform unique run of the code with provided params.")
@click.option("--config", default="files/template_config.yml")
@click.option("--train-data", default="files/training_data.yml")
@click.option("--validation-data", default="files/test_data.yml")
def  workflow(config,train_data,validation_data):
    with mlflow.start_run():
        mlflow.set_experiment("track_rasa")
        logger.info("Starting to train")
        train_model = _get_or_run("train", {"config":config, "training":train_data})
        logger.info("Training complete")
        model_uri = os.path.join(train_model.info.artifact_uri, "model")
        model_path = _transform_uri_to_path(model_uri)
        logger.info("Starting to test")
        test_model = _get_or_run("test", {"model_path": model_path, "validation": validation_data})
        logger.info("Testing complete")


if __name__ == "__main__":
    workflow()
