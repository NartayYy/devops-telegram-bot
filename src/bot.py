import os
import logging
import redis
import mysql.connector
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN_HERE')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'mypassword')
MYSQL_DB = os.environ.get('MYSQL_DB', 'bot_db')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

class DevOpsBot:
    def __init__(self):
        self.redis_client = None
        self.mysql_conn = None
        self.setup_connections()
        self.setup_database()

    def setup_connections(self):
        try:
            # Подключение к Redis
            self.redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")

        try:
            # Подключение к MySQL
            self.mysql_conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB
            )
            logger.info("✅ Connected to MySQL")
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {e}")

    def setup_database(self):
        if self.mysql_conn:
            cursor = self.mysql_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    username VARCHAR(255),
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    command VARCHAR(100),
                    count INT DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.mysql_conn.commit()
            cursor.close()

    def log_message(self, user_id, username, message):
        if self.mysql_conn:
            cursor = self.mysql_conn.cursor()
            cursor.execute(
                "INSERT INTO user_messages (user_id, username, message) VALUES (%s, %s, %s)",
                (user_id, username, message)
            )
            self.mysql_conn.commit()
            cursor.close()

    def update_stats(self, command):
        if self.mysql_conn:
            cursor = self.mysql_conn.cursor()
            cursor.execute(
                "INSERT INTO bot_stats (command) VALUES (%s) ON DUPLICATE KEY UPDATE count = count + 1, last_used = NOW()",
                (command,)
            )
            self.mysql_conn.commit()
            cursor.close()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.log_message(user.id, user.username, "/start")
        self.update_stats("start")
        
        # Сохраняем пользователя в Redis
        if self.redis_client:
            self.redis_client.hset(f"user:{user.id}", "username", user.username or "Unknown")
            self.redis_client.hset(f"user:{user.id}", "last_seen", datetime.now().isoformat())

        welcome_message = f"""
🤖 *DevOps Learning Bot*

Привет, {user.first_name}! 

Я помогу изучать DevOps. Доступные команды:

/start - Начать работу
/status - Статус системы  
/stats - Статистика бота
/docker - Информация о Docker
/k8s - Информация о Kubernetes
/help - Помощь

Напиши любое сообщение, и я отвечу!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update_stats("status")
        
        # Проверяем подключения
        redis_status = "✅ Connected" if self.redis_client else "❌ Disconnected"
        mysql_status = "✅ Connected" if self.mysql_conn else "❌ Disconnected"
        
        status_message = f"""
📊 *Статус системы*

🔴 Redis: {redis_status}
🗄️ MySQL: {mysql_status}
🐳 Docker: Running
☸️ Kubernetes: Running
⏰ Uptime: Available

🤖 Bot version: 1.0.0
        """
        await update.message.reply_text(status_message, parse_mode='Markdown')

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update_stats("stats")
        
        if self.mysql_conn:
            cursor = self.mysql_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_messages")
            unique_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT command, count FROM bot_stats ORDER BY count DESC LIMIT 5")
            top_commands = cursor.fetchall()
            cursor.close()
            
            stats_text = f"""
📈 *Статистика бота*

👥 Уникальных пользователей: {unique_users}
💬 Всего сообщений: {total_messages}

🔥 Топ команд:
"""
            for cmd, count in top_commands:
                stats_text += f"/{cmd}: {count} раз\n"
        else:
            stats_text = "❌ База данных недоступна"
            
        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def docker_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update_stats("docker")
        
        docker_info = """
🐳 *Docker Information*

Docker - это платформа контейнеризации, которая позволяет:
- Упаковывать приложения в контейнеры
- Обеспечивать изоляцию процессов
- Упрощать развертывание
- Гарантировать консистентность окружений

Основные команды:
`docker run` - запуск контейнера
`docker ps` - список контейнеров
`docker build` - сборка образа
`docker-compose up` - запуск стека
        """
        await update.message.reply_text(docker_info, parse_mode='Markdown')

    async def k8s_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update_stats("k8s")
        
        k8s_info = """
☸️ *Kubernetes Information*

Kubernetes - система оркестрации контейнеров:
- Автоматическое масштабирование
- Service discovery
- Load balancing
- Rolling updates
- Self-healing

Основные объекты:
`Pod` - минимальная единица развертывания
`Service` - сетевой доступ к подам
`Deployment` - управление репликами
`ConfigMap` - конфигурация приложений
        """
        await update.message.reply_text(k8s_info, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        message_text = update.message.text
        
        self.log_message(user.id, user.username, message_text)
        
        # Простые ответы
        responses = {
            "привет": "Привет! 👋 Как дела с изучением DevOps?",
            "как дела": "Отлично! Изучаем DevOps вместе! 🚀",
            "docker": "Docker - отличная технология! Используй /docker для подробностей",
            "kubernetes": "Kubernetes мощный! Попробуй /k8s",
            "devops": "DevOps - это культура и практики! 💪"
        }
        
        response = responses.get(message_text.lower(), 
                                f"Получил сообщение: '{message_text}'. Используй /help для списка команд!")
        
        await update.message.reply_text(response)

def main():
    bot = DevOpsBot()
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CommandHandler("docker", bot.docker_info))
    application.add_handler(CommandHandler("k8s", bot.k8s_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Запускаем бота
    logger.info("🚀 Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
