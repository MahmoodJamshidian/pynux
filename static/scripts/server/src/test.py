import server

index = 0
def res(msg:bytes):
    global p, index
    index+=1
    print("received:", msg)
    if index > 20:
        return
    p.write(f"{index} msg".encode())

p = server.PyProc('cat', res)
p.start()
p.write(b'hi!')