from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from typing import List
from db.client import db_client
from db.schemas.user import user_schema, users_schema
from bson import ObjectId

router = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}}
                   )



@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

# Path
@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))
# Query
@router.get("/")
async def user(id: str):
    return search_user("_id", ObjectId(id))

# Post
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está en uso")
    
    user_dict = dict(user)
    del user_dict["id"]
    
    id = db_client.users.insert_one(user_dict).inserted_id
    
    new_user  = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)


# Put
@router.put("/", response_model=User)
async def update_user(user: User):
    
    user_dict = dict(user)
    del user_dict["id"]

    try:
        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error": "No se ha actualizado ningún usuario"}
        
    
    return search_user("_id", ObjectId(user.id))
 


# Delete
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    
    if not found:
        return {"error": "No se ha eliminado ningún usuario"}

# Function search user by email
def search_user(field: str, key):
    try:
        user = user_schema(db_client.users.find_one({field: key}))
        return User(**user)
    except:
        return {"error": "Usuario no encontrado"}
    
