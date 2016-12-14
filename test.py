import time
pastTime = int(time.time())
time.sleep(10)
currentTime = int(time.time())
diff = [0,0,0,0]

def timeConvert(remainder, diff):
    diff[0] = remainder // 86400
    remainder = remainder % 86400
    diff[1] = remainder // 3600
    remainder = remainder % 3600
    diff[2] = remainder // 60
    diff[3] = remainder % 60
    return diff
    
print(timeConvert(currentTime - pastTime, diff))    
