# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:02:24 2024
@author: NhanLe
Common fucntions
"""

# math_helpers.py

#############################################
# Function DIVIDE(a,b,NaN)
# Process all NULL NaN value | empty from denominator b
# np.divide được sử dụng với các tham số out và where để xử lý phép chia. 
# out=np.zeros_like(a, dtype=float) sẽ đảm bảo rằng nếu có lỗi xảy ra trong phép chia, giá trị 0 sẽ được trả về.
# Tham số where xác định điều kiện thực hiện phép chia, đảm bảo rằng phép chia chỉ được thực hiện khi b không phải là 0 và không phải là NaN.
#############################################
def divide(a, b):
    import numpy as np
    return np.divide(a, b, out=np.zeros_like(a, dtype=float), where=(b != 0) & ~np.isnan(b))
