"""Kenya public holidays calendar client."""
from datetime import datetime, timedelta
from typing import Optional

import requests

from config import settings
from logger import logger


class KenyaHolidaysClient:
    """Fetch Kenya public holidays."""

    def __init__(self):
        """Initialize holidays client."""
        self.base_url = settings.HOLIDAYS_API_URL
        self.country_code = settings.COUNTRY_CODE
        self.timeout = 10

    def get_holidays(
        self, year: int, month: Optional[int] = None
    ) -> list[dict]:
        """
        Fetch holidays for Kenya.

        Args:
            year: Calendar year
            month: Specific month (optional)

        Returns:
            List of holiday dictionaries
        """
        try:
            if month:
                url = (
                    f"{self.base_url}/PublicHolidays/{year}/{self.country_code}?"
                    f"type=public"
                )
            else:
                url = (
                    f"{self.base_url}/PublicHolidays/{year}/{self.country_code}?"
                    f"type=public"
                )

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            holidays = response.json()

            logger.info(
                f"Retrieved {len(holidays)} holidays for {self.country_code}/{year}"
            )
            return holidays
        except requests.RequestException as e:
            logger.error(f"Failed to fetch holidays: {e}")
            return []

    def is_holiday(self, date: datetime) -> bool:
        """
        Check if a date is a public holiday.

        Args:
            date: Date to check

        Returns:
            True if date is a holiday
        """
        holidays = self.get_holidays(date.year)
        holiday_dates = [
            datetime.strptime(h["date"], "%Y-%m-%d").date()
            for h in holidays
        ]
        return date.date() in holiday_dates

    def get_holiday_period(
        self, start_date: datetime, end_date: datetime
    ) -> list[datetime]:
        """
        Get all holidays in a date range.

        Args:
            start_date: Start of range
            end_date: End of range

        Returns:
            List of holiday dates
        """
        holidays_list = []
        for year in range(start_date.year, end_date.year + 1):
            holidays = self.get_holidays(year)
            for holiday in holidays:
                holiday_date = datetime.strptime(
                    holiday["date"], "%Y-%m-%d"
                )
                if start_date <= holiday_date <= end_date:
                    holidays_list.append(holiday_date)

        return sorted(holidays_list)

    def get_business_days(
        self, start_date: datetime, end_date: datetime
    ) -> int:
        """
        Calculate business days excluding weekends and holidays.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Number of business days
        """
        business_days = 0
        current = start_date
        holidays = self.get_holiday_period(start_date, end_date)
        holiday_dates = {h.date() for h in holidays}

        while current <= end_date:
            # Skip weekends (5=Saturday, 6=Sunday)
            if current.weekday() < 5:
                # Skip holidays
                if current.date() not in holiday_dates:
                    business_days += 1
            current += timedelta(days=1)

        return business_days


# Create global instance
holidays_client = KenyaHolidaysClient()
