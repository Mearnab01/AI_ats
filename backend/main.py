from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.core.logger import setup_logger


logger = setup_logger("main")

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    

def create_app()-> FastAPI:
    app = FastAPI(
        title="ATS Intelligence Platform API",
        description="Hybrid BERT + Groq Resume Analysis Engine",
        version="1.0.0"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    items_db = {}
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the FastAPI backend!"}

    @app.post("/items/{item_id}")
    def create_item(item_id: int, item: Item):
        items_db[item_id] = item
        return {"message": f"Item with ID {item_id} created successfully!", "item": item}

    @app.get("/items/{item_id}")
    def read_item(item_id: int):
        item = items_db.get(item_id)
        if item:
            return {"item_id": item_id, "item": item}
        else:
            return {"message": f"Item with ID {item_id} not found."}
        
        
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("FastAPI server started on http://localhost:8000")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
        
