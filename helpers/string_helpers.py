# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:14:12 2024
@author: NhanLe- Dell
"""

# helpers/string_helpers.py

def capitalize_words(s):
    return ' '.join(word.capitalize() for word in s.split())