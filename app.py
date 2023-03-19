from service import Cacher, Expander
from exceptions import URLNotShortenedException

from fastapi import (
    FastAPI,
    HTTPException, Path, Request, Body, Query,
    status
)
from fastapi.responses import PlainTextResponse, RedirectResponse


URL_TTL_SECONDS = 60 * 60 * 24
URL_LENGTH = 7


app = FastAPI()


@app.post("/")
async def short_url(
        request: Request,
        url_to_be_shortened: str = Body(
            example="https://google.com",
            max_length=2000
        ),
        ttl: int = Query(
            default=URL_TTL_SECONDS,
            gt=0, lt=URL_TTL_SECONDS*3,
            description="Time to live"
        ),
        one_time: bool = Query(
            default=False,
            alias="one-time",
            description="If true, after following a url, url becomes invalid"
        )
):
    cacher = Cacher(ttl, URL_LENGTH)

    shorted_url_id = cacher.cache_url_and_get_id(url_to_be_shortened, one_time)

    redirect_url = f"{request.headers['Host']}/{shorted_url_id}"

    return PlainTextResponse(redirect_url)


@app.get("/{shorted_url_id}")
async def redirect_by_shorted_url(
    shorted_url_id: str = Path(
        regex=r'[a-zA-Z0-9]{7,}',
        example="wfZy2mH"
    )
):
    expander = Expander()
    try:
        expanded_url: str = expander.expand(shorted_url_id)
    except URLNotShortenedException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(expanded_url, status_code=status.HTTP_303_SEE_OTHER)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
