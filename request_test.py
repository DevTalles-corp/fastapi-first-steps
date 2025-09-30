import asyncio
import httpx
import time

URL = "http://127.0.0.1:8000/posts/async"


async def hit(t, client: httpx.AsyncClient):
    start = time.perf_counter()
    r = await client.get(URL, params={"t": t})
    elapsed = time.perf_counter() - start
    return t, elapsed, r.json()


async def main():
    # sube el timeout para cubrir el mayor 't'
    timeout = httpx.Timeout(20.0)  # o None para sin límite
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        start = time.perf_counter()
        results = await asyncio.gather(
            hit(3.0, client),
            hit(5.5, client),
            hit(7.8, client),
            hit(9.7, client),
            return_exceptions=True,   # para ver si alguna falla
        )
        total = time.perf_counter() - start

    print("\n--- Resultados ---")
    for res in results:
        if isinstance(res, Exception):
            print("Error:", repr(res))
        else:
            t, elapsed, body = res
            print(f"sleep={t:<4}  tardó={elapsed:.2f}s  respuesta={body}")
    print(f"\nTiempo total de pared: {total:.2f}s\n")

if __name__ == "__main__":
    asyncio.run(main())
