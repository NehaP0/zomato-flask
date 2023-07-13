from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

menu = []

@app.route('/')
def home():
    return "Welcome to Zesty Zomato!"


@app.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    if request.method == 'POST':
        # Get form inputs
        dish_id = request.form.get('dish_id')
        dish_name = request.form.get('dish_name')
        price = request.form.get('price')
        availability = request.form.get('availability')

        # Create a dictionary for the new dish
        dish = {
            'id': dish_id,
            'name': dish_name,
            'price': float(price),
            'availability': availability == 'yes'
        }

        # Add the new dish to the menu
        menu.append(dish)

        return redirect(url_for('manage_menu'))

    return render_template('menu.html', menu=menu)



@app.route('/order', methods=['GET', 'POST'])
def manage_orders():
    if request.method == 'POST':
        # Get form inputs
        customer_name = request.form.get('customer_name')
        dish_ids = request.form.getlist('dish_ids')

        # Check if all dishes are available
        available_dishes = []
        unavailable_dishes = []
        for dish_id in dish_ids:
            dish = next((item for item in menu if item['id'] == dish_id), None)
            if dish and dish['availability']:
                available_dishes.append(dish)
            else:
                unavailable_dishes.append(dish_id)

        if unavailable_dishes:
            return render_template('order.html', menu=menu, error=f"Dish IDs {', '.join(unavailable_dishes)} are unavailable.")

        # Process the order
        order_id = len(menu) + 1  # Placeholder for the order ID

        # Create a dictionary for the order
        order = {
            'id': order_id,
            'customer_name': customer_name,
            'dishes': available_dishes,
            'status': 'received'
        }

        # Add the order to the menu
        menu.append(order)

        return redirect(url_for('manage_orders'))

    return render_template('order.html', menu=menu)




@app.route('/order/<int:order_id>/update', methods=['GET','POST'])
def update_order_status(order_id):
    status = request.form.get('status')

    order = next((item for item in menu if isinstance(item, dict) and item['id'] == order_id), None)

    if not order:
        return "Order not found."

    order['status'] = status

    return redirect(url_for('manage_orders'))



if __name__ == '__main__':
    app.run(debug=True)
