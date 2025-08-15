from mcp_api.app import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run("mcp_api.main:app", host="0.0.0.0", port=9000, reload=True)



