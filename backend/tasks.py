from celery import current_task
from .extensions import db, mail
from .models import User, Admin, Reservation, ParkingLot, ParkingSpot
from datetime import datetime, timedelta
import csv
import io
from flask_mail import Message
from flask import current_app
import requests

# Import celery from app context
from .app import celery

@celery.task(name='backend.tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders to users: reservation reminder or lot suggestion"""
    try:
        users = User.query.all()
        for user in users:
            active_res = Reservation.query.filter_by(user_id=user.id, leaving_timestamp=None).first()
            if active_res:
                # Remind about reservation
                send_active_reservation_reminder(user.email, user.full_name, active_res)
            else:
                # Suggest a lot to book (pick lot with most available spots)
                lots = ParkingLot.query.all()
                best_lot = None
                max_available = -1
                for lot in lots:
                    available = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
                    if available > max_available:
                        max_available = available
                        best_lot = lot
                if best_lot:
                    send_lot_suggestion_email(user.email, user.full_name, best_lot.prime_location_name)
        return f"Sent daily reminders to {len(users)} users"
    except Exception as e:
        return f"Error sending reminders: {str(e)}"

@celery.task(name='backend.tasks.send_monthly_reports')
def send_monthly_reports():
    """Send monthly activity summary to all admins"""
    try:
        admins = Admin.query.all()
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        lots = ParkingLot.query.all()
        # Gather stats per lot
        lot_stats = []
        for lot in lots:
            reservations = Reservation.query.join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot.id,
                Reservation.parking_timestamp >= current_month
            ).all()
            total_res = len(reservations)
            total_rev = sum(r.parking_cost or 0 for r in reservations)
            occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            available = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            lot_stats.append({
                'name': lot.prime_location_name,
                'total_reservations': total_res,
                'total_revenue': total_rev,
                'occupied_spots': occupied,
                'available_spots': available
            })
        # Generate HTML report
        report_html = generate_admin_monthly_report(lot_stats, current_month)
        for admin in admins:
            send_monthly_report_email(admin.username, admin.username, report_html)
        return f"Sent monthly report to {len(admins)} admin(s)"
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

def send_active_reservation_reminder(email, name, reservation):
    """Send reminder email to user with active reservation details"""
    try:
        msg = Message(
            "ParkBuddy - Reservation Reminder",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"""
        Hi {name},
        
        This is a reminder that you have an active parking reservation:
        Lot: {reservation.spot.lot.prime_location_name}
        Spot ID: {reservation.spot_id}
        Parked At: {reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M')}
        
        Have a great day!
        ParkBuddy Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending reservation reminder email: {e}")

def send_lot_suggestion_email(email, name, lot_name):
    """Suggest a lot to book to user"""
    try:
        msg = Message(
            "ParkBuddy - Book a Spot!",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"""
        Hi {name},
        
        Looking for parking? We recommend booking a spot at our {lot_name} lot, which currently has the most availability!
        
        See you soon,
        ParkBuddy Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending lot suggestion email: {e}")

def send_monthly_report_email(email, name, report_html):
    """Send monthly report email to admin"""
    try:
        msg = Message(
            "ParkBuddy - Monthly Lot Activity Summary",
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

def generate_admin_monthly_report(lot_stats, current_month):
    """Generate HTML summary report for all lots for admins"""
    html = f"""
    <html>
    <body>
        <h2>ParkBuddy Monthly Lot Activity Summary</h2>
        <p>Report for: {current_month.strftime('%B %Y')}</p>
        <table border='1' cellpadding='5' cellspacing='0'>
            <tr><th>Lot Name</th><th>Total Reservations</th><th>Total Revenue</th><th>Occupied Spots</th><th>Available Spots</th></tr>
    """
    for lot in lot_stats:
        html += f"<tr><td>{lot['name']}</td><td>{lot['total_reservations']}</td><td>₹{lot['total_revenue']:.2f}</td><td>{lot['occupied_spots']}</td><td>{lot['available_spots']}</td></tr>"
    html += """
        </table>
        <p>Thank you for managing ParkBuddy!</p>
    </body>
    </html>
    """
    return html