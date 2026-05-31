from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from routes.stats import router as stats_router
from routes.contests import router as contests_router
from routes.profiles import router as profiles_router
from routes.badges import router as badges_router
from routes.heatmap import router as heatmap_router
from routes.unified import router as unified_router
from routes.docs import router as docs_router

app = FastAPI(
    title="LeetCode Stats API",
    description="A FastAPI service to fetch and display public LeetCode statistics.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom docs landing page lives at "/"; the unified router's canonical
# endpoints are registered before the catch-all "/{username}" stats route.
app.include_router(docs_router)
app.include_router(unified_router)
app.include_router(contests_router)
app.include_router(profiles_router)
app.include_router(badges_router)
app.include_router(heatmap_router)
app.include_router(stats_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=Config.DEBUG)
