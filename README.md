# Terminal_2048

### Introduction
This is a simplified, terminal version of 2048 game.<br>
I developed it just for fun.<br>
Play the original game [here](https://play2048.co/)!

### Download and run it in your terminal
1. Download the file into your own laptop
2. Run `$ python3 2048.py` in your terminal

### Algorithm: State Machine
- State machine is basically the `main()` function in my program. The state machine uses `state` variable to store the current state of the game. <br>

- The dictionary in `main()` called `state_actions` is the "rule" associating the state and the function that should be called in each state.
```
state_actions = {
    'Init': init,
    'Game': game,
    'Gameover': gameover,
    'Win': win,
    'Pause': pause
}
```
- While `state` is anything than 'Exit', the new state of game will be the return of the function linked to the current state. See the following code:
```
while state != 'Exit':
    state = state_actions[state]()
```

### Reference
- The original 2048 game: https://play2048.co/.
- Terminal_2048 original version: https://www.shiyanlou.com/courses/368.
