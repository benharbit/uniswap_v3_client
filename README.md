This library instructs how to use the uniswap python library.
[Uniswap Python library](https://github.com/uniswap-python/uniswap-python)
I am using a fork I make of that library that makes it easy to use.
[My Uniswap Python library fork](https://github.com/risingsun007/uniswap-python)

<H2> Instructions </H2>
1) Install program using poetry
2) Define Enviromental Variables
    a) PROVIDER: "a link to your node provider i.e an infura provider or you local provider (http://www.localhost:8545)
    b) PRIVATE_KEY: "your private key" 
3) Run program using "poetry run python uniswap/addLiquidity.py"

The main file is located in uniswap/addLiquidity.py
In that file you may want to change token0 and token1 to the tokens on your network you want to use.
Also you can change amount0 and amount1 to determine how much liquidity to add.

