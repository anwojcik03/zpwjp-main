import time
from functools import wraps
import streamlit as st


NAMES = {
    "fetch_stock": "historical data fetching",
    "compute_features": "computing stock features (MeanReturn, Volatility, etc.)"
}

def get_name(func_name):
    
    return NAMES.get(func_name, f"function '{func_name}'")

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        
        name = get_name(func.__name__)
        
        
        st.toast(f"{name.capitalize()} finished in {duration:.3f}s.")
        return result
    return wrapper

def cache(func):
    
    if 'custom_memo' not in st.session_state:
        st.session_state['custom_memo'] = {}
    
    @wraps(func)
    def wrapper(*args):
        key = (func.__name__, args)
        
        if key in st.session_state['custom_memo']:
            name = get_name(func.__name__)
            
            st.toast(f"Used cached data for {name}.")
            return st.session_state['custom_memo'][key]
        
        result = func(*args)
        st.session_state['custom_memo'][key] = result
        return result
    return wrapper