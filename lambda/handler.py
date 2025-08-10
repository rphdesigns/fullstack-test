import os
import json
import uuid
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME")
table = dynamodb.Table(TABLE_NAME)

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    http_method = event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod")
    path = event.get("rawPath") or event.get("path") or ""
    body = event.get("body")
    if body and isinstance(body, str):
        try:
            body = json.loads(body)
        except:
            body = {}

    # GET /items
    if http_method == "GET" and path.endswith("/items"):
        items = table.scan().get("Items", [])
        return response(200, items)

    # POST /items
    if http_method == "POST" and path.endswith("/items"):
        item_id = str(uuid.uuid4())
        item = {
            "id": item_id,
            "title": body.get("title",""),
            "completed": body.get("completed", False)
        }
        table.put_item(Item=item)
        return response(201, item)

    # GET /items/{id}
    if http_method == "GET" and "/items/" in path:
        item_id = path.split("/items/")[-1]
        res = table.get_item(Key={"id": item_id})
        item = res.get("Item")
        if not item:
            return response(404, {"message":"Not found"})
        return response(200, item)

    # PUT /items/{id}
    if http_method == "PUT" and "/items/" in path:
        item_id = path.split("/items/")[-1]
        update = {}
        if "title" in body:
            update["title"] = body["title"]
        if "completed" in body:
            update["completed"] = body["completed"]
        # simple replace
        item = {"id": item_id, **update}
        table.put_item(Item=item)
        return response(200, item)

    # DELETE /items/{id}
    if http_method == "DELETE" and "/items/" in path:
        item_id = path.split("/items/")[-1]
        table.delete_item(Key={"id": item_id})
        return response(204, {})

    return response(400, {"message":"Unsupported route"})
