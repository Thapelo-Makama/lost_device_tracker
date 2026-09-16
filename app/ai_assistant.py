from flask import current_app
from difflib import get_close_matches

class AIAssistant:
    def __init__(self):
        self.api_key = None

    def initialize(self):
        self.api_key = current_app.config.get('OPENAI_API_KEY')

    def generate_response(self, msg, user_context=None, page_url=None, user_id=None):
        return self._match(msg.lower().strip())

    def _match(self, msg):
        topics = {
            'register': (['register','sign up','signup','create account','new user','registration'],
                "📝 <b>How to Register:</b><br><br>"
                "1. Click 'Register' at the top right<br>"
                "2. Fill in: Username, Email, Full Name, Phone, SA ID<br>"
                "3. Create a password (min 8 characters)<br>"
                "4. Submit the form<br>"
                "5. Wait for admin approval ⏳<br>"
                "6. Once approved, you can login and register devices"),
            'login': (['login','sign in','log in','cant login',"can't login",'forgot password'],
                "🔐 <b>How to Login:</b><br><br>"
                "1. Go to the Login page<br>"
                "2. Enter your username and password<br>"
                "3. Click 'Sign In'<br><br>"
                "<b>Trouble?</b><br>"
                "• Check Caps Lock<br>"
                "• Contact admin if you forgot your password<br>"
                "• Your account must be approved by admin first"),
            'track': (['track','location','find','where','locate','gps','map'],
                "📍 <b>How to Track Your Device:</b><br><br>"
                "1. Login to your account<br>"
                "2. Go to Dashboard<br>"
                "3. Find your device in the list<br>"
                "4. Click 'Track'<br>"
                "5. The map shows the last known location<br>"
                "6. Click 'Update Location' to share current GPS<br><br>"
                "<b>Important:</b> GPS must be enabled on your device"),
            'evidence': (['evidence','affidavit','receipt','proof','upload','document','verify'],
                "📄 <b>How to Upload Evidence:</b><br><br>"
                "1. Login and open your device<br>"
                "2. Click 'Upload Evidence'<br>"
                "3. Choose type: Affidavit, Receipt, Photo, ID<br>"
                "4. Upload your file (PDF, JPG, PNG, DOC)<br>"
                "5. Add a description<br>"
                "6. Submit<br><br>"
                "⏳ Admin will verify within 24-48 hours"),
            'admin': (['admin','contact admin','support','message admin'],
                "👤 <b>How to Contact Admin:</b><br><br>"
                "1. Go to Messages<br>"
                "2. Click 'New Message'<br>"
                "3. Select 'admin' as recipient<br>"
                "4. Type your message<br>"
                "5. Send<br><br>"
                "Admin can help with: device tracking, evidence verification, police reports, account issues"),
            'report': (['report','police','case','officer','station','saps'],
                "🚔 <b>How to File a Police Report:</b><br><br>"
                "1. Login and open your device<br>"
                "2. Click 'File Report'<br>"
                "3. Fill in: description, police station, case number<br>"
                "4. Submit<br><br>"
                "Admin will review and share location data with SAPS"),
            'platform': (['platform','what is','about','system','website','how does','explain'],
                "🌐 <b>Welcome to the Lost Device Tracking System!</b><br><br>"
                "<b>Features:</b><br>"
                "• Register your devices with IMEI/serial numbers<br>"
                "• Upload ownership evidence (affidavit, receipts)<br>"
                "• Track device locations with GPS<br>"
                "• Communicate with admin<br>"
                "• File police reports<br>"
                "• Admin verifies ownership and assists with recovery"),
            'device': (['device','register device','add device','phone','laptop','tablet'],
                "📱 <b>How to Register a Device:</b><br><br>"
                "1. Login to your account<br>"
                "2. Click 'Register Device'<br>"
                "3. Enter: device name, type, IMEI, serial, brand, model, color<br>"
                "4. If lost, check 'Mark as Lost' and enter date/location<br>"
                "5. Submit<br><br>"
                "💡 Keep your IMEI/serial safe — it proves ownership"),
            'message': (['message','chat','send','inbox','communicate'],
                "💬 <b>How to Send a Message:</b><br><br>"
                "1. Click 'Messages' in the navbar<br>"
                "2. Click 'New Message'<br>"
                "3. Choose recipient (a user or admin)<br>"
                "4. Type subject and message<br>"
                "5. Send"),
            'imei': (['imei','serial','imei number'],
                "🔢 <b>What is IMEI?</b><br><br>"
                "IMEI (International Mobile Equipment Identity) is a unique 15-digit number for phones. "
                "You can find it by dialing <b>*#06#</b> on your phone, on the SIM tray, or on the box.<br><br>"
                "It helps prove the device is yours and is used by SAPS for recovery."),
            'lock': (['lock','locked','locking'],
                "🔒 <b>Locking a Device:</b><br><br>"
                "On your device page, you can mark it as lost/locked. "
                "This tells admin that the device needs recovery assistance."),
            'help': (['help','support','guide','assist','what can'],
                "❓ <b>I can help with:</b><br><br>"
                "• How to register an account<br>"
                "• How to login<br>"
                "• How to register a device<br>"
                "• How to upload evidence<br>"
                "• How to track a device<br>"
                "• How to contact admin<br>"
                "• How to file a police report<br>"
                "• What is IMEI<br><br>"
                "Just ask your question!"),
        }
        for key, (kw_list, resp) in topics.items():
            for kw in kw_list:
                if kw in msg:
                    return resp
        all_kw = [k for v in topics.values() for k in v[0]]
        matches = get_close_matches(msg, all_kw, n=1, cutoff=0.55)
        if matches:
            for key, (kw_list, resp) in topics.items():
                if matches[0] in kw_list:
                    return resp
        return ("I'm here to help with the Lost Device Tracking System!<br><br>"
                "Try asking:<br>"
                "• <i>How do I register?</i><br>"
                "• <i>How do I track a device?</i><br>"
                "• <i>How do I upload evidence?</i><br>"
                "• <i>What is IMEI?</i><br>"
                "• <i>How do I contact admin?</i>")

    def get_suggestion_buttons(self, page_url):
        mapping = {
            '/': ["What is this platform?", "How to register?", "How to track?"],
            '/auth/login': ["How to register?", "Forgot password?", "Why pending approval?"],
            '/auth/register': ["What details do I need?", "How long for approval?"],
            '/dashboard/user': ["How to register a device?", "Upload evidence?", "Track device?"],
            '/dashboard/admin': ["How to approve users?", "Verify evidence?"],
            '/devices/register': ["What is IMEI?", "How to prove ownership?"],
        }
        for path, b in mapping.items():
            if path in page_url:
                return b
        return ["What is this platform?", "How to track?", "Contact admin"]
