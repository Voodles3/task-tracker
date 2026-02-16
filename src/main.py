import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TypedDict

from pydantic import BaseModel, ValidationError

USER_DATA_PATH = Path("src") / "data" / "user_data.json"

NEW_USER_MESSAGE = """
Welcome to Task Tracker Extreme!
This is the best task tracker CLI program that has ever been made.
If the application is unsatisfactory, please reach out to me with your full name, phone number, email, and home address, and I'll be sure to make it right.
\n"""


class UserData(BaseModel):
    name: str | None = None
    age: str | None = None


class UserDataReadError(Exception):
    pass


class UserDataWriteError(Exception):
    pass


# class UserData(TypedDict, total=False):
#     name: str | None
#     age: str | None


def help_command():
    print("WORKED")


def read_user_data() -> UserData:
    try:
        with USER_DATA_PATH.open("r", encoding="UTF-8") as f:
            data = json.load(f)
            return UserData.model_validate(data)

    except FileNotFoundError as e:
        raise UserDataReadError(f"Missing file: {USER_DATA_PATH}") from e
    except json.JSONDecodeError as e:
        raise UserDataReadError(f"Invalid JSON in {USER_DATA_PATH}: {e}") from e
    except ValidationError as e:
        raise UserDataReadError(
            f"Invalid user data schema in {USER_DATA_PATH}: {e}"
        ) from e


def update_user_data(updated_data: dict[str, Any]) -> None:
    tmp_path = USER_DATA_PATH.with_suffix(USER_DATA_PATH.suffix + ".tmp")

    data = read_user_data().model_dump()
    data |= updated_data
    validated_data = UserData.model_validate(data)
    try:
        with tmp_path.open("w", encoding="UTF-8") as f:
            json.dump(validated_data, f)
        os.replace(tmp_path, USER_DATA_PATH)
    except Exception as e:
        raise UserDataWriteError(f"Failed to update user data: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)


command_map: dict[str, Callable] = {
    "help": help_command,
    "devwrite": update_user_data,
    "exit": exit,
}


def main():
    user_data = read_user_data()
    if not user_data.name:
        print(NEW_USER_MESSAGE)
        name = input("To start, what's your name?\n")
        update_user_data({"name": name})
        print(f"Glad you're here, {name}!")

    else:
        print(f"Welcome back, {user_data.name}!")

    while True:
        user_input = input(
            "What would you like to do? (type 'help' for commands, 'exit' to exit)\n"
        )
        input_words = user_input.split()
        if not input_words:
            continue

        command = input_words[0]
        args = []

        if len(input_words) >= 2:
            args = input_words[1:]

        print(f"    COMMAND: {command}")
        print(f"    ARGS: {args}")
        if command in command_map:
            command_map[user_input](*args)


if __name__ == "__main__":
    main()
