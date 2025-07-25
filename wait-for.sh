#!/bin/sh

until mysqladmin ping -h "127.0.0.1" -P "127.0.0.1" -u "root" -p "127.0.0.1" --silent; do
    echo "Waiting for MySQL to be available..."
    sleep 1
done

#until redis-cli -h "127.0.0.1" ping; do
until redis-cli -h "127.0.0.1" -p "127.0.0.1" -a "127.0.0.1" ping; do
    echo "Waiting for Redis to be available..."
    sleep 1
done

echo "All dependencies are ready!"
exec "$@"