from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

TITLE = "Secure End-to-End Encrypted Chat Application"
FILENAME = "Secure_Chat_Report.pdf"

sections = [
    ("Introduction", "This project implements a secure real-time chat application with end-to-end encryption (E2EE) using public key cryptography. The goal is to ensure that only intended recipients can read the messages, providing privacy and security for users."),
    ("Abstract", "The chat application leverages RSA for key exchange and AES for encrypting messages. Each user generates an RSA keypair, shares their public key, and uses AES for message encryption. The AES key is securely shared with recipients using RSA encryption. All messages are transmitted and stored in encrypted form, ensuring confidentiality even if the server is compromised."),
    ("Tools Used", "- Python 3\n- Flask & Flask-SocketIO\n- cryptography (RSA/AES)\n- reportlab (for PDF generation)\n- HTML/JavaScript (WebCrypto API)"),
    ("Steps Involved in Building the Project", "1. Set up Flask backend with SocketIO for real-time communication.\n2. Implement user registration and RSA keypair generation (client-side).\n3. Exchange public keys between users via the server.\n4. Encrypt messages with AES; encrypt AES key with recipient's RSA public key.\n5. Relay encrypted messages and keys via the server.\n6. Decrypt messages only on the client side.\n7. Store encrypted chat logs on the server.\n8. Generate this report as a project summary."),
    ("Conclusion", "The project demonstrates a practical approach to secure, real-time communication using end-to-end encryption. By combining RSA and AES, it ensures that messages remain confidential and accessible only to intended recipients, even if the server is compromised.")
]

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-2*cm, TITLE)
    c.setFont("Helvetica", 11)
    y = height-3.2*cm
    for section, text in sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, section)
        y -= 0.7*cm
        c.setFont("Helvetica", 11)
        for line in text.split('\n'):
            for subline in [line[i:i+100] for i in range(0, len(line), 100)]:
                c.drawString(2.5*cm, y, subline)
                y -= 0.55*cm
        y -= 0.3*cm
        if y < 3*cm:
            c.showPage()
            y = height-2*cm
    c.save()

if __name__ == "__main__":
    create_pdf(FILENAME)
    print(f"PDF report generated: {FILENAME}") 