import azure.functions as func
import logging
from Pipeline.loader import load_data
from Pipeline.features import save_features

app = func.FunctionApp()

@app.schedule(
    schedule="0 0 6 * * *",
    arg_name="mytimer",
    run_on_startup=False,
    use_monitor=True
)
def daily_currency_pipeline(mytimer: func.TimerRequest) -> None:
    logging.info("Timer triggered - starting pipeline")

    try:
        load_data()
        logging.info("Raw data loaded")

        save_features()
        logging.info("Features computed and saved")

    except Exception as e:
        logging.exception(f"Pipeline failed: {e}")
        raise