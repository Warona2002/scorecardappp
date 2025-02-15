document.addEventListener('DOMContentLoaded', function() {  // Ensure the DOM is fully loaded

    function calculateCreditScore() {
        const requiredFields = document.querySelectorAll('input[required], select[required]');
        let anyFieldEmpty = false;
        for (const field of requiredFields) {
            if (!field.value) {
                anyFieldEmpty = true;
                break;
            }
        }

        if (anyFieldEmpty) {
            document.getElementById('creditScoreResult').textContent = "0";
            document.getElementById('riskBandResult').textContent = ""; // Clear risk band
            document.getElementById('decisionResult').textContent = ""; // Clear decision
            document.getElementById('deliquencyrate').value = "0";
            document.getElementById('salaryToDsr').value = "0";

            return;
        }

        const numPayments = parseInt(document.getElementById('NumberofPayment').value);
        const delinquencies = parseInt(document.getElementById('deliquencies').value);
        const ageOnboarding = parseInt(document.getElementById('ageonboarding').value);
        const avgCurrentBalance = parseInt(document.getElementById('avgCurrentBalance').value);
        const avgSavings = parseInt(document.getElementById('avgSavings').value);
        const salary = parseInt(document.getElementById('salary').value);
        const dsr = parseFloat(document.getElementById('dsr').value);
        const jobYears = parseInt(document.getElementById('jobYears').value);

        const educationLevel = document.getElementById('educationLevel').value;
        const employmentSector = document.getElementById('employmentSector').value;
        const securedLoan = document.getElementById('securedLoan').value;
        const unsecuredLoan = document.getElementById('unsecuredLoan').value;

        const delinquencyRate = numPayments !== 0 ? delinquencies / (numPayments + 1) : 0;
        const salaryToDsr = salary * dsr;

        document.getElementById('deliquencyrate').value = delinquencyRate.toFixed(4);
        document.getElementById('salaryToDsr').value = salaryToDsr.toFixed(2);

        const customerData = [
            numPayments, delinquencies, ageOnboarding, avgCurrentBalance,
            avgSavings, salary, dsr, jobYears, delinquencyRate, salaryToDsr,
            educationLevel, employmentSector, securedLoan, unsecuredLoan
        ];

        console.log("Sending Data:", customerData);

        fetch('http://127.0.0.1:5000/calculate-credit-score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ customer_data: customerData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Backend Error:', data.error);
                document.getElementById('creditScoreResult').textContent = "Error: " + data.error;
                document.getElementById('riskBandResult').textContent = ""; // Clear risk band
                document.getElementById('decisionResult').textContent = ""; // Clear decision
            } else {
                document.getElementById('creditScoreResult').textContent = data.credit_score.toFixed(2);
                document.getElementById('riskBandResult').textContent = data.risk_band;
                document.getElementById('decisionResult').textContent = data.decision;

                const decisionElement = document.getElementById('decisionResult');
                decisionElement.classList.remove("red", "orange", "green");
                decisionElement.classList.add(data.color);
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            document.getElementById('creditScoreResult').textContent = "Error fetching data";
            document.getElementById('riskBandResult').textContent = ""; // Clear risk band
            document.getElementById('decisionResult').textContent = ""; // Clear decision
        });
    }

    // Attach the calculateCreditScore function to the button click
    const calculateButton = document.querySelector('button[type="button"]'); // Select the button
    if (calculateButton) { // Check if the button exists
        calculateButton.addEventListener('click', calculateCreditScore);
    } else {
        console.error("Calculate button not found!");
    }
});