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
            description="If true, after following a url, url becomes invalid"
        ),
        alias: str | None = Query(
            default=None,
            min_length=7, max_length=URL_LENGTH*2,
            regex=r'[a-zA-Z0-9]{7,}',
            example="wfZy2mH",
            description="Desired alias, if already taken or invalid - generates new"
        )
):
    cacher = Cacher(ttl, URL_LENGTH)

    is_alias_not_provided_or_is_taken = (alias is None) or cacher.is_cached(alias)

    if is_alias_not_provided_or_is_taken:
        alias = cacher.generate_free_alias()

    if one_time:
        cacher.cache_one_time_url(url_to_be_shortened, alias)
    else:
        cacher.cache_url(url_to_be_shortened, alias)

    redirect_url = f"{request.headers['Host']}/{alias}"

    return PlainTextResponse(redirect_url)


@app.get("/{alias}")
async def redirect_by_shorted_url(
    alias: str = Path(
        regex=r'[a-zA-Z0-9]{7,}',
        min_length=7, max_length=URL_LENGTH*2,
        example="wfZy2mH"
    )
):
    expander = Expander()
    try:
        expanded_url: str = expander.expand(alias)
    except URLNotShortenedException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(expanded_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
