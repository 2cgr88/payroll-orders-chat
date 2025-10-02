# payroll-orders-chat
A secure chat-based web app where agents log in to query payroll totals and customer orders using natural language.

# Agent Dashboard - Payroll & Order Query System

A secure web application that enables agents to query payroll data and customer order information through a ChatGPT-style conversational interface.

## Features

- **Secure Authentication**: Email/password login with bcrypt password hashing
- **ChatGPT-Style Interface**: Intuitive chat interface with scrollable message history
- **Natural Language Processing**: Understands various query formats for payroll and orders
- **Payroll Queries**: Get payroll summaries for different time periods
- **Customer Order Lookup**: Find project details by customer name
- **Session Persistence**: Chat history preserved during browser session

## Tech Stack

**Backend:**
- Python 3.11
- Flask (web framework)
- PyMySQL (MySQL database connector)
- bcrypt (password hashing)
- python-dateutil (date parsing)

**Frontend:**
- HTML5
- CSS3 (responsive design with gradients)
- Vanilla JavaScript

## Setup Instructions

### Prerequisites

1. MySQL database server running with the following schema:
   - `user_employees` table
   - `orders` table
   - `payout` table
   
   (See database schema in `Database.pdf`)

2. Python 3.11 or higher

### Installation

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install flask pymysql bcrypt python-dateutil
   ```

3. **Configure database connection**
   
   Set the following environment variables (or use Replit Secrets):
   ```
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=test
   SESSION_SECRET=your_secret_key
   ```

4. **Update user passwords in database**
   
   Run the password setup script to hash the test passwords:
   ```bash
   python3 setup_passwords.py
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```
   
   The application will be available at `http://localhost:5000`

## Test Credentials

Use these credentials to log in:

| Email | Password | Position |
|-------|----------|----------|
| john@example.com | john123 | Sales Closer |
| jane@example.com | jane123 | Sales Manager |
| mike@example.com | mike123 | Installer |

**Note**: Mike's account is set to "Inactive" in the database and cannot log in unless status is changed to "Active".

## Usage Examples

### Payroll Queries

The system understands various time-based queries:

- **This week**: "Show me payroll for this week"
- **This month**: "What's the payroll for this month?"
- **Last month**: "Payroll for last month"
- **This year**: "Show payroll this year"
- **Custom date range**: "Payroll from 2025-08-01 to 2025-08-31"
- **Alternative formats**: "Show me payments between 2025-08-01 and 2025-08-15"

### Customer Order Queries

Find customer orders by name:

- "Find orders for Alice Johnson"
- "Show me customer John Doe"
- "What projects does Bob Williams have?"
- "Customer Charlie Green orders"

## NLP Approach & Assumptions

### Natural Language Processing Strategy

The application uses a rule-based NLP parser (`nlp_parser.py`) that:

1. **Query Classification**: Identifies query type (payroll vs. customer orders) using keyword matching
2. **Date Extraction**: Uses regex patterns to extract date ranges from natural language
3. **Entity Recognition**: Extracts customer names from various query formats

### Keyword Detection

**Payroll Keywords**: payroll, payout, payment, pay, salary, earnings, compensation

**Customer Keywords**: customer, order, project, client

### Date Parsing Logic

- **Relative dates**: Calculated from current date using Python's `datetime` and `dateutil`
  - "this week" = Monday to Sunday of current week
  - "this month" = 1st to last day of current month
  - "last month" = 1st to last day of previous month
  - "this year" = January 1st to December 31st of current year

- **Custom dates**: Extracted using regex patterns that match:
  - `from YYYY-MM-DD to YYYY-MM-DD`
  - `between YYYY-MM-DD and YYYY-MM-DD`
  - `YYYY-MM-DD to YYYY-MM-DD`

### Customer Name Extraction

Uses multiple regex patterns to handle various query formats:
- "customer [name]"
- "orders for [name]"
- "find [name]"
- "show orders by [name]"

Names are title-cased for database matching with fuzzy LIKE search.

### Assumptions

1. **Date Formats**: Custom dates must be in ISO format (YYYY-MM-DD)
2. **Case Insensitive**: All queries are converted to lowercase for matching
3. **Partial Matching**: Customer names use SQL LIKE with wildcards for flexible matching
4. **Single Query Type**: Each message handles one query type (either payroll OR customer)
5. **Active Sessions**: Users must be logged in with "Active" status
6. **Browser Sessions**: Chat history persists only in current browser session (sessionStorage)

## Project Structure

```
.
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── db.py                   # Database connection utilities
├── nlp_parser.py          # Natural language query parser
├── setup_passwords.py      # Password hashing setup script
├── templates/
│   ├── login.html         # Login page
│   └── dashboard.html     # Chat dashboard
├── static/
│   ├── style.css          # Stylesheet
│   └── chat.js            # Chat interface JavaScript
├── requirements.txt        # Required libariries
└── README.md              # This file
```

## Security Features

- **Password Hashing**: All passwords stored using bcrypt with salt
- **Session Management**: Flask sessions with secret key
- **SQL Injection Prevention**: Parameterized queries using PyMySQL
- **Status Verification**: Only "Active" users can log in
- **Environment Variables**: Sensitive credentials stored in environment secrets

## Development Notes

### Time Log & Key Decisions

1. **Framework Choice**: Flask chosen for simplicity and Python compatibility
2. **Database**: PyMySQL selected for pure-Python MySQL connectivity
3. **NLP Approach**: Rule-based parsing selected over ML for reliability and transparency
4. **Frontend**: Vanilla JS to avoid framework overhead for simple chat UI
5. **Storage**: Session storage for chat history (easy to upgrade to database later)
6. **Security**: bcrypt for password hashing (industry standard)
7. **Date Handling**: python-dateutil for robust date calculations

### Potential Improvements

- Database-backed chat history for persistence across sessions
- More advanced NLP using spaCy or transformers for intent classification
- Export functionality (CSV/PDF) for payroll reports
- Real-time notifications using WebSockets
- Admin dashboard for user management
- Multi-language support
- Enhanced date parsing (e.g., "last week", "yesterday", "Q3 2025")
- Autocomplete suggestions for customer names

## Database Schema Reference

The application expects the following MySQL tables (as provided):

- **user_employees**: Employee records with authentication
- **orders**: Customer project/order information
- **payout**: Payroll transaction records with dates and types

See `Database.pdf` for complete schema and sample data.

## Troubleshooting

**Connection Refused Error**: Ensure MySQL server is running and credentials are correct

**Login Failed**: Verify passwords have been updated using `setup_passwords.py`

**No Data Returned**: Check that sample data exists in database tables

**Session Errors**: Ensure `SESSION_SECRET` environment variable is set

## env file structure 
DB_HOST=localhost
DB_PORT=3306(by default)
DB_USER=user name
DB_PASSWORD=your password
DB_NAME=Database name
SESSION_SECRET=secret_key

## License

This project was created as a demonstration application for agent payroll and order query functionality.
