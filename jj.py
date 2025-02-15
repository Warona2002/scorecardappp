from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

# Encoding functions (same as before)
def encode_education_level(level):
    mapping = {
        "not_selected": 0,
        'no_Matric': 47.2985712,
        'certificate': 47.2985712,
        'matric': -9.7765383,
        'diploma': 46.1489145,
        'bachelor_degree': 46.1489145,
        'honors': 46.1489145,
        'master_degree': 46.1489145,
        'doctorate': 46.1489145,
        'scholar': 46.1489145
    }
    return mapping.get(level, 0)

def encode_employment_sector(sector):
    mapping = {
        "not_selected": 0,
        'primarysec': 0.66621704,
        'financialsec': -30.62562262,
        'service&trade': -21.44300162,
        'publicsector&gov': -8.39504661,
        'Manufacturing': 29.00971087
    }
    return mapping.get(sector, 0)

def encode_secured_loan(secured_loan):
    return 30.65169099 if secured_loan == "yes" else 0 if secured_loan != "not_selected" else 0

def encode_unsecured_loan(unsecured_loan):
    return -12.35633917 if unsecured_loan == "yes" else 0 if unsecured_loan != "not_selected" else 0

def calculate_credit_score(customer_data):
    if any(val is None for val in customer_data[:10]):  # Check first 10 values (numeric ones)
        return None, "Missing required numeric values."

def calculate_credit_score(customer_data):
    try:
        mean = np.array([32.65045, 21.56048, 36.38829, 3228.468, 1778.43, 9825.076, 0.50039, 4.904003, 1.123527, 4269.451])
        std_dev = np.array([28.76983, 20.1968, 8.041285, 47365.58, 17395.5, 17115.58, 0.334145, 6.57808, 1.52261, 60517.556])
        model_points = np.array([18.81217545, -50.68923262, 3.99596907, 12.15660839, 9.67186972, 0.08246172, -11.46435919, 8.33872061, -33.3210361, -1.35485186])

        if len(customer_data) != 14:
            return None, "Invalid input length. Expected 14 values."
    
     # Convert numeric values to correct types immediately
        customer_data_numeric = [float(x) if isinstance(x, (int, float)) else 0.0 for x in customer_data[:10]] # Handles int, float, or string numbers
        num_payments, delinquencies, age_onboarding, chk_balances, avg_savings, salary, dsr, job_years, delinquency_rate, salary_to_dsr = customer_data_numeric


       # Extract and convert numeric variables, handling None values
        num_payments = customer_data[0] if customer_data[0] is not None else 0
        delinquencies = customer_data[1] if customer_data[1] is not None else 0
        age_onboarding = customer_data[2] if customer_data[2] is not None else 0
        chk_balances = customer_data[3] if customer_data[3] is not None else 0
        avg_savings = customer_data[4] if customer_data[4] is not None else 0
        salary = customer_data[5] if customer_data[5] is not None else 0
        dsr = customer_data[6] if customer_data[6] is not None else 0
        job_years = customer_data[7] if customer_data[7] is not None else 0
        delinquency_rate = customer_data[8] if customer_data[8] is not None else 0
        salary_to_dsr = customer_data[9] if customer_data[9] is not None else 0

        # Extract categorical variables (as STRINGS from the frontend)
        education_level = customer_data[10]
        employment_sector = customer_data[11]
        secured_loan = customer_data[12]
        unsecured_loan = customer_data[13]

        # Encode the categorical variables (NOW that we have the strings)
        encoded_level = encode_education_level(education_level)
        encoded_sector = encode_employment_sector(employment_sector)
        encoded_secured_loan = encode_secured_loan(secured_loan)
        encoded_unsecured_loan = encode_unsecured_loan(unsecured_loan)

        # Calculate salary_to_dsr, handling division by zero
        salary_to_dsr = salary * dsr if dsr != 0 else 0  # Or choose a different strategy


        # Standardize continuous variables (prevent division by zero)
        customer_data_values = np.array([
            num_payments, delinquencies, age_onboarding, chk_balances, avg_savings, salary, dsr, job_years, delinquency_rate, salary_to_dsr
        ])
        std_dev[std_dev == 0] = 1  # Important: Handle potential division by zero
        standardized_values = (customer_data_values - mean) / std_dev

        # Apply model points to standardized values
        continuous_variable_points = model_points * standardized_values

        # Final credit score calculation
        credit_score = np.sum(continuous_variable_points) + 600 + encoded_sector + encoded_secured_loan + encoded_unsecured_loan + encoded_level

        return credit_score, None

    except Exception as e:
        return None, str(e)
    
def determine_risk_band_and_decision(credit_score):
    if credit_score <= 500:
        return "500 and Below", "Decline"
    elif 500 < credit_score <= 550:
        return ">500 to 550", "Decline"
    elif 550 < credit_score <= 600:
        return ">550 to 600", "Decline"
    elif 600 < credit_score <= 650:
        return ">600 to 650", "Further Assessment"
    elif 650 < credit_score <= 700:
        return ">650 to 700", "Approve"
    else:
        return "Above 700", "Approve"    

@app.route('/calculate-credit-score', methods=['POST'])
def calculate_credit_score_route():
    try:
        data = request.get_json()
        print("Received data:", data)

        if 'customer_data' not in data:
            return jsonify({'error': 'Missing customer_data field'}), 400

        customer_data = data['customer_data']
        credit_score, error = calculate_credit_score(customer_data)

        if error:
            return jsonify({'error': error}), 400
        
        risk_band, decision = determine_risk_band_and_decision(credit_score)

        print("Calculated Credit Score:", credit_score) # helpful for debugging
        return jsonify({
            'credit_score': credit_score,
            'risk_band': risk_band,
            'decision': decision
        })


    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)