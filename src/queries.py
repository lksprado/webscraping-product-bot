sql_query = """
WITH ranked_prices AS (
    SELECT 
        product_name,
        product_price,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY created_at ASC) AS row_num_asc,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY created_at DESC) AS row_num_desc
    FROM dw_lcs.wish_list
),
final_query AS (
SELECT 
    product_name,
    MAX(CASE WHEN row_num_asc = 1 THEN product_price END) AS first_price,
    MAX(CASE WHEN row_num_desc = 1 THEN product_price END) AS current_price,
    CASE
    	WHEN  MAX(CASE WHEN row_num_asc = 1 THEN product_price END) < MAX(CASE WHEN row_num_desc = 1 THEN product_price END) THEN 'PRECO AUMENTOU'
    	WHEN  MAX(CASE WHEN row_num_asc = 1 THEN product_price END) > MAX(CASE WHEN row_num_desc = 1 THEN product_price END) THEN 'PRECO DIMINUIU'
    	ELSE 'MANTEVE'    	
    END PRECO
FROM ranked_prices
GROUP BY product_name
)
SELECT
product_name,
current_price,
first_price - current_price AS dif,
concat(preco,' EM R$ ',first_price - current_price) AS preco
FROM final_query WHERE PRECO <> 'MANTEVE';
"""