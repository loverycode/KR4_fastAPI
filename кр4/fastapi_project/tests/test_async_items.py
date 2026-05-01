import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from main import app

fake = Faker()

@pytest.fixture(autouse=True)
def clean_async_db():
    """Очищает in-memory хранилище перед каждым тестом"""
    from main import async_items_db, async_items_counter
    async_items_db.clear()
    async_items_counter = 1
    yield
    async_items_db.clear()


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_item_success(async_client):
    """Тест успешного создания элемента (201)"""
    item_data = {
        "name": fake.name(),
        "quantity": fake.random_int(min=1, max=100),
        "price": fake.random_int(min=10, max=1000)
    }
    
    response = await async_client.post("/async/items", params=item_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == item_data["name"]
    assert data["quantity"] == item_data["quantity"]
    assert data["price"] == item_data["price"]


@pytest.mark.asyncio
async def test_create_item_minimal_data(async_client):
    response = await async_client.post("/async/items", params={"name": fake.name()})
    
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 1
    assert data["price"] == 0


@pytest.mark.asyncio
async def test_get_existing_item(async_client):
    create_response = await async_client.post("/async/items", params={"name": "Test Item", "quantity": 5})
    item_id = create_response.json()["id"]
    response = await async_client.get(f"/async/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["quantity"] == 5
    assert data["name"] == "Test Item"


@pytest.mark.asyncio
async def test_get_nonexistent_item(async_client):
    response = await async_client.get("/async/items/99999")
    
    assert response.status_code == 404
    assert "not found" in response.text.lower()


@pytest.mark.asyncio
async def test_delete_existing_item(async_client):
    create_response = await async_client.post("/async/items", params={"name": "To Delete"})
    item_id = create_response.json()["id"]
    response = await async_client.delete(f"/async/items/{item_id}")
    assert response.status_code == 204
    get_response = await async_client.get(f"/async/items/{item_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_item(async_client):
    response = await async_client.delete("/async/items/99999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()


@pytest.mark.asyncio
async def test_delete_twice(async_client):
    create_response = await async_client.post("/async/items", params={"name": "Double Delete"})
    item_id = create_response.json()["id"]
    response1 = await async_client.delete(f"/async/items/{item_id}")
    assert response1.status_code == 204
    response2 = await async_client.delete(f"/async/items/{item_id}")
    assert response2.status_code == 404


@pytest.mark.asyncio
async def test_multiple_items_with_faker(async_client):
    created_ids = []
    for _ in range(5):
        name = fake.name()
        quantity = fake.random_int(min=1, max=100)
        price = fake.random_int(min=10, max=1000)
        response = await async_client.post("/async/items", params={
            "name": name, "quantity": quantity, "price": price
        })
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    for item_id in created_ids:
        response = await async_client.get(f"/async/items/{item_id}")
        assert response.status_code == 200
    for item_id in created_ids:
        response = await async_client.delete(f"/async/items/{item_id}")
        assert response.status_code == 204
        get_response = await async_client.get(f"/async/items/{item_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_boundary_values(async_client):
    response_min = await async_client.post("/async/items", params={"name": "a", "quantity": 0, "price": 0})
    assert response_min.status_code == 201
    response_negative = await async_client.post("/async/items", params={"name": "negative", "quantity": -5, "price": -100})
    assert response_negative.status_code == 201

    long_name = "x" * 1000
    response_long = await async_client.post("/async/items", params={"name": long_name})
    assert response_long.status_code == 201
    assert len(response_long.json()["name"]) == 1000
