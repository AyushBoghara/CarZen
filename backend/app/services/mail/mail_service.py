from decimal import Decimal
from email.message import EmailMessage
import logging
import os
from pathlib import Path
import smtplib

logger = logging.getLogger(__name__)


def _money(value) -> str:
    return f"INR {Decimal(str(value or 0)):,.2f}"


def create_mail_service(receiver_email: str, request, filename: str):
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise RuntimeError(
            "SENDER_EMAIL or SENDER_PASSWORD is missing from environment variables."
        )

    if not receiver_email:
        raise ValueError("Customer email address is missing.")

    if not filename:
        raise ValueError("Invoice PDF path is missing.")

    pdf_path = Path(filename)

    user = getattr(request, "user", None)
    customer_name = "Customer"
    if user:
        customer_name = (
            getattr(user, "name", None)
            or f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '') or ''}".strip()
            or getattr(user, "username", "Customer")
        )

    msg = EmailMessage()

    email_template = f"""Dear {customer_name},
    
    Greetings from CarZen!
    
    We are pleased to inform you that the service for your vehicle has been successfully completed.
    
    Service Details:
    
    Customer Name: {customer_name}
    Service Date: {str(request.scheduled_date or "-")}
    Service Provider: CarZen
    Total Service Cost: {_money(request.total_amount)}
    
    Please find the service invoice attached as a PDF for your reference. It contains the details of the services performed and the final amount charged.
    
    Thank you for choosing CarZen. We appreciate your trust in our service and look forward to serving you again.
    
    If you have any questions regarding the service or invoice, please feel free to contact us.
    
    Best regards,
    CarZen Service Team
    CarZen – Your Trusted Car Service Partner
    """
    
    msg["Subject"] = "CarZen – Your Car Service Has Been Completed"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content(email_template)

    if pdf_path.is_file():
        try:
            with pdf_path.open("rb") as f:
                file_data = f.read()
                file_name = os.path.basename(f.name)

                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="pdf",
                    filename=file_name,
                )
        except Exception as e:
            logger.warning(f"Could not attach PDF invoice {filename}: {e}")
    else:
        logger.warning(
            f"Invoice PDF file not found at {filename}. Sending email without attachment."
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"Service invoice email sent successfully to {receiver_email}.")
        return {
            "success": True,
            "message": "Service invoice email sent successfully.",
        }
    except Exception as e:
        logger.error(f"Failed to send email to {receiver_email}: {e}")
        raise RuntimeError(f"Failed to send service invoice email: {e}") from e
