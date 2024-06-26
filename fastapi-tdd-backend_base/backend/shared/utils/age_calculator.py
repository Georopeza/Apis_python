from datetime import date, datetime

from dateutil.relativedelta import relativedelta


def calculate_age(birthdate: date) -> int:
    dob = birthdate
    today = date.today()
    age = relativedelta(today, dob)
    if age.years < 1:
        return 0
    return age.years


def calculate_age_string(birthdate: date) -> str:
    dob = birthdate
    today = date.today()
    age = relativedelta(today, dob)
    if age.years < 1:
        if age.months < 1:
            return f"{age.days} día(s)"
        return f"{age.months} mes(es)"
    return f"{age.years} año(s)"
