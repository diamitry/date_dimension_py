
# Date Dimension in Python

This repo is inspired by [Eliott Johnson](https://github.com/elliott-with-the-longest-name-on-github) and his [Awesome Date Dimension in T-SQL](https://github.com/elliott-with-the-longest-name-on-github/awesome-date-dimension). Just like Eliott, I was looking for a way to generate a date dimension, and stumbled upon Eliott's one, which was perfect, except written in T-SQL. Took a stab to create one in Python.

## Overview
The script is divided into several sections, which are self-explanatory. Main function generate_date_dimension takes several True/False flags to generate columns. Sub ifs control execution of logical groups. Pandas are being used as a primary generator and data frame manipulator engine. US Holidays and specific holidays are being imported from standard libraries.

## Limitations
Since this script is based on Pandas, the date range limitation exist, roughtly from September 9, 1677 to April 11, 2262.

## Holidays
This is the most complex logic in the script. Some holidays are dynamic (e.g. last Monday of the month), and some are static (e.g. fall on the same date every year, like Pi Day). Adjust values in both of these sections to add/remove custom holidays.

## Burnups
Toggle to specify a flag to return 1 if the current date is equal or later than the date. Comes handy for the YTD/MTD charts.

## Fiscal Fields
Toggle and specify the start of the fiscal year to have custom fiscal quarters and years. Specify the fiscal_year_start_month to have a custom fiscal period start date. FiscalQuarter, FiscalYearMonth, and FiscalYeearWeek will calculate automatically.

## Keys
A variety of key columns can be specified to tie to the other columns in the data warehouse, such as Business Key, Surrogate Key, etc.

## Test script
Remove the docstring triple quotes and run the entire file to generate a .csv / .parquet sample.
