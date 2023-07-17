from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/zesty_zomato'
mongo = PyMongo(app)

# Route for managing the menu
@app.route('/', methods=['GET', 'POST'])
def manage_menu():
    if request.method == 'POST':
        # Get form inputs
        dish_id = request.form.get('dish_id')
        dish_name = request.form.get('dish_name')
        price = request.form.get('price')
        availability = request.form.get('availability')

        # Validate inputs
        if not dish_id or not dish_name or not price or not availability:
            return render_template('menu.html', menu=mongo.db.menu.find(), error='Please fill in all the fields.')

        # Create a dictionary for the new dish
        dish = {
            'id': dish_id,
            'name': dish_name,
            'price': float(price),
            'availability': availability == 'yes',
            'ratings': []
        }

        # Add the new dish to the menu
        mongo.db.menu.insert_one(dish)

        return redirect(url_for('manage_menu'))

    return render_template('menu.html', menu=mongo.db.menu.find(), error=None)


# Route for removing a dish from the menu
@app.route('/menu/remove/<dish_id>', methods=['POST'])
def remove_dish(dish_id):
    mongo.db.menu.delete_one({'id': dish_id})
    return redirect(url_for('manage_menu'))

# Route for updating a dish in the menu
@app.route('/menu/update/<dish_id>', methods=['GET', 'POST'])
def update_dish(dish_id):
    dish = mongo.db.menu.find_one({'id': dish_id})

    if not dish:
        return "Dish not found."

    if request.method == 'POST':
        # Get form inputs
        dish_name = request.form.get('dish_name')
        price = request.form.get('price')
        availability = request.form.get('availability')

        # Validate inputs
        if not dish_name or not price or not availability:
            return render_template('update_dish.html', dish=dish, error='Please fill in all the fields.')

        # Update the dish details
        dish['name'] = dish_name
        dish['price'] = float(price)
        dish['availability'] = availability == 'yes'

        # Update the dish in the database
        mongo.db.menu.update_one({'id': dish_id}, {'$set': dish})

        return redirect(url_for('manage_menu'))

    return render_template('update_dish.html', dish=dish, error=None)

# Route for taking orders
@app.route('/order', methods=['GET', 'POST'])
def manage_orders():
    if request.method == 'POST':
        # Get form inputs
        customer_name = request.form.get('customer_name')
        dish_ids = request.form.get('dish_ids')

        # Validate inputs
        if not customer_name or not dish_ids:
            return render_template('order.html', menu=mongo.db.menu.find(), error='Please fill in all the fields.')

        # Split dish IDs into a list
        dish_ids = [dish_id.strip() for dish_id in dish_ids.split(',')]

        # Check if all dishes are available
        available_dishes = []
        unavailable_dishes = []
        for dish_id in dish_ids:
            dish = mongo.db.menu.find_one({'id': dish_id})
            if dish and dish['availability']:
                available_dishes.append(dish)
            else:
                unavailable_dishes.append(dish_id)

        if unavailable_dishes:
            error_message = f"Dish IDs {', '.join(unavailable_dishes)} are unavailable."
            return render_template('order.html', menu=mongo.db.menu.find(), error=error_message)

        # Process the order
        order_id = str(mongo.db.orders.count_documents({}) + 1)  # Generate a unique order ID

        # Create a dictionary for the order
        order = {
            'id': order_id,
            'customer_name': customer_name,
            'dishes': available_dishes,
            'status': 'received'
        }

        # Add the order to the orders collection
        mongo.db.orders.insert_one(order)

        return redirect(url_for('provide_feedback', order_id=order_id))

    return render_template('order.html', menu=mongo.db.menu.find(), error=None)

# Route for providing feedback for an order
@app.route('/order/<order_id>/feedback', methods=['GET', 'POST'])
def provide_feedback(order_id):
    order = mongo.db.orders.find_one({'id': order_id})

    if not order:
        return "Order not found."

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        review = request.form.get('review')

        # Validate inputs
        if not rating or not review:
            return render_template('feedback.html', order=order, error='Please provide both rating and review.')

        # Update the dish's ratings in the menu collection
        for dish in order['dishes']:
            dish_id = dish['id']
            menu_dish = mongo.db.menu.find_one({'id': dish_id})
            menu_dish['ratings'].append({'order_id': order_id, 'rating': rating, 'review': review})
            mongo.db.menu.update_one({'id': dish_id}, {'$set': menu_dish})

        return redirect(url_for('manage_menu'))

    return render_template('feedback.html', order=order, error=None)

if __name__ == '__main__':
    app.run(debug=True)
