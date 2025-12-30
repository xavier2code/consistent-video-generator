from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# 请求模型
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

# 示例数据存储
items_db = []

@router.get("/items", tags=["items"])
async def get_items():
    """获取所有项目"""
    return {"items": items_db}

@router.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    """获取单个项目"""
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="项目未找到")
    return items_db[item_id]

@router.post("/items", response_model=ItemResponse, tags=["items"])
async def create_item(item: ItemCreate):
    """创建新项目"""
    new_item = {
        "id": len(items_db),
        "name": item.name,
        "description": item.description,
        "price": item.price
    }
    items_db.append(new_item)
    return new_item

@router.put("/items/{item_id}", response_model=ItemResponse, tags=["items"])
async def update_item(item_id: int, item: ItemCreate):
    """更新项目"""
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="项目未找到")
    
    updated_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price
    }
    items_db[item_id] = updated_item
    return updated_item

@router.delete("/items/{item_id}", tags=["items"])
async def delete_item(item_id: int):
    """删除项目"""
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="项目未找到")
    
    deleted_item = items_db.pop(item_id)
    return {"message": "项目已删除", "item": deleted_item}
