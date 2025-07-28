from celery import current_task
from .extensions import db
from .models import User, Reservation, ParkingLot
from datetime import datetime, timedelta
import csv
import io
from flask_mail import Message
from flask import current_app
import requests

# Import celery and mail from app context
from .app import celery, mail

@celery.task
def send_daily_reminders():
    """Send daily reminders to users who haven't used the parking system"""
    try:
        # Get users who haven't made any reservations in the last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        inactive_users = User.query.filter(
            ~User.reservations.any(Reservation.parking_timestamp >= week_ago)
        ).all()
        
        for user in inactive_users:
            # Send reminder via email (you can also implement Google Chat webhook)
            send_reminder_email(user.email, user.full_name)
            
        return f"Sent reminders to {len(inactive_users)} users"
    except Exception as e:
        return f"Error sending reminders: {str(e)}"

@celery.task
def send_monthly_reports():
    """Send monthly activity reports to all users"""
    try:
        users = User.query.all()
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        for user in users:
            # Get user's monthly activity
            monthly_reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.parking_timestamp >= current_month
            ).all()
            
            if monthly_reservations:
                report_html = generate_monthly_report(user, monthly_reservations)
                send_monthly_report_email(user.email, user.full_name, report_html)
                
        return f"Sent monthly reports to {len(users)} users"
    except Exception as e:
        return f"Error sending monthly reports: {str(e)}"

@celery.task
def export_user_csv(user_id):
    """Export user's parking history as CSV"""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
            
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reservation ID', 'Spot ID', 'Lot Name', 'Parking Time', 'Leaving Time', 'Cost', 'Duration (hours)'])
        
        for res in reservations:
            duration = 0
            if res.leaving_timestamp:
                duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
                
            writer.writerow([
                res.id,
                res.spot_id,
                res.spot.lot.prime_location_name,
                res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
                res.leaving_timestamp.strftime("%Y-%m-%d %H:%M") if res.leaving_timestamp else "Active",
                res.parking_cost or 0,
                round(duration, 2)
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Send CSV via email
        send_csv_email(user.email, user.full_name, csv_content)
        
        return f"CSV exported for user {user.email}"
    except Exception as e:
        return f"Error exporting CSV: {str(e)}"

def send_reminder_email(email, name):
    """Send reminder email to user"""
    try:
        msg = Message(
            "ParkBuddy - Daily Reminder",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"""
        Hi {name},
        
        We noticed you haven't used ParkBuddy in a while. 
        Don't forget to book your parking spot when needed!
        
        Best regards,
        ParkBuddy Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending reminder email: {e}")

def send_monthly_report_email(email, name, report_html):
    """Send monthly report email to user"""
    try:
        msg = Message(
            "ParkBuddy - Monthly Activity Report",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.html = report_html
        mail.send(msg)
    except Exception as e:
        print(f"Error sending monthly report email: {e}")

def send_csv_email(email, name, csv_content):
    """Send CSV export email to user"""
    try:
        msg = Message(
            "ParkBuddy - Your Parking History Export",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"""
        Hi {name},
        
        Please find your parking history export attached.
        
        Best regards,
        ParkBuddy Team
        """
        msg.attach("parking_history.csv", "text/csv", csv_content)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending CSV email: {e}")

def generate_monthly_report(user, reservations):
    """Generate HTML monthly report"""
    total_cost = sum(r.parking_cost or 0 for r in reservations)
    total_duration = sum(
        (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600 
        for r in reservations if r.leaving_timestamp
    )
    
    # Most used parking lot
    lot_usage = {}
    for res in reservations:
        lot_name = res.spot.lot.prime_location_name
        lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
    
    most_used_lot = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else "None"
    
    html = f"""
    <html>
    <body>
        <h2>ParkBuddy Monthly Report</h2>
        <p>Hi {user.full_name},</p>
        <p>Here's your parking activity for this month:</p>
        <ul>
            <li>Total Reservations: {len(reservations)}</li>
            <li>Total Cost: ₹{total_cost:.2f}</li>
            <li>Total Duration: {total_duration:.2f} hours</li>
            <li>Most Used Parking Lot: {most_used_lot}</li>
        </ul>
        <p>Thank you for using ParkBuddy!</p>
    </body>
    </html>
    """
    return html 