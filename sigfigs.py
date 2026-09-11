"""Significant-figure parsing and rounding from the student's original text."""
import re
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP

NUMBER=re.compile(r'^[+-]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][+-]?\d+)?$')

def decimal_value(text):
    if not isinstance(text,str) or not NUMBER.fullmatch(text.strip()):
        raise ValueError('Enter one ordinary or scientific-notation number')
    try: value=Decimal(text.strip())
    except InvalidOperation as exc: raise ValueError('Invalid number') from exc
    if not value.is_finite(): raise ValueError('Number must be finite')
    return value

def count_sig_figs(text):
    raw=text.strip() if isinstance(text,str) else ''
    decimal_value(raw)
    mantissa=raw.lower().split('e',1)[0].lstrip('+-')
    if '.' in mantissa:
        digits=mantissa.replace('.','').lstrip('0')
        return len(digits) if digits else len(mantissa.split('.',1)[1])
    digits=mantissa.lstrip('0').rstrip('0')
    return len(digits) if digits else 1

def round_sig_figs(value_text,figures):
    if type(figures) is not int or not 1<=figures<=15: raise ValueError('Significant figures must be 1–15')
    value=decimal_value(value_text)
    if value==0:return '0.'+'0'*(figures-1) if figures>1 else '0'
    quantum=Decimal(1).scaleb(value.copy_abs().adjusted()-figures+1)
    rounded=value.quantize(quantum,rounding=ROUND_HALF_UP)
    return format(rounded,'f')

def analyze_sig_figs(value_text,expected=None):
    count=count_sig_figs(value_text)
    result={'status':'sig_figs_counted','count':count,'message':f'{value_text.strip()} has {count} significant figure'+('' if count==1 else 's')+'.'}
    if expected is not None:
        if type(expected) is not int or not 1<=expected<=15:raise ValueError('Expected significant figures must be 1–15')
        result['status']='sig_figs_match' if count==expected else 'sig_figs_review'
        result['message']+=(' It matches the requested precision.' if count==expected else f' The requested precision is {expected}; review leading and trailing zeros.')
    return result

