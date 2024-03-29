from marshmallow import Schema, fields, post_load

from omtool.core.configs import InputConfig


class InputConfigSchema(Schema):
    format = fields.Str(
        required=True, description="Format of the input file. Can be 'csv' or 'fits'."
    )
    filenames = fields.List(
        fields.Str(),
        required=True,
        description="List of filenames. In case of csv file they will be stacked together, in case "
        "of fits only the first one will be taken and the rest will be ignored.",
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return InputConfig(**data)
