# schmittie_chess
Small chess game with UI and crude AI. 

## Setup

Install with pip using `python -m pip install -e .`, you can start a game with:
```py
from schmittie_chess import Game
game = Game()
game.mainloop()
```

## Example 

The first game i managed to win against my V0 MiniMax player went like this. Even though i missed two mate-in-ones i somehow ended up victorious. 
1. d4 e6 2. e4 Nc6 3. Bb5 a6 4. Bxc6 dxc6 5. Nf3 Bb4+ 6. Nbd2 Be7 7. O-O Bb4 8. Qe2 a5 9. c3 Bd6 10. a3 Bf4 11. b4 axb4 12. cxb4 Bxd2 13. Bxd2 Ne7 14. Rfd1 Ng6 15. Bg5 f6 16. Bh4 Nxh4 17. Nxh4 Rg8 18. Rd3 Rh8 19. Rad1 Rg8 20. Nf3 Rh8 21. d5 Qd6 22. dxe6 Qxd3 23. Rxd3 Bxe6 24. e5 fxe5 25. Nxe5 Rg8 26. Nd7 Rd8 27. Nc5 Rxd3 28. Qxd3 Bd5 29. a4 h6 30. h3 Rh8 31. Qe2+ Kf8 32. Nd7+ Kf7 33. Ne5+ Kf6 34. Nd3 Bc4 35. Qe5+ Kg6 36. Qe4+ Kh5 37. Qxc4 Kg5 38. g3 Kh5 39. Ne5 Rf8 40. Qg4# 1-0
