import pandas as pd
from models.topk import top_popularity_items, top_popularity_items_by_index, top_popularity_items_by_index

data = pd.read_csv('laba3\\data\\transactions_train.csv')
articles = pd.read_csv('laba3\\data\\articles.csv')

d = (
    data
    .groupby('article_id')
    .size()
    .reset_index(name='purchase_count')
)

clean_data = d[d['purchase_count'] > 304]

mask = articles['article_id'].isin(clean_data['article_id'])
articles = articles[mask]
articles.shape[0]

mask = data['article_id'].isin(clean_data['article_id'])
data = data[mask]

top_at_all = top_popularity_items(data, k = 6)

prepare_date = data.merge(
    articles[['article_id', 'index_group_name', 'product_group_name']],
    on = 'article_id',
    how = 'left'
)
prepare_date = prepare_date[['customer_id', 'article_id', 'index_group_name', 'product_group_name']]


def get_name_by_label(articles: pd.DataFrame = articles, top_at_all: list = top_at_all) -> list:
    """
    Получает названия и описания для списка article_id

    articles - информацией о товарах
    top_at_all - список article_id
    """   
    filtered_articles = articles[articles['article_id'].isin(top_at_all)]
    result = []
    
    for _, row in filtered_articles.iterrows():
        result.append({
            'name': row['prod_name'],
            'desc': row['detail_desc']
        })
    return result
