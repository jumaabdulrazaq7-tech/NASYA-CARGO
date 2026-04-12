"""
================================================================
NASYA CARGO — Quote API Server
File:    api/server.py
Stack:   Python 3.8+ · Flask · SQLite · smtplib
================================================================
Endpoints:
  POST /api/quote      → Receive quote from website
  GET  /api/quotes     → List all quotes (staff portal)
  GET  /api/quote/<id> → Get single quote
  PUT  /api/quote/<id> → Update quote status
  GET  /api/health     → Health check

Run:
  pip install -r requirements.txt
  python server.py
================================================================
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import smtplib
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)   # Allow requests from website (any origin)

# ── CONFIG ────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'quotes.db')

# Email config — update with your Gmail credentials
EMAIL_CONFIG = {
    'sender':   'nasyacargo@gmail.com',
    'password': 'YOUR_GMAIL_APP_PASSWORD',  # Use Gmail App Password
    'notify':   'nasyacargo@gmail.com',     # Where to send notifications
    'smtp':     'smtp.gmail.com',
    'port':     587
}

# WhatsApp notify via wa.me (simple link — no Twilio needed)
WHATSAPP_PHONE = '971547417800'   # Dubai WhatsApp (no +)


# ── DATABASE SETUP ────────────────────────────────────────────
def init_db():
    """Create quotes table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_ref   TEXT UNIQUE,
            name        TEXT NOT NULL,
            company     TEXT,
            email       TEXT NOT NULL,
            phone       TEXT NOT NULL,
            cargo_type  TEXT,
            ship_mode   TEXT,
            origin      TEXT,
            destination TEXT,
            weight      TEXT,
            volume      TEXT,
            cargo_value TEXT,
            notes       TEXT,
            status      TEXT DEFAULT 'New',
            created_at  TEXT,
            updated_at  TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database ready:", DB_PATH)


def generate_ref():
    """Generate unique quote reference e.g. QT-2025-0042"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM quotes")
    count = c.fetchone()[0] + 1
    conn.close()
    year = datetime.now().year
    return f"QT-{year}-{count:04d}"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── EMAIL NOTIFICATION ────────────────────────────────────────
def send_email_notification(quote_data: dict):
    """Send email to team when new quote arrives."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚚 New Quote Request — {quote_data['quote_ref']} | {quote_data['name']}"
        msg['From']    = EMAIL_CONFIG['sender']
        msg['To']      = EMAIL_CONFIG['notify']

        html = f"""
        <html><body style="font-family:Arial,sans-serif;color:#1A1A1A;">
          <div style="max-width:600px;margin:0 auto;border:1px solid #E8E8E8;border-radius:10px;overflow:hidden;">
            <div style="background:#0A0A0A;padding:24px;text-align:center;">
              <h2 style="color:#F0C828;margin:0;">NASYA CARGO</h2>
              <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;font-size:13px;">New Quote Request Received</p>
            </div>
            <div style="padding:28px;">
              <table width="100%" cellpadding="8" style="border-collapse:collapse;">
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;width:35%;padding:10px 14px;">Quote Ref</td>
                  <td style="padding:10px 14px;font-weight:700;color:#00B4D2;">{quote_data['quote_ref']}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Customer</td>
                  <td style="padding:10px 14px;">{quote_data['name']}</td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Company</td>
                  <td style="padding:10px 14px;">{quote_data.get('company', '—')}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Email</td>
                  <td style="padding:10px 14px;"><a href="mailto:{quote_data['email']}">{quote_data['email']}</a></td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Phone / WhatsApp</td>
                  <td style="padding:10px 14px;">{quote_data['phone']}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Cargo Type</td>
                  <td style="padding:10px 14px;">{quote_data.get('cargo_type', '—')}</td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Shipping Mode</td>
                  <td style="padding:10px 14px;">{quote_data.get('ship_mode', '—')}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Origin</td>
                  <td style="padding:10px 14px;">{quote_data.get('origin', '—')}</td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Destination</td>
                  <td style="padding:10px 14px;">{quote_data.get('destination', '—')}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Weight</td>
                  <td style="padding:10px 14px;">{quote_data.get('weight', '—')} kg</td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Cargo Value</td>
                  <td style="padding:10px 14px;">{quote_data.get('cargo_value', '—')}</td>
                </tr>
                <tr>
                  <td style="font-weight:700;padding:10px 14px;">Notes</td>
                  <td style="padding:10px 14px;">{quote_data.get('notes', '—')}</td>
                </tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;padding:10px 14px;">Received At</td>
                  <td style="padding:10px 14px;">{quote_data['created_at']}</td>
                </tr>
              </table>

              <div style="margin-top:24px;padding:16px;background:#FFF9E6;border-radius:8px;border-left:4px solid #F0C828;">
                <strong>⚡ Action Required:</strong> Please respond to this quote within 2 hours.
              </div>
            </div>
            <div style="background:#0A0A0A;padding:16px;text-align:center;">
              <p style="color:rgba(255,255,255,0.35);font-size:12px;margin:0;">
                Nasya Cargo · nasyacargo@gmail.com · +971 54 741 7800
              </p>
            </div>
          </div>
        </body></html>
        """

        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP(EMAIL_CONFIG['smtp'], EMAIL_CONFIG['port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
        server.sendmail(EMAIL_CONFIG['sender'], EMAIL_CONFIG['notify'], msg.as_string())
        server.quit()
        print(f"✅ Email sent for {quote_data['quote_ref']}")
        return True
    except Exception as e:
        print(f"⚠️  Email failed: {e}")
        return False


# ── AUTO-REPLY TO CUSTOMER ────────────────────────────────────
def send_customer_reply(quote_data: dict):
    """Send confirmation email to customer."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"✅ Quote Request Received — {quote_data['quote_ref']} | Nasya Cargo"
        msg['From']    = EMAIL_CONFIG['sender']
        msg['To']      = quote_data['email']

        html = f"""
        <html><body style="font-family:Arial,sans-serif;color:#1A1A1A;">
          <div style="max-width:600px;margin:0 auto;border:1px solid #E8E8E8;border-radius:10px;overflow:hidden;">
            <div style="background:#0A0A0A;padding:32px;text-align:center;">
              <h2 style="color:#F0C828;margin:0;font-size:28px;">NASYA CARGO</h2>
              <p style="color:rgba(255,255,255,0.5);margin:6px 0 0;">Dubai, UAE ↔ Dar es Salaam, Tanzania</p>
            </div>
            <div style="padding:32px;">
              <h3 style="color:#0A0A0A;">Dear {quote_data['name']},</h3>
              <p style="line-height:1.7;color:#444;">
                Thank you for your quote request. We have received your shipment details and our team
                will prepare a competitive quote and contact you within <strong>2 business hours</strong>.
              </p>

              <div style="background:#F8F8F6;border-radius:10px;padding:20px;margin:20px 0;">
                <p style="margin:0 0 8px;font-weight:700;color:#0A0A0A;">Your Quote Reference:</p>
                <p style="margin:0;font-size:22px;font-weight:800;color:#00B4D2;">{quote_data['quote_ref']}</p>
              </div>

              <table width="100%" cellpadding="6" style="border-collapse:collapse;font-size:14px;">
                <tr><td style="font-weight:700;width:40%;">Route:</td>
                    <td>{quote_data.get('origin','—')} → {quote_data.get('destination','—')}</td></tr>
                <tr style="background:#F8F8F6;">
                  <td style="font-weight:700;">Cargo Type:</td>
                  <td>{quote_data.get('cargo_type','—')}</td></tr>
                <tr><td style="font-weight:700;">Shipping Mode:</td>
                    <td>{quote_data.get('ship_mode','—')}</td></tr>
              </table>

              <p style="line-height:1.7;color:#444;margin-top:20px;">
                For urgent enquiries, please contact us directly:
              </p>
              <div style="display:flex;gap:10px;margin:16px 0;">
                <a href="https://wa.me/{WHATSAPP_PHONE}" style="background:#25D366;color:white;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:700;">💬 WhatsApp</a>
                <a href="tel:+97145708547" style="background:#0A0A0A;color:#F0C828;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:700;">📞 Call Us</a>
              </div>
            </div>
            <div style="background:#0A0A0A;padding:20px;text-align:center;">
              <p style="color:rgba(255,255,255,0.35);font-size:12px;margin:0;">
                © 2025 Nasya Cargo · nasyacargo@gmail.com · +971 4 570 8547
              </p>
            </div>
          </div>
        </body></html>
        """

        msg.attach(MIMEText(html, 'html'))
        server = smtplib.SMTP(EMAIL_CONFIG['smtp'], EMAIL_CONFIG['port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
        server.sendmail(EMAIL_CONFIG['sender'], quote_data['email'], msg.as_string())
        server.quit()
        print(f"✅ Auto-reply sent to {quote_data['email']}")
        return True
    except Exception as e:
        print(f"⚠️  Auto-reply failed: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

# ── POST /api/quote — Receive new quote from website ──────────
@app.route('/api/quote', methods=['POST'])
def create_quote():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data received'}), 400

    # Validate required fields
    required = ['name', 'email', 'phone']
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({
            'success': False,
            'error': f"Missing required fields: {', '.join(missing)}"
        }), 422

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    quote_data = {
        'quote_ref':   generate_ref(),
        'name':        data.get('name', '').strip(),
        'company':     data.get('company', '').strip(),
        'email':       data.get('email', '').strip().lower(),
        'phone':       data.get('phone', '').strip(),
        'cargo_type':  data.get('cargo_type', ''),
        'ship_mode':   data.get('ship_mode', ''),
        'origin':      data.get('origin', '').strip(),
        'destination': data.get('destination', '').strip(),
        'weight':      data.get('weight', ''),
        'volume':      data.get('volume', ''),
        'cargo_value': data.get('cargo_value', ''),
        'notes':       data.get('notes', '').strip(),
        'status':      'New',
        'created_at':  now,
        'updated_at':  now,
    }

    # Save to database
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO quotes
              (quote_ref, name, company, email, phone, cargo_type, ship_mode,
               origin, destination, weight, volume, cargo_value, notes,
               status, created_at, updated_at)
            VALUES
              (:quote_ref, :name, :company, :email, :phone, :cargo_type, :ship_mode,
               :origin, :destination, :weight, :volume, :cargo_value, :notes,
               :status, :created_at, :updated_at)
        ''', quote_data)
        conn.commit()
        conn.close()
        print(f"✅ Quote saved: {quote_data['quote_ref']}")
    except Exception as e:
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500

    # Send notifications (non-blocking — won't fail the request)
    send_email_notification(quote_data)
    send_customer_reply(quote_data)

    return jsonify({
        'success':   True,
        'quote_ref': quote_data['quote_ref'],
        'message':   'Quote received! We will contact you within 2 hours.',
    }), 201


# ── GET /api/quotes — List all quotes (for cargo app) ─────────
@app.route('/api/quotes', methods=['GET'])
def list_quotes():
    status = request.args.get('status')   # ?status=New
    limit  = int(request.args.get('limit',  50))
    offset = int(request.args.get('offset',  0))

    conn  = get_db_connection()
    query = 'SELECT * FROM quotes'
    params = []

    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params += [limit, offset]

    rows   = conn.execute(query, params).fetchall()
    total  = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    conn.close()

    return jsonify({
        'success': True,
        'total':   total,
        'quotes':  [dict(r) for r in rows]
    })


# ── GET /api/quote/<id> — Single quote ────────────────────────
@app.route('/api/quote/<int:quote_id>', methods=['GET'])
def get_quote(quote_id):
    conn = get_db_connection()
    row  = conn.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'error': 'Quote not found'}), 404
    return jsonify({'success': True, 'quote': dict(row)})


# ── PUT /api/quote/<id> — Update quote status ─────────────────
@app.route('/api/quote/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data'}), 400

    allowed_statuses = ['New', 'Reviewing', 'Quoted', 'Confirmed', 'Rejected', 'Completed']
    status = data.get('status')

    if status and status not in allowed_statuses:
        return jsonify({'success': False, 'error': f'Invalid status. Use: {allowed_statuses}'}), 422

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()

    updates = []
    params  = []

    if status:
        updates.append('status = ?')
        params.append(status)
    if 'notes' in data:
        updates.append('notes = ?')
        params.append(data['notes'])

    if not updates:
        return jsonify({'success': False, 'error': 'Nothing to update'}), 400

    updates.append('updated_at = ?')
    params.append(now)
    params.append(quote_id)

    conn.execute(f'UPDATE quotes SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Quote {quote_id} updated'})


# ── GET /api/stats — Dashboard stats for cargo app ────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    stats = {}
    for status in ['New', 'Reviewing', 'Quoted', 'Confirmed', 'Completed', 'Rejected']:
        count = conn.execute(
            'SELECT COUNT(*) FROM quotes WHERE status = ?', (status,)
        ).fetchone()[0]
        stats[status.lower()] = count
    stats['total'] = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]

    # Today's quotes
    today = datetime.now().strftime('%Y-%m-%d')
    stats['today'] = conn.execute(
        "SELECT COUNT(*) FROM quotes WHERE created_at LIKE ?", (f'{today}%',)
    ).fetchone()[0]

    conn.close()
    return jsonify({'success': True, 'stats': stats})


# ── GET /api/health — Health check ────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status':  'online',
        'service': 'Nasya Cargo Quote API',
        'version': '1.0.0',
        'time':    datetime.now().isoformat()
    })


# ── MAIN ───────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("  NASYA CARGO QUOTE API")
    print("="*50)
    print("  Running at: http://localhost:5000")
    print("  Endpoints:")
    print("    POST /api/quote       → Receive quote")
    print("    GET  /api/quotes      → List all quotes")
    print("    GET  /api/quote/<id>  → Get single quote")
    print("    PUT  /api/quote/<id>  → Update status")
    print("    GET  /api/stats       → Dashboard stats")
    print("    GET  /api/health      → Health check")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
