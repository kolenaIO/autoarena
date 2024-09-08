import argparse

import uvicorn


if __name__ == "__main__":
    ap = argparse.ArgumentParser("autoarena")
    ap.add_argument("-d", "--dev", action="store_true", help="Run in development mode")
    args = ap.parse_args()
    uvicorn.run("autoarena.main:main", host="localhost", port=8899, reload=args.dev, factory=True)
