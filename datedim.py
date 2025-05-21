import pandas as pd
from datetime import timedelta, date
from dateutil.easter import easter
import holidays

# -----------------------------
# Helper: Dynamic Company Holidays
# -----------------------------
# dynamic company holidays which are dynamic, i.e. last monday of the month, Easter, etc.
def get_dynamic_company_holidays(year_range):
    holiday_dict = {}
    for year in year_range:
        easter_sunday = easter(year)
        holiday_dict[(year, 5, last_weekday_of_month(year, 5, 0))] = "Memorial Day"
        holiday_dict[(year, 11, nth_weekday_of_month(year, 11, 3, 3) + 1)] = "Black Friday"
        holiday_dict[(year, easter_sunday.month, easter_sunday.day)] = "Easter"
    return holiday_dict

def last_weekday_of_month(year, month, weekday):
    last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    while last_day.weekday() != weekday:
        last_day -= timedelta(days=1)
    return last_day.day

def nth_weekday_of_month(year, month, weekday, n):
    count = 0
    for day in range(1, 32):
        try:
            d = date(year, month, day)
        except ValueError:
            break
        if d.weekday() == weekday:
            count += 1
            if count == n + 1:
                return day
    return None

# -----------------------------
# Main Function
# -----------------------------
def generate_date_dimension(
    start_date,
    end_date,
    fiscal_year_start_month=1,
    include_calendar_fields=True,
    include_offsets=True,
    include_holidays=True,
    include_dynamic_holidays=True,
    include_flags=True,
    include_burnups=True,
    include_fiscal_fields=True,
    include_datets=True,
    include_datebk=True,
    include_datesk=True,
    include_weekmonth_bounds=True,
    include_labels=True,
    company_holidays=None
):
    today = pd.Timestamp.today().normalize()
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({'TheDate': dates})
    df['DateKey'] = df['TheDate'].dt.strftime('%Y%m%d').astype(int)

    # -----------------------------
    # TS, BK, SK
    # -----------------------------
    if include_datets:
        df['DateTS'] = pd.to_datetime(df['TheDate'].dt.strftime('%Y-%m-%d 00:00:00'))

    if include_datebk:
        df['DateBK'] = df['TheDate'].dt.strftime('%Y%m%d')

    if include_datesk:
        df['DateSK'] = range(1, len(df) + 1)

    # -----------------------------
    # Calendar Fields
    # -----------------------------
    if include_calendar_fields:
        df['ISODateName'] = df['TheDate'].dt.strftime('%Y-%m-%d')
        df['AmericanDateName'] = df['TheDate'].dt.strftime('%m/%d/%Y')
        df['DayOfWeekName'] = df['TheDate'].dt.day_name()
        df['DayOfWeekAbbrev'] = df['DayOfWeekName'].str[:3]
        df['MonthName'] = df['TheDate'].dt.month_name()
        df['MonthAbbrev'] = df['MonthName'].str[:3]
        df['Year'] = df['TheDate'].dt.year
        df['Quarter'] = 'Q' + df['TheDate'].dt.quarter.astype(str)
        df['Month'] = df['TheDate'].dt.month
        df["Day"] = df['TheDate'].dt.day
        df['WeekNumber'] = 'W' + df['TheDate'].dt.isocalendar().week.astype(str)
        df['YearMonth'] = df['TheDate'].dt.strftime('%Y%m').astype(int)
        df['YearQuarter'] = (df['Year'].astype(str) + df['TheDate'].dt.quarter.astype(str)).astype(int)

    # -----------------------------
    # Offsets
    # -----------------------------
    if include_offsets:
        df['DayOffsetFromToday'] = (df['TheDate'] - today).dt.days
        df['MonthOffsetFromToday'] = ((df['Year'] - today.year) * 12 + df['Month'] - today.month).astype(int)
        df['QuarterOffsetFromToday'] = ((df['Year'] - today.year) * 4 + df['TheDate'].dt.quarter - today.quarter).astype(int)
        df['YearOffsetFromToday'] = df['Year'] - today.year

    # -----------------------------
    # Holidays
    # -----------------------------
    if include_holidays:
        us_holidays = holidays.US(years=range(df['Year'].min(), df['Year'].max() + 1))
        df['USPublicHolidayFlag'] = df['TheDate'].dt.date.isin(us_holidays)
        df['USPublicHolidayName'] = df['TheDate'].dt.date.map(us_holidays).fillna("")

        # specific company holidays which are not dynamic
        if company_holidays is None:
            company_holidays = {
                (y, m, d): name for y in range(df['Year'].min(), df['Year'].max() + 1)
                for (m, d), name in [
                    ((2, 14), "Valentine's Day"),
                    ((3, 14), "Pi Day"),
                    ((4, 22), "Earth Day"),
                    ((5, 4), "Star Wars Day"),
                    ((10, 31), "Halloween")
                ]
            }

        if include_dynamic_holidays:
            dyn = get_dynamic_company_holidays(range(df['Year'].min(), df['Year'].max() + 1))
            company_holidays.update(dyn)

        df['CompanyHolidayFlag'] = df['TheDate'].apply(lambda d: (d.year, d.month, d.day) in company_holidays)
        df['CompanyHolidayName'] = df['TheDate'].apply(lambda d: company_holidays.get((d.year, d.month, d.day), ''))

    # -----------------------------
    # Flags
    # -----------------------------
    if include_flags:
        df['TodayFlag'] = df['TheDate'] == today
        df['WeekdayFlag'] = df['TheDate'].dt.weekday < 5
        df['BusinessDayFlag'] = df['WeekdayFlag'] & (~df['CompanyHolidayFlag'].fillna(False))

    # -----------------------------
    # Burnups
    # -----------------------------
    if include_burnups:
        df['DayOfMonth'] = df['TheDate'].dt.day
        df['DayOfYear'] = df['TheDate'].dt.dayofyear
        df['DayOfWeekStartingMonday'] = df['TheDate'].dt.weekday + 1
        df['DayOfWeek'] = df['TheDate'].dt.dayofweek + 1
        df['DayOfQuarter'] = df['TheDate'].dt.dayofyear % 90  # rough estimate

        df['WeeklyBurnupStartingMonday'] = (df['DayOfWeekStartingMonday'] <= today.weekday() + 1).astype(int)
        df['WeeklyBurnup'] = (df['DayOfWeek'] <= today.weekday() + 1).astype(int)
        df['MonthlyBurnup'] = (df['DayOfMonth'] <= today.day).astype(int)
        df['QuarterlyBurnup'] = (df['DayOfQuarter'] <= (today.dayofyear % 90)).astype(int)
        df['YearlyBurnup'] = (df['DayOfYear'] <= today.dayofyear).astype(int)

    # -----------------------------
    # Relative Date Bounds
    # -----------------------------
    if include_weekmonth_bounds:
        df['WeekStart'] = df['TheDate'] - pd.to_timedelta(df['TheDate'].dt.weekday, unit='d')
        df['WeekEnd'] = df['WeekStart'] + pd.Timedelta(days=6)
        df['MonthStart'] = df['TheDate'].values.astype('datetime64[M]')
        df['MonthEnd'] = (df['MonthStart'] + pd.offsets.MonthEnd(0)).dt.normalize()

    # -----------------------------
    # Fiscal Fields
    # -----------------------------
    if include_fiscal_fields:
        fiscal_year_start = fiscal_year_start_month
        df['FiscalYear'] = df['TheDate'].apply(lambda x: x.year if x.month >= fiscal_year_start else x.year - 1)
        df['FiscalQuarter'] = 'Q' + (((df['TheDate'].dt.month - fiscal_year_start + 12) % 12) // 3 + 1).astype(str)

    return df
'''
# -----------------------------
# Test Script (remove triple quotes & run the entire script)
# -----------------------------
if __name__ == "__main__":
    df = generate_date_dimension(
        # must be >= then 1677-09-21
        start_date="2024-01-01",
        # must be <= then 2262-04-11
        end_date="2025-12-31",
        include_calendar_fields=True,
        include_offsets=False,
        include_holidays=True,
        include_dynamic_holidays=True,
        include_flags=True,
        include_burnups=False,
        include_fiscal_fields=False,
        include_datets=True,
        include_datebk=True,
        include_datesk=True,
        include_weekmonth_bounds=True,
        include_labels=True,
    )

    df.to_csv("date_dimension_sample.csv", index=False)
    # df.to_parquet("date_dimension_sample.parquet", index=False)
    print("✅ Exported to CSV and Parquet")
    print(df.head())
'''
