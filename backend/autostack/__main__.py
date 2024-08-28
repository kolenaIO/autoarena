import sys
import uvicorn

if __name__ == "__main__":
    print(
        """
!!!!!!!!!! WARNING !!!!!!!!!!
* * * * * * * * * * * * * * *
* running in developer mode *
* ------------------------- *
*  not for production use   *
* * * * * * * * * * * * * * *
!!!!!!!!!! WARNING !!!!!!!!!!
""",
        file=sys.stderr,
    )

    uvicorn.run(
        "autostack.main:app",
        host="0.0.0.0",
        port=8899,
        reload=True,
    )
