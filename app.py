import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from parser import parse_pdf
from excel_generator import generate_excel

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
        
    if file and allowed_file(file.filename):
        # Save file with a unique name to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse statement
            metadata, transactions = parse_pdf(filepath)
            
            # Clean up the uploaded PDF file after parsing
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return jsonify({
                'success': True,
                'metadata': metadata,
                'transactions': transactions
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Cleanup on failure
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Failed to parse PDF statement: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Allowed file types are: pdf'}), 400

@app.route('/api/export', methods=['POST'])
def export_excel():
    data = request.get_json() or {}
    metadata = data.get('metadata', {})
    transactions = data.get('transactions', [])
    currency_symbol = data.get('currency', '₹')
    
    if not transactions:
        return jsonify({'error': 'No transaction data provided for export'}), 400
        
    try:
        # Create a unique filename for the download
        unique_id = str(uuid.uuid4())[:8]
        filename = f"statement_analysis_{unique_id}.xlsx"
        filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        # Generate styled Excel
        generate_excel(metadata, transactions, filepath, currency_symbol)
        
        return jsonify({
            'success': True,
            'download_url': f'/api/download/{filename}'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to generate Excel file: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    # Security check to prevent path traversal
    filename = secure_filename(filename)
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Binds to 0.0.0.0 to make the server accessible over the local network (LAN)
    app.run(debug=True, host='0.0.0.0', port=5000)
