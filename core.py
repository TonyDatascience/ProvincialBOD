def update_progress(progress):
    barLength = 20  # Modify this value to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = Fore.RED + "Halt!\r\n"
    if progress >= .999:
        progress = 1
        status = Fore.GREEN + " Complete!\r\n"
    block = int(round(barLength*progress))
    text = "\r[*] Progress: [{0}] {1}% {2}".format("#"*block + "-"*(barLength-block), round(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()
def gs_control():
    global tp,ExpiredOrder,ExpiredPosition,SpreadSec,ServerControl,lot
    if os.path.exists(json_file_name):
        f = open(json_file_name)
        data = json.load(f)
        df = json.loads(data)
        #print("GS CONTROL=",data)
        tp=df['TP']
        sl=df['SL']
        ExpiredOrder=df['ExpiredOrder']
        ExpiredPosition=df['ExpiredPosition']
        ServerControl=df['Mode']
        SpreadSec=df['OrderGap']
        lot=df['Lot']
    else:
        print("JSON DOES NOT EXISTS");
        tp=50
        sl=5
        ExpiredOrder=3
        ExpiredPosition=22
        ServerControl='Run'
        SpreadSec=10
        lot=0.05

def DBinit():
    con = sqlite3.connect(dbMarketFile)
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE name='MarketTime'")
    ExistNum=res.fetchall()
    TblOrders='2024_all_orders'
    if(len(ExistNum)==0):
        cur.execute("""CREATE TABLE MarketTime(
                Name TEXT NOT NULL,Mon TEXT NULL,Tue TEXT NULL,Wed TEXT NULL,Thu TEXT NULL,Fri TEXT NULL,Sat TEXT NULL,Sun TEXT NULL,
                ClosedDatesIn2024 TEXT NULL,TargetGap INTEGER DEFAULT 8 NOT NULL,TARGETMIN INTEGER DEFAULT 25 NOT NULL,COEFFICIENT INTEGER DEFAULT 1 NOT NULL)""")
        con.commit()
        cur.execute("""
        INSERT INTO MarketTime VALUES
        ('EURUSD', '00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','','','','','',''),
        ('JPYUSD', '00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','23:02-23:59','','','',''),
        ('XAUUSD', '00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','','','','','')
        """)
        con.commit()
    else:
        
        cur.execute("DROP TABLE IF EXISTS MarketTime")
        con.commit()
        cur.execute("""CREATE TABLE MarketTime(
                Name TEXT NOT NULL,Mon TEXT NULL,Tue TEXT NULL,Wed TEXT NULL,Thu TEXT NULL,Fri TEXT NULL,Sat TEXT NULL,Sun TEXT NULL,
                ClosedDatesIn2024 TEXT NULL,TargetGap INTEGER DEFAULT 8 NOT NULL,TARGETMIN INTEGER DEFAULT 25 NOT NULL,COEFFICIENT INTEGER DEFAULT 1 NOT NULL)""")
        con.commit()
        cur.execute("""
        INSERT INTO MarketTime VALUES
        ('EURUSD', '00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','00:00-23:58','',''),
        ('JPYUSD', '00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','00:00-22:58;23:02-23:59','23:02-23:59','','','',''),
        ('XAUUSD', '00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','00:02-22:58','','','','','')
        """)
        con.commit()
    con.close()
    #Order Collection and performance
    con = sqlite3.connect(dbOrdersFile)
    cur = con.cursor()
    TblOrders='Tbl_2024_all_orders'
    txtSql= "SELECT name FROM sqlite_master WHERE name='"+TblOrders+ "'"
    res = cur.execute(txtSql)
    #print(txtSql)
    ExistNum=res.fetchall()
    print(len(ExistNum)," = existNum")
    if(len(ExistNum)==0):
        cur.execute("""CREATE TABLE {}(
                Date TEXT NOT NULL,Time TEXT NOT NULL,OrderNumber INTEGER NULL,PredictType TEXT NOT NULL,Volume REAL DEFAULT 0 NOT NULL,
                PRICE REAL NULL,TP REAL NOT NULL,STATUS TEXT NULL,PROFIT REAL DEFAULT 0 NOT NULL, NOTE TEXT NULL)""".format(TblOrders))
        con.commit()
    else:
        print("DROP TABLE")
        cur.execute("DROP TABLE IF EXISTS {}".format(TblOrders))
        con.commit()
        cur.execute("""CREATE TABLE {}(
                Date TEXT NOT NULL,Time TEXT NOT NULL,OrderNumber INTEGER NULL,PredictType TEXT NOT NULL,Volume REAL DEFAULT 0 NOT NULL,
                PRICE REAL NULL,TP REAL NOT NULL,STATUS TEXT NULL,PROFIT REAL DEFAULT 0 NOT NULL, NOTE TEXT NULL)""".format(TblOrders))
        con.commit()
    con.close()
    return True
def ReadMarketTime(reqDate,MarketName='EURUSD'):
    DayName=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    con = sqlite3.connect(dbMarketFile)
    df = pd.read_sql_query("SELECT * FROM MarketTime", con)
    con.close()
    ChooseDay=DayName[reqDate.weekday()]
    txt=reqDate #ChooseDay='Mon' #print('Day=',ChooseDay)
    OperationHours=df[df['Name']==MarketName][ChooseDay] #print("size=",OperationHours.size) print(OperationHours)
    nparr=np.array(OperationHours) #print(nparr.shape)
    if (nparr[0]==''):
        SlotArray=[]
    else:
        SlotArray=nparr[0].split(';')
    RetVal = {
        "Market" : MarketName,
        "TradeHours": SlotArray
    }
    return RetVal
def AllowTrade(SlotTrade):
    bufferIn=timedelta(minutes = 25)
    bufferOut=timedelta(minutes = 5)
    txt=date.today()
    Allowable = False
    if len(SlotTrade)>0:
        #print("slot =",SlotTrade)
        for SlotNum in SlotTrade:
            #print("slotnum =",SlotNum)
            TimeOpenClose=SlotNum.split('-')   
            formatOpenTime=str(txt) +' '+ TimeOpenClose[0] + ":00"
            formatCloseTime=str(txt) +' '+ TimeOpenClose[1]+ ":59"
            date_format = '%Y-%m-%d %H:%M:%S'
            OpenTime = datetime.strptime(formatOpenTime, date_format)
            CloseTime = datetime.strptime(formatCloseTime, date_format)
            #print("now =",datetime.now()) print('Open =',OpenTime,' \nClose=',CloseTime) print(datetime.now()> OpenTime+bufferIn," Open Bool") print(datetime.now()< CloseTime - bufferOut," Close Bool")

            if(datetime.now()> OpenTime+bufferIn) & (datetime.now()< CloseTime - bufferOut):
                Allowable=True
                break
    if(Allowable):
        gs_control()
        print("Round :",RunCode," SERVER CONTROL: ",ServerControl)
        if(ServerControl=='Run'):
            Allowable=True
        elif(ServerControl=='Pause'):
            time.sleep(180)
        elif(ServerControl=='End'):
            sys.exit()
        elif(ServerControl=='ClearAllOrders'):
            print("Clear orders")
            ClearAllOrdersFromServer()
        elif(ServerControl=='ClearAllPositions'):
            print("Clear All Pos.")
            ClearAllPositionsFromServer()
        else:
            print("ERROR from google sheet")
            Allowable=False
    return Allowable


def PortCheck():

    if(useMT5):

        authorized=mt5.login(login=UN, password=PW,server=sv)
        if authorized:
            account_info=mt5.account_info()
            if account_info!=None:
                #print(account_info)
                # display trading account data in the form of a dictionary
                account_info_dict = mt5.account_info()._asdict()
                if(account_info_dict['balance']>TradeSafety):
                    TradeCheck=True
                else:
                    TradeCheck=False
                    print("Critical value:{:,.2f}, safety floor is{:,.2f},margin free is{:,.2f}".format(account_info_dict['balance'],TradeSafety,account_info_dict['margin_free']))
        else:
            print("failed to connect to trade account {}, error code =".format(UN,mt5.last_error()))
            TradeCheck=False
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()
    else:
        TradeCheck=True
    return TradeCheck
def InsertOrdersBook(OrderNumber,OrderType,Volume,Price,Tp):
    con = sqlite3.connect(dbOrdersFile)
    cur = con.cursor()
    TblOrdersAll='Tbl_2024_all_orders'
    #Date	Time	OrdrNumber,PredictType	Volume	BID	ASK	STATUS	PROFIT	NOTE
    txtInsertSql="INSERT INTO {} VALUES ('{}','{}',{},'{}',{},{},{},'{}',{},'{}')".format(TblOrdersAll,
        date.today().strftime('%Y-%m-%d'),datetime.now().strftime('%H:%M:%S'),
        OrderNumber,OrderType,Volume,Price,Tp,'Unmatched',0,'NeedUpdated')#print(txtInsertSql)
    cur.execute(txtInsertSql)
    con.commit()
    con.close()
    
def UpdateOrdersBook():
    con = sqlite3.connect(dbOrdersFile)
    cur = con.cursor()
    df = pd.read_sql_query("SELECT OrderNumber FROM {} WHERE Note='NeedUpdated'".format(TblOrders), con)
    OrderNumbers=np.array(df)
    for i in OrderNumbers:
        txtUpdateSql="UPDATE {} SET STATUS='{}', NOTE='{}' WHERE OrderNumber={}".format(TblOrders,'Matched','Updated',i[0])                                                          
        cur.execute(txtUpdateSql)
        con.commit()
    con.close()

def OverLossConditions(type,price_gap):
    val =0
    if type==0: #Buy
        if(price_gap<-sl): val=1
    else: #Sell
        if(price_gap>sl):   val=1
    return val

def ClearAllOrders():
    #Clear Expired Order
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    orders=mt5.orders_get(symbol=symbol)
    if(len(orders)>0):
        df=pd.DataFrame(list(orders),columns=orders[0]._asdict().keys())
        current_time=datetime.now()
        exp_time=datetime.now()-timedelta(minutes=ExpiredOrder)
        exp_time_new_gmt= gap_timezone.localize(exp_time)
        exp_time_stamp=int(exp_time_new_gmt.timestamp())
        ExpiredTickets=df[df['time_setup']<exp_time_stamp]['ticket']
        result =  "{}: There are ongoing orders but not expired".format(current_time)
        if(len(ExpiredTickets)>0):
            for eTicket in ExpiredTickets:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": eTicket,
                    "comment": "Expired Order Remove"
                }
                result = mt5.order_send(request)
                print("remove tickets no.=",eTicket)#," and time=",df[df['ticket']==eTicket]['time_setup'])
                result = 'All expired orders have been removed.'
        return result
def ClearAllOrdersFromServer():
    #Clear Expired Order
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    orders=mt5.orders_get(symbol=symbol)
    if(len(orders)>0):
        df=pd.DataFrame(list(orders),columns=orders[0]._asdict().keys())
        ExpiredTickets=df['ticket']
        if(len(ExpiredTickets)>0):
            for eTicket in ExpiredTickets:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": eTicket,
                    "comment": "Server Remove All Orders"
                }
                result = mt5.order_send(request)
                print("remove tickets no.=",eTicket)#," and time=",df[df['ticket']==eTicket]['time_setup'])
                result = 'All orders have been removed by server.'
        return result
def OverLossConditions(type,price_gap):
    val =0
    if type==0: #Buy
        if(price_gap<-sl): val=1
    else: #Sell
        if(price_gap>sl):   val=1
    return val

def ClearAllPositions():
    #Clear False Order
    positions=mt5.positions_get(symbol=symbol)
    if(len(positions)>0):
        # display these positions as a table using pandas.DataFrame
        df=pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
        #display(df)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        #print(df)
        
        exp_time=datetime.now()-timedelta(minutes=ExpiredPosition)
        exp_time_new_gmt= gap_timezone.localize(exp_time)
        exp_time_stamp=int(exp_time_new_gmt.timestamp())
        ExpiredPositionTickets=df[df['time_update']<exp_time_stamp]['ticket']
        #print("Expired:")
        #display(ExpiredPositionTickets)
        current_time=datetime.now()
        result =  "{}: There are ongoing orders but not expired".format(current_time)
        df["price_gap"]=10**5*(df['price_current']-df['price_open'])
        df['BoolLoss'] = df.apply(lambda x: OverLossConditions(x.type, x.price_gap), axis=1)
        OverLossPositionTickets=df[df['BoolLoss']==1]['ticket']
        #print("Loss:")
        sc=set(list(OverLossPositionTickets)+list(ExpiredPositionTickets))
        #print(sc)
        All_to_remove=df[df['ticket'].isin(sc)]
        
        if len(All_to_remove)>0:
            for i in range(len(All_to_remove)):
                print("i=",i)
                eOrder =All_to_remove.iloc[i]
                print("REMOVE position number= ",eOrder)
                #mt5.Close(symbol,ticket=int(eOrder['ticket']))
                if eOrder['type']==mt5.ORDER_TYPE_SELL:
                    print('Close order sell of',eOrder['ticket'])
                    op_order=mt5.ORDER_TYPE_BUY
                    matched_price=mt5.symbol_info_tick(symbol).ask
                else:
                    print('Close order buy of',eOrder['ticket'])
                    op_order=mt5.ORDER_TYPE_SELL
                    matched_price=mt5.symbol_info_tick(symbol).bid
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": eOrder['volume'],
                    "position": int(eOrder['ticket']),
                    "type": op_order, 
                    "price": matched_price,
                    "comment": "Expired POSITION",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }
                result = mt5.order_send(request)
                #print(result)
def ClearAllPositionsFromServer():
    #Clear False Order
    positions=mt5.positions_get(symbol=symbol)
    if(len(positions)>0):
        # display these positions as a table using pandas.DataFrame
        df=pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
        ExpiredPositionTickets=df['ticket']
        if len(All_to_remove)>0:
            for i in range(len(All_to_remove)):
                print("i=",i)
                eOrder =All_to_remove.iloc[i]
                print("REMOVE position number= ",eOrder)
                #mt5.Close(symbol,ticket=int(eOrder['ticket']))
                if eOrder['type']==mt5.ORDER_TYPE_SELL:
                    print('Close order sell of',eOrder['ticket'])
                    op_order=mt5.ORDER_TYPE_BUY
                    matched_price=mt5.symbol_info_tick(symbol).ask
                else:
                    print('Close order buy of',eOrder['ticket'])
                    op_order=mt5.ORDER_TYPE_SELL
                    matched_price=mt5.symbol_info_tick(symbol).bid
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": eOrder['volume'],
                    "position": int(eOrder['ticket']),
                    "type": op_order, 
                    "price": matched_price,
                    "comment": "Removed All Pos From server",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }
                result = mt5.order_send(request)
                #print(result)

                
def OrderHisorySave():
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit() 
    # get the number of deals in history
    from_date=datetime.strptime(str(date.today())+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    to_date=datetime.now()
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals=mt5.history_deals_get(from_date, to_date, group="*EUR*")
    if len(deals) > 0:
        df=pd.DataFrame(list(deals),columns=deals[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        con = sqlite3.connect(dbOrdersFile)
        cur = con.cursor()
        df.to_sql(name=TblOrders,con=con)
        con.close()
    # shut down connection to the MetaTrader 5 terminal
    #mt5.shutdown()
def SendOrder(symbol,lot,order_type,price,included_tp):
    # if the symbol is unavailable in MarketWatch, add it
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit() 
    # get the number of deals in history
    order_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    exp_time =  int((datetime.now()+timedelta(minutes=1)).timestamp())
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "tp": included_tp,
        "magic": 138252,
        "comment": order_time,
        "expiration": exp_time,
        "type_time":mt5.ORDER_TIME_SPECIFIED_DAY,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    # send a trading request
    result = mt5.order_send(request)
    #print(result)
    return result
def HitProb(RangeLowHi,BuyAt):
    #RangeLowHi = np.array[Lo, High],dim (2,)
    #BuyAt = np.array[Buy], dim(1,)
    if(RangeLowHi[0] != RangeLowHi[1]):
        if(BuyAt>=RangeLowHi[0]) & (BuyAt<=RangeLowHi[1]):
            Prox=np.absolute(BuyAt-RangeLowHi[0])/(RangeLowHi[1]-RangeLowHi[0])
            Dist=np.absolute(RangeLowHi[1]-BuyAt)/(RangeLowHi[1]-RangeLowHi[0])
            Ptile = np.minimum(Prox,Dist)/np.maximum(Prox,Dist)
            if Ptile==0: Ptile=0.00001
        else:
            Ptile = 0
    else:
        if (BuyAt== RangeLowHi[0]):
            Ptile=1
        else:
            Ptile = 0    
    #print(RangeLowHi.shape," - Range low hi=",RangeLowHi,", buy shape=",BuyAt.shape," at=",BuyAt," P-tile=",Ptile)
    return(Ptile)
def BoolHitProb(RangeLowHi,BuyAt):
    #RangeLowHi = np.array[Lo, High],dim (2,)
    #BuyAt = np.array[Buy], dim(1,)
    if(BuyAt>=RangeLowHi[0]) & (BuyAt<=RangeLowHi[1]):
        Ptile = 1
    else:
        Ptile = 0    
    #print(RangeLowHi.shape," - Range low hi=",RangeLowHi,", buy shape=",BuyAt.shape," at=",BuyAt," P-tile=",Ptile)
    return(Ptile)
def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y
def CreateWindowPD(x_input=np.nan,y_input=np.nan,batch_length=100,number_of_step=25,stride=1):
    #For X
    number_of_batch=np.floor(x_input.shape[0]/batch_length).astype(int) #print("num batch=",number_of_batch)
    retX=pd.DataFrame()
    retY=pd.DataFrame()
    for i in range(number_of_batch):
        x_batch=x_input.iloc[:][(i*batch_length):((i+1)*batch_length)]   
        y_batch=y_input[(i*batch_length):((i+1)*batch_length)]  #print("x batch=",x_batch.shape," type=",type(x_batch)) print("y batch=",y_batch.shape)
        number_of_minimal_batch=np.floor((x_batch.shape[0]-number_of_step+stride)/stride).astype(int) #print("num min batch=",number_of_minimal_batch)
        for j in range(number_of_minimal_batch):
            startPos=(j*stride)
            stopPos=startPos+number_of_step #print("j_x",j,"=",x_batch[startPos:stopPos].shape) #print("j_y",j,"=",y_batch[stopPos-1:stopPos].shape)
            retX=pd.concat([retX,x_batch[startPos:stopPos]],ignore_index=True)
            retY=pd.concat([retY,y_batch[(stopPos-1):stopPos]],ignore_index=True)
    #For Y ,print(retX.shape), print(retY.shape), #retY=np.nan
    dict = {"X": retX,"Y": retY} #print(retX.shape)
    return(dict)

def NonOverlapChunk(x_inp,pre_chunk_need=25,chunk_size=100,post_chunk_need=25):
    retX=pd.DataFrame()
    i=0
    #Min =1 but have 2 blocks therfer we need 150 blocks, Gap Min will equal to 149 
    TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need
    LastChunkIndex=TotalChunkSize-1
    while(i<=(x_inp.shape[0]-TotalChunkSize)):
        if ((x_inp.iloc[i+LastChunkIndex]['TimeMin']-x_inp.iloc[i]['TimeMin'])==timedelta(minutes=LastChunkIndex)):
            retX=pd.concat([retX,x_inp[i:i+LastChunkIndex+1]],ignore_index=True)
            i=i+TotalChunkSize
        else:
            #print("time dela=",(x_inp.iloc[i+LastChunkIndex]['TimeMin']-x_inp.iloc[i]['TimeMin']))
            i=i+1
    return retX
def OverlapChunk(x_inp,pre_chunk_need=25,chunk_size=100,post_chunk_need=25):
    retX=pd.DataFrame()
    i=0
    #Min =1 but have 2 blocks therfer we need 150 blocks, Gap Min will equal to 149 
    TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need
    LastChunkIndex=TotalChunkSize-1
    while(i<=(x_inp.shape[0]-TotalChunkSize)):
        if (i %1000) == 0 & i>0 : update_progress(i/(x_inp.shape[0]-TotalChunkSize))
        if ((x_inp.iloc[i+LastChunkIndex]['TimeMin']-x_inp.iloc[i]['TimeMin'])==timedelta(minutes=LastChunkIndex)):
            retX=pd.concat([retX,x_inp[i:i+LastChunkIndex+1]],ignore_index=True)
            i=i+TotalChunkSize-post_chunk_need-pre_chunk_need
        else:
            #print("time del=",(x_inp.iloc[i+LastChunkIndex]['TimeMin']-x_inp.iloc[i]['TimeMin']))
            i=i+1
    update_progress(1)
    return retX

def CreateBoolean_XMin_XPoints_Performance(row,MinTxt='10',Trigger=10):
    if row>=Trigger or row<=-Trigger:
        val=1
    else:
        val=0
    return val
def CreateSoftMax_XMin_XPoints_Performance(row,MinTxt='10',Trigger=10):
    #0 = Neutral, 1= Long, 2= Short
    if row>=Trigger:
        val=1
    elif row<=-Trigger:
        val=2
    else:
        val=0
    return val
def CreateEMA(SubSmallChunk):
    #print(SubSmallChunk.shape)
    EMA5_All=SubSmallChunk['Close'].values[0]
    #print("GAP =",int(coeff*(SubSmallChunk['Median1'].values[1]-SubSmallChunk['Median1'].values[0])))
    Momentum_EMA5_All=(coeff*(SubSmallChunk['Median1'].values[1]-SubSmallChunk['Median1'].values[0])*SubSmallChunk['Volume'].values[0])
    Momentum_EMA10_All=Momentum_EMA5_All
    Momentum_EMA15_All=Momentum_EMA5_All
    Momentum_EMA25_All=Momentum_EMA5_All
    EMA5s=[EMA5_All]
    EMA10s=[EMA5_All]
    EMA15s=[EMA5_All]
    EMA25s=[EMA5_All]
    Momentum_EMA5s=[Momentum_EMA5_All]
    Momentum_EMA10s=[Momentum_EMA5_All]
    Momentum_EMA15s=[Momentum_EMA5_All]
    Momentum_EMA25s=[Momentum_EMA5_All]
    
    #.values[i-1]*(EMA_Constant/6) )+(pd_bar['Momentum_EMA5'].values[i-2]*(1-(EMA_Constant/6))),5)
    for i in range(1,len(SubSmallChunk)):
        EMA5_All=np.round(SubSmallChunk['Close'].values[i]*(EMA_Constant/6)+(EMA5_All*(1-(EMA_Constant/6))),5)
        EMA10_All=np.round(SubSmallChunk['Close'].values[i]*(EMA_Constant/11)+(EMA5_All*(1-(EMA_Constant/11))),5)
        EMA15_All=np.round(SubSmallChunk['Close'].values[i]*(EMA_Constant/16)+(EMA5_All*(1-(EMA_Constant/16))),5)
        EMA25_All=np.round(SubSmallChunk['Close'].values[i]*(EMA_Constant/26)+(EMA5_All*(1-(EMA_Constant/26))),5)
        EMA5s=EMA5s+[EMA5_All]
        EMA10s=EMA10s+[EMA10_All]
        EMA15s=EMA15s+[EMA15_All]
        EMA25s=EMA25s+[EMA25_All]
        #print(Momentum_EMA5s)
        #Momentum_EMA5_All=(coeff*(SubSmallChunk['Median1'].values[1]-SubSmallChunk['Median1'].values[0])*SubSmallChunk['Volume'].values[0])
    
        Current_EMA=(int(coeff*(SubSmallChunk['Median1'].values[i]-SubSmallChunk['PrevMedian1'].values[i]))*SubSmallChunk['Volume'].values[i])
        Momentum_EMA5_All=np.round(Current_EMA*(EMA_Constant/6)+(Momentum_EMA5_All*(1-(EMA_Constant/6))),5)
        Momentum_EMA10_All=np.round(Current_EMA*(EMA_Constant/11)+(Momentum_EMA10_All*(1-(EMA_Constant/11))),5)
        Momentum_EMA15_All=np.round(Current_EMA*(EMA_Constant/16)+(Momentum_EMA15_All*(1-(EMA_Constant/16))),5)
        Momentum_EMA25_All=np.round(Current_EMA*(EMA_Constant/26)+(Momentum_EMA25_All*(1-(EMA_Constant/26))),5)
        
        Momentum_EMA5s=Momentum_EMA5s+[Momentum_EMA5_All]
        Momentum_EMA10s=Momentum_EMA10s+[Momentum_EMA10_All]
        Momentum_EMA15s=Momentum_EMA15s+[Momentum_EMA15_All]
        Momentum_EMA25s=Momentum_EMA25s+[Momentum_EMA25_All]
    return(EMA5s,EMA10s,EMA15s,EMA25s,Momentum_EMA5s,Momentum_EMA10s,Momentum_EMA15s,Momentum_EMA25s)
def retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL):
    b=np.array([BuyTP,BuySL,SellTP,SellSL])
    if sum(b==np.inf)==4:
        val=int(0)
    else:

        if(b[0]<b[2]):
            #Should Buy
            if(b[1]>b[0]):
                val=int(1) #Buy
            else:
                val=int(0)
        elif(b[2]<b[0]):
            #Should Sell
            if(b[3]>b[2]):
                val=int(2) #Sell
            else:
                val=int(0)        
        else:
            val=int(0)
    return val
def convert(lst):
   res_dict = {}
   for i in range(len(lst)):
       res_dict[lst[i]] = i
   return res_dict
def PredictOrder(symbol):
    #start_time =timeit.default_timer()
    #GetData
    if(useMT5):
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 26)
        rates_frame = pd.DataFrame(rates)
        #display(rates_frame)
        rates_frame.columns = ['TimeMin', 'Open', 'High','Low','Close','Volume','Spread','RealVolume']
        rates_frame['TimeMin']=pd.to_datetime(rates_frame['TimeMin'])
        pd_bar=rates_frame
    else:
        # For Testing purpose
        dat_2023 = pd.read_csv("Data/EURUSD_small.csv",sep="\t")
        dat_2023.columns = ['DATE', 'TIME', 'Open', 'High','Low','Close','Volume','RealVolume','Spread']
        dat_2023['DATE']=pd.to_datetime(dat_2023['DATE'])
        tmp = pd.to_datetime((dat_2023['DATE'].astype(str)+ " " + dat_2023['TIME'].astype(str)))
        dat_2023.drop(['DATE','TIME'], axis=1)
        dat_2023.insert(0,"TimeMin",tmp)
        pd_bar=dat_2023[-26:]
        #AllNonOverlapData=pd.read_pickle("non_overlap_21_23.pkl")
        #NonOverlapData=AllNonOverlapData[-150:]
    #NonOverlapData=
    
    OrderType=PredictSoftMax120_70_Identical_Chunk(pd_bar)
    #print(OrderType)
    rPrice=pd_bar['Close'].values[-1]
    Orders={
        'Type' : OrderType,
        'Price' : rPrice
    }
    #end_time=timeit.default_timer()
    #elapsed_time=end_time - start_time
    #print("working time=",elapsed_time," sec")
    return Orders
def PredictSoftMax45_5(NonOverlapData):
    TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need
    TotalChunkNumber=NonOverlapData.shape[0]/TotalChunkSize
    pd_bar=copy.copy(NonOverlapData)

    if(True):
        pd_bar=pd_bar.assign(Median1= np.round((pd_bar['High'] + pd_bar['Low'])/2,5))
        pd_bar=pd_bar.assign(PrevMedian1=np.nan,
                             #Past Section
                             PastHigh3=np.nan,PastLow3=np.nan,Median3=np.nan,
                             PastHigh5=np.nan,PastLow5=np.nan,Median5=np.nan,
                             PastHigh10=np.nan,PastLow10=np.nan,Median10=np.nan,
                             PastHigh15=np.nan,PastLow15=np.nan,Median15=np.nan,
                             PastHigh25=np.nan,PastLow25=np.nan,Median25=np.nan,
                             pMomentum1_Volume=np.nan,pMomentum1_Spread=np.nan,pMomentum1_VS=np.nan,
                             pMomentum_EMA5_Volume=np.nan,pMomentum_EMA10_Volume=np.nan,pMomentum_EMA15_Volume=np.nan,pMomentum_EMA25_Volume=np.nan,
                             pMomentum_EMA5_Spread=np.nan,pMomentum_EMA10_Spread=np.nan,pMomentum_EMA15_Spread=np.nan,pMomentum_EMA25_Spread=np.nan,
                             pMomentum_EMA5_VS=np.nan,pMomentum_EMA10_VS=np.nan,pMomentum_EMA15_VS=np.nan,pMomentum_EMA25_VS=np.nan
                            )
        jStop=int(TotalChunkNumber)
        pd_pre_chunk_post=pd.DataFrame()
        pd_only_chunk=pd.DataFrame()
        for j in range(jStop):
            pd_tmp=pd_bar[(j*TotalChunkSize):(j+1)*TotalChunkSize]
            PrevMedian1=pd_tmp['Median1'].shift()
            pd_tmp.loc[:,'PrevMedian1']=PrevMedian1

            pd_tmp['pMomentum1_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA5_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA10_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA25_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]

            pd_tmp['pMomentum1_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA5_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA10_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA25_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum1_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA5_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA10_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA25_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]

            VS_init=pd_tmp['Volume'].values[0]*pd_tmp['Spread'].values[0]
            pd_tmp['pMomentum1_VS'].values[0]=VS_init
            pd_tmp['pMomentum1_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA5_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA5_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA10_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA10_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA15_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA15_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA25_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA25_VS'].values[1]=VS_init
            for i in range(TotalChunkSize):
                if(i>=2):
                    #MOMENTUM IN VOLUME
                    pd_tmp['pMomentum1_Volume'].values[i]=(coeff*(pd_tmp['Median1'].values[i-2]-pd_tmp['Median1'].values[i-1]))*pd_tmp['Volume'].values[i-1]
                    pd_tmp['pMomentum_EMA5_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/6) +(pd_tmp['pMomentum_EMA5_Volume'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/11) +(pd_tmp['pMomentum_EMA10_Volume'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/16) +(pd_tmp['pMomentum_EMA15_Volume'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/26) +(pd_tmp['pMomentum_EMA25_Volume'].values[i-2]*(1-(EMA_Constant/26))),5)
                    #MOMENTUM IN SPREAD
                    pd_tmp['pMomentum1_Spread'].values[i]=(coeff*(pd_tmp['Median1'].values[i-2]-pd_tmp['Median1'].values[i-1]))*pd_tmp['Spread'].values[i-1]
                    pd_tmp['pMomentum_EMA5_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/6) )+(pd_tmp['pMomentum_EMA5_Spread'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/11) )+(pd_tmp['pMomentum_EMA10_Spread'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/16) )+(pd_tmp['pMomentum_EMA15_Spread'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/26) )+(pd_tmp['pMomentum_EMA25_Spread'].values[i-2]*(1-(EMA_Constant/26))),5)
                    #VolumexSpread
                    pd_tmp['pMomentum1_VS'].values[i]=(pd_tmp['Volume'].values[i-1])*(pd_tmp['Spread'].values[i-1])
                    pd_tmp['pMomentum_EMA5_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/6) )+(pd_tmp['pMomentum_EMA5_VS'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/11) )+(pd_tmp['pMomentum_EMA10_VS'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/16) )+(pd_tmp['pMomentum_EMA15_VS'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/26) )+(pd_tmp['pMomentum_EMA25_VS'].values[i-2]*(1-(EMA_Constant/26))),5)
                if i>=3:
                    pd_tmp['PastHigh3'].values[i]=np.max(pd_bar['High'].values[(i-3):i])
                    pd_tmp['PastLow3'].values[i]=np.min(pd_bar['Low'].values[(i-3):i])
                    pd_tmp['Median3'].values[i]=np.round((pd_bar['PastHigh3'].values[i] + pd_bar['PastLow3'].values[i])/2,5)    
                if i>=5:
                    pd_tmp['PastHigh5'].values[i]=np.max(pd_bar['High'].values[(i-5):i])
                    pd_tmp['PastLow5'].values[i]=np.min(pd_bar['Low'].values[(i-5):i])
                    pd_tmp['Median5'].values[i]=np.round((pd_bar['PastHigh5'].values[i] + pd_bar['PastLow5'].values[i])/2,5)

                if i>=10:
                    pd_tmp['PastHigh10'].values[i]=np.max(pd_bar['High'].values[(i-10):i])
                    pd_tmp['PastLow10'].values[i]=np.min(pd_bar['Low'].values[(i-10):i])
                    pd_tmp['Median10'].values[i]=np.round((pd_bar['PastHigh10'].values[i] + pd_bar['PastLow10'].values[i])/2,5)

                if i>=15:
                    pd_tmp['PastHigh15'].values[i]=np.max(pd_bar['High'].values[(i-15):i])
                    pd_tmp['PastLow15'].values[i]=np.min(pd_bar['Low'].values[(i-15):i])
                    pd_tmp['Median15'].values[i]=np.round((pd_bar['PastHigh15'].values[i] + pd_bar['PastLow15'].values[i])/2,5)

                if i>=25:
                    pd_tmp['PastHigh25'].values[i]=np.max(pd_bar['High'].values[(i-25):i])
                    pd_tmp['PastLow25'].values[i]=np.min(pd_bar['Low'].values[(i-25):i])
                    pd_tmp['Median25'].values[i]=np.round((pd_bar['PastHigh25'].values[i] + pd_bar['PastLow25'].values[i])/2,5)
            pd_pre_chunk_post=pd.concat([pd_pre_chunk_post,pd_tmp],ignore_index=True)
        #end_time=timeit.default_timer()
        #elapsed_time=end_time - start_time
        #print(f'Elapse time creation features {elapsed_time} seconds')
    pd_sub=pd_pre_chunk_post.dropna()
    Train_Block=pd_sub[-100:]
    xSelectedFeatures=['pMomentum_EMA5_Volume', 'pMomentum_EMA10_Volume','pMomentum_EMA15_Volume', 'pMomentum_EMA25_Volume']
    
    x_Train=Train_Block[xSelectedFeatures]
    #Standard caler
                       
    std_scaler=joblib.load(scalerfile)
    model_cnn3 = tf.keras.models.load_model(model_file)

    x_stdscaled=std_scaler.fit_transform(x_Train)
    x_Train_stdscaled=x_Train
    for i in range(x_Train_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i]=x_stdscaled[:,i]

    #Low pass filter
    fs = 40.0       # sample rate, Hz
    cutoff = 1.3  # desired cutoff frequency of the filter, Hz
    order = 6
    T = 10000.0         # seconds
    n = int(T * fs) # total number of samples
    t = np.linspace(0, T, n, endpoint=False)
    totalF=int(fs*T)


    for i in range(x_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i] = butter_lowpass_filter(x_stdscaled[:,i], cutoff, fs, order)
    x_Train_stdscaled_filtered=x_Train_stdscaled
    x_Train_reshape=np.reshape(x_Train_stdscaled_filtered,(int(4*x_Train_stdscaled_filtered.shape[0]/100),25,4))

    yhat_Train_cnn3 = model_cnn3.predict(x_Train_reshape)
                       
    y_decode_cnn3=np.argmax(yhat_Train_cnn3,axis=1)
                       
    predict_cnn3=y_decode_cnn3[-1]
    return predict_cnn3

def PredictSoftMax120_70_Identical_Chunk(NonOverlapData):
    start_time=timeit.default_timer()
    NonOverlapData=NonOverlapData.assign( Median1 = np.round((NonOverlapData['High'] + NonOverlapData['Low'])/2,5),
                                          PrevClose=NonOverlapData['Close'].shift())
    NonOverlapData=NonOverlapData.assign( PrevMedian1=NonOverlapData['Median1'].shift())
    SmallChunk=NonOverlapData 
    EMAS=CreateEMA(SmallChunk)
    SmallChunk=SmallChunk.assign(EMA5=EMAS[0][0],EMA10=EMAS[0][1],EMA15=EMAS[0][2],EMA25=EMAS[0][3],
                                Momentum_EMA5=EMAS[0][4],Momentum_EMA10=EMAS[0][5],Momentum_EMA15=EMAS[0][6],Momentum_EMA25=EMAS[0][7])
    #Show column names
    All_Column_Names=SmallChunk.columns #for i in range(len(All_Column_Names)): #    print(i,":",All_Column_Names[i])
    X_selected_Index=list(range(13,21)) #print("Chosen columns=",All_Column_Names[list(range(13,21))])
    X_Test=SmallChunk.iloc[:,X_selected_Index] #print("X_Test=",X_Test.shape)
    #Apply Standard scaler
    X_Test_stdscaled=std_scaler.fit_transform(X_Test)
    #Apply Low pass filter and reshaped
    fs = 40.0; cutoff = 1.3; order = 6;T = 10000.0;n = int(T * fs);t = np.linspace(0, T, n, endpoint=False);totalF=int(fs*T)
    for i in range(X_Test_stdscaled.shape[1]):
        X_Test_stdscaled[:,i] = butter_lowpass_filter(X_Test_stdscaled[:,i], cutoff, fs, order)
    X_Test_stdscaled_filtered=X_Test_stdscaled
    X_Test_stdscaled_filtered_reshaped=np.reshape(X_Test_stdscaled_filtered,(1,X_Test.shape[0],X_Test.shape[1]))
    #Prediction All but retrieve the last one
    yhat_Test_cnn3 = model_cnn3.predict(X_Test_stdscaled_filtered_reshaped) #print("Shape=",yhat_Test_cnn3.shape) #print(yhat_Test_cnn3)
    y_decode_cnn3=np.argmax(yhat_Test_cnn3,axis=1)                   
    predict_cnn3=y_decode_cnn3[-1] #print("PREDICT=",predict_cnn3) #end_time=timeit.default_timer() #elapsed_time=end_time - start_time #print("working time for data preparation=",elapsed_time," sec") #0.095
    return predict_cnn3
         
def PredictSoftMax120_70(NonOverlapData):
    TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need
    TotalChunkNumber=NonOverlapData.shape[0]/TotalChunkSize
    pd_bar=copy.copy(NonOverlapData)
    pd_bar=pd_bar.assign(Median1= np.round((pd_bar['High'] + pd_bar['Low'])/2,5))
    pd_bar=pd_bar.assign(PrevMedian1=pd_bar['Median1'].shift(),
                     EMA5=pd_bar['Median1'].shift(),
                     EMA10=pd_bar['Median1'].shift(),
                     EMA15=pd_bar['Median1'].shift(),
                     EMA25=pd_bar['Median1'].shift(),
                     Median1Gap=lambda x: np.round(coeff*(x['PrevMedian1'] -x['Median1']),0),
                     Momentum1=lambda x: (x['Median1Gap']*x['Volume']))
    pd_bar=pd_bar.assign(Momentum_EMA5=pd_bar['Momentum1'].shift(),
                     Momentum_EMA10=pd_bar['Momentum1'].shift(),
                     Momentum_EMA15=pd_bar['Momentum1'].shift(),
                     Momentum_EMA25=pd_bar['Momentum1'].shift())
    pd_pre_chunk_post=pd.DataFrame()
    pd_only_chunk=pd.DataFrame()
    jStop=len(OverlapData)
    for j in range(2,jStop):
        EMA5=np.round((pd_bar['Median1'].values[i-1]*(EMA_Constant/6) )+(pd_bar['EMA5'].values[i-2]*(1-(EMA_Constant/6))),5)
        EMA10=np.round((pd_bar['Median1'].values[i-1]*(EMA_Constant/11) )+(pd_bar['EMA10'].values[i-2]*(1-(EMA_Constant/11))),5)
        EMA15=np.round((pd_bar['Median1'].values[i-1]*(EMA_Constant/16) )+(pd_bar['EMA15'].values[i-2]*(1-(EMA_Constant/16))),5)
        EMA25=np.round((pd_bar['Median1'].values[i-1]*(EMA_Constant/26) )+(pd_bar['EMA25'].values[i-2]*(1-(EMA_Constant/26))),5)
        Momentum_EMA5=np.round((pd_bar['Momentum1'].values[i-1]*(EMA_Constant/6) )+(pd_bar['Momentum_EMA5'].values[i-2]*(1-(EMA_Constant/6))),5)
        Momentum_EMA10=np.round((pd_bar['Momentum1'].values[i-1]*(EMA_Constant/11) )+(pd_bar['Momentum_EMA10'].values[i-2]*(1-(EMA_Constant/11))),5)
        Momentum_EMA15=np.round((pd_bar['Momentum1'].values[i-1]*(EMA_Constant/16) )+(pd_bar['Momentum_EMA15'].values[i-2]*(1-(EMA_Constant/16))),5)
        Momentum_EMA25=np.round((pd_bar['Momentum1'].values[i-1]*(EMA_Constant/26) )+(pd_bar['Momentum_EMA25'].values[i-2]*(1-(EMA_Constant/26))),5)
        pd_bar['EMA5'].values[i]=EMA5
        pd_bar['EMA10'].values[i]=EMA10
        pd_bar['EMA15'].values[i]=EMA15
        pd_bar['EMA25'].values[i]=EMA25
        pd_bar['Momentum_EMA5'].values[i]=Momentum_EMA5
        pd_bar['Momentum_EMA10'].values[i]=Momentum_EMA10
        pd_bar['Momentum_EMA15'].values[i]=Momentum_EMA15
        pd_bar['Momentum_EMA25'].values[i]=Momentum_EMA25   
    pd_pre_chunk_post=pd_bar
    pd_sub=pd_pre_chunk_post.dropna()
    Train_Block=pd_sub[-100:]
    xSelectedFeatures=['Momentum_EMA5','Momentum_EMA10','Momentum_EMA15','Momentum_EMA25']
    
    x_Train=Train_Block[xSelectedFeatures]
    #Standard caler
                       
    std_scaler=joblib.load(scalerfile)
    model_cnn3 = tf.keras.models.load_model(model_file)

    x_stdscaled=std_scaler.fit_transform(x_Train)
    x_Train_stdscaled=x_Train
    for i in range(x_Train_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i]=x_stdscaled[:,i]

    #Low pass filter
    fs = 40.0       # sample rate, Hz
    cutoff = 1.3  # desired cutoff frequency of the filter, Hz
    order = 6
    T = 10000.0         # seconds
    n = int(T * fs) # total number of samples
    t = np.linspace(0, T, n, endpoint=False)
    totalF=int(fs*T)


    for i in range(x_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i] = butter_lowpass_filter(x_stdscaled[:,i], cutoff, fs, order)
    x_Train_stdscaled_filtered=x_Train_stdscaled
    x_Train_reshape=np.reshape(x_Train_stdscaled_filtered,(int(4*x_Train_stdscaled_filtered.shape[0]/100),25,4))

    yhat_Train_cnn3 = model_cnn3.predict(x_Train_reshape)
                       
    y_decode_cnn3=np.argmax(yhat_Train_cnn3,axis=1)
                       
    predict_cnn3=y_decode_cnn3[-1]
    return predict_cnn3
         
def PredictBinSoft(NonOverlapData,scalerfile,model_bin_file,model_softmax_file):
    #start_time =timeit.default_timer()
    
    EMA_Constant=2
    pre_chunk_need=25
    chunk_size=100
    post_chunk_need=25
    TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need
    TotalChunkNumber=NonOverlapData.shape[0]/TotalChunkSize
    pd_bar=copy.copy(NonOverlapData)
    if(True):
        pd_bar=pd_bar.assign(Median1= np.round((pd_bar['High'] + pd_bar['Low'])/2,5))
        pd_bar=pd_bar.assign(PrevMedian1=np.nan,
                             #Past Section
                             PastHigh3=np.nan,PastLow3=np.nan,Median3=np.nan,
                             PastHigh5=np.nan,PastLow5=np.nan,Median5=np.nan,
                             PastHigh10=np.nan,PastLow10=np.nan,Median10=np.nan,
                             PastHigh15=np.nan,PastLow15=np.nan,Median15=np.nan,
                             PastHigh25=np.nan,PastLow25=np.nan,Median25=np.nan,
                             pMomentum1_Volume=np.nan,pMomentum1_Spread=np.nan,pMomentum1_VS=np.nan,
                             pMomentum_EMA5_Volume=np.nan,pMomentum_EMA10_Volume=np.nan,pMomentum_EMA15_Volume=np.nan,pMomentum_EMA25_Volume=np.nan,
                             pMomentum_EMA5_Spread=np.nan,pMomentum_EMA10_Spread=np.nan,pMomentum_EMA15_Spread=np.nan,pMomentum_EMA25_Spread=np.nan,
                             pMomentum_EMA5_VS=np.nan,pMomentum_EMA10_VS=np.nan,pMomentum_EMA15_VS=np.nan,pMomentum_EMA25_VS=np.nan
                            )
        jStop=int(TotalChunkNumber)
        pd_pre_chunk_post=pd.DataFrame()
        pd_only_chunk=pd.DataFrame()
        for j in range(jStop):
            pd_tmp=pd_bar[(j*TotalChunkSize):(j+1)*TotalChunkSize]
            PrevMedian1=pd_tmp['Median1'].shift()
            pd_tmp.loc[:,'PrevMedian1']=PrevMedian1

            pd_tmp['pMomentum1_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA5_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA10_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA25_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]

            pd_tmp['pMomentum1_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA5_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA10_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum_EMA25_Volume'].values[0:2]=pd_tmp['Volume'].values[0:2]
            pd_tmp['pMomentum1_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA5_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA10_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]           
            pd_tmp['pMomentum_EMA15_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]
            pd_tmp['pMomentum_EMA25_Spread'].values[0:2]=pd_tmp['Spread'].values[0:2]

            VS_init=pd_tmp['Volume'].values[0]*pd_tmp['Spread'].values[0]
            pd_tmp['pMomentum1_VS'].values[0]=VS_init
            pd_tmp['pMomentum1_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA5_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA5_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA10_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA10_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA15_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA15_VS'].values[1]=VS_init
            pd_tmp['pMomentum_EMA25_VS'].values[0]=VS_init
            pd_tmp['pMomentum_EMA25_VS'].values[1]=VS_init
            for i in range(TotalChunkSize):
                if(i>=2):
                    #MOMENTUM IN VOLUME
                    pd_tmp['pMomentum1_Volume'].values[i]=(coeff*(pd_tmp['Median1'].values[i-2]-pd_tmp['Median1'].values[i-1]))*pd_tmp['Volume'].values[i-1]
                    pd_tmp['pMomentum_EMA5_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/6) +(pd_tmp['pMomentum_EMA5_Volume'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/11) +(pd_tmp['pMomentum_EMA10_Volume'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/16) +(pd_tmp['pMomentum_EMA15_Volume'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_Volume'].values[i]=np.round((pd_tmp['pMomentum1_Volume'].values[i-1]*EMA_Constant/26) +(pd_tmp['pMomentum_EMA25_Volume'].values[i-2]*(1-(EMA_Constant/26))),5)
                    #MOMENTUM IN SPREAD
                    pd_tmp['pMomentum1_Spread'].values[i]=(coeff*(pd_tmp['Median1'].values[i-2]-pd_tmp['Median1'].values[i-1]))*pd_tmp['Spread'].values[i-1]
                    pd_tmp['pMomentum_EMA5_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/6) )+(pd_tmp['pMomentum_EMA5_Spread'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/11) )+(pd_tmp['pMomentum_EMA10_Spread'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/16) )+(pd_tmp['pMomentum_EMA15_Spread'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_Spread'].values[i]=np.round((pd_tmp['pMomentum1_Spread'].values[i-1]*(EMA_Constant/26) )+(pd_tmp['pMomentum_EMA25_Spread'].values[i-2]*(1-(EMA_Constant/26))),5)
                    #VolumexSpread
                    pd_tmp['pMomentum1_VS'].values[i]=(pd_tmp['Volume'].values[i-1])*(pd_tmp['Spread'].values[i-1])
                    pd_tmp['pMomentum_EMA5_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/6) )+(pd_tmp['pMomentum_EMA5_VS'].values[i-2]*(1-(EMA_Constant/6))),5)
                    pd_tmp['pMomentum_EMA10_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/11) )+(pd_tmp['pMomentum_EMA10_VS'].values[i-2]*(1-(EMA_Constant/11))),5)
                    pd_tmp['pMomentum_EMA15_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/16) )+(pd_tmp['pMomentum_EMA15_VS'].values[i-2]*(1-(EMA_Constant/16))),5)
                    pd_tmp['pMomentum_EMA25_VS'].values[i]=np.round((pd_tmp['pMomentum1_VS'].values[i-1]*(EMA_Constant/26) )+(pd_tmp['pMomentum_EMA25_VS'].values[i-2]*(1-(EMA_Constant/26))),5)
                if i>=3:
                    pd_tmp['PastHigh3'].values[i]=np.max(pd_bar['High'].values[(i-3):i])
                    pd_tmp['PastLow3'].values[i]=np.min(pd_bar['Low'].values[(i-3):i])
                    pd_tmp['Median3'].values[i]=np.round((pd_bar['PastHigh3'].values[i] + pd_bar['PastLow3'].values[i])/2,5)    
                if i>=5:
                    pd_tmp['PastHigh5'].values[i]=np.max(pd_bar['High'].values[(i-5):i])
                    pd_tmp['PastLow5'].values[i]=np.min(pd_bar['Low'].values[(i-5):i])
                    pd_tmp['Median5'].values[i]=np.round((pd_bar['PastHigh5'].values[i] + pd_bar['PastLow5'].values[i])/2,5)

                if i>=10:
                    pd_tmp['PastHigh10'].values[i]=np.max(pd_bar['High'].values[(i-10):i])
                    pd_tmp['PastLow10'].values[i]=np.min(pd_bar['Low'].values[(i-10):i])
                    pd_tmp['Median10'].values[i]=np.round((pd_bar['PastHigh10'].values[i] + pd_bar['PastLow10'].values[i])/2,5)

                if i>=15:
                    pd_tmp['PastHigh15'].values[i]=np.max(pd_bar['High'].values[(i-15):i])
                    pd_tmp['PastLow15'].values[i]=np.min(pd_bar['Low'].values[(i-15):i])
                    pd_tmp['Median15'].values[i]=np.round((pd_bar['PastHigh15'].values[i] + pd_bar['PastLow15'].values[i])/2,5)

                if i>=25:
                    pd_tmp['PastHigh25'].values[i]=np.max(pd_bar['High'].values[(i-25):i])
                    pd_tmp['PastLow25'].values[i]=np.min(pd_bar['Low'].values[(i-25):i])
                    pd_tmp['Median25'].values[i]=np.round((pd_bar['PastHigh25'].values[i] + pd_bar['PastLow25'].values[i])/2,5)
            pd_pre_chunk_post=pd.concat([pd_pre_chunk_post,pd_tmp],ignore_index=True)
        #end_time=timeit.default_timer()
        #elapsed_time=end_time - start_time
        #print(f'Elapse time creation features {elapsed_time} seconds')
    pd_sub=pd_pre_chunk_post.dropna()
    Train_Block=pd_sub[-100:]
    xSelectedFeatures=['PrevMedian1','PastHigh3', 'PastLow3', 'Median3', 'PastHigh5',
           'PastLow5', 'Median5', 'PastHigh10', 'PastLow10', 'Median10',
           'PastHigh15', 'PastLow15', 'Median15', 'PastHigh25', 'PastLow25',
           'Median25',
           'pMomentum1_Volume', 'pMomentum1_Spread', 'pMomentum1_VS',
           'pMomentum_EMA5_Volume', 'pMomentum_EMA10_Volume',
           'pMomentum_EMA15_Volume', 'pMomentum_EMA25_Volume',
           'pMomentum_EMA5_Spread', 'pMomentum_EMA10_Spread',
           'pMomentum_EMA15_Spread', 'pMomentum_EMA25_Spread', 'pMomentum_EMA5_VS',
           'pMomentum_EMA10_VS', 'pMomentum_EMA15_VS', 'pMomentum_EMA25_VS']
    x_Train=Train_Block[xSelectedFeatures]
    #Standard caler
    std_scaler=joblib.load(scalerfile)
    x_stdscaled=std_scaler.fit_transform(x_Train)
    x_Train_stdscaled=x_Train
    for i in range(x_Train_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i]=x_stdscaled[:,i]


    #Low pass filter
    fs = 40.0       # sample rate, Hz
    cutoff = 1.3  # desired cutoff frequency of the filter, Hz
    order = 6
    T = 10000.0         # seconds
    n = int(T * fs) # total number of samples
    t = np.linspace(0, T, n, endpoint=False)
    totalF=int(fs*T)


    for i in range(x_stdscaled.shape[1]):
        x_Train_stdscaled.iloc[:,i] = butter_lowpass_filter(x_stdscaled[:,i], cutoff, fs, order)
    x_Train_stdscaled_filtered=x_Train_stdscaled
    x_Train_stdscaled_filtered_reshaped = np.reshape(x_Train_stdscaled,(x_Train_stdscaled.shape[0],x_Train_stdscaled.shape[1],1))
    model_cnn_bin = tf.keras.models.load_model(model_bin_file)
    yhat_cnn_bin = model_cnn_bin.predict(x_Train_stdscaled_filtered_reshaped)
    model_cnn = tf.keras.models.load_model(model_softmax_file)
    yhat_cnn = model_cnn.predict(x_Train_stdscaled_filtered_reshaped)
    y_decode_bin=np.argmax(yhat_cnn_bin,axis=1)
    y_decode_softmax=np.argmax(yhat_cnn,axis=1)
    predict_bin_soft=y_decode_bin[-1]*y_decode_softmax[-1]
    predict_soft=y_decode_softmax[-1]
    return predict_bin_soft
def ProvFunction(TP=1,FP=1,FN=1,TN=1):
    F1 = np.round(2*TP/(2*TP + FP + FN),3)
    Acc = np.round((TP+TN)/(TP+TN+FP+FN),3)
    Sensitivity=np.round(TP/(TP + FN),3)
    Specificity=np.round(TN/(FP + TN),3)
    PPV=np.round(TP / (TP + FP),3)
    NPV=np.round(TN / (TN + FN),3)
    FPR=np.round(FP / (FP + TN),3)
    FNR=np.round(FN / (FN + TP),3)
    dict = {"F1": F1,"Accuracy": Acc,
           'Sensitivity':Sensitivity, 'Specificity':Specificity,
           'PPV': PPV,'NPV':NPV,
           'FPR': FPR, 'FNR': FNR} #print(retX.shape)
    return dict
def ThanawatScore(NPRcoeff=1.5,PPR=1,NPR=0):
    val = PPR-(NPRcoeff*NPR)
    return val
def PrepRowsSelected(PrepChunk,FutureSoftmax=False):
    PrepChunk=PrepChunk.assign(Median1 = np.round((PrepChunk['High'] + PrepChunk['Low'])/2,5),
                                        PrevClose=PrepChunk['Close'].shift())
    PrepChunk=PrepChunk.assign(PrevMedian1=PrepChunk['Median1'].shift())
    PrepChunk['PrevClose'].values[0]=PrepChunk['PrevClose'].values[1]
    PrepChunk['PrevMedian1'].values[0]=PrepChunk['PrevMedian1'].values[1]
    EMAS=CreateEMA(PrepChunk)
    PrepChunk=PrepChunk.assign(EMA5=EMAS[0],EMA10=EMAS[1],EMA15=EMAS[2],EMA25=EMAS[3],
                                Momentum_EMA5=EMAS[4],Momentum_EMA10=EMAS[5],Momentum_EMA15=EMAS[6],
                                Momentum_EMA25=EMAS[7])
    MaxMinutes=25
    Spread=43
    if(FutureSoftmax):
        PrepChunk['softmax_tp100_sl70']=np.nan
        PrepChunk['softmax_tp120_sl70']=np.nan
        PrepChunk['High25']=max(PrepChunk['High'].values[pre_chunk_need:pre_chunk_need+MaxMinutes])-PrepChunk['Close'].values[pre_chunk_need-1]
        PrepChunk['Low25']=PrepChunk['Close'].values[pre_chunk_need-1]-min(PrepChunk['Low'].values[pre_chunk_need:pre_chunk_need+MaxMinutes])
        
        for j in range(pre_chunk_need,pre_chunk_need+MaxMinutes):
            HighGap=PrepChunk['High'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]
            LowGap=PrepChunk['Low'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]
            stp=100/coeff
            ssl=(70/coeff)-Spread
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp100_sl70'].values[pre_chunk_need-1]=int(retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL))
            stp=120/coeff
            ssl=(70/coeff)-Spread
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp120_sl70'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
    return PrepChunk[0:pre_chunk_need]

def PrepRows(PrepChunk,FutureSoftmax=False):
    PrepChunk=PrepChunk.assign(Median1 = np.round((PrepChunk['High'] + PrepChunk['Low'])/2,5),
                                        PrevClose=PrepChunk['Close'].shift())
    PrepChunk=PrepChunk.assign(PrevMedian1=PrepChunk['Median1'].shift())
    PrepChunk['PrevClose'].values[0]=PrepChunk['PrevClose'].values[1]
    PrepChunk['PrevMedian1'].values[0]=PrepChunk['PrevMedian1'].values[1]
    EMAS=CreateEMA(PrepChunk)
    PrepChunk=PrepChunk.assign(EMA5=EMAS[0],EMA10=EMAS[1],EMA15=EMAS[2],EMA25=EMAS[3],
                                Momentum_EMA5=EMAS[4],Momentum_EMA10=EMAS[5],Momentum_EMA15=EMAS[6],
                                Momentum_EMA25=EMAS[7])
    MaxMinutes=25
    if(FutureSoftmax):
        PrepChunk['softmax_tp30_sl5']=np.nan
        PrepChunk['softmax_tp40_sl5']=np.nan
        PrepChunk['softmax_tp43_sl5']=np.nan
        PrepChunk['softmax_tp45_sl5']=np.nan
        PrepChunk['softmax_tp47_sl5']=np.nan
        PrepChunk['softmax_tp50_sl5']=np.nan
        PrepChunk['softmax_tp55_sl5']=np.nan
        for j in range(30,pre_chunk_need+MaxMinutes):
            HighGap=PrepChunk['High'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]
            LowGap=PrepChunk['Low'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]
            stp=30/coeff
            ssl=5/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp30_sl5'].values[pre_chunk_need-1]=int(retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL))
            stp=40/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp40_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
            stp=43/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp43_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
            stp=45/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp45_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
            stp=47/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp47_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
            stp=50/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp50_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
            stp=55/coeff
            BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
            BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
            SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
            SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
            PrepChunk['softmax_tp55_sl5'].values[pre_chunk_need-1]=retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL)
    return PrepChunk[0:pre_chunk_need]


def ReturnOrderCSV(SmallChunk,model_choice):
    #print(SmallChunk.shape) print(SmallChunk['TimeMin'])
    Order=0
    if(model_choice=='120_70'): 
        model=model_cnn3_120_70
        std_scaler=std_scaler_120_70
    else:
        model=model_cnn3_100_70
        std_scaler=std_scaler_100_70
    TimeTotal=(pd.Timedelta(SmallChunk['TimeMin'].values[-1]-SmallChunk['TimeMin'].values[0]).seconds)/60
    #print("TIME TOTAL=",TimeTotal)
    if(TimeTotal==pre_chunk_need-1):    
        eAllChunks=PrepRows(SmallChunk,FutureSoftmax=False)
        Combine_Chunks=eAllChunks[Chosen_X_Feature]

        For_X_Test=np.reshape(Combine_Chunks,(pre_chunk_need,Combine_Chunks.shape[1]))
        X_Test_stdscaled=std_scaler.fit_transform(For_X_Test)
        #Low pass filter
        fs = 40.0;cutoff = 1.3;order = 6;T = 10000.0;n = int(T * fs);t = np.linspace(0, T, n, endpoint=False);totalF=int(fs*T)
        for i in range(X_Test_stdscaled.shape[1]):
            X_Test_stdscaled[:,i] = butter_lowpass_filter(X_Test_stdscaled[:,i], cutoff, fs, order)
        X_Test_stdscaled_filtered=X_Test_stdscaled
        X_Test_stdscaled_filtered_reshaped_120_70=np.reshape(X_Test_stdscaled_filtered,(1,pre_chunk_need,Combine_Chunks.shape[1]))
        yhat_Test = model.predict(X_Test_stdscaled_filtered_reshaped_120_70, verbose=0)
        y_Test_decode=np.argmax(yhat_Test,axis=1)
        Order=y_Test_decode[-1]
        
    else:
        print("Gap in data")
        
    return Order

def ReturnOrderOnline(model_choice):
    Order=0
    if(model_choice=='120_70'): 
        model=model_cnn3_120_70
        std_scaler=std_scaler_120_70
    else:
        model=model_cnn3_100_70
        std_scaler=std_scaler_100_70
    if(useMT5):
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, pre_chunk_need)
        rates_frame = pd.DataFrame(rates)
        #display(rates_frame)
        rates_frame.columns = ['TimeMin', 'Open', 'High','Low','Close','Volume','Spread','RealVolume']
        rates_frame['TimeMin']=pd.to_datetime(rates_frame['TimeMin'], unit='s')
        SmallChunk=rates_frame
        TimeTotal=(pd.Timedelta(SmallChunk['TimeMin'].values[-1]-SmallChunk['TimeMin'].values[0]).seconds)/60
        if(TimeTotal==pre_chunk_need-1):    
            eAllChunks=PrepRows(SmallChunk,FutureSoftmax=False)
            Combine_Chunks=eAllChunks[Chosen_X_Feature]

            For_X_Test=np.reshape(Combine_Chunks,(pre_chunk_need,Combine_Chunks.shape[1]))
            X_Test_stdscaled=std_scaler.fit_transform(For_X_Test)
            #Low pass filter
            fs = 40.0;cutoff = 1.3;order = 6;T = 10000.0;n = int(T * fs);t = np.linspace(0, T, n, endpoint=False);totalF=int(fs*T)
            for i in range(X_Test_stdscaled.shape[1]):
                X_Test_stdscaled[:,i] = butter_lowpass_filter(X_Test_stdscaled[:,i], cutoff, fs, order)
            X_Test_stdscaled_filtered=X_Test_stdscaled
            X_Test_stdscaled_filtered_reshaped_120_70=np.reshape(X_Test_stdscaled_filtered,(1,pre_chunk_need,Combine_Chunks.shape[1]))
            yhat_Test = model.predict(X_Test_stdscaled_filtered_reshaped_120_70)
            y_Test_decode=np.argmax(yhat_Test,axis=1)
            Order=y_Test_decode[-1]
        
    else:
        print("Gap in data")
        
    return Order
def PrepRowsGrid(PrepChunk,FutureSoftmax=False):
    PrepChunk=PrepChunk.assign(Median1 = np.round((PrepChunk['High'] + PrepChunk['Low'])/2,5),
                                        PrevClose=PrepChunk['Close'].shift())
    PrepChunk=PrepChunk.assign(PrevMedian1=PrepChunk['Median1'].shift())
    PrepChunk['PrevClose'].values[0]=PrepChunk['PrevClose'].values[1]
    PrepChunk['PrevMedian1'].values[0]=PrepChunk['PrevMedian1'].values[1]
    EMAS=CreateEMA(PrepChunk)
    PrepChunk=PrepChunk.assign(EMA5=EMAS[0],EMA10=EMAS[1],EMA15=EMAS[2],EMA25=EMAS[3],
                                Momentum_EMA5=EMAS[4],Momentum_EMA10=EMAS[5],Momentum_EMA15=EMAS[6],
                                Momentum_EMA25=EMAS[7])
    MaxMinutes=25
    Spread=43
    if(FutureSoftmax):
        PrepChunk['High25']=max(PrepChunk['High'].values[pre_chunk_need:pre_chunk_need+MaxMinutes])-PrepChunk['Close'].values[pre_chunk_need-1]
        PrepChunk['Low25']=PrepChunk['Close'].values[pre_chunk_need-1]-min(PrepChunk['Low'].values[pre_chunk_need:pre_chunk_need+MaxMinutes])
        
        for j in range(pre_chunk_need,pre_chunk_need+MaxMinutes):
            HighGap=PrepChunk['High'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]
            LowGap=PrepChunk['Low'].values[pre_chunk_need:j]-PrepChunk['PrevClose'].values[pre_chunk_need-1]    
            for tp in Dict['TP']:
                for sl in Dict['SL']:
                    #print("TP={},SL={}".format(tp,sl))
                    ColumnText='softmax_tp'+str(tp)+"_sl"+str(sl)
                    PrepChunk[ColumnText]=np.nan
                    stp=tp/coeff
                    ssl=(sl/coeff)-Spread
                    BuyTP=np.min(np.append(np.where(HighGap>stp)[0],np.inf))
                    BuySL=np.min(np.append(np.where(LowGap<-ssl)[0],np.inf))
                    SellTP=np.min(np.append(np.where(LowGap<-stp)[0],np.inf))
                    SellSL=np.min(np.append(np.where(HighGap>ssl)[0],np.inf))
                    PrepChunk[ColumnText].values[pre_chunk_need-1]=int(retSoftMaxCondition(BuyTP,BuySL,SellTP,SellSL))
    return PrepChunk[0:pre_chunk_need]
def testImport(H):
    print("Form IMPORT",H)