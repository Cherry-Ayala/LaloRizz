from flask import Flask, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = Flask(__name__)

# Define your AI model and constants here
model_name = "gpt2"
model_path = model_name
model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Define investment portfolios CONSTANTS
# Definitions of risk - 1 Extremely Low, 2 - Low, 3 - Medium risk, 4 - Moderate Risk, 5 - High Risk
portfolios = [
    {'num': 1, "cardonaScore": 0.70166},
    {'num': 2, "cardonaScore": 5.35},  # 5.35 annual, extremely low risk,
    {'num': 3, "cardonaScore": -5.46},  # underperformed -10.92 annual at
    {'num': 4, "cardonaScore": 0.5675},  # 11.35 annual at 4 years, high risk
    {'num': 5, "cardonaScore": 0.94583}  # Random really haha 15.7 anual, medium risk, 4 years
]

# Define the portfolio names for each risk level
num_to_name = {
    1: "High Liquidity: NTECT F7",
    2: "Strong: NTEPZO1",
    3: "Dollars Liquidity: NTEDLS F5",
    4: "Mexican Stocks: NTEIPC F5",
    5: "International Sustainable Stock: NTEESG"
}

# Function to extract information from user input
def extract_information(input_text):
    # Split the input by commas to get the values
    values = input_text.split(',')

    # Check if there are exactly three values (amount, risk, time)
    if len(values) == 3:
        try:
            investmentAmount = float(values[0].strip())
            riskLevel = int(values[1].strip())
            timePeriod = int(values[2].strip())
            return investmentAmount, riskLevel, timePeriod
        except ValueError:
            pass
    return None, None, None

# Create a text-generation pipeline
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Function for your AI logic
def ai_investment_advisor(user_input):
    try:
        # Extract information from user input
        investmentAmount, riskLevel, timePeriod = extract_information(user_input)

        if not investmentAmount or not (1 <= riskLevel <= 5) or not timePeriod:
            return "Invalid input. Please provide the investment amount, risk level (1-5), and years separated by commas."

        # Generate a custom response from the GPT-2 model
        input_prompt = f"You want to invest {investmentAmount:.2f} dollars for {timePeriod} years with a risk level of {riskLevel}."
        custom_response = generator(input_prompt, max_length=50, do_sample=True)[0]['generated_text']

        # Cherry Multiplier H*R
        userCherryMult = riskLevel * timePeriod

        # Calculate user's Cardona Score based on the formula
        userCardonaScore = 0.1 * userCherryMult  # Asumiendo que el user quiere un return de 10 % anual Note to self: Preguntarle a Cherry si se  podría obtener también el retorno querido 

        # Calculate the absolute difference between user's Cardona Score and each portfolio's Cardona Score
        differences = [(abs(userCardonaScore - portfolio['cardonaScore']), portfolio) for portfolio in portfolios]

        # Find the portfolio with the closest Cardona Score
        closest_portfolio = min(differences, key=lambda x: x[0])[1]

        # Get the name of the closest portfolio
        closest_portfolio_name = num_to_name[closest_portfolio['num']]

        return f"Lalito says: {custom_response}\n\nInvestment Recommendations:\nBased on your Cardona Score, the closest portfolio is {closest_portfolio_name} - Portfolio {closest_portfolio['num']}."

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""

    if request.method == 'POST':
        user_input = request.form['input_text']
        if user_input.lower() in ['bye', 'exit']:
            output = "Bye"
        else:
            # Call the AI function to get the response
            output = ai_investment_advisor(user_input)

    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
