import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
from typing import List, Dict
from tqdm import tqdm

def create_item_id_to_iid(prepare_date: pd.DataFrame) -> Dict:
    """
        Создание словаря item - id
        prepare_data - данные о взаимодествии юзеров с айтемами
    """
    item_id_to_iid = {}
    for row in tqdm(prepare_date.itertuples()):
        iid = item_id_to_iid.setdefault(row.article_id, len(item_id_to_iid))
    return item_id_to_iid


def get_vector_for_new_customers(user_selected_labels: list, item_id_to_iid: dict, articles: pd.DataFrame) -> np.ndarray:
    """
    Создает вектор для нового пользователя на основе выбранных категорий

    user_selected_labels - список выбранных айтемов
    item_id_to_iid - маппинг article_id -> индекс в матрице
    articles - DataFrame с информацией о товарах
    """
    selected_articles = articles[articles['article_id'].isin(user_selected_labels)]
    selected_index_groups = selected_articles['index_group_name'].unique()
    selected_product_groups = selected_articles['product_group_name'].unique()
    matching_articles = articles[
        (articles['index_group_name'].isin(selected_index_groups)) |
        (articles['product_group_name'].isin(selected_product_groups))
    ]
    matching_article_ids = matching_articles['article_id'].tolist()

    new_user_vector = np.zeros(len(item_id_to_iid), dtype=int)
    for article_id in matching_article_ids:
        if article_id in item_id_to_iid: 
            idx = item_id_to_iid[article_id]
            new_user_vector[idx] = 1

    return new_user_vector