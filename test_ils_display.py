#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת תצוגת מחירים בשקלים
"""

from dbmodel import PortfolioModel
from portfolio_controller import PortfolioController


def test_ils_display():
    """בודק שהמחירים מוצגים בשקלים"""
    
    print('🔍 בודק תצוגת מחירים בשקלים...')
    print('=' * 50)
    
    # יוצר מופעים
    portfolio_model = PortfolioModel()
    portfolio_controller = PortfolioController(portfolio_model)
    
    # מקבל את התיק
    portfolio = portfolio_controller.get_portfolio()
    
    if not portfolio:
        print('❌ התיק ריק')
        return
    
    print('💰 מחירים בתיק (בשקלים):')
    total_value = 0
    
    for item in portfolio:
        name = item['name']
        price = item['price']
        amount = item['amount']
        value = price * amount
        total_value += value
        
        print(f'   {name}: {amount} × ₪{price:.2f} = ₪{value:,.2f}')
    
    print('=' * 50)
    print(f'💎 סך התיק: ₪{total_value:,.2f}')
    print(f'💵 (בערך ${total_value/3.5:,.2f} בדולר)')
    
    # בדיקה שהמחירים הגיוניים (יותר מ-50 שקל למניה)
    reasonable_prices = all(item['price'] > 50 for item in portfolio)
    
    if reasonable_prices:
        print('✅ כל המחירים נראים הגיוניים בשקלים')
    else:
        print('⚠️ יש מחירים שנראים נמוכים מדי')
    
    return portfolio


if __name__ == '__main__':
    test_ils_display() 