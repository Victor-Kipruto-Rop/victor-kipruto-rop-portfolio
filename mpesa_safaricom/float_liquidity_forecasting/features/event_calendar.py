"""Event calendar for significant events impacting float demand."""
from datetime import datetime

import pandas as pd

from ingestion.calendar_client import holidays_client
from logger import logger


class EventCalendar:
    """Manage events that impact M-Pesa float demand."""

    # Kenya-specific events and their impact factors (0-1)
    EVENTS = {
        "new_year": {"month": 1, "day": 1, "impact": 0.8},
        "labour_day": {"month": 5, "day": 1, "impact": 0.7},
        "independence_day": {"month": 12, "day": 12, "impact": 0.7},
        "christmas": {"month": 12, "day": 25, "impact": 0.9},
        "boxing_day": {"month": 12, "day": 26, "impact": 0.8},
    }

    # Shopping seasons
    SHOPPING_SEASONS = {
        "back_to_school": {"month": 8, "day": 1, "duration_days": 30},
        "festive_season": {"month": 11, "day": 1, "duration_days": 60},
        "post_christmas": {"month": 12, "day": 26, "duration_days": 10},
    }

    def __init__(self):
        """Initialize event calendar."""
        self.logger = logger

    def mark_holidays(self, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Mark public holidays.

        Args:
            dates: DateTime index

        Returns:
            Series with holiday indicators
        """
        is_holiday = pd.Series(False, index=dates)

        for i, date in enumerate(dates):
            if holidays_client.is_holiday(date):
                is_holiday[i] = True

        self.logger.info(f"Marked {is_holiday.sum()} holidays")
        return is_holiday

    def mark_special_events(
        self, dates: pd.DatetimeIndex
    ) -> tuple[pd.Series, dict]:
        """
        Mark special events and their impact factors.

        Args:
            dates: DateTime index

        Returns:
            Tuple of (Series with event indicators, dict with impacts)
        """
        is_event = pd.Series(False, index=dates)
        impact_factors = {}

        for event_name, event_info in self.EVENTS.items():
            for i, date in enumerate(dates):
                if (
                    date.month == event_info["month"]
                    and date.day == event_info["day"]
                ):
                    is_event[i] = True
                    impact_factors[event_name] = event_info["impact"]

        self.logger.info(f"Marked {is_event.sum()} special events")
        return is_event, impact_factors

    def mark_shopping_seasons(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Mark shopping seasons.

        Args:
            dates: DateTime index

        Returns:
            DataFrame with shopping season indicators
        """
        df = pd.DataFrame(index=dates)

        for season_name, season_info in self.SHOPPING_SEASONS.items():
            df[f"shopping_{season_name}"] = False

            for i, date in enumerate(dates):
                season_start = datetime(
                    date.year,
                    season_info["month"],
                    season_info["day"],
                )
                season_end = season_start + pd.Timedelta(
                    days=season_info["duration_days"]
                )

                if season_start <= date <= season_end:
                    df.loc[i, f"shopping_{season_name}"] = True

        self.logger.info("Marked shopping seasons")
        return df

    def mark_elections(self, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Mark election periods (Kenya elections every 5 years).

        Args:
            dates: DateTime index

        Returns:
            Series with election indicators
        """
        is_election = pd.Series(False, index=dates)

        # Kenya general elections
        election_years = {
            2022: (datetime(2022, 8, 1), datetime(2022, 8, 31)),
            2027: (datetime(2027, 8, 1), datetime(2027, 8, 31)),
        }

        for year, (start, end) in election_years.items():
            for i, date in enumerate(dates):
                if start <= date <= end:
                    is_election[i] = True

        self.logger.info(f"Marked {is_election.sum()} election days")
        return is_election

    def get_event_calendar(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Create comprehensive event calendar.

        Args:
            dates: DateTime index

        Returns:
            DataFrame with all event indicators
        """
        df = pd.DataFrame(index=dates)

        # Add all event types
        df["is_holiday"] = self.mark_holidays(dates)
        df["is_special_event"], _ = self.mark_special_events(dates)
        df["is_election"] = self.mark_elections(dates)

        # Add shopping seasons
        shopping = self.mark_shopping_seasons(dates)
        for col in shopping.columns:
            df[col] = shopping[col]

        self.logger.info(f"Created event calendar with {len(df.columns)} features")
        return df

    def get_event_impact(self, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Calculate overall event impact factor.

        Args:
            dates: DateTime index

        Returns:
            Series with impact factors (0-1, where 1 is maximum impact)
        """
        impact = pd.Series(0.0, index=dates)

        # Base impacts
        _, special_events = self.mark_special_events(dates)
        holidays = self.mark_holidays(dates)
        elections = self.mark_elections(dates)

        # Assign impact factors
        for i, date in enumerate(dates):
            if holidays[i]:
                impact[i] += 0.3
            if elections[i]:
                impact[i] += 0.4
            for event_name, event_impact in special_events.items():
                impact[i] += event_impact * 0.2

            # Shopping season boost
            impact[i] = min(impact[i], 1.0)  # Cap at 1.0

        self.logger.info("Calculated event impact factors")
        return impact
