"""Deterministic controller for the pinned mGBA core."""
import pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parent.parent
class Emulator:
    def __init__(self, rom, elf):
        self.symbols={}
        self.all_symbols={}
        for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines():
            bits=line.split()
            if len(bits)==3:
                self.symbols[bits[2]]=int(bits[0],16)
                self.all_symbols.setdefault(bits[2],[]).append(int(bits[0],16))
        self.p=subprocess.Popen([str(ROOT/'.build-deps/emulator-driver'),str(rom)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        assert self.p.stdout.readline().strip()=='READY'
    def command(self,line):
        self.p.stdin.write(line+'\n');self.p.stdin.flush()
        reply=self.p.stdout.readline().strip()
        assert reply, f'Emulator terminated on {line}'
        return reply
    def frames(self, keys=0, count=30): return self.command(f'F {keys} {count}')
    def tap(self, keys, count=2, wait=20):
        self.frames(keys,count);self.frames(0,wait)
    def read(self,address,size=4):
        if isinstance(address,str): address=self.symbols[address]
        return int.from_bytes(bytes.fromhex(self.command(f'R {address:x} {size}')),'little')
    def bytes(self,address,size): return bytes.fromhex(self.command(f'R {address:x} {size}'))
    def screenshot(self,path): return self.command('S '+str(path))
    def save(self,path): return self.command('SAVE '+str(path))
    def load(self,path): return self.command('LOAD '+str(path))
    def callback(self):
        cb=self.read(self.symbols['gMain']+4)&~1
        return next((k for k,v in self.symbols.items() if v==cb),hex(cb))
    def tasks(self):
        names=[]
        for i in range(16):
            address=self.symbols['gTasks']+i*40
            if self.read(address+4,1):
                cb=self.read(address)&~1
                names.append(next((k for k,v in self.symbols.items() if v==cb),hex(cb)))
        return names
    def close(self):
        self.p.stdin.write('Q\n');self.p.stdin.flush();self.p.wait(timeout=10)
