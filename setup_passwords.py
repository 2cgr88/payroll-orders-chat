import pymysql
from config import Config

def update_passwords():
    """Update user passwords with bcrypt hashed test passwords"""
    connection = pymysql.connect(
        host=Config.DB_CONFIG['host'],
        user=Config.DB_CONFIG['user'],
        password=Config.DB_CONFIG['password'],
        database=Config.DB_CONFIG['database'],
        port=Config.DB_CONFIG['port']
    )
    
    try:
        with connection.cursor() as cursor:
            passwords = {
                'john@example.com': '$2b$12$25jqUYRGK7M5sTSiiXZ71eDl40d0LtPj1W6xb1tKII8CYdKhAPSna',
                'jane@example.com': '$2b$12$DWunt9foHvZqZUM9PBz9Z.TuTiUJ3sXrOgWZ5uP5WtxIkZCl24Eoq',
                'mike@example.com': '$2b$12$G6iqF.XpqOodPb/hxqGYu.3HriJUlfyyrx.coVrJH0dyuE5ouh35y'
            }
            
            for email, password_hash in passwords.items():
                cursor.execute(
                    "UPDATE user_employees SET Password = %s WHERE Email = %s",
                    (password_hash, email)
                )
                print(f"Updated password for {email}")
            
            connection.commit()
            print("\nAll passwords updated successfully!")
            print("\nTest credentials:")
            print("- john@example.com / john123")
            print("- jane@example.com / jane123")
            print("- mike@example.com / mike123")
            
    except Exception as e:
        print(f"Error updating passwords: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    update_passwords()
