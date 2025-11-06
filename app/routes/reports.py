"""
Report System Routes
Users can report issues, admins can review and respond
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import UserReport, User, Order
from app.decorators import admin_required
from datetime import datetime

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/submit/<int:order_id>', methods=['POST'])
@login_required
def submit_report(order_id):
    """Submit a report from order page modal"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # Verify user is buyer of this order
        if order.buyer_id != current_user.id:
            flash('Unauthorized action', 'danger')
            return redirect(url_for('retailer.orders'))
        
        report_type = request.form.get('report_type')  # 'vendor' or 'driver'
        issue_category = request.form.get('issue_category')
        description = request.form.get('description', '').strip()
        severity = request.form.get('severity', 'medium')
        
        # Validate
        if not all([report_type, issue_category, description]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('retailer.orders'))
        
        # Determine reported user
        if report_type == 'vendor':
            reported_user_id = order.seller_id
            subject = f"Issue with Vendor: {issue_category.replace('_', ' ').title()}"
        elif report_type == 'driver':
            if not order.assigned_driver_id:
                flash('No driver assigned to this order', 'danger')
                return redirect(url_for('retailer.orders'))
            reported_user_id = order.assigned_driver_id
            subject = f"Issue with Driver: {issue_category.replace('_', ' ').title()}"
        else:
            flash('Invalid report type', 'danger')
            return redirect(url_for('retailer.orders'))
        
        # Create report
        report = UserReport(
            reporter_id=current_user.id,
            reported_user_id=reported_user_id,
            order_id=order_id,
            report_type=report_type,
            subject=subject,
            description=f"[{severity.upper()}] {issue_category.replace('_', ' ').title()}\n\n{description}",
            severity=severity,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash(f'Report submitted successfully against {report_type}. Admin will review it soon.', 'success')
        return redirect(url_for('retailer.orders'))
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error submitting report: {e}")
        import traceback
        traceback.print_exc()
        flash('Error submitting report. Please try again.', 'danger')
        return redirect(url_for('retailer.orders'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_report():
    """Submit a new report"""
    
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        reported_user_id = request.form.get('reported_user_id', type=int)
        order_id = request.form.get('order_id', type=int)
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate
        if not all([report_type, subject, description]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('reports.create_report'))
        
        # Create report
        report = UserReport(
            reporter_id=current_user.id,
            reported_user_id=reported_user_id,
            order_id=order_id,
            report_type=report_type,
            subject=subject,
            description=description,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report submitted successfully. We will review it soon.', 'success')
        return redirect(url_for('reports.my_reports'))
    
    # Get users and orders for dropdowns
    vendors = User.query.filter_by(user_type='vendor').all()
    drivers = User.query.filter_by(user_type='driver').all()
    
    # Get user's orders if retailer
    orders = []
    if current_user.user_type == 'retailer':
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).limit(20).all()
    elif current_user.user_type == 'vendor':
        orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).limit(20).all()
    
    return render_template('reports/create_report.html',
                         vendors=vendors,
                         drivers=drivers,
                         orders=orders)


@bp.route('/my-reports')
@login_required
def my_reports():
    """View reports submitted by current user"""
    
    reports = UserReport.query.filter_by(
        reporter_id=current_user.id
    ).order_by(UserReport.created_at.desc()).all()
    
    return render_template('reports/my_reports.html', reports=reports)


@bp.route('/<int:report_id>')
@login_required
def view_report(report_id):
    """View a specific report"""
    
    report = UserReport.query.get_or_404(report_id)
    
    # Check access
    if current_user.user_type != 'admin' and report.reporter_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('reports/view_report.html', report=report)


@bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard to view and manage all reports"""
    
    status_filter = request.args.get('status', 'all')
    
    query = UserReport.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    reports = query.order_by(UserReport.created_at.desc()).all()
    
    # Get stats
    stats = {
        'total': UserReport.query.count(),
        'pending': UserReport.query.filter_by(status='pending').count(),
        'in_review': UserReport.query.filter_by(status='in_review').count(),
        'resolved': UserReport.query.filter_by(status='resolved').count(),
        'rejected': UserReport.query.filter_by(status='rejected').count()
    }
    
    return render_template('reports/admin_dashboard.html',
                         reports=reports,
                         stats=stats,
                         current_filter=status_filter)


@bp.route('/admin/<int:report_id>/update-status', methods=['POST'])
@admin_required
def update_status(report_id):
    """Admin updates report status"""
    
    report = UserReport.query.get_or_404(report_id)
    
    new_status = request.form.get('status')
    admin_response = request.form.get('admin_response', '').strip()
    
    if new_status not in ['pending', 'in_review', 'resolved', 'rejected']:
        flash('Invalid status', 'danger')
        return redirect(url_for('reports.view_report', report_id=report_id))
    
    report.status = new_status
    if admin_response:
        report.admin_response = admin_response
    report.reviewed_by_admin_id = current_user.id
    report.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Report status updated to {new_status}', 'success')
    return redirect(url_for('reports.admin_dashboard'))


@bp.route('/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    """Delete a report (only by reporter or admin)"""
    
    report = UserReport.query.get_or_404(report_id)
    
    if current_user.user_type != 'admin' and report.reporter_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('reports.my_reports'))
    
    db.session.delete(report)
    db.session.commit()
    
    flash('Report deleted successfully', 'success')
    
    if current_user.user_type == 'admin':
        return redirect(url_for('reports.admin_dashboard'))
    else:
        return redirect(url_for('reports.my_reports'))


@bp.route('/api/stats')
@admin_required
def get_stats():
    """API endpoint for report statistics"""
    
    stats = {
        'total': UserReport.query.count(),
        'pending': UserReport.query.filter_by(status='pending').count(),
        'in_review': UserReport.query.filter_by(status='in_review').count(),
        'resolved': UserReport.query.filter_by(status='resolved').count(),
        'rejected': UserReport.query.filter_by(status='rejected').count()
    }
    
    # Recent reports
    recent = UserReport.query.order_by(UserReport.created_at.desc()).limit(5).all()
    
    return jsonify({
        'stats': stats,
        'recent_count': len(recent)
    })
