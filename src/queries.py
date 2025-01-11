sql_query = """
WITH 
ranked_prices AS (
    SELECT 
        product_name,
        product_price,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY created_at DESC) AS row_num_desc, -- PRECO ATUAL
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY product_price ASC) AS row_num_asc
    FROM dw_lcs.wish_list
),
prices AS (
SELECT 
    product_name,
    MAX(CASE WHEN row_num_asc = 1 THEN product_price END) AS min_price,
    MAX(CASE WHEN row_num_desc = 1 THEN product_price END) AS current_price
FROM ranked_prices
GROUP BY product_name
),
final_query AS (
SELECT 
    product_name,
    current_price,
    CASE
    	WHEN current_price > min_price THEN 'O PREÇO AUMENTOU'
    	WHEN current_price = min_price THEN 'MENOR PRECO REGISTRADO!' 
    END PRECO,
    abs(min_price - current_price) AS dif
FROM prices
)
SELECT
product_name,
current_price,
CASE 
	WHEN dif > 0 THEN concat(preco,' EM R$ ',dif)
	ELSE preco
END AS preco
FROM final_query;
"""