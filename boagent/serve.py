#!/usr/bin/env python3

import uvicorn

if __name__ == "__main__":
    '''
    Entrypoint to run the FastAPI application (without using the FastAPI/Uvicorn CLI).
    Because a python script can't import relatively, we apply a sys.path hack to import the application.

    Typically you do not need this and simply invoke one of the following:
    * rye run fastapi dev ./src/backend/app.py
    * fastapi run dev ./src/backend/app.py
    '''
    import os
    import sys

    sys.path.append(os.path.abspath('../'))

    from api import configure_app

    app = configure_app
    uvicorn.run(app, host="0.0.0.0", port=8000)
