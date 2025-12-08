-- SQL запросы для проверки данных в таблицах

-- Проверка таблицы Users
SELECT * FROM erp_tools_users;

-- Проверка таблицы Accounts
SELECT * FROM erp_tools_accounts;

-- Подсчет записей
SELECT 
    (SELECT COUNT(*) FROM erp_tools_users) as users_count,
    (SELECT COUNT(*) FROM erp_tools_accounts) as accounts_count;

-- Детальная информация с JOIN
SELECT 
    u.id as user_id,
    u.phone,
    u.role,
    u.bio,
    u.owner_id,
    a.id as account_id,
    a.slug,
    a.date_create,
    a.date_expired
FROM erp_tools_users u
LEFT JOIN erp_tools_accounts a ON u.owner_id = a.id;

