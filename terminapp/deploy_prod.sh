cp .env.dev .env
docker compose up -d --build --remove-orphans
echo "✅ Готово билд создан!"

docker compose run web python manage.py loaddata data_fixture/cashflow/base_activity_type.json
docker compose run web python manage.py loaddata data_fixture/cashflow/base_category_data.json
echo "✅ Готово фикстуры загружены!"