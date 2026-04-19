from flask import Blueprint, render_template, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

faq_responses = {
    "hi": "Hello! How can I assist you today?",
    "how to sell crops": "Go to the 'My Crops' section and click 'Add Crop'.",
    "market price": "You can view current prices on the 'Marketplace' page.",
    "weather": "Check the Weather section for forecasts.",
    "predict crop": "Use the AI Crop Prediction tool under Services.",
    "bye": "Goodbye! Have a great day!"
}

def get_bot_response(user_input):
    user_input = user_input.lower().strip()
    return faq_responses.get(user_input, "Sorry, I didn't understand that. Please try asking something else.")

@chatbot_bp.route('/', methods=['GET', 'POST'], endpoint='home')
def chatbot():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            user_input = data.get('query', '')
            response = get_bot_response(user_input)
            return jsonify({'response': response})
        else:
            user_input = request.form.get('query', '')
            response = get_bot_response(user_input)
            return render_template('chatbot.html', response=response)
    return render_template('chatbot.html')





