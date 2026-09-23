
async def build_layout():
    import subprocess

    CONTAINER = "llm_sandbox"

    # Check if structure already exists
    check_script = "[ -f /workspace/app/main.py ] && echo 'exists' || echo 'missing'"
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", check_script],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if "exists" in result.stdout:
        print("✅ Structure already exists, skipping creation.")
        return

    script = r"""
    mkdir -p \
    /workspace/app/config \
    /workspace/app/api/v1 \
    /workspace/app/models \
    /workspace/app/schemas \
    /workspace/app/services \
    /workspace/app/repositories \
    /workspace/app/core \
    /workspace/app/db/migrations \
    /workspace/app/tasks \
    /workspace/app/integrations \
    /workspace/app/storage \
    /workspace/app/search \
    /workspace/app/cache \
    /workspace/app/events \
    /workspace/app/permissions \
    /workspace/app/utils \
    /workspace/app/tests

    find /workspace/app -type d -exec touch {}/__init__.py \;

    touch \
    /workspace/app/main.py \
    /workspace/app/config/settings.py \
    /workspace/app/config/logging.py \
    /workspace/app/config/security.py \
    /workspace/app/config/database.py \
    /workspace/app/api/dependencies.py \
    /workspace/app/api/middleware.py \
    /workspace/app/api/exceptions.py \
    /workspace/app/api/v1/router.py \
    /workspace/app/api/v1/auth.py \
    /workspace/app/api/v1/users.py \
    /workspace/app/api/v1/products.py \
    /workspace/app/api/v1/categories.py \
    /workspace/app/api/v1/brands.py \
    /workspace/app/api/v1/inventory.py \
    /workspace/app/api/v1/cart.py \
    /workspace/app/api/v1/orders.py \
    /workspace/app/api/v1/checkout.py \
    /workspace/app/api/v1/payments.py \
    /workspace/app/api/v1/shipping.py \
    /workspace/app/api/v1/coupons.py \
    /workspace/app/api/v1/reviews.py \
    /workspace/app/api/v1/wishlist.py \
    /workspace/app/api/v1/addresses.py \
    /workspace/app/api/v1/notifications.py \
    /workspace/app/api/v1/admin.py \
    /workspace/app/db/base.py \
    /workspace/app/db/session.py \
    /workspace/app/db/seed.py
    """

    subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", script],
        check=True,
    )

    print("✅ FastAPI project structure created successfully.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(build_layout())