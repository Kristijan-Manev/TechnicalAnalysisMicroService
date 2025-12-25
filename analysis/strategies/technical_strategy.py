from analysis.strategies.base import AnalysisStrategy
import pandas as pd

class TechnicalAnalysisStrategy(AnalysisStrategy):
    """Strategy for performing technical analysis on a cryptocurrency"""
    def __init__(self, analyzer, logger):
        self.analyzer = analyzer
        self.logger = logger

    def analyze(self, crypto_id, time_frame='daily', historical_data=None):
        # --- Step 1: Validate incoming data ---
        if historical_data is None:
            self.logger.warning(f"No historical data received for {crypto_id}")
            return None

        df = pd.DataFrame(historical_data)
        self.logger.info(f"Executing technical analysis for {crypto_id} with {len(df)} rows ({time_frame} timeframe)")

        # --- Step 2: Check required columns ---
        required_cols = ['date', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                self.logger.error(f"Missing required column {col} for {crypto_id}")
                return None

        # --- Step 3: Clean data more gently ---
        # Instead of dropping everything, keep partial rows
        df = df[(df[['open', 'high', 'low', 'close']] != 0).any(axis=1)]
        df = df.dropna(subset=['close'])  # only drop if 'close' missing

        # --- Step 4: Skip strict 50-row limit ---
        if len(df) < 10:
            self.logger.warning(f"Only {len(df)} rows available for {crypto_id}, continuing anyway")

        # --- Step 5: Calculate indicators ---
        analysis_df = self.analyzer.calculate_indicators(df, time_frame)
        if analysis_df is None or analysis_df.empty:
            self.logger.error(f"Technical analysis failed for {crypto_id}")
            return None

        summary = self.analyzer.get_analysis_summary(analysis_df)

        return {
            'crypto_id': crypto_id,
            'time_frame': time_frame,
            'data_points': len(analysis_df),
            'analysis_data': analysis_df.to_dict('records')[-100:],  # last 100 points
            'summary': summary
        }