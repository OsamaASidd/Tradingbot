import tkinter as tk
from tkinter import ttk
import pandas as pd
import time
import sched
from datetime import datetime
import ccxt

exchange = ccxt.binance({
  "apiKey": 'my5nw1BwA5Hqv8xxZ5rHd8p1xIsZhlojXDv1PRsn85eVjFvjqafvdNpFKQNFOqym',
  "secret": 'jhOz9nwsXSzWFU54RA4rg700dMJL7sQvYmc0SPhTynJneyJ8B4C7SAKGfbGwoco9'
})

class CryptoBot:
  def __init__(self):
    self.var = 1
    self.signal = 0
    self.scheduler = sched.scheduler(time.time, time.sleep)

    self.exchange = ccxt.binance()
    self.root = tk.Tk()
    self.root.title("Crypto Bot")

    self.tree = ttk.Treeview(self.root, columns=("Symbol", "DateTime", "CurrentTimestamp", "Funding Rate"), height=30)
    self.tree.heading("#1", text="Symbol")
    self.tree.heading("#2", text="Datetime")
    self.tree.heading("#3", text="Funding Timestamp")
    self.tree.heading("#4", text="Funding Rate")
    
    self.tree.pack()

    # Add a button to start the bot
    start_button = tk.Button(self.root, text="Start Bot", command=self.run_bot)
    start_button.pack()

  def run_bot(self):
    print("Starting the bot...")

    while self.var == 1:
      
      self.update_gui() 

      print("Inside the bot loop...")
      print(f"Fetching new funding rate for {datetime.now().isoformat()}")

      funding_rate = exchange.fetch_funding_rates() 
      df = pd.DataFrame(funding_rate)
      df = df.transpose()
      filteredDf = df[abs(df['fundingRate']) > 0.001]
      if(len(filteredDf) > 0):
        self.add_data_to_table(filteredDf)
      else:
        print('No record found...')  

      time.sleep(60)

  def add_data_to_table(self, df):
    for i in range(len(df)):
      self.tree.insert("", "end", values=(df.iloc[i]['symbol'] , df.iloc[i]['datetime'], df.iloc[i]['fundingTimestamp'], df.iloc[i]['fundingRate']))

  def update_gui(self):
    self.root.update()

  def start(self):
    self.root.mainloop()


if __name__ == "__main__":
  bot = CryptoBot()
  bot.start()
