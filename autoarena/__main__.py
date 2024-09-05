import uvicorn

from autoarena.args import get_command_line_args

if __name__ == "__main__":
    args = get_command_line_args()
    uvicorn.run("autoarena.main:app", host="localhost", port=8899, reload=args.dev)
