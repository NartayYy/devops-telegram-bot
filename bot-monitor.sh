#!/bin/bash

echo "=== Telegram Bot DevOps Monitor ==="
echo "Time: $(date)"
echo ""

echo "=== Docker Compose Services ==="
docker-compose ps
echo ""

echo "=== Bot Logs (last 10 lines) ==="
docker-compose logs --tail=10 telegram-bot
echo ""

echo "=== Database Connection Test ==="
docker-compose exec -T mysql mysql -uroot -pbotpassword -e "SELECT COUNT(*) as total_messages FROM bot_db.user_messages;"
echo ""

echo "=== Redis Status ==="
docker-compose exec -T redis redis-cli ping
echo ""

echo "=== Resource Usage ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

echo "=== Network Status ==="
docker network ls | grep telegram-bot-project
