import uvicorn

from autostack.args import get_command_line_args
from autostack.log import initialize_logger

if __name__ == "__main__":
    args = get_command_line_args()
    initialize_logger()
    uvicorn.run("autostack.main:app", host="0.0.0.0", port=8899, reload=args.dev)
