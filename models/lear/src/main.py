import pandas as pd
from enfobench import AuthorInfo, ForecasterType, ModelInfo
from enfobench.evaluation.server import server_factory
from enfobench.evaluation.utils import create_forecast_index
from datetime import datetime, timedelta
from epftoolbox.models import LEAR

class PeriodicallyRecalibratedLearModel:

    def info(self) -> ModelInfo:
        return ModelInfo(
            name="PeriodicallyRecalibratedLearModel",
            authors=[AuthorInfo(name="Margarida Mascarenhas", email="margarida.mascarenhas@kuleuven.be")],
            type=ForecasterType.quantile,
            params={},
        )

    def __init__(self, recalibration_period: str):
        self.recalibration_period = pd.Timedelta(recalibration_period)
        self.last_recalibrated: pd.Timestamp = pd.Timestamp(0)  # Never recalibrated
        self.model = None

    def forecast(
        self,
        horizon: int,
        history: pd.DataFrame,
        past_covariates: pd.DataFrame | None = None,
        future_covariates: pd.DataFrame | None = None,
        metadata: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        # Create index for prediction
        original_forecast_index = create_forecast_index(history, horizon)
        hourly_forecast_index = pd.date_range(
            start=original_forecast_index[0],
            end=original_forecast_index[-1],
            freq='1h',
        )
        Feat_selection = True
        steps = len(hourly_forecast_index)

        # Resample the history to hourly frequency
        resampled_history = history.resample('1h').mean()
        if resampled_history.isna().any().any():
            resampled_history.interpolate(method='linear', inplace=True)

        common_columns = past_covariates.columns.intersection(future_covariates.columns)
        past_covariates = past_covariates[common_columns]
        merged_df = pd.merge(resampled_history, past_covariates, left_index=True, right_index=True, how='outer')
        # Merge the future covariates
        if future_covariates is not None:
            merged_df = pd.concat(
                [merged_df, future_covariates.drop(columns=['cutoff_date'])], axis=0  # don't need the cutoff dates
            )

        calibration_window = (hourly_forecast_index[0].date()-pd.Timedelta(weeks=2) - history.first_valid_index().date()).days
        
        n_exogenous_inputs = len(merged_df.columns) - 1
        n_features = 96 + 8 + n_exogenous_inputs * 72

        if calibration_window < n_features+1:
            Feat_selection = False

        train=False
        current_time = history.index[-1]# Last index of history for example
        if current_time - self.last_recalibrated > self.recalibration_period:
            self.model = LEAR(calibration_window=calibration_window)
            train=True
            self.last_recalibrated = current_time 

        # Forecast using the model
        y_pred = self.model.predict_with_horizon(
            df=merged_df,
            hourly_forecast_index=hourly_forecast_index,
            forecast_horizon_steps=steps,
            Feat_selection=Feat_selection,
            train=train
        )

        #model = LEAR(calibration_window=calibration_window)

        # Create the prediction DataFrame by resampling the forecast to the original frequency
        original_freq = metadata['freq']
        new_index = pd.date_range(
        start=hourly_forecast_index.min(),
        end=hourly_forecast_index.max() + pd.Timedelta(hours=1) - pd.Timedelta(original_freq.replace('T', 'min')),
        freq=original_freq.replace('T', 'min')
        )
        forecast = (
            pd.DataFrame({'timestamp': hourly_forecast_index, 'yhat': y_pred})
            .set_index('timestamp')
            .reindex(new_index)
            .interpolate(method="linear")
            .loc[original_forecast_index]
        )
        return forecast

# Instantiate your model
model = PeriodicallyRecalibratedLearModel(recalibration_period= '7D')

# Create a forecast server by passing in your model
app = server_factory(model)

# Run the server if this script is the main one being executed
if __name__ == "__main__":
    app.run()
