import ccxt
import config
import schedule
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time 
import json 
import threading

import tkinter as tk
from tkinter import messagebox
import threading  # Import the threading module
from datetime import datetime
import pandas as pd
from PIL import Image, ImageTk

from IPython.display import clear_output
import matplotlib
matplotlib.use('Agg')
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

exchange = ccxt.binance({
    "apiKey": 'my5nw1BwA5Hqv8xxZ5rHd8p1xIsZhlojXDv1PRsn85eVjFvjqafvdNpFKQNFOqym',
    "secret": 'jhOz9nwsXSzWFU54RA4rg700dMJL7sQvYmc0SPhTynJneyJ8B4C7SAKGfbGwoco9'
})


        
class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.var = 1 
        self.root.title("Trading Bot")
        
        self.root.grid_rowconfigure(1, minsize=20)
        
        self.crypto_label = tk.Label(root, text="Enter Cryptocurrency Name:")
        self.crypto_label.grid(row=2, column=1, sticky='w')
        
        self.crypto_entry = tk.Entry(root)
        self.crypto_entry.grid(row=2, column=2)
        
        self.time_label = tk.Label(root, text="Enter time period:")
        self.time_label.grid(row=3, column=1, sticky='w')
        
        self.time_entry = tk.Entry(root)
        self.time_entry.grid(row=3, column=2)
        
        self.ST_Period_label = tk.Label(root, text="Enter Super-Trend period:")
        self.ST_Period_label.grid(row=4, column=1,sticky='w')
        
        self.ST_Period_Entry = tk.Entry(root)
        self.ST_Period_Entry.grid(row=4, column=2)
        
        self.ST_mul_label = tk.Label(root, text="Enter Super-Trend multiplier:")
        self.ST_mul_label.grid(row=5,column=1, sticky='w')
        
        self.ST_mul_Entry = tk.Entry(root)
        self.ST_mul_Entry.grid(row=5,column=2)
        
        self.root.grid_rowconfigure(6, minsize=20)
        self.root.grid_rowconfigure(8, minsize=20)

        self.image_label = tk.Label(root, image=photo,bg="Grey")
        self.image_label.grid(row=0, column=0,columnspan=7)
        
  
        self.text = tk.Text(root)
        self.text.grid(row=10, column=0, columnspan=7, pady=8)
        self.text_scrollbar = tk.Scrollbar(root, command=self.text.yview)
        self.text_scrollbar.grid(row=10, column=7, sticky='ns')  
        self.text.config(yscrollcommand=self.text_scrollbar.set) 
        

    def run_bot(self,crypto,time_interval,period,mul):
        global signal
       # print(self.var)
        print("Starting the bot...")  # Debug line

            
        while self.var == 1:
            
            schedule.run_pending()
            print("Inside the bot loop...")  # Debug line

        
            print(f"Fetching new bars for {datetime.now().isoformat()}")
            bars = exchange.fetch_ohlcv(crypto, timeframe=time_interval, limit=100)
            df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            period = int(period)    
            mul =int(mul)
            supertrend_data = self.supertrend(df,period,mul)
          
            signal = self.check_buy_sell_signals(crypto,supertrend_data)
            self.plot_supertrend(df,crypto)
            
            self.update_signal_text()    
            self.show_trend(df)            
            
            #df.to_csv("CrpytoBot.csv")
            clear_output(wait = True)
            
            p2 = Image.open("supertrend_plot.png")
            resized_image2 = p2.resize((350,200))
            photo2 = ImageTk.PhotoImage(resized_image2)
            self.plot_label_text = tk.Label(root, text="Supertrend plot:")
            self.plot_label_text.grid(row=7,column=1, sticky='w')
            self.plot_label = tk.Label(root, image=photo2,bg="Grey")
            self.plot_label.grid(row=7, column=2,columnspan=4)
           # schedule.run_pending()
            time.sleep(60)
    
    def plot_supertrend(self, data, crypto, filename = "supertrend_plot.png"):
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        colors = []
        for index, row in df.iterrows():
            if row['in_uptrend'] == True:
                colors.append('green')
            elif row['in_uptrend'] == False:
                colors.append('red')
            else:
                colors.append('blue')
                

        plt.figure(figsize=(5, 3))
        plt.plot(df.index, df['close'], label='Closing Price', color='black')
        plt.scatter(df.index, df['close'], c=colors, marker='o')
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
       # plt.title(f"Supertrend Indicator for {crypto}")
        plt.legend()
        plt.grid(True)
    
    # Save the plot as an image
        plt.savefig(filename)
    
    # Close the plot to release resources (optional)
        plt.close()        


    
    def tr(self,data):
        data['previous_close'] = data['close'].shift(1)
        data['high-low'] = abs(data['high'] - data['low'])
        data['high-pc'] = abs(data['high'] - data['previous_close'])
        data['low-pc'] = abs(data['low'] - data['previous_close'])
        tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)
        return tr        
    
    def atr(self,data, period):
        data['tr'] = self.tr(data)
        atr = data['tr'].rolling(period).mean()
        return atr
            
    def update_signal_text(self):
        self.text.insert(tk.END, f"Signal: {signal}\n")
        self.text.see(tk.END)
        #print("Updating signal text...")  # Debug line
        #self.root.after(60000, self.update_signal_text)
        
        
    def show_trend(self,df):
        self.text.insert(tk.END, f"Uptrend values: \n{df['in_uptrend'].tail(5)}\n")
        self.text.see(tk.END)
        #print("Showing trend...")  # Debug line
        #self.root.after(60000, self.show_trend, df)            
    
    def check_buy_sell_signals(self,crypto,df):
        global in_position
        global signal
        print("checking for buy and sell signals")
        print(df.tail(5))
        last_row_index = len(df.index) - 1
        previous_row_index = last_row_index - 1
        
        if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
            print(f"Current position of bot = {in_position}") 
            if not in_position:
                signal = 'Green'
                self.order(crypto,signal)
                in_position = True       
            else:
                print("already in position, nothing to do")
    
        if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
            print(f"Current position of bot = {in_position}")
            if in_position:
                signal = 'Red'
                self.order(crypto,signal)
                in_position = False            
            else:
                print("You aren't in position, nothing to sell")               
            
    def set_var(self):
        if self.var == 1:
            self.var = 0
        else:
            self.var = 1           
             
        self.check_var()    

    def check_var(self):
        
        if self.var == 1:
            pass
        else:
            self.text.insert(tk.END, f"\n\n*** BOT EXITED ***\n\n")
            self.text.see(tk.END)
            self.root.after(3000, self.exit_app) 
            #exit()
            
    def exit_app(self):
        self.root.destroy()
        exit()
        
    def start_bot_thread(self):
        self.var = 1
        self.text.delete("1.0", tk.END)
        bot_thread = threading.Thread(target=self.run_bot, args=(self.crypto_entry.get(), self.time_entry.get(), self.ST_Period_Entry.get(), self.ST_mul_Entry.get()))
        bot_thread.start()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
    
        
    def supertrend(self,df, period, atr_multiplier):
        hl2 = (df['high'] + df['low']) / 2
        df['atr'] = self.atr(df, period)
        df['upperband'] = hl2 + (atr_multiplier * df['atr'])
        df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
        df['in_uptrend'] = True

        for current in range(1, len(df.index)):
            previous = current - 1
            if df['close'][current] > df['upperband'][previous]:
                df['in_uptrend'][current] = True
            elif df['close'][current] < df['lowerband'][previous]:
                df['in_uptrend'][current] = False
            else:
                df['in_uptrend'][current] = df['in_uptrend'][previous]

                if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                    df['lowerband'][current] = df['lowerband'][previous]

                if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                    df['upperband'][current] = df['upperband'][previous]
        
        return df



        
    def order(self,crypto, signal):
        #Set up Binance API endpoints for the testnet
        base_url = 'https://testnet.binance.com'
        api_endpoint = '/api/v3/order'
        if signal == 'Green':
            params = {
            'symbol': crypto,
            'side': 'BUY',
            'type': 'MARKET',  # Market order
            'quantity': 0.001,  # Quantity to buy
            'timestamp': int(time.time() * 1000)
            }
            headers = {'X-MBX-APIKEY': 'iq8APK5nDLbAQsFOy2eFNxVaFrYzVxG66JTii45sTtvp1eYfyahilobVLUifsFXh'}
            buy_response = requests.post(base_url + api_endpoint, params=params, headers=headers)
            print(buy_response.text)
        elif signal == 'Red':
            params = {
            'symbol': crypto,
            'side': 'SELL',
            'type': 'MARKET',  # Market order
            'quantity': 0.001,  # Quantity to sell
            'timestamp': int(time.time() * 1000)
            }
            headers = {'X-MBX-APIKEY': 'iq8APK5nDLbAQsFOy2eFNxVaFrYzVxG66JTii45sTtvp1eYfyahilobVLUifsFXh'}
            sell_response = requests.post(base_url + api_endpoint, params=params, headers=headers)
            print(sell_response.text)
            pass
        else:
            print("No trading decision")


if __name__ == "__main__":
    in_position = False
    signal = 'None'
    root = tk.Tk()
    image = Image.open("binancelogo.jpg")
    resized_image = image.resize((665,100))
    photo = ImageTk.PhotoImage(resized_image)
    
    root.geometry("665x700")
    root.resizable(False,True)
    app = TradingBotGUI(root)

    start_button = tk.Button(root, text="Start bot", command=app.start_bot_thread)
    start_button.grid(row=9, column=1)
    
    stop_button = tk.Button(root, text="Stop bot", command=app.set_var)
    stop_button.grid(row=9, column=2)

    root.mainloop()
        