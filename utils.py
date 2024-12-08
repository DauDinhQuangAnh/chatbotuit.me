import math
import uuid
import tiktoken
import streamlit as st
import re

# Hàm xử lý dữ liệu theo batch
def process_batch(batch_df, model, collection):
    """Mã hóa và lưu dữ liệu theo batch vào Chroma với kích thước batch đã chỉ định."""
    try:
        # Mã hóa dữ liệu trong cột 'chunk' thành vector cho batch này
        embeddings = model.encode(batch_df['chunk'].tolist())

        # Thu thập tất cả metadata vào một danh sách
        metadatas = [row.to_dict() for _, row in batch_df.iterrows()]

        # Tạo ID duy nhất cho mỗi phần tử trong batch
        batch_ids = [str(uuid.uuid4()) for _ in range(len(batch_df))]

        # Thêm batch vào Chroma
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    # Xử lý ngoại lệ nếu có lỗi trong quá trình mã hóa hoặc thêm vào Chroma
    except Exception as e:
        if str(e) == "'NoneType' object has no attribute 'encode'":
            raise RuntimeError("Vui lòng thiết lập mô hình ngôn ngữ tại phần #1 trước khi chạy xử lý.")
        raise RuntimeError(f"Lỗi khi lưu dữ liệu vào Chroma cho một batch: {str(e)}")

# Hàm chia DataFrame thành các batch nhỏ dựa trên kích thước batch
def divide_dataframe(df, batch_size):
    """Chia DataFrame thành các phần nhỏ dựa trên kích thước batch."""
    num_batches = math.ceil(len(df) / batch_size)  # Tính số lượng batch
    return [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

# Làm sạch tên của collection (tập dữ liệu) để phù hợp với quy định
def clean_collection_name(name):
    # Chỉ cho phép các ký tự chữ và số, gạch dưới, dấu gạch ngang, và một dấu chấm giữa
    cleaned_name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)   # Loại bỏ các ký tự không hợp lệ
    cleaned_name = re.sub(r'\.{2,}', '.', cleaned_name)    # Loại bỏ các dấu chấm liên tiếp
    cleaned_name = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', cleaned_name)  # Loại bỏ ký tự không hợp lệ ở đầu/cuối

    return cleaned_name[:63] if 3 <= len(cleaned_name) <= 63 else None
