
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta, datetime
from sklearn.preprocessing import RobustScaler
plt.style.use("bmh")

import ta

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

from config import *

import warnings
warnings.simplefilter("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

symbols = STOCK_UNIVERSE
indicators = INDICATORS


def split_sequence(seq, n_steps_in, n_steps_out):
    X, y = [], []
    
    for i in range(len(seq)):
        end = i + n_steps_in
        out_end = end + n_steps_out
        
        if out_end > len(seq):
            break

        seq_x, seq_y = seq[i:end, :], seq[end:out_end, 0]
        
        X.append(seq_x)
        y.append(seq_y)
    
    return np.array(X), np.array(y)
  
  
def visualize_training_results(results):
    history = results.history
    plt.figure(figsize=(16,5))
    plt.plot(history['val_loss'])
    plt.plot(history['loss'])
    plt.legend(['val_loss', 'loss'])
    plt.title('Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.show()
    
    plt.figure(figsize=(16,5))
    plt.plot(history['val_accuracy'])
    plt.plot(history['accuracy'])
    plt.legend(['val_accuracy', 'accuracy'])
    plt.title('Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.show()
    
    
def layer_maker(model, n_layers, n_nodes, activation, drop=None, d_rate=.5):
    for x in range(1,n_layers+1):
        model.add(LSTM(n_nodes, activation=activation, return_sequences=True))

        try:
            if x % drop == 0:
                model.add(Dropout(d_rate))
        except:
            pass
          
          
def validater(model, df, n_per_in, n_per_out, n_features, close_scaler):
    predictions = pd.DataFrame(index=df.index, columns=[df.columns[0]])

    for i in range(n_per_in, len(df)-n_per_in, n_per_out):
        x = df[-i - n_per_in:-i]

        yhat = model.predict(np.array(x).reshape(1, n_per_in, n_features))
        yhat = close_scaler.inverse_transform(yhat)[0]

        pred_df = pd.DataFrame(yhat, 
                               index=pd.date_range(start=x.index[-1], 
                                                   periods=len(yhat), 
                                                   freq="B"),
                               columns=[x.columns[0]])

        predictions.update(pred_df)
        
    return predictions


def val_rmse(df1, df2):
    df = df1.copy()
    df['close2'] = df2.close
    
    df.dropna(inplace=True)
    df['diff'] = df.close - df.close2
    rms = (df[['diff']]**2).mean()
    
    return float(np.sqrt(rms))


def forecast_trend(symbol):
    try:
        df = pd.read_csv(f"stocks/{symbol}/raw.csv")
    except Exception as e:
        print(f"Couldn't load data for {symbol} - {e}")
        return None

    print(df)
    df['date'] = pd.to_datetime(df.date)
    df.set_index('date', inplace=True)
    df.dropna(inplace=True)
    df = ta.add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
    df.drop(['open', 'high', 'low', 'volume'], axis=1, inplace=True)
    df = df.tail(1000)
    
    close_scaler = RobustScaler()
    close_scaler.fit(df[['close']])

    scaler = RobustScaler()
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

    n_per_in  = 90
    n_per_out = 30
    n_features = df.shape[1]

    X, y = split_sequence(df.to_numpy(), n_per_in, n_per_out)

    model = Sequential()
    activ = "tanh"

    model.add(LSTM(90,
               activation=activ, 
               return_sequences=True, 
               input_shape=(n_per_in, n_features)))

    layer_maker(model=model, n_layers=1,
                n_nodes=30, 
                activation=activ)

    model.add(LSTM(60, activation=activ))
    model.add(Dense(n_per_out))
    model.summary()
    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    res = model.fit(X, y, epochs=50, batch_size=128, validation_split=0.1, verbose=1)

    # visualize_training_results(res)

    # actual = pd.DataFrame(close_scaler.inverse_transform(df[["close"]]), 
    #                       index=df.index, 
    #                       columns=[df.columns[0]])
    # predictions = validater(model, df, n_per_in, n_per_out, n_features, close_scaler)
    # print("RMSE:", val_rmse(actual, predictions))
    # plt.figure(figsize=(16,6))
    # plt.plot(predictions, label='Predicted')
    # plt.plot(actual, label='Actual')
    # plt.title(f"Predicted vs Actual Closing Prices")
    # plt.ylabel("Price")
    # plt.legend()
    # plt.show()

    yhat = model.predict(np.array(df.tail(n_per_in)).reshape(1, n_per_in, n_features))
    yhat = close_scaler.inverse_transform(yhat)[0]

    preds = pd.DataFrame(yhat, 
                         index=pd.date_range(start=df.index[-1]+timedelta(days=1), 
                                             periods=len(yhat), 
                                             freq="B"), 
                         columns=[df.columns[0]])

    pers = n_per_in
    actual = pd.DataFrame(close_scaler.inverse_transform(df[["close"]].tail(pers)), 
                          index=df.close.tail(pers).index, 
                          columns=[df.columns[0]]).append(preds.head(1))
    print(preds)

    # plt.figure(figsize=(16,6))
    # plt.plot(actual, label="Actual Prices")
    # plt.plot(preds, label="Predicted Prices")
    # plt.ylabel("Price")
    # plt.xlabel("Dates")
    # plt.title(f"Forecasting the next {len(yhat)} days")
    # plt.legend()
    # plt.show()

    pct_change = preds.close.pct_change().sum()
    print(pct_change)
    return pct_change


def get_percent_change(row, df, n):
    try:
        return (row["close"] - df.iloc[row.name-10]["open"]) / df.iloc[row.name-10]["open"]
    except:
        return None


def set_trend_score(symbol):
    length = 7
    try:
        df = pd.read_csv(f"stocks/{symbol}/raw.csv")
    except Exception as e:
        print(f"Couldn't load data for {symbol} - {e}")
        return None

    df = df.dropna().reset_index(drop=True)
    df["change"] = df.apply(lambda row: get_percent_change(row, df, 10), axis=1)
    df = df.dropna().reset_index(drop=True)
    df["change"] = df["change"].rolling(10).mean()
    df = df.dropna().tail(1000).reset_index(drop=True)

    return df.iloc[-1]["change"]


def main():
    trends = []
    new_symbols = []
    for symbol in symbols:
        score = forecast_trend(symbol)
        if score:
            trends.append(score)
            new_symbols.append(symbol)

    df = pd.DataFrame(zip(new_symbols, trends), columns=["Symbol", "Trend"])
    df = df.sort_values(["Trend"], ascending=True)
    df = df.reset_index(drop=True)

    print(df)
    _date = str(datetime.now().date())
    df.to_csv(f"trades/StockRank_{_date}.csv", index=False)


if __name__=="__main__":
    main()
