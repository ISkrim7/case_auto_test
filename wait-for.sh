#!/bin/sh

until mysqladmin ping -h "127.0.0.1" -P "3306" -u "root" -p "sdkjfhsdkjhfsdkhfksd" --silent; do
    echo "Waiting for MySQL to be available..."
    sleep 1
done

until redis-cli -h "127.0.0.1" ping; do
    echo "Waiting for Redis to be available..."
    sleep 1
done

echo "All dependencies are ready!"
exec "$@"