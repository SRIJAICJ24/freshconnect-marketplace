"""
Review & Rating System Routes
Retailers can review vendors and products after delivery
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Order, ProductReview, User
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@bp.route('/create/<int:order_id>', methods=['GET', 'POST'])
@login_required
def create_review(order_id):
    """Create a review for a delivered order (retailer only)"""
    
    order = Order.query.get_or_404(order_id)
    
    # Check if order belongs to current user
    if order.buyer_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('retailer.dashboard'))
    
    # Check if order is delivered
    if order.order_status != 'delivered':
        flash('You can only review delivered orders', 'warning')
        return redirect(url_for('retailer.orders'))
    
    # Check if already reviewed
    existing_review = ProductReview.query.filter_by(
        order_id=order_id,
        retailer_id=current_user.id
    ).first()
    
    if existing_review and request.method == 'GET':
        flash('You have already reviewed this order. You can edit your review.', 'info')
    
    if request.method == 'POST':
        rating_quality = request.form.get('rating_quality', type=int)
        rating_delay = request.form.get('rating_delay', type=int)
        rating_communication = request.form.get('rating_communication', type=int)
        driver_rating = request.form.get('driver_rating', type=int)  # Optional driver rating
        comment = request.form.get('comment', '').strip()
        
        # Validate ratings
        if not all([rating_quality, rating_delay, rating_communication]):
            flash('Please provide all vendor ratings', 'danger')
            return redirect(url_for('retailer.orders'))
        
        if not all(1 <= r <= 5 for r in [rating_quality, rating_delay, rating_communication]):
            flash('Ratings must be between 1 and 5', 'danger')
            return redirect(url_for('retailer.orders'))
        
        # Validate driver rating if provided
        if driver_rating and not (1 <= driver_rating <= 5):
            flash('Driver rating must be between 1 and 5', 'danger')
            return redirect(url_for('retailer.orders'))
        
        try:
            if existing_review:
                # Update existing review
                existing_review.rating_quality = rating_quality
                existing_review.rating_delay = rating_delay
                existing_review.rating_communication = rating_communication
                existing_review.driver_rating = driver_rating if driver_rating else existing_review.driver_rating
                existing_review.comment = comment
                existing_review.edited_at = datetime.utcnow()
                message = 'Review updated successfully!'
            else:
                # Create new review
                review = ProductReview(
                    order_id=order_id,
                    product_id=order.items[0].product_id if order.items else None,
                    retailer_id=current_user.id,
                    vendor_id=order.seller_id,
                    driver_id=order.assigned_driver_id,
                    rating_quality=rating_quality,
                    rating_delay=rating_delay,
                    rating_communication=rating_communication,
                    driver_rating=driver_rating,  # Add driver rating
                    comment=comment,
                    created_at=datetime.utcnow()
                )
                db.session.add(review)
                message = 'Review submitted successfully! Thank you for your feedback.'
            
            # Update vendor's average rating
            update_user_ratings(order.seller_id)
            
            # Update driver's rating if assigned and rated
            if order.assigned_driver_id and driver_rating:
                update_user_ratings(order.assigned_driver_id)
            
            db.session.commit()
            
            flash(message, 'success')
            return redirect(url_for('retailer.orders'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error submitting review: {e}")
            import traceback
            traceback.print_exc()
            flash('Error submitting review. Please try again.', 'danger')
            return redirect(url_for('retailer.orders'))
    
    return render_template('reviews/create_review.html',
                         order=order,
                         existing_review=existing_review)


@bp.route('/vendor/<int:vendor_id>')
@login_required
def vendor_reviews(vendor_id):
    """View all reviews for a vendor"""
    
    vendor = User.query.get_or_404(vendor_id)
    
    if vendor.user_type != 'vendor':
        flash('Invalid vendor', 'danger')
        return redirect(url_for('retailer.browse'))
    
    reviews = ProductReview.query.filter_by(
        vendor_id=vendor_id
    ).order_by(ProductReview.created_at.desc()).all()
    
    # Calculate rating breakdown
    rating_breakdown = get_rating_breakdown(vendor_id)
    
    return render_template('reviews/vendor_reviews.html',
                         vendor=vendor,
                         reviews=reviews,
                         rating_breakdown=rating_breakdown)


@bp.route('/my-reviews')
@login_required
def my_reviews():
    """View reviews written by current user (retailer) or received (vendor/driver)"""
    
    if current_user.user_type == 'retailer':
        # Reviews written by retailer
        reviews = ProductReview.query.filter_by(
            retailer_id=current_user.id
        ).order_by(ProductReview.created_at.desc()).all()
        template = 'reviews/my_reviews_retailer.html'
    
    elif current_user.user_type == 'vendor':
        # Reviews received by vendor
        reviews = ProductReview.query.filter_by(
            vendor_id=current_user.id
        ).order_by(ProductReview.created_at.desc()).all()
        template = 'reviews/my_reviews_vendor.html'
    
    elif current_user.user_type == 'driver':
        # Reviews received by driver
        reviews = ProductReview.query.filter_by(
            driver_id=current_user.id
        ).order_by(ProductReview.created_at.desc()).all()
        template = 'reviews/my_reviews_driver.html'
    
    else:
        flash('Invalid user type', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template(template, reviews=reviews)


@bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review (only by the author)"""
    
    review = ProductReview.query.get_or_404(review_id)
    
    if review.retailer_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('reviews.my_reviews'))
    
    vendor_id = review.vendor_id
    driver_id = review.driver_id
    
    db.session.delete(review)
    
    # Update ratings
    update_user_ratings(vendor_id)
    if driver_id:
        update_user_ratings(driver_id)
    
    db.session.commit()
    
    flash('Review deleted successfully', 'success')
    return redirect(url_for('reviews.my_reviews'))


def update_user_ratings(user_id):
    """Recalculate average rating for a user"""
    
    if not user_id:
        return
    
    user = User.query.get(user_id)
    if not user:
        return
    
    # Get all reviews for this user
    if user.user_type == 'vendor':
        reviews = ProductReview.query.filter_by(vendor_id=user_id).all()
        # Calculate average of vendor ratings (quality, delay, communication)
        total_ratings = []
        for review in reviews:
            avg = (review.rating_quality + review.rating_delay + review.rating_communication) / 3
            total_ratings.append(avg)
            
    elif user.user_type == 'driver':
        reviews = ProductReview.query.filter_by(driver_id=user_id).filter(
            ProductReview.driver_rating.isnot(None)
        ).all()
        # Calculate average of driver ratings
        total_ratings = [review.driver_rating for review in reviews if review.driver_rating]
    else:
        return
    
    if not total_ratings:
        user.average_rating = 0.0
        user.total_reviews = 0
        return
    
    user.average_rating = round(sum(total_ratings) / len(total_ratings), 2)
    user.total_reviews = len(reviews)


def get_rating_breakdown(user_id):
    """Get breakdown of ratings (how many 5-star, 4-star, etc.)"""
    
    reviews = ProductReview.query.filter_by(vendor_id=user_id).all()
    
    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    for review in reviews:
        avg = round((review.rating_quality + review.rating_delay + review.rating_communication) / 3)
        breakdown[avg] = breakdown.get(avg, 0) + 1
    
    total = len(reviews)
    
    # Calculate percentages
    percentages = {}
    for rating, count in breakdown.items():
        percentages[rating] = {
            'count': count,
            'percentage': int((count / total * 100)) if total > 0 else 0
        }
    
    return percentages


@bp.route('/api/vendor/<int:vendor_id>/rating')
def get_vendor_rating(vendor_id):
    """API endpoint to get vendor rating (for AJAX)"""
    
    vendor = User.query.get_or_404(vendor_id)
    
    return jsonify({
        'vendor_id': vendor_id,
        'average_rating': float(vendor.average_rating) if vendor.average_rating else 0.0,
        'total_reviews': vendor.total_reviews or 0,
        'business_name': vendor.business_name or vendor.name
    })
