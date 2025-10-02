import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class QueryParser:
    """Parse natural language queries for payroll and order information"""
    
    def __init__(self):
        self.query_type = None
        self.start_date = None
        self.end_date = None
        self.customer_name = None
    
    def parse(self, query_text):
        """
        Parse the query text and determine query type and parameters
        Returns: dict with query_type, start_date, end_date, customer_name
        """
        query_lower = query_text.lower().strip()
        
        if self._is_payroll_query(query_lower):
            return self._parse_payroll_query(query_lower)
        elif self._is_customer_query(query_lower):
            return self._parse_customer_query(query_text)
        else:
            return {
                'query_type': 'unknown',
                'message': 'I can help you with payroll queries (this week, this month, this year, last month, or custom date ranges) and customer order lookups. Try asking "Show me payroll for this month" or "Find orders for Alice Johnson".'
            }
    
    def _is_payroll_query(self, query):
        """Check if query is about payroll"""
        payroll_keywords = ['payroll', 'payout', 'payment', 'salary', 'earnings', 'compensation']
        customer_keywords = ['customer', 'order', 'project', 'client']
        
        has_payroll = any(keyword in query for keyword in payroll_keywords)
        has_customer = any(keyword in query for keyword in customer_keywords)
        
        if has_payroll and not has_customer:
            return True
        elif has_payroll and has_customer:
            return 'for' not in query and 'by' not in query
        return False
    
    def _is_customer_query(self, query):
        """Check if query is about customer/orders"""
        customer_keywords = ['customer', 'order', 'project', 'client']
        return any(keyword in query for keyword in customer_keywords)
    
    def _parse_payroll_query(self, query):
        """Parse payroll-specific query for date ranges"""
        today = datetime.now().date()
        
        if 'this week' in query:
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            period_name = "this week"
        
        elif 'this month' in query:
            start_date = today.replace(day=1)
            next_month = start_date + relativedelta(months=1)
            end_date = next_month - timedelta(days=1)
            period_name = "this month"
        
        elif 'last month' in query:
            first_of_this_month = today.replace(day=1)
            end_date = first_of_this_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
            period_name = "last month"
        
        elif 'this year' in query:
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            period_name = "this year"
        
        else:
            date_range = self._extract_date_range(query)
            if date_range:
                start_date, end_date = date_range
                period_name = f"from {start_date} to {end_date}"
            else:
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=12, day=31)
                period_name = "this year (default)"
        
        return {
            'query_type': 'payroll',
            'start_date': start_date,
            'end_date': end_date,
            'period_name': period_name
        }
    
    def _parse_customer_query(self, query):
        """Parse customer/order query to extract customer name"""
        patterns = [
            r'(?:show|get|list)\s+(?:me\s+)?customer\s+([a-z][a-z\s]+?)(?:\s*$|\?|\'s)',
            r'customer\s+(?:named?\s+)?([a-z][a-z\s]+?)(?:\s*$|\?|\'s|\s+orders?|\s+projects?)',
            r'orders?\s+(?:for|from|by)\s+([a-z][a-z\s]+?)(?:\s*$|\?)',
            r'projects?\s+(?:for|from|by)\s+([a-z][a-z\s]+?)(?:\s*$|\?)',
            r'(?:does|do)\s+([a-z][a-z\s]+?)\s+have',
            r'find\s+(?:customer\s+)?([a-z][a-z\s]+?)(?:\s+orders?|\s+projects?|\s*$|\?)',
            r'(?:show|get|list)\s+(?:me\s+)?(?:orders?|projects?)\s+(?:for|from|by)\s+([a-z][a-z\s]+?)(?:\s*$|\?)',
            r'(?:what|which)\s+(?:orders?|projects?)\s+(?:does|do)\s+([a-z][a-z\s]+?)\s+have',
        ]
        
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                customer_name = match.group(1).strip()
                customer_name = ' '.join(customer_name.split())
                if customer_name and len(customer_name) > 2:
                    return {
                        'query_type': 'customer',
                        'customer_name': customer_name.title()
                    }
        
        return {
            'query_type': 'customer',
            'error': True,
            'message': 'Please specify a customer name, for example: "Show orders for Alice Johnson" or "Find customer John Doe".'
        }
    
    def _extract_date_range(self, query):
        """Extract custom date range from query"""
        date_patterns = [
            r'(?:from|between)\s+(\d{4}-\d{2}-\d{2})\s+(?:to|and)\s+(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
            r'between\s+(\d{4}-\d{2}-\d{2})\s+and\s+(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, query)
            if match:
                try:
                    start_str, end_str = match.groups()
                    start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                    return (start_date, end_date)
                except ValueError:
                    continue
        
        return None
