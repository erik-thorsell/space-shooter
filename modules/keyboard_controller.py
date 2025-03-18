import pygame

class Controller:
    def __init__(self) -> object:
        self.keybinds = {}

    def register(self, key, function=None, onKeyUp=None, holdable: bool=False) -> None:
        if type(key) == list:
            for k in key:
                self.keybinds[k[0]] = {"function": k[1], "onKeyUp": k[2] if len(k) > 2 else None, "holdable": holdable, "paused": False}
            return
        self.keybinds[key] = {"function": function, "onKeyUp": onKeyUp, "holdable": holdable, "paused": False}
    
    def release(self, key):
        self.keybinds[key] = None

    def pause(self, key):
        if key in self.keybinds:
            self.keybinds[key]["paused"] = True

    def unpause(self, key):
        if key in self.keybinds:
            self.keybinds[key]["paused"] = False
    
    def process_events(self, events):
        for event in events:
            match event.type:
                case pygame.KEYDOWN:
                    if event.key in self.keybinds and not self.keybinds[event.key]["paused"]:
                        self.keybinds[event.key]["function"]()
                
                case pygame.KEYUP:
                    if event.key in self.keybinds and self.keybinds[event.key]["onKeyUp"] and not self.keybinds[event.key]["paused"]:
                        self.keybinds[event.key]["onKeyUp"]()
    
        keys = pygame.key.get_pressed()
        for key in self.keybinds:
            if keys[key] and self.keybinds[key]["holdable"] and not self.keybinds[key]["paused"]:
                self.keybinds[key]["function"]()
            
    

    