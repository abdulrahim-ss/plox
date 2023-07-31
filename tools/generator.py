import argparse

def define_ast(output_dir:str, name:str, types:dict) -> None:
    path = output_dir + "/" + name + ".py"
    with open(path, "w") as f:
        f.write("from plox_token import PloxToken\n")
        if name != "Expr":
            f.write("from Expr import Expr\n\n")
        f.write(f"\nclass {name}:\n")
        f.write("\tdef accept(self, visitor):\n")
        f.write("\t\tpass\n\n\n")

        for type, fields in types.items():
            define_type(f, name, type, fields)

        define_visitor(f, name, types)

        f.close()

def define_visitor(file, basename:str, types: dict) -> None:
    file.write(f"class {basename}Visitor:\n")
    for type in types.keys():
        file.write(f"\tdef visit{type}(self, expr:{type}):\n")
        file.write("\t\traise NotImplementedError\n\n")

def define_type(file, basename: str, classname:str, fields: list) -> None:
    file.write(f"class {classname}({basename}):\n")
    init_args = ""
    for field in fields:
        init_args += ", " + field['name'] + ": " + field["type"]
    file.write(f"\tdef __init__(self{init_args}):\n")
    for field in fields:
        temp_name = field['name']
        file.write(f"\t\tself.{temp_name} = {temp_name}\n")

    file.write(f"\n\tdef accept(self, visitor):\n")
    file.write(f"\t\treturn visitor.visit{classname}(self)\n")

    file.write(f"\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="syntax tree generator")
    parser.add_argument("output", type=str)
    args = parser.parse_args()
    if not args.output:
        print("Please provide outoput path")
        exit(64)
    output = args.output

    expr = {
        "Assign": [
            {"type": "PloxToken", "name": "name"},
            {"type": "Expr", "name": "value"},
        ],
        "Binary": [
            {"type": "Expr", "name": "left"},
            {"type": "PloxToken", "name": "operator"},
            {"type": "Expr", "name": "right"},
        ],
        "Grouping": [
            {"type": "Expr", "name": "expression"},
        ],
        "Literal": [
            {"type": "object", "name": "value"},
        ],
        "Unary": [
            {"type": "PloxToken", "name": "operator"},
            {"type": "Expr", "name": "right"},
        ],
        "Conditional": [
            {"type": "Expr", "name": "condition"},
            {"type": "Expr", "name": "then_clause"},
            {"type": "Expr", "name": "else_clause"},
        ],
        "Variable": [
            {"type": "PloxToken", "name": "name"},
        ],
    }
    stmt = {
        "Expression": [
            {"type": "Expr", "name": "expression"},
        ],
        "Print": [
            {"type": "Expr", "name": "expression"},
        ],
        "Var": [
            {"type": "PloxToken", "name": "name"},
            {"type": "Expr", "name": "Initializer"},
        ],
    }
    define_ast(output, "Expr", expr)
    define_ast(output, "Stmt", stmt)