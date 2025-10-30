from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import extract, and_
from sqlalchemy.sql import func

from ..utils import admin_required, set_last_visited_page
from ..models import db, User, Sale, UserShippingInfo, CardDetails, Payment, Product, ShowcaseImage


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('admin_dashboard.html')


@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def admin_users():
    try:
        users = User.query.all()
        if not users:
            flash("No users found.", "info")
            return render_template('users.html', users=[])
        return render_template('users.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        flash('An error occurred while fetching users.', 'error')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/products')
@admin_required
def admin_products():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('admin_products.html')


@admin_bp.route('/getsales', methods=['GET'])
@admin_required
def get_sales():
    try:
        period = request.args.get('period', 'daily').lower()
        now = datetime.utcnow()

        # Base query with necessary joins
        sales_query = db.session.query(
            Sale.sale_id,
            Sale.username,
            Sale.product_id,
            Sale.product_name,
            Sale.quantity,
            Sale.total_price,
            Sale.created_at,
            Payment.payment_method,
            Payment.transaction_id,
            CardDetails.card_number,
            CardDetails.card_holder_name,
            CardDetails.expiration_date,
            UserShippingInfo.full_name.label('shipping_full_name'),
            UserShippingInfo.address_line1,
            UserShippingInfo.address_line2,
            UserShippingInfo.city,
            UserShippingInfo.province,
            UserShippingInfo.postal_code,
            UserShippingInfo.phone_number,
        ).join(
            Payment, Sale.sale_id == Payment.order_id, isouter=True
        ).join(
            CardDetails, CardDetails.user_id == Sale.username, isouter=True
        ).join(
            UserShippingInfo, Payment.payment_id == UserShippingInfo.payment_id, isouter=True
        )

        # Filter sales based on the period
        if period == 'daily':
            sales_query = sales_query.filter(
                func.date(Sale.created_at) == func.date(now))
        elif period == 'weekly':
            start_of_week = now - timedelta(days=now.weekday())
            sales_query = sales_query.filter(Sale.created_at >= start_of_week,
                                             Sale.created_at < start_of_week + timedelta(days=7))
        elif period == 'monthly':
            sales_query = sales_query.filter(
                and_(extract('year', Sale.created_at) == now.year,
                     extract('month', Sale.created_at) == now.month))
        elif period == 'quarterly':
            quarter_start_month = (now.month - 1) // 3 * 3 + 1
            start_of_quarter = datetime(now.year, quarter_start_month, 1)
            sales_query = sales_query.filter(Sale.created_at >= start_of_quarter,
                                             Sale.created_at < start_of_quarter + timedelta(days=90))
        elif period == 'yearly':
            sales_query = sales_query.filter(
                extract('year', Sale.created_at) == now.year)

        # Fetch the results
        sales = sales_query.all()

        # Prepare response data
        sales_data = [{
            'sale_id': sale.sale_id,
            'username': sale.username,
            'product_id': sale.product_id,
            'product_name': sale.product_name,
            'quantity': sale.quantity,
            'total_price': sale.total_price,
            'created_at': sale.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': sale.payment_method or 'N/A',
            # Masked card number
            'card_number': sale.card_number[-4:] if sale.card_number else 'N/A',
            'card_holder_name': sale.card_holder_name or 'N/A',
            'expiration_date': sale.expiration_date or 'N/A',
            'shipping_full_name': sale.shipping_full_name or 'N/A',
            'address_line1': sale.address_line1 or 'N/A',
            'address_line2': sale.address_line2 or 'N/A',
            'city': sale.city or 'N/A',
            'province': sale.province or 'N/A',
            'postal_code': sale.postal_code or 'N/A',
            'phone_number': sale.phone_number or 'N/A'
        } for sale in sales]

        return jsonify(sales_data), 200
    except Exception as e:
        print(f"Error fetching sales: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/inventory')
@admin_required
def inventory():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('inventory.html')


@admin_bp.route('/sales')
@admin_required
def sales_page():
    set_last_visited_page(request.path)  # Track last visited page
    try:
        now = datetime.utcnow()
        daily_sales = Sale.query.filter(
            func.date(Sale.created_at) == func.date(now)
        ).all()
        sales_list = [{
            'sale_id': s.sale_id,
            'username': s.username,
            'product_id': s.product_id,
            'product_name': s.product_name,
            'quantity': s.quantity,
            'total_price': s.total_price,
            # Format date for the template
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for s in daily_sales]
        return render_template('sales.html', sales=sales_list)
    except Exception as e:
        print(f'Error fetching daily sales data: {str(e)}')
        flash('Unable to load sales data. Please try again.', 'error')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/addproduct', methods=['POST'])
@admin_required
def add_product():
    data = request.get_json()
    new_product = Product(
        product_name=data['product_name'],
        price=float(data['price']),
        stock=int(data['stock']),
        category=data['category'],
        image_url=data['image_url']
    )
    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add product', 'error': str(e)}), 400


@admin_bp.route('/updateproduct', methods=['POST'])
@admin_required
def update_product():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    product.product_name = data.get('product_name', product.product_name)
    product.price = float(data.get('price', product.price)
                          ) if data.get('price') else product.price
    product.stock = int(data.get('stock', product.stock)
                        ) if data.get('stock') else product.stock
    product.image_url = data.get('image_url', product.image_url)
    try:
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 400


@admin_bp.route('/analytics')
@admin_required
def analytics():
    set_last_visited_page(request.path)  # Track last visited page
    return render_template('analytics.html')


@admin_bp.route('/analytics/data', methods=['GET'])
@admin_required
def analytics_data():
    try:
        # Total Users
        total_users = db.session.query(func.count(
            User.user_id)).scalar() or 1  # Avoid division by zero
        # Gender Distribution
        gender_stats = (
            db.session.query(User.gender, func.count(
                User.gender).label('count'))
            .group_by(User.gender)
            .all()
        )
        gender_percentage = {
            gender: (count / total_users) * 100 for gender, count in gender_stats
        }
        # Frequent Buyers
        frequent_buyers = (
            db.session.query(Sale.username, func.count(
                Sale.sale_id).label('purchase_count'))
            .group_by(Sale.username)
            .order_by(func.count(Sale.sale_id).desc())
            .limit(10)  # Optional: Limit to top 10 buyers
            .all()
        )
        frequent_buyers_data = [
            {'username': buyer.username, 'count': buyer.purchase_count}
            for buyer in frequent_buyers
        ]
        # Frequently Bought Items
        frequent_items = (
            db.session.query(Product.product_name, func.count(
                Sale.product_id).label('purchase_count'))
            .join(Sale, Product.product_id == Sale.product_id)
            .group_by(Product.product_name)
            .order_by(func.count(Sale.product_id).desc())
            .limit(10)  # Optional: Limit to top 10 items
            .all()
        )
        frequent_items_data = [
            {'product_name': item.product_name, 'count': item.purchase_count}
            for item in frequent_items
        ]
        # Most Spent by Users
        spending_stats = (
            db.session.query(Sale.username, func.sum(
                Sale.total_price).label('total_spent'))
            .group_by(Sale.username)
            .order_by(func.sum(Sale.total_price).desc())
            .limit(10)  # Optional: Limit to top 10 spenders
            .all()
        )
        spending_stats_data = [
            {'username': stat.username,
                'total_spent': round(stat.total_spent, 2)}
            for stat in spending_stats
        ]

        # Frequently Bought Items by Category
        category_stats = (
            db.session.query(Product.category, func.count(
                Sale.product_id).label('purchase_count'))
            .join(Sale, Product.product_id == Sale.product_id)
            .group_by(Product.category)
            .all()
        )
        category_data = {
            category: count for category, count in category_stats
        }
        # Combine results into a single JSON response
        response_data = {
            'gender_percentage': gender_percentage,
            'frequent_buyers': frequent_buyers_data,
            'frequent_items': frequent_items_data,
            'spending_stats': spending_stats_data,
            'category_data': category_data,
        }
        print(f"Analytics data generated: {response_data}")
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Error in analytics_data: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch analytics data', 'details': str(e)}), 500


@admin_bp.route('/showcase', methods=['GET', 'POST'])
@admin_required
def showcase():
    if request.method == 'POST':
        try:
            data = request.get_json()
            image_links = data.get('imageLinks', [])
            # Add new images to the database
            for link in image_links:
                if not ShowcaseImage.query.filter_by(image_url=link).first():
                    new_image = ShowcaseImage(image_url=link)
                    db.session.add(new_image)
            db.session.commit()
            return jsonify({"message": "Images added successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error adding images: {str(e)}"}), 500
    # For GET requests, render the showcase page with all images
    try:
        images = ShowcaseImage.query.all()
        return render_template('showcase.html', images=images)
    except Exception as e:
        return jsonify({"message": f"Error loading showcase images: {str(e)}"}), 500


@admin_bp.route('/remove_image', methods=['POST'])
@admin_required
def remove_image():
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        if not image_url:
            return jsonify({"message": "No image URL provided"}), 400
        # Mark the image as removed by updating a removed field in the database
        image = ShowcaseImage.query.filter_by(image_url=image_url).first()
        if not image:
            return jsonify({"message": "Image not found"}), 404
        image.removed = True
        db.session.commit()
        return jsonify({"message": "Image removed from menu successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error removing image: {str(e)}"}), 500


@admin_bp.route('/user_info', methods=['GET'])
@admin_required
def admin_user_info():
    try:
        print("Fetching all users...")
        users = User.query.all()  # Get all users

        users_info = []  # Initialize an empty list to hold user info
        for user in users:
            print(f"Processing user: {user.username}")

            # Fetch the user's payments
            payments = Payment.query.filter_by(user_id=user.user_id).all()
            print(
                f"Payments fetched for {user.username}: {len(payments)}")

            # Calculate total spent by the user through sales
            total_spent = db.session.query(func.sum(Sale.total_price)).filter_by(
                username=user.username).scalar() or 0.0
            print(f"Total spent for {user.username}: {total_spent}")

            # Fetch the user's shipping info
            shipping_info = UserShippingInfo.query.filter_by(
                user_id=user.user_id).all()
            print(
                f"Shipping info fetched for {user.username}: {len(shipping_info)}")

            # Capture sales information, if needed
            sales_info = Sale.query.filter_by(username=user.username).all()
            print(f"Sales info fetched for {user.username}: {len(sales_info)}")

            # Create user data structure
            user_data = {
                'user': user,
                'payments': payments,
                # Round to 2 decimal places
                'total_spent': round(total_spent, 2),
                'shipping_info': shipping_info,
                'sales_info': sales_info
            }

            users_info.append(user_data)  # Append structured info to the list

        # Now passing make sure that users_info is structured as expected in the template
        return render_template('user_info.html', users_info=users_info)

    except Exception as e:
        # Log the error
        print(f"Error loading user info: {e}", exc_info=True)
        flash("Failed to load user information.",
              "error")  # Flash error message
        # Redirect if there's an error
        return redirect(url_for('admin.admin_dashboard'))
