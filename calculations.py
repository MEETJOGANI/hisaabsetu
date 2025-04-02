from datetime import datetime
import math

def calculate_number_of_days(start_date, end_date):
    """Calculate the number of days between two dates"""
    delta = end_date - start_date
    return max(1, delta.days + 1)  # Include both start and end days

def calculate_number_of_months(days):
    """Calculate the number of months from days"""
    return days / 30.0

def calculate_interest_amount(total_amount, interest_rate, number_of_days, year_type=365):
    """
    Calculate the interest amount
    Formula: Principal * Rate * (12/year_type) * days
    Default year type is 365 days.
    """
    return (total_amount * interest_rate * 12 / year_type * number_of_days)

def calculate_dalali_amount(total_amount, dalali_rate, number_of_days, year_type=365):
    """
    Calculate the dalali (brokerage) amount
    Formula: Principal * Rate * (12/year_type) * days
    Default year type is 365 days.
    """
    return (total_amount * dalali_rate * 12 / year_type * number_of_days)

def calculate_lenaar_return_amount(total_amount, interest_amount):
    """Calculate the amount to be returned by Lenaar Party"""
    return total_amount + interest_amount

def calculate_apnaar_received_amount(total_amount, interest_amount, dalali_amount):
    """Calculate the amount received by Apnaar Party"""
    return total_amount + interest_amount - dalali_amount

def calculate_interest_received_by_apnar(interest_amount, dalali_amount):
    """Calculate the interest received by Apnaar after dalali deduction"""
    return interest_amount - dalali_amount

def calculate_all(total_amount, interest_rate, dalali_rate, start_date, end_date, year_type=365):
    """
    Calculate all financial metrics at once
    Default year type is 365 days. Custom year type can be specified.
    """
    # Convert percentage rates to decimal
    interest_rate_decimal = interest_rate / 100
    dalali_rate_decimal = dalali_rate / 100
    
    # Calculate number of days
    number_of_days = calculate_number_of_days(start_date, end_date)
    
    # Calculate number of months
    number_of_months = calculate_number_of_months(number_of_days)
    
    # Calculate interest and dalali amounts
    interest_amount = calculate_interest_amount(
        total_amount, 
        interest_rate_decimal, 
        number_of_days, 
        year_type
    )
    
    dalali_amount = calculate_dalali_amount(
        total_amount, 
        dalali_rate_decimal, 
        number_of_days, 
        year_type
    )
    
    # Calculate other derived values
    lenaar_return_amount = calculate_lenaar_return_amount(total_amount, interest_amount)
    apnaar_received_amount = calculate_apnaar_received_amount(total_amount, interest_amount, dalali_amount)
    interest_received_by_apnar = calculate_interest_received_by_apnar(interest_amount, dalali_amount)
    
    # Return all calculated values
    return {
        'number_of_days': number_of_days,
        'number_of_months': number_of_months,
        'interest_amount': round(interest_amount, 2),
        'dalali_amount': round(dalali_amount, 2),
        'lenaar_return_amount': round(lenaar_return_amount, 2),
        'apnaar_received_amount': round(apnaar_received_amount, 2),
        'interest_received_by_apnar': round(interest_received_by_apnar, 2)
    }

def calculate_remaining_lenaar_return_amount(remaining_amount, pending_interest):
    """Calculate the amount to be returned by Lenaar Party for remaining amount"""
    return remaining_amount + pending_interest
