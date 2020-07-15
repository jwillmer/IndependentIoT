def getLiPoPercentage(voltage):
    # Numbers from https://blog.ampow.com/lipo-voltage-chart/
    voltageDic = {
        4.20: 100,
        4.15: 95,
        4.11: 90,
        4.08: 85,
        4.02: 80,
        3.98: 75,
        3.95: 70,
        3.91: 65,
        3.87: 60,
        3.85: 55,
        3.84: 50,
        3.82: 45,
        3.80: 40,
        3.79: 35,
        3.77: 30,
        3.75: 25,
        3.73: 20,
        3.71: 15,
        3.69: 10,
        3.61: 5,
        3.27: 0
    }

    voltageDicPercentage = list(voltageDic.values())
    voltageDicVolt = list(voltageDic)

    vi1_index = closestVoltageItem(voltageDic, voltage)
    vi1_volt = voltageDicVolt[vi1_index]
    vi1_percent = voltageDicPercentage[vi1_index]

    vi2_index = vi1_index - 1 if vi1_volt < voltage else vi1_index + 1
    if vi2_index >= len(voltageDic) or vi2_index < 0:
        return vi1_volt

    vi2_volt = voltageDicVolt[vi2_index]
    vi2_percent = voltageDicPercentage[vi2_index]
    
    minV = vi1_volt if vi1_volt < vi2_volt else vi2_volt
    minVpercent = vi1_percent if vi1_volt < vi2_volt else vi2_percent
    maxV = vi1_volt if vi1_volt > vi2_volt else vi2_volt

    part = (voltage - minV) * 100
    whole = (maxV - minV) * 100

    p =  float(part)/float(whole) * 5
    return round(minVpercent + p)

def closestVoltageItem(voltageList, voltage):
    closestNumber = -1
    aux = []
    for valor in voltageList:
        aux.append(abs(voltage-valor))

    return aux.index(min(aux))