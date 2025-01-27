import logging

from db import DB
import config
from service import Cacher, Expander
from exceptions import URLNotShortenedException

from fastapi import (
    FastAPI,
    HTTPException, Path, Request, Body,
    status,
)
from fastapi.responses import PlainTextResponse, RedirectResponse


app = FastAPI()
logger = logging.getLogger("api_logger")
db = DB(config.REDIS_HOST, config.REDIS_PORT)


@app.post("/")
async def short_url(
        request: Request,
        url_to_be_shortened: str = Body(
            example="https://google.com",
            max_length=2000
        ),
        ttl: int = Body(
            default=config.MIN_URL_TTL_SECONDS,
            gt=config.MIN_URL_TTL_SECONDS,
            lt=config.MAX_URL_TTL_SECONDS,
            description="Time to live"
        ),
        one_time: bool = Body(
            default=False,
            description="If true, after following a url, url becomes invalid"
        ),
        alias: str | None = Body(
            default=None,
            min_length=config.MIN_URL_ALIAS_LEN, max_length=config.MAX_URL_ALIAS_LEN,
            regex=r'[a-zA-Z0-9]{7,}',
            example="wfZy2mH",
            description="Desired alias, if already taken or invalid - generates new"
        )
):
    cacher = Cacher(ttl, config.MIN_URL_ALIAS_LEN, db)

    is_alias_not_provided_or_is_taken = (alias is None) or cacher.is_cached(alias)

    if is_alias_not_provided_or_is_taken:
        alias = cacher.generate_free_alias()
        logger.debug(f"Generated new free alias '{alias}' for url {url_to_be_shortened}")

    if one_time:
        cacher.cache_one_time_url(url_to_be_shortened, alias)
    else:
        cacher.cache_url(url_to_be_shortened, alias)

    logger.debug(f"Cached url {url_to_be_shortened} with alias '{alias}'")

    redirect_url = f"{request.headers['Host']}/{alias}"
    logger.info(f"Shortened url {url_to_be_shortened} with alias '{alias}' from '{request.client.host}'")

    return PlainTextResponse(redirect_url)

@app.get("/ping")
async def ping():
    return PlainTextResponse(content="pong", status_code=status.HTTP_200_OK)


@app.get("/{alias}")
async def redirect_by_shorted_url(
    alias: str = Path(
        regex=r'[a-zA-Z0-9]{7,}',
        min_length=config.MIN_URL_ALIAS_LEN,
        max_length=config.MAX_URL_ALIAS_LEN,
        example="wfZy2mH"
    )
):
    expander = Expander(db)
    try:
        expanded_url: str = expander.expand(alias)
    except URLNotShortenedException:
        logger.warning(f"URL with alias '{alias}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logger.info(f"Expanded url {expanded_url} from alias '{alias}'")
    return RedirectResponse(expanded_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
