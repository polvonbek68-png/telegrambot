import asyncio
from keep_alive import keep_alive
import main  # bu sizning main.py

# Flask serverni ishga tushiramiz
keep_alive()

# Botni ishga tushiramiz
if __name__ == "__main__":
    asyncio.run(main.main())