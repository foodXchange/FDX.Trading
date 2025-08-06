
cd ~/fdx
cp .env .env.backup
sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require|' .env
echo 'Database connection updated'
grep DATABASE_URL .env
