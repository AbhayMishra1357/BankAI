from django.shortcuts import render

# Create your views here.

def home_view(request):
    return render(request, 'home.html')
def features(request):
    return render(request, 'features.html')
def Contact(request):
    return render(request, 'Contact.html')
def about(request):
    return render(request, 'about.html')
def bot_iframe(request):
    return render(request, 'bot.html')

# loan calculator
from django.shortcuts import render

def calculate_loan_repayment(amount, interest_rate_annual, tenure_years):
    principal = amount
    monthly_rate = (interest_rate_annual / 100) / 12  # Monthly interest rate
    total_months = tenure_years * 12  # Number of monthly installments

    # Calculate EMI
    if monthly_rate == 0:
        monthly_emi = principal / total_months
    else:
        monthly_emi = (principal * monthly_rate * (1 + monthly_rate) ** total_months) / \
                      ((1 + monthly_rate) ** total_months - 1)

    interest_paid = (monthly_emi * total_months) - principal
    total_payment = monthly_emi * total_months

    return {
        "monthly_emi": round(monthly_emi, 2),
        "principal": round(principal, 2),
        "interest_paid": round(interest_paid, 2),
        "total_payment": round(total_payment, 2),
    }

def loan_calculator_view(request):
    result = None

    if request.method == 'POST':
        loan_amount = float(request.POST.get('loan_amount'))
        interest_rate = float(request.POST.get('interest_rate'))
        loan_tenure = int(request.POST.get('loan_tenure'))

        result = calculate_loan_repayment(loan_amount, interest_rate, loan_tenure)

    return render(request, 'loan_calculator.html', {'result': result})


# SIP

from django.shortcuts import render

def calculate_sip_web(monthly_investment, investment_years, annual_rate=12):
    P = monthly_investment
    r = annual_rate / 100  # Convert percentage to decimal
    n = 12  # Compounding monthly
    t = investment_years

    # Total amount invested
    total_invested = P * n * t

    # Future Value (FV) calculation
    fv = P * (((1 + r / n) ** (n * t) - 1) / (r / n))

    # Profit earned
    profit = fv - total_invested

    return {
        "total_invested": round(total_invested, 2),
        "future_value": round(fv, 2),
        "profit": round(profit, 2),
    }

def sip_calculator_view_web(request):
    result = None

    if request.method == 'POST':
        monthly_investment = float(request.POST.get('monthly_investment'))
        investment_years = int(request.POST.get('investment_years'))
        annual_rate = float(request.POST.get('annual_rate'))

        result = calculate_sip_web(monthly_investment, investment_years, annual_rate)

    return render(request, 'sip_calculator.html', {'result': result})


#     mutual funds


import openai
import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import asyncio

# OpenAI API Key Setup
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# Load CSV Data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file_path = os.path.join(BASE_DIR, "bank_data.csv")

try:
    bank_data = pd.read_csv(csv_file_path)
    print("CSV loaded successfully! Columns:", bank_data.columns)
except FileNotFoundError:
    bank_data = None
    print("Error: CSV file not found.")

# OpenAI Recommendation Function (with response limit)
def get_mutual_fund_recommendations(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=75  # Approx. 300 characters
        )
        return response.choices[0].message.content.strip()[:300].split("\n")
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return ["Error fetching recommendations. Please try again later."]

# Mutual Fund Recommendation View
def mutual_fund_recommendation(request):
    recommendations = []
    scheme_details = []

    if request.method == "POST":
        goal = request.POST.get("goal")
        risk = request.POST.get("risk").lower()
        duration = int(request.POST.get("duration"))
        print(f"this is the value of the risk {risk}")
        # OpenAI Prompt
        prompt = f"Suggest mutual funds for '{goal}' with '{risk}' risk and {duration}-year duration."
        recommendations = get_mutual_fund_recommendations(prompt)

        if bank_data is not None:
            try:
                # Normalize column names
                bank_data.columns = [col.lower().strip() for col in bank_data.columns]
                risk_column = 'riskometer**'
                scheme_column = 'name of scheme'

                # Filter data
                filtered_schemes = bank_data[bank_data[risk_column].str.lower() == risk]

                # Select details based on duration
                if duration >= 10:
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs', 'returns for 5 yrs', 'returns for incep',
                        risk_column, 'scheme category'
                    ]].to_dict('records')
                elif duration >= 5:
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs', 'returns for 5 yrs',
                        risk_column, 'scheme category'
                    ]].to_dict('records')
                else:
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs',
                        risk_column, 'scheme category'
                    ]].to_dict('records')

            except KeyError as e:
                print(f"Error: Missing column '{e}'. Check the CSV structure.")

    return render(request, "mutual_fund_recommendation.html", {
        "recommendations": recommendations,
        "scheme_details": scheme_details
    })


# ============================================================================================================================================================

# bot

@csrf_exempt
def dialogflow_webhook(request):
    response_text=" "
    if request.method == 'POST':
        try:
            req = json.loads(request.body) 

            # Extract intent name
            intent_name = req.get('queryResult', {}).get('intent', {}).get('displayName')

            # Extract parameters
            parameters = req.get('queryResult', {}).get('parameters', {})

            print(f"Intent: {intent_name}, Parameters: {parameters}")
            scheme_details = []
            # Call the respective function based on the intent name
            if intent_name == "suggest_mutual_fund":
                scheme_details =  mutual_fund_recommendation_bot(parameters)
                #  response_text="this is the response ['1. Vanguard Education Savings Trust: This mutual fund is specifically designed for education savings. It focuses on low-risk investments and has a track record of good performance over time.', '', '2. T. Rowe Price College Savings Plan: This mutual fund offers a range of investment options with varying le']"
                print(f"this is the response {scheme_details}")
            # elif intent_name == "calculate_loan":
            #     response_text = loan_calculator(parameters)
            elif intent_name == "sip_calculator":
                response_text = handle_sip_calculator(parameters)
            
            elif intent_name == "loan_calculator":
                response_text = loan_emi_calculator(int(parameters.get("loan_amount")),int(parameters.get("loan_tenure")),float(parameters.get("loan_interest_rate")))
            # else:
            #     response_text = f"Unknown intent: {intent_name}"
            
            if intent_name=="suggest_mutual_fund":
                if not scheme_details:
                    return {
                        "fulfillmentText": "No mutual fund schemes were found for the specified criteria."
                    }
                
                response_text = "Here are the recommended mutual fund schemes based on your preferences:\n\n"
                # Start building the response
                response_messages = [{
                    "text": {
                        "text": ["Here are the recommended mutual fund schemes based on your preferences:"]
                    }
                }]

                for idx, scheme in enumerate(scheme_details, 1):
                    scheme_info = f"{idx}. *{scheme.get('name of scheme', 'N/A')}*\n" \
                                f"   - Category: {scheme.get('scheme category', 'N/A')}\n" \
                                f"   - Risk Level: {scheme.get('riskometer**', 'N/A')}\n" \
                                f"   - Returns (3 years): {scheme.get('returns for 3 yrs', 'N/A')}\n" \
                                f"   - Returns (5 years): {scheme.get('returns for 5 yrs', 'N/A')}\n"

                    # Add each scheme as a separate message
                    response_messages.append({
                        "text": {
                            "text": [scheme_info]
                        }
                    })

                # Return structured response
                return JsonResponse({
                    "fulfillmentMessages": response_messages,
                    "fulfillmentText": "Here are the recommended mutual fund schemes based on your preferences."
                })
            elif intent_name=="sip_calculator":
                return JsonResponse({
                    
                    "fulfillmentText": response_text
                })
            elif intent_name=="loan_calculator":
                return JsonResponse({
                    
                    "fulfillmentText": response_text
                })
                
    
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return JsonResponse({'fulfillmentText': "An error occurred while processing the request."})

    return JsonResponse({'fulfillmentText': "Invalid request method."})

# def dialogflow_webhook(request):  
#     if request.method == 'POST':
#         try:
#             req = json.loads(request.body)
#             # Extract intent name
#             intent_name = req.get('queryResult', {}).get('intent', {}).get('displayName')

#         # Extract parameters
#             parameters = req.get('queryResult', {}).get('parameters', {})
            
#             response_text = f"Received intent: {intent_name} with parameters: {parameters}"
#             print(f"Intent: {intent_name}, Parameters: {parameters}, Response: {response_text}")

#             # print(f" data is {intent_name} and {response_text}")
#             # return JsonResponse({'fulfillmentText': response_text})

#         except Exception as e:
#             print("r")

#         #     # return JsonResponse({'fulfillmentText': f"Error processing request: {str(e)}"})

#         # return JsonResponse({'fulfillmentText': "Invalid request method."})


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def mutual_fund_recommendation_bot(parameters):
    recommendations = []
    scheme_details = []
   # Extract risk profile with error handling
    risk = parameters.get('risk_profile', [None])
    risk = risk[0] if risk and isinstance(risk, list) else "Moderate"  # Default to "Moderate" if not found

    # Extract investment goal with a default value
    goal = parameters.get('investment_goal', [])
    goal = goal[0] if goal and isinstance(goal, list) else "General Investment"

    # Extract investment amount with error handling
    inv_amount = parameters.get('investment_amount', None)
    inv_amount = int(inv_amount) if inv_amount and inv_amount.isdigit() else 0  # Default to 0 if invalid

    # Extract investment duration safely
    investment_duration = parameters.get('investment_duration', [None])
    investment_duration = int(investment_duration[0]) if investment_duration else 1  # Default to 1 year if not valid

    scheme_details = []

    print("before the if risk inside the suggest_,utual_fnc")
    if risk:
     
        # OpenAI Prompt
        print("inside the if risk")
        prompt = f"Suggest mutual funds for '{goal}' with '{risk}' risk and {investment_duration}-year duration."
        # recommendations = await get_mutual_fund_recommendations(prompt)
    try:
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo-16k",
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=75  # Approx. 300 characters
        # )
        # recommendations= response.choices[0].message.content.strip()[:300].split("\n")
   
        if bank_data is not None:
            
                # Normalize column names
                bank_data.columns = [col.lower().strip() for col in bank_data.columns]
                risk_column = 'riskometer**'
                scheme_column = 'name of scheme'

                # Filter data
                filtered_schemes = bank_data[bank_data[risk_column].str.lower() == risk.lower()]
               
                # Select details based on duration
                if investment_duration >= 10:
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs', 'returns for 5 yrs', 'returns for incep',
                        risk_column, 'scheme category'
                    ]].to_dict('records')
                elif investment_duration >= 5:
                    print("inside the 5 ears")
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs', 'returns for 5 yrs', 
                        risk_column, 'scheme category'
                    ]].to_dict('records')
                   
                else:
                    scheme_details = filtered_schemes[[
                        scheme_column, 'returns for 3 yrs',
                        risk_column, 'scheme category'
                    ]].to_dict('records')

    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return ["Error fetching recommendations. Please try again later."]
           

      
    return scheme_details

    # return render(request, "mutual_fund_recommendation.html", {
    #     "recommendations": recommendations,
    #     "scheme_details": scheme_details
    # })


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




# def sip_calculator(monthly_investment, investment_years, annual_rate=0.12):
#     """
#     Calculate the future value of a SIP (Systematic Investment Plan).

#     Parameters:
#     - monthly_investment (float): Amount invested every month.
#     - investment_years (int): Number of years to invest.
#     - annual_rate (float): Annual rate of return. Default is 12% (0.12).

#     Returns:
#     - float: Future value of the investment.
#     """   
#     # Convert years to months
#     months = investment_years * 12

#     # Monthly rate of return
#     monthly_rate = 12

#     # Formula to calculate the future value of SIP
#     future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
#     print(f"this is future price of calculate sip {future_value}")

#     return round(future_value, 2)
def sip_calculator(monthly_investment,investment_years,annual_rate = 12):
    
    P = monthly_investment
    r = annual_rate / 100  # Convert percentage to decimal
    n = 12  # Compounding monthly
    t = investment_years

    # Total amount invested
    total_invested = P * n * t

    # Future Value (FV)
    fv = P * (((1 + r / n) ** (n * t) - 1) / (r / n))

    # Profit earned
    profit = fv - total_invested

    return f"The total amount invested : {total_invested} . Your Earnings :{profit} . The value of your SIP {total_invested+profit}"


from django.http import JsonResponse

def handle_sip_calculator(parameters):
    try:
        # Extracting parameters
        monthly_investment = float(parameters.get("sip_monthly_investment"))
        investment_years = int(parameters.get("sip_years"))
        print(monthly_investment)
        print(investment_years)
        # Calculate SIP Future Value
        future_value = sip_calculator(monthly_investment, investment_years,12)
        print(f"this is future price of handle sip {future_value}")
        response_text = (   
            f"With a monthly investment of ₹{monthly_investment} for {investment_years} years, "
            f"the future value of your SIP at an annual return of 12% will be approximately ₹{future_value}."
        )

    except Exception as e:
        print(f"Error calculating SIP: {str(e)}")
        response_text = "There was an issue calculating your SIP. Please check the input values and try again."

    return response_text
   

def loan_emi_calculator(loan_amount, annual_interest_rate, loan_tenure_years):
    P = loan_amount
    r = (annual_interest_rate / 100) / 12  # Monthly interest rate
    n = loan_tenure_years * 12  # Total number of monthly installments

    # EMI Calculation
    emi = (P * r * (1 + r) ** n) / ((1 + r) ** n - 1)

    # Total interest paid over the loan tenure
    total_interest = (emi * n) - P

    # Total amount paid (Principal + Interest)
    total_payment = emi * n

    result = (
        f"Loan EMI Calculation:\n"
        f"Monthly EMI: ₹{emi:.2f}\n"
        f"Principal Amount: ₹{P:.2f}\n"
        f"Total Interest Paid: ₹{total_interest:.2f}\n"
        f"Total Payment (Principal + Interest): ₹{total_payment:.2f}"
    )

    return result
    #return emi, P, total_interest, total_payment