import pandas as pd
from typing import List

def top_popularity_items(df: pd.DataFrame, k: int = 10) -> List[int]:
    """
        Создает бейзлайн-рекомендации на основе популярных айтемов 
        по всей истории покупок

        df - история покупок 
        k - количество топ айтемов    
    
    """
    top_items = (
        df
        .groupby("article_id", as_index = False)["customer_id"]
        .count()
        .rename(columns = {'customer_id': "purchase_count"})
        .sort_values("purchase_count", ascending = False)
        .head(k)
        ["article_id"]
        .tolist()
    )
    return top_items

def top_popularity_items_by_index(df: pd.DataFrame,index: str, k: int = 10) -> List[int]:
    """
        Создает бейзлайн-рекомендации на основе популярных айтемов 
        каждой группы индексов покупок (женские товары, 
        мужские, детские, спорт)

        df - история покупок 
        k - количество топ айтемов    
    
    """
    top_items = (
        df[df['index_group_name'] == index]
        .groupby( "article_id", as_index = False)["customer_id"]
        .count()
        .rename(columns = {'customer_id': "purchase_count"})
        .sort_values("purchase_count", ascending = False)
        .head(k)
        ["article_id"]
        .tolist()
    )
    return top_items


def top_popularity_items_by_product(df: pd.DataFrame, product: str, k: int = 10) -> List[int]:
    """
        Создает бейзлайн-рекомендации на основе популярных айтемов 
        каждой группы товаров 

        df - история покупок 
        k - количество топ айтемов    
    
    """
    top_items = (
        df[df['product_group_name'] == product]
        .groupby("article_id", as_index = False)["customer_id"]
        .count()
        .rename(columns = {'customer_id': "purchase_count"})
        .sort_values("purchase_count", ascending = False)
        .head(k)
        ["article_id"]
        .tolist()
    )
    return top_items