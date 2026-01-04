import os
import stripe
import json

# This is your test secret API key.
stripe.api_key = os.environ['STRIPE_SECRET_KEY']
STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]

from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify

load_dotenv()

app = Flask(__name__,
  static_url_path='',
  template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "views"),
  static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

# Just hardcoding amounts here to avoid using a database
PRODUCTS = {
    "1": {
        "title": "The Art of Doing Science and Engineering",
        "amount": 2300,
    },
    "2": {
        "title": "The Making of Prince of Persia",
        "amount": 2500,
    },
    "3": {
        "title": "Working in Public",
        "amount": 2800,
    },
}

# Home route
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

# Checkout route
@app.route('/checkout', methods=['GET'])
def checkout():
  item = request.args.get("item")
  product = PRODUCTS.get(item)
  error = None

  if not product:
     error = 'No item selected'

  return render_template('checkout.html', item_id=item, title=product["title"], amount=product["amount"], error=error, stripe_pk=STRIPE_PUBLISHABLE_KEY)

# Calculate order amount
def calculate_order_amount(items):
    # Recieve items: [{"id": "1"}, {"id": "2"}] ...
    total = 0
    for item in items:
        product = PRODUCTS.get(str(item["id"]))
        if not product:
            raise ValueError(f"Invalid item id: {item['id']}")
        total += product["amount"]
    return total

# Create payment intent route
@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount = calculate_order_amount(data['items']),
            currency = 'usd',
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
            automatic_payment_methods = {
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

# Complete route
@app.route('/complete', methods=['GET'])
def complete():
    return render_template('complete.html', stripe_pk=STRIPE_PUBLISHABLE_KEY)

if __name__ == '__main__':
  app.run(port=4242, host='0.0.0.0', debug=True)