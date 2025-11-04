from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from markupsafe import Markup
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..utils import user_required, set_last_visited_page
from ..models import db, ShowcaseImage, Product, CartItem, Order, User, Sale, CardDetails, Payment, UserShippingInfo

# Create the blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def root():
    return redirect(url_for('user.login'))


@main_bp.route('/menu', methods=['GET'])
def menu():
    try:
        # Retrieve all images from the database
        images = ShowcaseImage.query.all()
        return render_template('menu.html', images=images)
    except Exception as e:
        flash(f"Error loading menu: {str(e)}", 'bg-red-300 text-red-700')
        return redirect(url_for("user.login"))


@main_bp.route('/products')
@user_required
def products():
    set_last_visited_page(request.path)  # Track last visited page
    try:
        products = Product.query.all()
        return render_template('products.html', products=products)
    except Exception as e:
        print(f'Error loading products: {str(e)}')
        flash('An error occurred while trying to fetch products.',
              'bg-red-300 text-red-700')
        return redirect(url_for('main.menu'))  # Redirect to a sensible default


@main_bp.route('/faq')
@user_required
def faq():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('faq.html')


@main_bp.route('/contact')
@user_required
def contact():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('contacts.html')


@main_bp.route('/orders')
@user_required
def orders():
    set_last_visited_page(request.path)  # Track last visited page
    try:
        orders = Order.query.filter_by(user_id=session['user_id']).all()

        orders_list = [{
            'order_id': o.order_id,
            'sale_id': o.sale_id,
            'product_name': o.product_name,
            'price': o.price,
            'category': o.category,
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        } for o in orders]

        return render_template('orders.html', orders=orders_list)
    except Exception as e:
        print(
            f'An error occurred while fetching orders: {str(e)}')
        flash(
            f'An error occurred while fetching orders: {str(e)}', 'bg-red-300 text-red-700')
        return redirect(url_for('main.menu'))


@main_bp.route('/cart', methods=['GET'])
@user_required
def get_cart():
    set_last_visited_page(request.path)  # Track last visited page
    try:
        cart_items = db.session.query(CartItem).filter(
            CartItem.user_id == session['user_id']).all()
        subtotal = 0
        cart_list = []
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                item_total = item.quantity * product.price
                subtotal += item_total  # Calculate subtotal
                cart_list.append({
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'price': product.price,
                    'quantity': item.quantity,
                    'image_url': product.image_url or '/static/default_image.png'  # Use default if no image
                })
        return render_template('cart.html', cart_items=cart_list, subtotal=subtotal)
    except Exception as e:
        print(f"Failed to load cart: {str(e)}")
        flash("Failed to load cart. Please try again later.",
              'bg-red-300 text-red-700')
        return redirect(url_for('main.menu'))


@main_bp.route('/updatecart', methods=['POST'])
@user_required
def update_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    try:
        cart_item = CartItem.query.filter_by(
            user_id=session['user_id'], product_id=product_id).first()
        if not cart_item:
            return jsonify({'message': 'Item not found in cart'}), 404
        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        db.session.commit()
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        subtotal = sum(Product.query.get(item.product_id).price *
                       item.quantity for item in cart_items)
        return jsonify({'message': 'Cart updated successfully', 'new_subtotal': subtotal}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update cart', 'error': str(e)}), 400


@main_bp.route('/addtocart', methods=['POST'])
@user_required
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        if product.stock < quantity:
            return jsonify({'message': f'Insufficient stock for {product.product_name}'}), 400

        existing_item = CartItem.query.filter_by(
            user_id=session['user_id'], product_id=product_id).first()
        if existing_item:
            if product.stock < existing_item.quantity + quantity:
                return jsonify({'message': f'Insufficient stock for {product.product_name}'}), 400
            existing_item.quantity += quantity
        else:
            new_cart_item = CartItem(
                user_id=session['user_id'], product_id=product_id, quantity=quantity)
            db.session.add(new_cart_item)
        db.session.commit()
        return jsonify({'message': 'Item added to cart'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add item to cart', 'error': str(e)}), 400


@main_bp.route('/checkout', methods=['POST'])
@user_required
def checkout():
    try:
        # Clear any previous card session details
        session.pop('payment_info', None)

        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400

        # Prompt user to provide card details and validate
        # Ensure this logic integrates with the add_card_details logic
        order_summary = {
            'cart_items': [
                {
                    'product_id': item.product_id,
                    'product_name': Product.query.get(item.product_id).product_name,
                    'quantity': item.quantity,
                    'price': Product.query.get(item.product_id).price
                } for item in cart_items
            ],
            'subtotal': sum(Product.query.get(item.product_id).price * item.quantity for item in cart_items)
        }
        return jsonify({'message': 'Checkout initialized. Please provide card details.', 'order_summary': order_summary}), 200
    except Exception as e:
        print(f"Error during checkout: {str(e)}")
        return jsonify({'message': 'Failed to initialize checkout', 'error': str(e)}), 500


@main_bp.route('/complete_order', methods=['POST'])
@user_required
def complete_order():
    try:
        data = request.get_json()
        # Payment ID is now passed from the frontend
        payment_id = data.get('payment_id')
        # Ensure required pieces of information are present
        if not payment_id:
            return jsonify({'message': 'Missing required information to complete the order'}), 400
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400
        # Loop through each item in the cart
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product.stock < item.quantity:
                return jsonify({'message': f'Insufficient stock for {product.product_name}'}), 400

            # Update stock in products
            product.stock -= item.quantity
            total_price = product.price * item.quantity

            # Create a new sale record
            new_sale = Sale(
                product_id=product.product_id,
                username=User.query.get(session['user_id']).username,
                product_name=product.product_name,
                quantity=item.quantity,
                total_price=total_price
            )
            db.session.add(new_sale)
            db.session.flush()  # Get sale_id for linking to the order

            # Create a new order record
            new_order = Order(
                user_id=session['user_id'],
                sale_id=new_sale.sale_id,
                product_name=product.product_name,
                price=total_price,
                category=product.category
            )
            db.session.add(new_order)

        # Clear the cart after processing
        CartItem.query.filter_by(user_id=session['user_id']).delete()
        # Commit the transaction
        db.session.commit()

        return jsonify({'message': 'Order completed successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error completing order: {str(e)}")
        return jsonify({'message': 'Failed to complete order', 'error': str(e)}), 500


@main_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').strip()
    products = Product.query.all()
    if query:
        filtered_products = [
            p for p in products if query.lower() in p.product_name.lower()]
        highlighted_products = []
        for product in filtered_products:
            highlighted_name = Markup(
                product.product_name.replace(query, f'<mark>{query}</mark>'))
            highlighted_products.append({
                'product_id': product.product_id,
                'product_name': highlighted_name,
                'price': product.price
            })
    else:
        highlighted_products = [{
            'product_id': p.product_id,
            'product_name': p.product_name,
            'price': p.price
        } for p in products]
    return render_template('search_results.html', products=highlighted_products, query=query)


@main_bp.route('/getproducts', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'product_id': p.product_id,
        'product_name': p.product_name,
        'price': p.price,
        'stock': p.stock,
        'category': p.category,
        'image_url': p.image_url
    } for p in products])


@main_bp.route('/getproduct/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'price': product.price,
            'stock': product.stock,
            'category': product.category,
            'image_url': product.image_url
        })
    else:
        return jsonify({'message': 'Product not found'}), 404


@main_bp.route('/process_payment', methods=['POST'])
@user_required
def process_payment():
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')

        if not payment_method:
            return jsonify({'message': 'Payment method is required'}), 400

        e_wallet_provider = None
        card_provider = None

        if payment_method == 'E-Wallet':
            e_wallet_provider = data.get('e_wallet_provider')
            if e_wallet_provider not in ['GCASH', 'MAYA']:
                return jsonify({'message': 'Invalid E-Wallet provider'}), 400

        elif payment_method == 'Card':
            card_provider = data.get('card_provider')
            if card_provider not in ['BDO', 'BPI', 'MetroBank']:
                return jsonify({'message': 'Invalid Card provider'}), 400

        # Calculate the total amount
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400

        total_amount = sum(
            Product.query.get(item.product_id).price * item.quantity
            for item in cart_items
        )

        # Create payment record
        payment = Payment(
            user_id=session['user_id'],
            amount=total_amount,
            payment_method=payment_method,
            e_wallet_provider=e_wallet_provider,
            card_provider=card_provider,
            transaction_id=f"TXN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{session['user_id']}",
            status='pending'
        )
        db.session.add(payment)
        db.session.flush()  # Flushing here will allow you to get the ID of the Payment

        # Store payment info in session for later use
        session['payment_info'] = {
            'payment_id': payment.payment_id,
            'amount': total_amount
        }

        db.session.commit()
        return jsonify({
            'message': 'Payment recorded successfully.',
            'payment_id': payment.payment_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to record payment', 'error': str(e)}), 500


@main_bp.route('/add_card_details', methods=['POST'])
@user_required
def add_card_details():
    data = request.get_json()

    # Validate incoming data
    card_number = data.get('card_number')
    card_holder_name = data.get('card_holder_name')
    expiration_date = data.get('expiration_date')
    cvv = data.get('cvv')

    if not all([card_number, card_holder_name, expiration_date, cvv]):
        return jsonify({'message': 'Missing required card details'}), 400

    # Create a new card detail entry
    new_card = CardDetails(
        user_id=session['user_id'],
        card_number=card_number,
        card_holder_name=card_holder_name,
        expiration_date=expiration_date,
        cvv=cvv
    )

    try:
        # Save the new card details to the database
        db.session.add(new_card)
        db.session.commit()
        return jsonify({'message': 'Card details submitted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error saving card details: {str(e)}")
        return jsonify({'message': f'Failed to save card details: {str(e)}'}), 500


@main_bp.route('/add_shipping_info', methods=['POST'])
@user_required
def add_shipping_info():
    data = request.get_json()
    print(f"Incoming shipping info data: {data}")

    # Extract information from the incoming request
    full_name = data.get('full_name')
    address_line1 = data.get('address_line1')
    address_line2 = data.get('address_line2', '')  # Optional
    city = data.get('city')
    province = data.get('province')  # Optional
    postal_code = data.get('postal_code')
    phone_number = data.get('phone_number')
    # Get the selected payment method
    payment_method = data.get('payment_method', 'Cash on Delivery')

    # Validate required fields
    if not all([full_name, address_line1, city, postal_code, phone_number]):
        return jsonify({'message': 'Missing required shipping information'}), 400

    try:
        # Create or link a payment record if it's not "Cash on Delivery"
        if payment_method != "Cash on Delivery":
            payment_info = session.get('payment_info')
            if not payment_info:
                return jsonify({'message': 'Payment information not found for processing order.'}), 400

            payment_id = payment_info['payment_id']
        else:
            # Handle case for "Cash on Delivery"
            payment = Payment(
                user_id=session['user_id'],
                amount=0.0,  # No upfront payment
                payment_method=payment_method,
                status='pending',
                transaction_id=f"COD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{session['user_id']}",
            )
            db.session.add(payment)
            db.session.flush()  # Get payment ID
            payment_id = payment.payment_id

        # Create a new shipping info record
        new_shipping_info = UserShippingInfo(
            user_id=session['user_id'],
            payment_id=payment_id,
            full_name=full_name,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            province=province,
            postal_code=postal_code,
            phone_number=phone_number
        )
        db.session.add(new_shipping_info)

        # Fetch the user's cart items
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400

        # Process each cart item for sales and orders
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product.stock < item.quantity:
                return jsonify({'message': f'Insufficient stock for {product.product_name}'}), 400

            # Update product stock
            product.stock -= item.quantity

            # Create a Sale record
            new_sale = Sale(
                product_id=product.product_id,
                username=User.query.get(session['user_id']).username,
                product_name=product.product_name,
                quantity=item.quantity,
                total_price=product.price * item.quantity
            )
            db.session.add(new_sale)
            db.session.flush()  # Get the sale ID

            # Create an Order record
            new_order = Order(
                user_id=session['user_id'],
                sale_id=new_sale.sale_id,
                product_name=product.product_name,
                price=new_sale.total_price,  # Connecting to sale total price
                category=product.category
            )
            db.session.add(new_order)

        # Clear the cart after processing
        CartItem.query.filter_by(user_id=session['user_id']).delete()

        # Commit the transaction
        db.session.commit()

        # Return success response
        return jsonify({'message': 'Order completed successfully!'}), 200

    except IntegrityError as e:
        db.session.rollback()
        print(f"Integrity error: {str(e)}")
        return jsonify({'message': 'An integrity error occurred while processing your order.'}), 500

    except Exception as e:
        db.session.rollback()
        print(f"Error saving shipping information: {str(e)}")
        return jsonify({'message': f"Failed to save shipping information: {str(e)}"}), 500


@main_bp.route('/get_saved_card', methods=['GET'])
@user_required
def get_saved_card():
    card = CardDetails.query.filter_by(user_id=session['user_id']).first()
    if card:
        return jsonify({
            # Return only the last 4 digits for security
            'card_number': card.card_number[-4:],
            'card_holder_name': card.card_holder_name,
            'expiration_date': card.expiration_date
        }), 200
    else:
        return jsonify({'message': 'No saved card found'}), 404
