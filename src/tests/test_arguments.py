from typing import Annotated, Literal

import pytest
import typer
from pydantic import BaseModel
from typer.testing import CliRunner

from typer_model_args import flatten_parameter_model_to_signature


class CliArgs(BaseModel):
    argument: Annotated[
        str,
        typer.Option("--nested-arg")
    ]

runner = CliRunner()

class TestAnnotatedKeepTyperProps:

    def test_flattens_parameters(self):

        @flatten_parameter_model_to_signature()
        def my_cli_function(
            cli_arg: Annotated[str, typer.Option("--first-level-arg")],
            cli_args_class: CliArgs,
        ):
            pass

        my_cli_function(argument="value", cli_arg="value2")


    def test_keep_annotated_typer_properties(self):
        app = typer.Typer()

        @app.command()
        @flatten_parameter_model_to_signature()
        def my_cli_function(
                cli_arg: Annotated[str, typer.Option("--first-level-arg")],
                cli_args_class: CliArgs
        ):
            pass

        result = runner.invoke(app, ["--nested-arg", "value1", "--first-level-arg", "value2"])

        assert result.exit_code == 0

    def test_flat_duplicated_keys_raise_error(self):

        with pytest.raises(Exception) as exec_info:
            @flatten_parameter_model_to_signature()
            def my_cli_function(
                argument: Annotated[str, typer.Option("--first-level-arg")],
                cli_args_class: CliArgs,
            ):
                pass

        assert exec_info.errisinstance(ValueError)
        assert str(exec_info.value) == "duplicate parameter name: 'argument'"

    def test_replace_literals_on_existing_typer_annotations(self):
        app = typer.Typer()

        class CliArgsWithLiteral(BaseModel):
            argument: Annotated[Literal["yes", "no"], typer.Option()] = "yes"

        @app.command()
        @flatten_parameter_model_to_signature(literals_to_enums=True)
        def my_cli_function(
            cli_args_class: CliArgsWithLiteral,
        ):
            pass

        result = runner.invoke(app, ["--argument", "yes"])

        assert result.exit_code == 0


