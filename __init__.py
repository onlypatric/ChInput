import os
import sys
from pynput import keyboard
from pynput.keyboard import Key,KeyCode
from colorama import Fore,Back,Style,init
init(1)

_DEFAULT_SETTINGS={
    "--colored"     : True,
    "--color"       : Fore.GREEN,
    "--reset"       : Fore.RESET,
    "--boxed"       : True,
    "--column"      : 2,
    "--maxlenght"   : 30,
    "--extended"    : False,
    "--start"       : True,
    "--unicode"     : True,
    "--down"        : Key.down,
    "--up"          : Key.up,
    "--submit"      : [Key.enter,Key.esc],
    "--newline"     : "\n"
}
_DEFAULT_SETTINGS.update({
    "--help"        : f"{Fore.WHITE}UP: {Fore.LIGHTBLACK_EX}<{Fore.YELLOW}{_DEFAULT_SETTINGS.get('--up')}{Fore.LIGHTBLACK_EX}> {Fore.WHITE}DOWN: {Fore.LIGHTBLACK_EX}<{Fore.YELLOW}{_DEFAULT_SETTINGS.get('--down')}{Fore.LIGHTBLACK_EX}>{Fore.RESET}\n",
})
TOP_LEFT            = "┌"
TOP_RIGHT           = "┐"
BOTTOM_LEFT         = "└"
BOTTOM_RIGHT        = "┘"
HORIZONTAL          = "─"
VERTICAL            = "│"

class TruncatedString(str):
    def truncate(self,maxsize:int=20):
        self.maxsize=maxsize
        self.fullstr=self.__str__()
        if len(self.fullstr)>self.maxsize:
            self.fullstr=self.fullstr[:self.maxsize-3]+"..."
        self.ismaxed = len(self.fullstr)==self.maxsize
        return self

class ChoiceInput:
    def __init__(
        self,
        choices:"list[str|int]",
        settings:"dict[str,str|bool]"=_DEFAULT_SETTINGS
    ) -> None:

        self.TOP_LEFT=self.TOP_RIGHT=self.BOTTOM_LEFT=self.BOTTOM_RIGHT=self.HORIZONTAL=self.VERTICAL=""
        if settings.get("--boxed",True)==1:
            if settings.get("--unicode",False):
                self.TOP_LEFT       =TOP_LEFT
                self.TOP_RIGHT      =TOP_RIGHT
                self.BOTTOM_LEFT    =BOTTOM_LEFT
                self.BOTTOM_RIGHT   =BOTTOM_RIGHT
                self.HORIZONTAL     =HORIZONTAL
                self.VERTICAL       =VERTICAL
                
            else:
                self.TOP_LEFT=self.TOP_RIGHT=self.BOTTOM_LEFT=self.BOTTOM_RIGHT="*"
                self.HORIZONTAL="-"
                self.VERTICAL="|"

        if settings.get("--maxlenght",os.get_terminal_size().columns-6)>=(os.get_terminal_size().columns-6):
            self.max_lenght = os.get_terminal_size().columns-6
        else:
            self.max_lenght=settings.get("--maxlenght")

        self.max_lines = os.get_terminal_size().lines-3
        self.column     = settings.get("--column",1)
        self.index      = 0
        self.isStarted  = False
        self.choices    = choices
        self.lenght     = max([len(str(i)) for i in self.choices])
        self.selected   = [not bool(i) for i in range(len(self.choices))];
        self.settings   = settings
        self.array      = self.toReadableStrings()
        self.lines      = len(self.choices)+self.settings.get("--boxed",True)*2
        if self.lines > self.max_lines:
            self.singleLine=True
        else:
            self.singleLine=False
        if (self.lenght>self.max_lenght):
            self.lenght=self.max_lenght
            settings.update({"--column":1})
        if self.settings.get("--start",True):
            sys.stdout.write(self.settings.get("--help",""))
            if self.singleLine:
                self.printSingleLine()
            else:
                self.printall()
            self.start()
    def toReadableStrings(self) -> "list[TruncatedString]":
        return [TruncatedString(i).truncate(maxsize=self.max_lenght) for i in self.choices]

    def printSingleLine(self):
        if self.settings.get("--boxed",True):sys.stdout.write(f"%s{self.HORIZONTAL*(self.lenght+2)}%s%s"%(self.TOP_LEFT,self.TOP_RIGHT,self.settings.get("--newline","\n")))
        sys.stdout.write(
            f"%s{self.settings.get('--color',Fore.GREEN) if self.settings.get('--colored',True) else ''}"
            f"%-{self.lenght+2}s"
            f"{self.settings.get('--reset',Fore.RESET) if self.settings.get('--colored',True) else ''}%s"
            "%s"
            %(
                self.VERTICAL,
                "("+self.array[self.selected.index(True)].fullstr+")",
                self.VERTICAL,
                self.settings.get("--newline","\n")
            )
        )
        if self.settings.get("--boxed",True):sys.stdout.write(f"%s({self.index}/{self.lines}){self.HORIZONTAL*(self.lenght+2-len(f'({self.index}/{self.lines})'))}%s%s"%(self.BOTTOM_LEFT,self.BOTTOM_RIGHT,self.settings.get("--newline","\n")))
    

    def printall(self):
        if self.settings.get("--boxed",True):sys.stdout.write(f"%s{self.HORIZONTAL*(self.lenght+2)}%s%s"%(self.TOP_LEFT,self.TOP_RIGHT,self.settings.get("--newline","\n")))
        for i,focus in zip(self.array,self.selected):
            sys.stdout.write(
                f"%s{(self.settings.get('--color',Fore.GREEN) if self.settings.get('--colored',True) else '') if focus else ''}"
                f"%-{self.lenght+2}s"
                f"{self.settings.get('--reset',Fore.RESET) if self.settings.get('--colored',True) else ''}%s"
                "%s"
                %(
                    self.VERTICAL,
                    ("(" if focus else ' ')+i.fullstr+(")" if focus else ' '),
                    self.VERTICAL,
                    self.settings.get("--newline","\n")
                )
            )
        if self.settings.get("--boxed",True):sys.stdout.write(f"%s{self.HORIZONTAL*(self.lenght+2)}%s%s"%(self.BOTTOM_LEFT,self.BOTTOM_RIGHT,self.settings.get("--newline","\n")))
    def onPress(self,key):
        if key==self.settings.get("--down",Key.down):
            if self.index==self.lines-self.settings.get("--boxed",True)*2-1:
                self.index=0
            else:
                self.index+=1
            self.selected.insert(self.index,self.selected.pop(self.selected.index(True)))
            self.update()
        elif key==self.settings.get("--up",Key.up):
            if self.index!=0:
                self.index-=1
            else:
                self.index=self.lines-self.settings.get("--boxed",True)*2-1
            self.selected.insert(self.index,self.selected.pop(self.selected.index(True)))
            self.update()
        elif key in self.settings.get("--submit",[Key.enter,Key.esc]):
            return False
    def start(self):
        with keyboard.Listener(on_press=self.onPress,suppress=True) as keybd:
            keybd.join()
    def update(self):
        if self.singleLine:
            sys.stdout.write("\033[A"*3)
            self.printSingleLine()
        else:
            sys.stdout.write("\033[A"*(int(self.lines/self.column)+3))
            self.printall()
    def get(self) -> str:
        for a,b in zip(self.array,self.selected):
            if b:
                return a.__str__();
    def __str__(self) -> str:
        return self.get()
    def getIndex(self):
        return self.selected.index(1)
if __name__=="__main__":
    choices=os.listdir("..")
    chinput=ChoiceInput(choices)
    print(chinput)