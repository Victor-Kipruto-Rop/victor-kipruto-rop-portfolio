"""Salary cycle analysis for float demand signals."""
from datetime import datetime, timedelta

import pandas as pd

from logger import logger


class SalaryCycleAnalyzer:
    """Analyze salary cycle impacts on M-Pesa float demand."""

    # Common salary payment dates in Kenya
    SALARY_DATES = [25, 28]  # Monthly salary dates

    def __init__(self):
        """Initialize salary cycle analyzer."""
        self.salary_dates = self.SALARY_DATES

    def mark_salary_days(self, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Mark salary payment dates.

        Args:
            dates: DateTime index

        Returns:
            Series with salary day indicators
        """
        is_salary_day = pd.Series(False, index=dates)

        for date in dates:
            if date.day in self.salary_dates:
                is_salary_day[date] = True

        logger.info(f"Marked {is_salary_day.sum()} salary days")
        return is_salary_day

    def get_post_salary_period(
        self, dates: pd.DatetimeIndex, days_after: int = 7
    ) -> pd.Series:
        """
        Identify post-salary periods (high spending/cash withdrawal).

        Args:
            dates: DateTime index
            days_after: Days after salary to consider

        Returns:
            Series indicating post-salary period
        """
        is_post_salary = pd.Series(False, index=dates)

        for date in dates:
            # Check if within days_after following a salary date
            for salary_date in self.salary_dates:
                if date.day >= salary_date and date.day <= (
                    salary_date + days_after
                ):
                    if date.day <= 28 or salary_date <= date.day:
                        is_post_salary[date] = True

        logger.info(f"Identified {is_post_salary.sum()} post-salary days")
        return is_post_salary

    def get_pre_salary_period(
        self, dates: pd.DatetimeIndex, days_before: int = 3
    ) -> pd.Series:
        """
        Identify pre-salary periods (low float, high demand).

        Args:
            dates: DateTime index
            days_before: Days before salary to consider

        Returns:
            Series indicating pre-salary period
        """
        is_pre_salary = pd.Series(False, index=dates)

        for date in dates:
            # Days before salary date
            for salary_date in self.salary_dates:
                days_until_salary = (
                    salary_date - date.day
                    if salary_date > date.day
                    else (salary_date + 30) - date.day
                )
                if 0 < days_until_salary <= days_before:
                    is_pre_salary[date] = True

        logger.info(f"Identified {is_pre_salary.sum()} pre-salary days")
        return is_pre_salary

    def get_month_end_impact(self, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Get month-end financial stress indicator.

        Args:
            dates: DateTime index

        Returns:
            Series with month-end impact factors (0-1)
        """
        impact = pd.Series(0.0, index=dates)

        for i, date in enumerate(dates):
            # Days remaining in month
            days_in_month = pd.Timestamp(
                year=date.year, month=date.month, day=1
            ) + pd.DateOffset(months=1) - pd.Timestamp(
                year=date.year, month=date.month, day=1
            )
            days_remaining = (
                days_in_month.days - date.day + 1
            ) / days_in_month.days

            # Month-end stress increases as we approach end
            impact[i] = 1 - (days_remaining / 30)

        logger.info("Calculated month-end impact factors")
        return impact

    def get_school_fees_period(self, year: int) -> tuple[datetime, datetime]:
        """
        Get school fees payment periods in Kenya.

        Typical school fees periods:
        - Term 1: January-March
        - Term 2: May-August
        - Term 3: September-November

        Args:
            year: Year to analyze

        Returns:
            Tuple of (start_date, end_date) for main fees period
        """
        # Typically highest in May-June and September-October
        return (
            datetime(year, 5, 1),
            datetime(year, 6, 30),
        )

    def mark_school_fees_period(
        self, dates: pd.DatetimeIndex, year: int
    ) -> pd.Series:
        """
        Mark school fees payment periods.

        Args:
            dates: DateTime index
            year: Year to analyze

        Returns:
            Series with school fees indicators
        """
        is_school_fees = pd.Series(False, index=dates)
        start, end = self.get_school_fees_period(year)

        for i, date in enumerate(dates):
            if start <= date <= end:
                is_school_fees[i] = True

        logger.info(f"Marked {is_school_fees.sum()} school fees days")
        return is_school_fees

    def get_financial_calendar(
        self, dates: pd.DatetimeIndex
    ) -> pd.DataFrame:
        """
        Create comprehensive financial calendar features.

        Args:
            dates: DateTime index

        Returns:
            DataFrame with all financial calendar features
        """
        df = pd.DataFrame(index=dates)

        # Get year from dates
        year = dates[0].year

        df["is_salary_day"] = self.mark_salary_days(dates)
        df["post_salary_period"] = self.get_post_salary_period(dates)
        df["pre_salary_period"] = self.get_pre_salary_period(dates)
        df["month_end_impact"] = self.get_month_end_impact(dates)
        df["school_fees_period"] = self.mark_school_fees_period(dates, year)

        logger.info("Created financial calendar with salary features")
        return df
