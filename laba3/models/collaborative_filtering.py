import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.sparse import csr_matrix
from typing import Dict, Tuple, List
from tqdm import tqdm
from bot.handlers.start import create_item_id_to_iid
from models.data_loader import prepare_date

def create_user_item_matrix(prepare_date: pd.DataFrame) -> Tuple[csr_matrix, Dict, Dict]:
    """
        Создание юзер-айтем матрицы
        prepare_data - данные о взаимодествии юзеров с айтемами
    """
    user_id_to_uid = {}
    item_id_to_iid = {}
    purches_list = []
    customers_list = []
    items_list = []
    for row in tqdm(prepare_date.itertuples()):
        uid = user_id_to_uid.setdefault(row.customer_id, len(user_id_to_uid))
        iid = item_id_to_iid.setdefault(row.article_id, len(item_id_to_iid))
        customers_list.append(uid)
        items_list.append(iid)
        purches_list.append(1)
        
    user_item_matrix = csr_matrix(
        (purches_list, (customers_list, items_list)),
        shape=(max(customers_list) + 1, max(items_list) + 1)
    )
    return user_item_matrix

def cosine_similarity(matrix: csr_matrix) -> csr_matrix:
    """
    Вычисляет косинусную схожесть
    matrix  - sparse.csr_matrix    (размерность - items*users)
    """
    matrix = matrix.tocsr()
    norms = np.sqrt(np.array(matrix.power(2).sum(axis = 1))).flatten()
    row_indices = np.repeat(np.arange(matrix.shape[0]), np.diff(matrix.indptr))
    data_norm = matrix.data / norms[row_indices]
    matrix_norm = csr_matrix((data_norm, matrix.indices, matrix.indptr), shape=matrix.shape)
    item_item = matrix_norm.dot(matrix_norm.T)
    return item_item

def create_item_item_matrix(user_item_matrix: csr_matrix) -> csr_matrix:
    """
        Создает item-item матрицу схожести с зануленной диагональю
        matrix  - sparse.csr_matrix    (размерность - items*users)
    """
    item_item_matrix_sparse = cosine_similarity(user_item_matrix.T)

    positions_range = range(item_item_matrix_sparse.shape[0])
    matrix_diag_ones = csr_matrix(
        (np.ones(len(positions_range)), (positions_range, positions_range)), 
        item_item_matrix_sparse.shape
    )
    item_item_matrix_wo_diag = item_item_matrix_sparse - matrix_diag_ones
    return item_item_matrix_wo_diag

def get_top_k_items(item_item_matrix_wo_diag: csr_matrix, TOP: int) -> csr_matrix:
    """
        Оставляет только TOP самых похожих товаров для каждого товара
        item_item_matrix_wo_diag - айтем-айтем матрица
        TOP - количество наиболее близких товаров
    """
    item_item_rows = []
    item_item_cols = []
    item_item_data = []
    not_top_k_indices_list = []
    empty_indices_list = []
    for i, item_item_row in tqdm(enumerate(item_item_matrix_wo_diag)):
        if item_item_row.nnz > TOP:
            top_row_args = np.argsort(item_item_row.data)[-TOP:]
            item_item_rows += [i] * TOP
            item_item_cols += item_item_row.indices[top_row_args].tolist()
            item_item_data += item_item_row.data[top_row_args].tolist()
        elif item_item_row.nnz > 0:
            not_top_k_indices_list.append(i)
            item_item_rows += [i] * item_item_row.nnz
            item_item_cols += item_item_row.indices.tolist()
            item_item_data += item_item_row.data.tolist()
        else:
            empty_indices_list.append(i)
    item_item_topk_matrix = csr_matrix(
        (
            item_item_data, 
            (item_item_rows, item_item_cols)
        ),
        shape=(item_item_matrix_wo_diag.shape[0], item_item_matrix_wo_diag.shape[1])
    )
    return item_item_topk_matrix


def get_k_recommendations(new_user_vector: np.array, item_item_matrix: csr_matrix, 
                          k: int = 10) -> List[int]:
    """
        Генерирует рекомендации для нового пользователя
        new_user_vector - вектор взаимодействий пользователя
        item_item_matrix - айтем-айтем матрица схожест
        k: количество рекомендаций
    """
    similarity_scores = item_item_matrix.dot(new_user_vector)
    purchased_indices = np.where(new_user_vector > 0)[0]
    similarity_scores[purchased_indices] = -np.inf
    top_k_indices = np.argsort(similarity_scores)[-k:][::-1]
    item_id_to_iid = create_item_id_to_iid(prepare_date)
    iid_to_item_id = {v: k for k,v in item_id_to_iid.items()}
    recommended_article_ids = [iid_to_item_id[idx] for idx in top_k_indices if idx in iid_to_item_id]
    
    return recommended_article_ids
