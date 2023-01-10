import calendar, datetime

def data_util(util=datetime.datetime.now()):
    dataAtual = util
    iteradorMes = calendar.Calendar(6).itermonthdates(dataAtual.year, dataAtual.month)
    listaDias = [val.strftime("%Y-%m-%d") for val in iteradorMes]
    dataString = dataAtual.strftime("%Y-%m-%d")
    monthName = dataAtual.strftime("%B")
    return dataString, monthName, listaDias

