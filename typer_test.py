import typer

## More info: https://typer.tiangolo.com/
def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)