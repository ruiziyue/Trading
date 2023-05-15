#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 22:11:53 2023

@author: ericrui
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import backtrader as bt

def next_morning(date_obj):
    current_datetime = date_obj.toordinal()

    if date_obj.weekday() == 4:  # Friday
        return datetime.datetime.fromordinal(current_datetime + 3).replace(hour=7, minute=29, second=0, microsecond=0)

    elif date_obj.weekday() == 5:  # Saturday
        return datetime.datetime.fromordinal(current_datetime + 2).replace(hour=7, minute=29, second=0, microsecond=0)
    
    else:
        return datetime.datetime.fromordinal(current_datetime + 1).replace(hour=7, minute=29, second=0, microsecond=0)
    
class TestStrategy(bt.Strategy):

    params = (
    ('closing_time', datetime.time(15, 59)),
    ('max_time', datetime.time(19, 30)),
    ('pc',11.5),
    ('wt',0.8),
    )
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        tm = self.datas[0].datetime.time()
        #print('%s, %s, %s' % (dt, tm, txt)) #Print date, time and close
        log_entry = '%s, %s, %s\n' % (dt, tm, txt)  # Create the log entry string
        with open("log.txt", "a") as file:
            file.write(log_entry) 

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.es_dataclose = self.datas[0].close
        self.call_dataclose = self.datas[1].close
        self.day_close_price = 0.0
        self.order = None
        self.buyprice = 0.0
        #self.next_morning = datetime.datetime.today()
        self.breakeven = 0.0
#        self.txntime = datetime.datetime.today()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f' %(order.executed.price))

                self.buyprice = order.executed.price
                
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f' %(order.executed.price))

            self.bar_executed = len(self)
            #self.log('position size is %.1f' % self.position.size)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f' %
                 (trade.pnl))
        
    def next(self):
        self.next_morning = next_morning(self.datas[0].datetime.date(0))
        
        if self.datas[0].datetime.date().weekday() !=6 and self.datas[0].datetime.time() == self.params.closing_time:
            self.day_close_price =self.es_dataclose[0]
            

# Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
# Check if we are in the market
        if self.getposition(data=self.datas[1]).size ==0 and self.getposition(data=self.datas[0]).size==0:
#        if not self.position:
            if self.datas[0].datetime.date().weekday() !=6 and self.params.closing_time<self.datas[0].datetime.time()<=self.params.max_time:
                 if self.day_close_price!=0 and self.es_dataclose[0]>(self.day_close_price+self.call_dataclose[0]*0.8):
                     self.log('Threshold reached @ %.2f, Close price is %.2f' % (self.day_close_price+self.call_dataclose[0]*0.8,self.day_close_price))
                     self.log('SELL CREATE, %.2f' % self.es_dataclose[0])
                     self.order = self.sell(data=self.datas[0],size = 1,exectype=bt.Order.Limit,price=self.es_dataclose[0])
                     self.log('Buy CREATE @ %.2f' % self.call_dataclose[0])
                     self.order = self.buy(data = self.datas[1],size = 1)
                     self.breakeven = self.es_dataclose[0]-self.call_dataclose[0]
                     self.log('Limit order should be triggered @ %.2f' % self.breakeven)
        else:
            if self.datas[0].datetime.time(0)>=self.params.max_time or self.datas[0].datetime.time()< datetime.time(7, 29):
                if self.es_dataclose[0]<=self.breakeven:
                    #self.log('maybe triggered') 
                    self.order=self.close(data=self.datas[0],size =1,exectype=bt.Order.Limit,price = self.breakeven)
                
            elif self.datas[0].datetime.time(0)== datetime.time(7, 29) and self.getposition(data=self.datas[0]).size!=0:
                self.order = self.close(data=self.datas[0],size =1,exectype=bt.Order.Limit,price = self.es_dataclose[0])
                self.order = self.close(data=self.datas[1],size =1,price = self.call_dataclose[0])
            
            elif self.datas[0].datetime.time(0)== datetime.time(7, 29) and self.getposition(data=self.datas[0]).size==0:
                self.order = self.close(data=self.datas[1],size =1,price = self.call_dataclose[0])
            
            else:
                return
                #self.log('next morning is %s' %str(self.next_morning))
                #self.log('Call position is %.1f,ES position is %.1f'% (self.getposition(data=self.datas[1]).size,self.getposition(data=self.datas[0]).size))

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    fromdate=datetime.datetime(2022, 1, 1)
    todate=datetime.datetime(2023, 4, 29)

    es_data = bt.feeds.GenericCSVData(
        dataname='ES2022-2023.txt',
        fromdate=fromdate,
        todate=todate,
        nullvalue=0.0,
        dtformat=('%Y%m%d'),
        tmformat=('%H%M'),
        datetime=0,
        time=1,
        high=3,
        low=4,
        open=2,
        close=5,
        volume=6,
        openinterest=-1,
        timeframe=bt.TimeFrame.TFrame("Minutes")
    )   

    call_data = bt.feeds.GenericCSVData(
        dataname='callprice_new.txt',
        fromdate=fromdate,
        todate=todate,
        nullvalue=0.0,
        dtformat=('%Y%m%d'),
        tmformat=('%H%M'),
        datetime=0,
        time=1,
        high=2,
        low=3,
        open=4,
        close=5,
        volume=-1,
        openinterest=-1,
        timeframe=bt.TimeFrame.TFrame("Minutes")
    )
    
    cerebro.adddata(es_data)
    cerebro.adddata(call_data)

    cerebro.addstrategy(TestStrategy)
    cerebro.run()
