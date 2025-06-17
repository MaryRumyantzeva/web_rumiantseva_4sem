class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_by_id(self, user_id):
        """Получить пользователя по ID"""
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT users.*, roles.name as role_name 
                FROM users 
                LEFT JOIN roles ON users.role_id = roles.id 
                WHERE users.id = %s;
            """, (user_id,))
            user = cursor.fetchone()
            return user

    def get_by_username_and_password(self, username, password):
        """Аутентификация пользователя"""
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT users.*, roles.name as role_name 
                FROM users 
                LEFT JOIN roles ON users.role_id = roles.id 
                WHERE username = %s AND password_hash = SHA2(%s, 256);
            """, (username, password))
            # print(cursor.statement)  # Для отладки SQL запроса
            user = cursor.fetchone()
            return user

    def get_all(self):
        """Получить всех пользователей с их ролями"""
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT users.*, roles.name as role_name, roles.description as role_description 
                FROM users 
                LEFT JOIN roles ON users.role_id = roles.id;
            """)
            # print(cursor.statement)  # Для отладки
            users = cursor.fetchall()
            return users

    def create(self, username, password, first_name, middle_name, last_name, role_id):
        """Создать нового пользователя"""
        with self.db_connector.connect().cursor() as cursor:
            cursor.execute("""
                INSERT INTO users 
                (username, password_hash, first_name, middle_name, last_name, role_id) 
                VALUES (%s, SHA2(%s, 256), %s, %s, %s, %s);
            """, (username, password, first_name, middle_name, last_name, role_id))
            self.db_connector.connect().commit()
            return cursor.lastrowid

    def get_volunteers_for_event(self, event_id):
        """Получить волонтеров для конкретного мероприятия"""
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT users.*, volunteer_registrations.status, 
                       volunteer_registrations.registration_date
                FROM volunteer_registrations
                JOIN users ON volunteer_registrations.volunteer_id = users.id
                WHERE volunteer_registrations.event_id = %s;
            """, (event_id,))
            volunteers = cursor.fetchall()
            return volunteers

    def register_volunteer(self, event_id, user_id, contact_info):
        """Зарегистрировать пользователя как волонтера на мероприятие"""
        with self.db_connector.connect().cursor() as cursor:
            cursor.execute("""
                INSERT INTO volunteer_registrations 
                (event_id, volunteer_id, contact_info, status) 
                VALUES (%s, %s, %s, 'pending');
            """, (event_id, user_id, contact_info))
            self.db_connector.connect().commit()
            return cursor.lastrowid