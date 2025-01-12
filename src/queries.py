sql_query = """
WITH 
ranked_prices AS (
    SELECT 
        product_name,
        product_price,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY created_at DESC) AS row_num_desc, -- PRECO ATUAL
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY product_price ASC) AS row_num_asc,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY created_at ASC) AS row_num_asc_date
    FROM dw_lcs.wish_list
),
prices AS (
SELECT 
    product_name,
    MAX(CASE WHEN row_num_asc = 1 THEN product_price END) AS min_price,
    MAX(CASE WHEN row_num_desc = 1 THEN product_price END) AS current_price,
	MAX(CASE WHEN row_num_asc_date = 1 THEN product_price END) AS first_price
FROM ranked_prices
GROUP BY product_name
)
,final_query AS (
SELECT 
    product_name,
    current_price,
    CASE
    	WHEN current_price > min_price THEN 'O PREÇO AUMENTOU'
    	WHEN current_price = min_price AND current_price = first_price THEN 'SEM VARIAÇÃO'
    	WHEN current_price = min_price THEN 'ESTÁ COM MENOR PRECO HISTÓRICO! DESCONTO DE' 
    END PRECO,
    abs(min_price - current_price) AS dif,
    abs(first_price - current_price) AS dif_2
FROM prices
)
SELECT
product_name,
current_price,
CASE 
	WHEN dif > 0 THEN concat(preco,' EM R$ ',dif, ' COMPARADO COM O MÍNIMO HISTÓRICO')
	WHEN dif_2 > 0 THEN concat(preco,' R$ ',dif_2)
	ELSE preco
END AS preco
FROM final_query;
"""