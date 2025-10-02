from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import bcrypt
from db import execute_query
from nlp_parser import QueryParser
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        user = execute_query(
            'SELECT EmpID, Name, Email, Password, Position, Status FROM user_employees WHERE Email = %s',
            (email,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        if user['Status'] != 'Active':
            return jsonify({'success': False, 'message': 'Account is inactive'}), 401
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                session['user_id'] = user['EmpID']
                session['user_name'] = user['Name']
                session['user_email'] = user['Email']
                session['user_position'] = user['Position']
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        except ValueError:
            return jsonify({'success': False, 'message': 'Password not configured. Please run setup_passwords.py first.'}), 500
        
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/dashboard')
def dashboard():
    """Main chat dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_name=session.get('user_name'))

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat queries"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    query_text = data.get('message', '').strip()
    
    if not query_text:
        return jsonify({'success': False, 'message': 'Empty query'}), 400
    
    parser = QueryParser()
    parsed_query = parser.parse(query_text)
    
    if parsed_query.get('error'):
        return jsonify({
            'success': True,
            'message': parsed_query.get('message')
        })
    
    if parsed_query['query_type'] == 'unknown':
        return jsonify({
            'success': True,
            'message': parsed_query.get('message')
        })
    
    elif parsed_query['query_type'] == 'payroll':
        result = get_payroll_data(parsed_query)
        return jsonify({
            'success': True,
            'message': result
        })
    
    elif parsed_query['query_type'] == 'customer':
        result = get_customer_orders(parsed_query)
        return jsonify({
            'success': True,
            'message': result
        })

def get_payroll_data(parsed_query):
    """Retrieve payroll data for the specified period"""
    start_date = parsed_query['start_date']
    end_date = parsed_query['end_date']
    period_name = parsed_query['period_name']
    
    query = """
        SELECT 
            SUM(Amount) as total_amount,
            COUNT(*) as transaction_count,
            Type,
            COUNT(DISTINCT EmpID) as employee_count
        FROM payout
        WHERE PayingDate BETWEEN %s AND %s
        GROUP BY Type
    """
    
    results = execute_query(query, (start_date, end_date))
    
    if not results:
        return f"No payroll data found for {period_name}."
    
    total_sum = sum(row['total_amount'] for row in results if row['total_amount'])
    
    response = f"📊 **Payroll Summary for {period_name}**\n\n"
    response += f"**Total Amount:** ${total_sum:,.2f}\n\n"
    response += "**Breakdown by Type:**\n"
    
    for row in results:
        amount = row['total_amount'] or 0
        count = row['transaction_count']
        payout_type = row['Type']
        response += f"- **{payout_type}:** ${amount:,.2f} ({count} transaction{'s' if count != 1 else ''})\n"
    
    overall_query = """
        SELECT COUNT(DISTINCT EmpID) as total_employees
        FROM payout
        WHERE PayingDate BETWEEN %s AND %s
    """
    emp_result = execute_query(overall_query, (start_date, end_date), fetch_one=True)
    
    response += f"\n**Employees Paid:** {emp_result['total_employees']}"
    response += f"\n**Date Range:** {start_date} to {end_date}"
    
    return response

def get_customer_orders(parsed_query):
    """Retrieve orders for the specified customer"""
    customer_name = parsed_query['customer_name']
    
    query = """
        SELECT 
            o.PID,
            o.CustomerName,
            o.Email,
            o.Phone,
            o.ContractPrice,
            o.SystemSize,
            o.Stage,
            o.Redline,
            e.Name as CloserName
        FROM orders o
        LEFT JOIN user_employees e ON o.Closer = e.EmpID
        WHERE o.CustomerName LIKE %s
        ORDER BY o.PID DESC
    """
    
    results = execute_query(query, (f'%{customer_name}%',))
    
    if not results:
        return f"No orders found for customer matching '{customer_name}'."
    
    if len(results) == 1:
        order = results[0]
        response = f"🔍 **Order Found for {order['CustomerName']}**\n\n"
        response += f"**Project ID:** {order['PID']}\n"
        response += f"**Email:** {order['Email']}\n"
        response += f"**Phone:** {order['Phone']}\n"
        response += f"**Contract Price:** ${order['ContractPrice']:,.2f}\n"
        response += f"**System Size:** {order['SystemSize']}\n"
        response += f"**Stage:** {order['Stage']}\n"
        response += f"**Redline:** {order['Redline']}\n"
        response += f"**Closer:** {order['CloserName']}\n"
    else:
        response = f"🔍 **{len(results)} Orders Found**\n\n"
        for order in results:
            response += f"**{order['CustomerName']}** (PID: {order['PID']})\n"
            response += f"- Contract: ${order['ContractPrice']:,.2f}\n"
            response += f"- System: {order['SystemSize']}\n"
            response += f"- Stage: {order['Stage']}\n"
            response += f"- Closer: {order['CloserName']}\n\n"
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
