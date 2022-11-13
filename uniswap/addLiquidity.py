from typing import List

from web3 import Web3

from uniswap import Uniswap
from uniswap.types import AddressLike
import os
import math

eth = Web3.toChecksumAddress("0x0000000000000000000000000000000000000000")
weth = Web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
usdt = Web3.toChecksumAddress("0xdac17f958d2ee523a2206206994597c13d831ec7")
vxv = Web3.toChecksumAddress("0x7d29a64504629172a429e64183d6673b9dacbfce")


def _perc(f: float) -> str:
    return f"{round(f * 100, 3)}%"


def usdt_to_vxv_v2():
    """
    Checks impact for a pool with very little liquidity.
    This particular route caused a $14k loss for one user: https://github.com/uniswap-python/uniswap-python/discussions/198
    """
    uniswap = Uniswap(address=None, private_key=None, version=2)

    route: List[AddressLike] = [usdt, weth, vxv]

    # Compare the results with the output of:
    # https://app.uniswap.org/#/swap?use=v2&inputCurrency=0xdac17f958d2ee523a2206206994597c13d831ec7&outputCurrency=0x7d29a64504629172a429e64183d6673b9dacbfce
    qty = 10 * 10 ** 8

    # price = uniswap.get_price_input(usdt, vxv, qty, route=route) / 10 ** 18
    # print(price)

    impact = uniswap.estimate_price_impact(usdt, vxv, qty, route=route)
    # NOTE: Not sure why this differs from the quote in the UI?
    #       Getting -27% in the UI for 10 USDT, but this returns >95%
    #       The slippage for v3 (in example below) returns correct results.
    print(
        f"Impact for buying VXV on v2 with {qty / 10**8} USDT:  {_perc(impact)}")

    qty = 13900 * 10 ** 8
    impact = uniswap.estimate_price_impact(usdt, vxv, qty, route=route)
    print(
        f"Impact for buying VXV on v2 with {qty / 10**8} USDT:  {_perc(impact)}")


def eth_to_vxv_v3():
    """Checks price impact for a pool with liquidity."""
    uniswap = Uniswap(address=None, private_key=None, version=3)

    # Compare the results with the output of:
    # https://app.uniswap.org/#/swap?use=v3&inputCurrency=ETH&outputCurrency=0x7d29a64504629172a429e64183d6673b9dacbfce
    qty = 1 * 10 ** 18
    impact = uniswap.estimate_price_impact(eth, vxv, qty, fee=10000)
    print(
        f"Impact for buying VXV on v3 with {qty / 10**18} ETH:  {_perc(impact)}")

    qty = 100 * 10 ** 18
    impact = uniswap.estimate_price_impact(eth, vxv, qty, fee=10000)
    print(
        f"Impact for buying VXV on v3 with {qty / 10**18} ETH:  {_perc(impact)}")


def price_to_tick(price: float, tick_spacing: int) -> int:
    """Converts a price to a tick."""
    return int(math.log(price) / math.log(1.0001) * 1e3)


def adj_price_for_decimals(uniswap, pool, price) -> float:
    decimal0 = uniswap.get_token(pool.functions.token0().call()).decimals
    decimal1 = uniswap.get_token(pool.functions.token1().call()).decimals
    return price*10**(decimal1 - decimal0)


def tick_to_price(uniswap, pool, price: float, round_down: bool) -> float:
    tick_spacing = pool.functions.tickSpacing().call()
    tick = math.log(adj_price_for_decimals(
        uniswap, pool, price))/math.log(1.0001)/tick_spacing
    rtn_tick = math.floor(tick) * tick_spacing
    if round_down == False and tick % tick_spacing != 0:
        rtn_tick += tick_spacing
    return rtn_tick


def addLiquidity(uniswap, pool, lower_prc, upper_prc, amount0, amount1):
    print("add liquidity params, ", lower_prc, " ", upper_prc, amount0, amount1, " ", tick_to_price(
        uniswap, pool, lower_prc, True), " ", tick_to_price(uniswap, pool, upper_prc, False))
    result = uniswap.mint_liquidity(pool, amount0, amount1, tick_to_price(
        uniswap, pool, lower_prc, True), tick_to_price(uniswap, pool, upper_prc, False))
    print("add liquidity result: ", result.hex())


def getPrice(uniswap, address0, address1, pool_fee):
    return uniswap.get_price_input(address0, address1, 10**3, pool_fee)/10**3


def close_position(uniswap, tokenid):
    result = uniswap.close_position(tokenid)
    print("result of close position: ", result.hex())
    return result


def get_liquidity_positions(uniswap):
    positions = uniswap.get_liquidity_positions()
    print("list of liquidity positions: ", positions)
    return positions


if __name__ == "__main__":
    token0 = Web3.toChecksumAddress(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    token1 = Web3.toChecksumAddress(
        "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6")
    pool_fee = 3000
    amount0 = 1000
    amount1 = 1000

    my_wallet = Web3().eth.account.from_key(os.environ["PRIVATE_KEY"])
    uniswap = Uniswap(
        address=my_wallet.address, private_key=my_wallet.privateKey, version=3)

    price = getPrice(uniswap, token0, token1, pool_fee)
    pool = uniswap.get_pool_instance(token0, token1, pool_fee)

    lower_prc = .99 * price
    upper_prc = 1.01 * price
    
    addLiquidity(uniswap, pool, lower_prc, upper_prc, amount0, amount1)
    positions = get_liquidity_positions(uniswap)
    if len(positions) > 0:
        close_position(uniswap, positions[-1])
